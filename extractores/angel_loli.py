"""
Extractor para ALFARERIA ANGEL Y LOLI (Lorenzo Lores García)

Alfarería artesanal de Níjar (Almería).
NIF: 75727068M

Formato factura (pdfplumber):
ARTÍCULO         CANTIDAD  PRECIO  TOTAL
PLATO LLANO      20        5,70    114,00
PLATO POSTRE     50        3,72    186,00
CUENCO           15        3,47    52,05

Cuadro fiscal con portes:
TIPO    IMPORTE   DESCUENTO   PORTES   BASE      I.V.A.    R.E.
21,00   549,50               45,00    594,50   124,85

IVA: 21%
Categoría fija: CACHARRERIA
NOTA: Los portes (ej: 45€) se prorratean proporcionalmente entre artículos

Creado: 26/12/2025
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar('ALFARERIA ANGEL Y LOLI', 'ANGEL Y LOLI', 'LORENZO LORES')
class ExtractorAngelLoli(ExtractorBase):
    """Extractor para facturas de ALFARERIA ANGEL Y LOLI."""
    
    nombre = 'ALFARERIA ANGEL Y LOLI'
    cif = '75727068M'
    iban = ''  # Pago transferencia (IBAN no disponible en factura)
    metodo_pdf = 'pdfplumber'
    categoria_fija = 'CACHARRERIA'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de productos y prorratea portes.
        
        Formato:
        PLATO LLANO 20 5,70 114,00
        """
        lineas = []
        portes = 0.0
        
        # Primero extraer portes del cuadro fiscal
        match_portes = re.search(r'PORTES\s+(\d+[.,]\d{2})', texto, re.IGNORECASE)
        if match_portes:
            portes = self._convertir_europeo(match_portes.group(1))
        
        # Alternativa: buscar en línea de totales "45,00" antes de BASE
        if portes == 0:
            match_portes2 = re.search(
                r'21,00\s+[\d.,]+\s+([\d.,]+)\s+[\d.,]+\s+[\d.,]+', 
                texto
            )
            if match_portes2:
                portes = self._convertir_europeo(match_portes2.group(1))
        
        for linea in texto.split('\n'):
            linea = linea.strip()
            if not linea:
                continue
            
            # Ignorar cabeceras y totales
            if any(x in linea.upper() for x in ['ARTÍCULO', 'CANTIDAD', 'PRECIO',
                                                  'DOCUMENTO', 'NÚMERO', 'PÁGINA',
                                                  'FECHA', 'OBSERVACIONES', 'TOTAL',
                                                  'TIPO', 'IMPORTE', 'DESCUENTO',
                                                  'PORTES', 'BASE', 'I.V.A', 'R.E.',
                                                  'FACTURA', 'LORENZO', 'LORES',
                                                  'ALFARERÍA', 'NÍJAR', 'ALMERIA',
                                                  'TASCA BAREA', 'RODAS', 'MADRID']):
                continue
            
            # Patrón: DESCRIPCION CANTIDAD PRECIO TOTAL
            # "PLATO LLANO 20 5,70 114,00"
            match = re.match(
                r'^([A-ZÁÉÍÓÚÑa-záéíóúñ][A-ZÁÉÍÓÚÑa-záéíóúñ\s]+?)\s+'  # Descripción
                r'(\d+)\s+'                                              # Cantidad
                r'(\d+[.,]\d{2})\s+'                                     # Precio
                r'(\d+[.,]\d{2})$',                                      # Total
                linea
            )
            
            if match:
                descripcion = match.group(1).strip()
                cantidad = int(match.group(2))
                precio = self._convertir_europeo(match.group(3))
                total = self._convertir_europeo(match.group(4))
                
                if total > 0 and len(descripcion) >= 3:
                    lineas.append({
                        'codigo': '',
                        'articulo': descripcion[:50],
                        'cantidad': cantidad,
                        'precio_ud': round(precio, 2),
                        'iva': 21,
                        'base': round(total, 2),
                        'categoria': self.categoria_fija
                    })
        
        # Prorratear portes si hay
        if portes > 0 and lineas:
            total_productos = sum(l['base'] for l in lineas)
            if total_productos > 0:
                for linea in lineas:
                    proporcion = linea['base'] / total_productos
                    porte_linea = portes * proporcion
                    linea['base'] = round(linea['base'] + porte_linea, 2)
                    if linea['cantidad'] > 0:
                        linea['precio_ud'] = round(linea['base'] / linea['cantidad'], 2)
        
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
        # Formato final: "TOTAL: 719,35"
        m = re.search(r'TOTAL[:\s]*(\d+[.,]\d{2})\s*$', texto, re.MULTILINE)
        if m:
            return self._convertir_europeo(m.group(1))
        
        # Alternativa: última línea con número grande
        m = re.search(r'(\d{3,}[.,]\d{2})\s*$', texto)
        if m:
            return self._convertir_europeo(m.group(1))
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        # Formato: "03/07/2025"
        m = re.search(r'(\d{2})/(\d{2})/(\d{4})', texto)
        if m:
            return f"{m.group(1)}/{m.group(2)}/{m.group(3)}"
        
        return None
