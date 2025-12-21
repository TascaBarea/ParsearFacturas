"""
Extractor para DISTRIBUCIONES LAVAPIES S.COOP.MAD.

Distribuidor de bebidas, refrescos, aguas, zumos.

Formato factura:
07/03/25 250150
...
N ALBARAN REF. DESCRIPCION CANT. DTO. IMPORTE TOTAL
149/2025 REFREV2 REVOLTOSA 2L LIMON 6 0,8 4,80 E
149/2025 REFCAS1 GASEOSA CASERA 1.5 L 6 0,87 5,22 E
...
BASE IMP. AL 21% 89,22 IVA 21% 18,74
BASE IMP. AL 10% 71,76 IVA 10% 7,18
...
TOTAL 107,96 E

NOTAS:
- IVA mixto: 10% para bebidas no alcoholicas, 21% para otros
- Formato linea: ALBARAN REF DESCRIPCION CANTIDAD PRECIO IMPORTE
- Total incluye IVA y posible recargo equivalencia

CIF: F88424072
IBAN: ES39 3035 0376 14 3760011213

Creado: 19/12/2025
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar('DISTRIBUCIONES LAVAPIES', 'LAVAPIES')
class ExtractorLavapies(ExtractorBase):
    """Extractor para facturas de Distribuciones Lavapies."""
    
    nombre = 'DISTRIBUCIONES LAVAPIES'
    cif = 'F88424072'
    iban = 'ES39 3035 0376 14 3760011213'
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae lineas de la factura.
        
        NOTA: Las facturas de Lavapies muestran IVA mixto pero los porcentajes
        reales pueden estar intercambiados en el PDF. Para cuadrar, extraemos
        las bases y los IVAs directamente del PDF.
        """
        lineas = []
        
        # Extraer bases e IVAs del PDF
        # Formato: BASE IMP. AL 21% 70,38 IVA 21% 7,04
        m21 = re.search(r'BASE\s+IMP\.\s+AL\s+21%\s+(\d+,\d{2})\s+IVA\s+21%\s+(\d+,\d{2})', texto)
        m10 = re.search(r'BASE\s+IMP\.\s+AL\s+10%\s+(\d+,\d{2})\s+IVA\s+10%\s+(\d+,\d{2})', texto)
        
        # Alternativo sin IVA explicito
        if not m21:
            m21 = re.search(r'BASE\s+IMP\.\s+AL\s+21%\s+(\d+,\d{2})', texto)
        if not m10:
            m10 = re.search(r'BASE\s+IMP\.\s+AL\s+10%\s+(\d+,\d{2})', texto)
        
        if m21:
            base_21 = self._convertir_europeo(m21.group(1))
            iva_21 = self._convertir_europeo(m21.group(2)) if len(m21.groups()) > 1 else base_21 * 0.21
            
            # Calcular el IVA real basado en el importe
            if base_21 > 0:
                iva_real = round(iva_21 / base_21 * 100, 0)
                lineas.append({
                    'codigo': '',
                    'articulo': 'BEBIDAS Y REFRESCOS',
                    'cantidad': 1,
                    'precio_ud': base_21,
                    'iva': int(iva_real) if iva_real in [10, 21] else 21,
                    'base': round(base_21, 2),
                    '_iva_importe': round(iva_21, 2)  # Guardar IVA real para validacion
                })
        
        if m10:
            base_10 = self._convertir_europeo(m10.group(1))
            iva_10 = self._convertir_europeo(m10.group(2)) if len(m10.groups()) > 1 else base_10 * 0.10
            
            if base_10 > 0:
                iva_real = round(iva_10 / base_10 * 100, 0)
                lineas.append({
                    'codigo': '',
                    'articulo': 'BEBIDAS',
                    'cantidad': 1,
                    'precio_ud': base_10,
                    'iva': int(iva_real) if iva_real in [10, 21] else 10,
                    'base': round(base_10, 2),
                    '_iva_importe': round(iva_10, 2)
                })
        
        return lineas
    
    def _convertir_europeo(self, texto: str) -> float:
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
        """
        Total en formato: TOTAL 107,96 E
        """
        patron = re.search(r'TOTAL\s+(\d+,\d{2})\s*€', texto, re.IGNORECASE)
        if patron:
            return self._convertir_europeo(patron.group(1))
        
        # Alternativo: buscar en vencimiento
        patron2 = re.search(r'VENCIMIENTO:\s*\d{2}/\d{2}/\d{2}\s+(\d+,\d{2})\s*€', texto)
        if patron2:
            return self._convertir_europeo(patron2.group(1))
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """
        Fecha en formato: 07/03/25 250150
        """
        patron = re.search(r'^(\d{2})/(\d{2})/(\d{2})\s+\d{6}', texto, re.MULTILINE)
        if patron:
            dia = patron.group(1)
            mes = patron.group(2)
            anio = patron.group(3)
            anio_completo = f"20{anio}" if int(anio) < 50 else f"19{anio}"
            return f"{dia}/{mes}/{anio_completo}"
        
        # Alternativo: buscar FECHA seguido de fecha
        patron2 = re.search(r'FECHA[^\d]*(\d{2})/(\d{2})/(\d{2})', texto)
        if patron2:
            dia = patron2.group(1)
            mes = patron2.group(2)
            anio = patron2.group(3)
            anio_completo = f"20{anio}"
            return f"{dia}/{mes}/{anio_completo}"
        
        return None
