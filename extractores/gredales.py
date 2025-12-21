"""
Extractor para LOS GREDALES DE EL TOBOSO.
Vinos ecológicos.
CIF: B83594150 | IBAN: ES82 2103 7178 2800 3001 2932

Actualizado: 18/12/2025 - pdfplumber
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict
import re


@registrar('LOS GREDALES', 'GREDALES', 'LOS GREDALES DEL TOBOSO', 'GREDALES DE EL TOBOSO')
class ExtractorGredales(ExtractorBase):
    nombre = 'LOS GREDALES'
    cif = 'B83594150'
    iban = 'ES82 2103 7178 2800 3001 2932'
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        
        patron_base = re.search(r'BASE IMPONIBLE\s*([\d,]+)\s*€', texto, re.IGNORECASE)
        
        if patron_base:
            base = self._convertir_importe(patron_base.group(1))
            lineas.append({
                'codigo': 'GREDALES',
                'articulo': 'VINOS ECOLOGICOS LOS GREDALES',
                'cantidad': 1,
                'precio_ud': base,
                'iva': 21,
                'base': base
            })
        
        return lineas
