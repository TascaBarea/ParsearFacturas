"""
Extractor para FRANCISCO GUERRA.
Carnes y embutidos.
CIF: 50449614B | IBAN: ES70 0049 4007 1428 1402 7169
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict
import re


@registrar('FRANCISCO GUERRA', 'GUERRA')
class ExtractorFranciscoGuerra(ExtractorBase):
    nombre = 'FRANCISCO GUERRA'
    cif = '50449614B'
    iban = 'ES70 0049 4007 1428 1402 7169'
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        
        patron = re.compile(
            r'^(\d{3,5})\s+'
            r'(.+?)\s{2,}'
            r'(\d+)\s+'
            r'(\d+[,\.]\d{2})\s+'
            r'(\d+[,\.]\d{2,3})$',
            re.MULTILINE
        )
        
        for match in patron.finditer(texto):
            codigo, articulo, cantidad, importe, precio = match.groups()
            articulo_limpio = articulo.strip()
            
            if any(x in articulo_limpio for x in ['Albarán', 'ALBARAN', 'Descripción']):
                continue
                
            lineas.append({
                'codigo': codigo,
                'articulo': articulo_limpio,
                'cantidad': int(cantidad),
                'precio_ud': self._convertir_importe(precio),
                'iva': 10,
                'base': self._convertir_importe(importe)
            })
        
        return lineas
