"""
Extractor para QUESOS NAVAS.
Quesos artesanales.
CIF: B37416419 | IBAN: ES62 2100 6153 0402 0001 6597
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict
import re


@registrar('CARLOS NAVAS', 'QUESERIA CARLOS NAVAS', 'QUESERIA NAVAS', 'QUESOS NAVAS')
class ExtractorQuesosNavas(ExtractorBase):
    nombre = 'QUESOS NAVAS'
    cif = 'B37416419'
    iban = 'ES62 2100 6153 0402 0001 6597'
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        
        patron = re.compile(
            r'(\d{1,2}[,\.]\d{3})'
            r'(\d{1,2})\s+'
            r'(QUESO[A-ZÑÁÉÍÓÚ\s\d]+?)\s+'
            r'(\d+[,\.]\d{3})\s+'
            r'(\d+[,\.]\d{2})\s+'
            r'(\d+[,\.]\d{2})'
            r'(\d{3,5})?',
            re.MULTILINE
        )
        
        for match in patron.finditer(texto):
            cantidad, codigo, articulo, precio, iva, subtotal, lote = match.groups()
            articulo_limpio = articulo.strip()
            iva_valor = int(float(iva.replace(',', '.')))
                
            lineas.append({
                'codigo': codigo,
                'articulo': articulo_limpio,
                'cantidad': self._convertir_importe(cantidad),
                'precio_ud': self._convertir_importe(precio),
                'iva': iva_valor,
                'base': self._convertir_importe(subtotal)
            })
        
        return lineas
