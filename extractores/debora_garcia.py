"""
Extractor para DEBORA GARCIA TOLEDANO

Suministro de CO2 alimentario para cerveza.
NIF: 47524622K
IBAN: ES84 0049 0821 9627 1013 3112 (Banco Santander)

Formato factura (pdfplumber) - NOTA: el nombre del artículo viene partido:
BOTELLA 10KG CO2
40,00 € 8,40 € (21%) -0,40 € (1%) 48,00 €
ALIMENTARIO

o con cantidad:
BOTELLA 10KG CO2
40,00 € 2 80,00 € 16,80 € (21%) -0,80 € (1%) 96,00 €
ALIMENTARIO

IVA: 21%
IRPF: 1% (retención)
Categoría fija: Co2 GAS PARA LA CERVEZA

Creado: 26/12/2025
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar('DEBORA GARCIA TOLEDANO', 'DEBORAH GARCIA', 'DEBORA GARCIA', 
           'BEDORAH GARCIA TOLEDANO', 'DG CO2')
class ExtractorDeboraGarcia(ExtractorBase):
    """Extractor para facturas de DEBORA GARCIA TOLEDANO (CO2)."""
    
    nombre = 'DEBORA GARCIA'
    cif = '47524622K'
    iban = 'ES84 0049 0821 9627 1013 3112'
    metodo_pdf = 'pdfplumber'
    categoria_fija = 'Co2 GAS PARA LA CERVEZA'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae línea de CO2.
        
        El texto viene partido:
        BOTELLA 10KG CO2
        40,00 € [Q] [BASE] 16,80 € (21%) -0,80 € (1%) 96,00 €
        ALIMENTARIO
        """
        lineas = []
        
        # Buscar "Base imponible" para obtener la base
        match_base = re.search(
            r'Base\s+imponible\s+(\d+[.,]\d{2})\s*€',
            texto,
            re.IGNORECASE
        )
        
        if match_base:
            base = self._convertir_europeo(match_base.group(1))
            
            # Buscar cantidad en el patrón con Q (cantidad)
            # Formato: "40,00 € 2 80,00 €" o "40,00 € 3 120,00 €"
            cantidad = 1
            
            # Patrón para formato con cantidad: PRECIO_UD € CANTIDAD BASE €
            match_con_cantidad = re.search(
                r'(\d+[.,]\d{2})\s*€\s+(\d+)\s+(\d+[.,]\d{2})\s*€\s+\d+[.,]\d{2}\s*€\s*\(21%\)',
                texto
            )
            
            if match_con_cantidad:
                precio_ud = self._convertir_europeo(match_con_cantidad.group(1))
                cantidad = int(match_con_cantidad.group(2))
                base_linea = self._convertir_europeo(match_con_cantidad.group(3))
                # Verificar que cuadra
                if abs(precio_ud * cantidad - base_linea) < 0.01:
                    base = base_linea
            
            if base > 0:
                lineas.append({
                    'codigo': '',
                    'articulo': 'BOTELLA 10KG CO2 ALIMENTARIO',
                    'cantidad': cantidad,
                    'precio_ud': round(base / cantidad, 2) if cantidad else base,
                    'iva': 21,
                    'base': round(base, 2),
                    'categoria': self.categoria_fija
                })
        
        return lineas
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo a float."""
        if not texto:
            return 0.0
        texto = texto.strip()
        if '.' in texto and ',' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            texto = texto.replace(',', '.')
        try:
            return float(texto)
        except:
            return 0.0
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """Extrae total de la factura."""
        # Formato: "Total 48,00 €" o "Total 96,00 €"
        m = re.search(r'^Total\s+(\d+[.,]\d{2})\s*€', texto, re.MULTILINE | re.IGNORECASE)
        if m:
            return self._convertir_europeo(m.group(1))
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        # Formato: "Emitida 02/10/2025"
        m = re.search(r'Emitida\s+(\d{2})/(\d{2})/(\d{4})', texto)
        if m:
            return f"{m.group(1)}/{m.group(2)}/{m.group(3)}"
        
        return None
