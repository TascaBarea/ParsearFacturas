"""
Extractor para SABORES DE PATERNA.
Embutidos y carnes.
CIF: B96771832 | IBAN: ES65 2100 8505 1802 0003 1050
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict
import re


@registrar('SABORES DE PATERNA', 'SABORES', 'PATERNA')
class ExtractorSaboresPaterna(ExtractorBase):
    nombre = 'SABORES DE PATERNA'
    cif = 'B96771832'
    iban = 'ES65 2100 8505 1802 0003 1050'
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        
        patron = re.compile(
            r'(\d{2}-\d{2}-\d{2})'
            r'([A-Z][A-Z\s\.\d]+?)\s+'
            r'([\d,]+)\s+'
            r'([\d,]+)\s+'
            r'(\d{1,3}[,\.]\d{2})'
            r'(\d{1,2})[,\.]0\s+'
            r'(\d+[,\.]\d{2})',
            re.MULTILINE
        )
        
        for match in patron.finditer(texto):
            fecha, descripcion, unidades, peso, precio, iva, importe = match.groups()
            descripcion_limpia = descripcion.strip()
            
            if len(descripcion_limpia) > 3:
                peso_val = float(peso.replace(',', '.'))
                uds_val = float(unidades.replace(',', '.'))
                cantidad = peso_val if peso_val > 0.1 else uds_val
                
                lineas.append({
                    'codigo': '',
                    'articulo': descripcion_limpia,
                    'cantidad': cantidad,
                    'precio_ud': self._convertir_importe(precio),
                    'iva': int(iva),
                    'base': self._convertir_importe(importe)
                })
        
        # Porte
        patron_porte = re.compile(
            r'^PORTE\s+[\d,]+\s+[\d,]+\s+(\d+[,\.]\d{2})(\d{1,2})[,\.]0\s+(\d+[,\.]\d{2})',
            re.MULTILINE
        )
        porte_match = patron_porte.search(texto)
        if porte_match:
            precio, iva, importe = porte_match.groups()
            lineas.append({
                'codigo': '',
                'articulo': 'PORTE',
                'cantidad': 1,
                'precio_ud': self._convertir_importe(precio),
                'iva': int(iva),
                'base': self._convertir_importe(importe)
            })
        
        return lineas
