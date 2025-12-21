"""
Extractor para BODEGAS BORBOTÓN.
Vinos de Toledo.
CIF: B45851755 | IBAN: ES37 2100 1913 1902 0013 5677

Actualizado: 18/12/2025 - pdfplumber + limpieza encoding
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict
import re


@registrar('BODEGAS BORBOTON', 'BORBOTON', 'BORBOTÓN')
class ExtractorBorboton(ExtractorBase):
    nombre = 'BODEGAS BORBOTON'
    cif = 'B45851755'
    iban = 'ES37 2100 1913 1902 0013 5677'
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        
        # Patrón principal: CODIGO DESC UDS PRECIO € % € TOTAL €
        patron = re.compile(
            r'^([A-Z]{3}\d{4})\s+(.+?)\s+(\d+)\s+([\d,]+)\s*€\s+[\d,]+\s*%\s+[\d,]+\s*€\s+([\d,]+)\s*€',
            re.MULTILINE
        )
        
        for match in patron.finditer(texto):
            codigo, desc, uds, precio, total = match.groups()
            desc_limpia = re.sub(r'\s+L\.\d+.*$', '', desc.strip())
            desc_limpia = re.sub(r'\s+Vintage.*$', '', desc_limpia, flags=re.IGNORECASE)
            
            lineas.append({
                'codigo': codigo,
                'articulo': desc_limpia.strip(),
                'cantidad': int(uds),
                'precio_ud': self._convertir_importe(precio),
                'iva': 21,
                'base': self._convertir_importe(total)
            })
        
        # Promociones
        patron_promo = re.compile(
            r'^Promoci[oó]n\s+(?:especial\s+)?(?:\d+\+\d+)?\s*(\d+)\s+(-?[\d,]+)\s*€\s+[\d,]+\s*%\s+(-?[\d,]+)\s*€\s+(-?[\d,]+)\s*€',
            re.MULTILINE
        )
        
        for match in patron_promo.finditer(texto):
            uds, precio, ud_precio, total = match.groups()
            lineas.append({
                'codigo': 'PROMO',
                'articulo': 'Promoción especial',
                'cantidad': int(uds),
                'precio_ud': self._convertir_importe(precio),
                'iva': 21,
                'base': self._convertir_importe(total)
            })
        
        return lineas
