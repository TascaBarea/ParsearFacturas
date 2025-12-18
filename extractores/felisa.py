"""
Extractor para FELISA GOURMET (PESCADOS DON FELIX).
CIF: B72113897 | IBAN: ES68 0182 1076 9502 0169 3908
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict
import re


@registrar('FELISA GOURMET', 'FELISA')
class ExtractorFelisa(ExtractorBase):
    nombre = 'FELISA GOURMET'
    cif = 'B72113897'
    iban = 'ES68 0182 1076 9502 0169 3908'
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        
        patron = re.compile(
            r'^([A-Z][A-Z0-9]*)\s+(.+?)\s+([\d,]+)\s+(?:Unidades|Kilos)\s+([\d,]+)\s+([\d,]+)',
            re.MULTILINE
        )
        
        for match in patron.finditer(texto):
            codigo, desc, cantidad, precio, importe = match.groups()
            desc_limpia = desc.strip()
            
            if 'Albaran' in desc_limpia or 'Lote:' in desc_limpia or len(desc_limpia) < 3:
                continue
            
            try:
                cant = self._convertir_importe(cantidad)
            except:
                cant = 1
                
            lineas.append({
                'codigo': codigo,
                'articulo': desc_limpia,
                'cantidad': cant,
                'precio_ud': self._convertir_importe(precio),
                'iva': 10,
                'base': self._convertir_importe(importe)
            })
        
        # TRANSPORTE
        if 'TRANSPORTE' in texto:
            match_transp = re.search(r'TRANSPORTE\s+([\d,]+)', texto)
            if match_transp:
                valor = self._convertir_importe(match_transp.group(1))
                if valor < 50:
                    lineas.append({
                        'codigo': 'TRANSP',
                        'articulo': 'TRANSPORTE',
                        'cantidad': 1,
                        'precio_ud': valor,
                        'iva': 21,
                        'base': valor
                    })
        
        return lineas
