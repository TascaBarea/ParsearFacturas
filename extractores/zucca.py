"""
Extractor para ZUCCA/FORMAGGIARTE.
Quesos italianos.
CIF: B42861948 | IBAN: ES05 1550 0001 2000 1157 7624
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict
import re


@registrar('ZUCCA', 'FORMAGGIARTE', 'QUESERIA ZUCCA')
class ExtractorZucca(ExtractorBase):
    nombre = 'ZUCCA'
    cif = 'B42861948'
    iban = 'ES05 1550 0001 2000 1157 7624'
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        
        patron = re.compile(
            r'^(\d{2,5})\s+'
            r'([A-Za-z][A-Za-z\s\d]+?)\s+'
            r'(\d+[.,]\d+)\s+'
            r'(\d+[.,]\d+)\s+'
            r'(\d+[.,]\d+)\s+'
            r'(\d+[.,]\d+)',
            re.MULTILINE
        )
        
        for match in patron.finditer(texto):
            codigo, articulo, cantidad, precio, subtotal, total = match.groups()
            articulo_limpio = articulo.strip()
            
            if 'Albarán' in articulo_limpio:
                continue
                
            lineas.append({
                'codigo': codigo,
                'articulo': articulo_limpio,
                'iva': 4,
                'base': self._convertir_importe(total)
            })
        
        return lineas
