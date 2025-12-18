"""
Extractor para GADITAUN / María Linarejos.
Patés y conservas gaditanas.
CIF: 34007216Z | IBAN: ES19 0081 0259 1000 0163 8268
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict
import re


@registrar('GADITAUN', 'MARILINA', 'MARIA LINAREJOS')
class ExtractorGaditaun(ExtractorBase):
    nombre = 'GADITAUN'
    cif = '34007216Z'
    iban = 'ES19 0081 0259 1000 0163 8268'
    metodo_pdf = 'ocr'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        
        patron_iva = re.compile(r'(\d{1,2})%\s+([\d,]+)\s*€\s+([\d,]+)\s*€', re.IGNORECASE)
        
        for m in patron_iva.finditer(texto):
            iva = int(m.group(1))
            base = self._convertir_importe(m.group(2))
            
            if base > 0:
                lineas.append({
                    'codigo': 'GADITAUN',
                    'articulo': f'PRODUCTOS GADITAUN IVA {iva}%',
                    'iva': iva,
                    'base': round(base, 2)
                })
        
        if not lineas:
            patron_base = re.search(r'Base\s*Imponible\s*([\d,]+)\s*€', texto, re.IGNORECASE)
            if patron_base:
                base = self._convertir_importe(patron_base.group(1))
                lineas.append({
                    'codigo': 'GADITAUN',
                    'articulo': 'PRODUCTOS GADITAUN',
                    'iva': 10,
                    'base': round(base, 2)
                })
        
        return lineas
