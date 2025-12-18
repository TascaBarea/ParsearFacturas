"""
Extractor para JAMONES Y EMBUTIDOS BERNAL.
CIF: B67784231 | IBAN: ES49 2100 7191 2902 0003 7620
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict
import re


@registrar('JAMONES BERNAL', 'BERNAL', 'EMBUTIDOS BERNAL')
class ExtractorBernal(ExtractorBase):
    nombre = 'JAMONES BERNAL'
    cif = 'B67784231'
    iban = 'ES49 2100 7191 2902 0003 7620'
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        
        patron_linea = re.compile(
            r'([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)([A-Z]{1,3}-[A-Z]+)',
        )
        
        bloques = texto.split('Lotes:')
        
        for bloque in bloques[1:]:
            match = patron_linea.search(bloque)
            if match:
                csec, uds, precio, dto, iva_str, importe, codigo = match.groups()
                
                parte_antes = bloque[:match.start()]
                desc = re.sub(r'^\s*[\d\-A-Z;]+\s*', '', parte_antes)
                desc_limpia = ' '.join(desc.split())
                
                if len(desc_limpia) < 3 or 'Producto' in desc_limpia:
                    continue
                
                try:
                    iva = int(float(iva_str.replace(',', '.')))
                    base = self._convertir_importe(importe)
                except:
                    continue
                    
                lineas.append({
                    'codigo': codigo,
                    'articulo': desc_limpia,
                    'iva': iva,
                    'base': base
                })
        
        return lineas
