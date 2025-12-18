"""
Extractor para LICORES MADRUEÑO S.L.

Distribuidor de licores y vinos.
CIF: B86705126
IBAN: ES78 0081 0259 1000 0184 4495

Formato factura:
- CÓDIGO + UNIDADES pegadas a DESC + IMPORTE,PRECIO
- Ejemplo: 1764 12XIC DA L FONS 43,203,60
- IVA siempre 21%

Creado: 18/12/2025
Migrado de: migracion_historico_2025_v3_57.py (líneas 2277-2315)
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar('LICORES MADRUEÑO', 'MADRUEÑO', 'MARIANO MADRUEÑO')
class ExtractorMadrueño(ExtractorBase):
    """Extractor para facturas de LICORES MADRUEÑO."""
    
    nombre = 'LICORES MADRUEÑO'
    cif = 'B86705126'
    iban = 'ES78 0081 0259 1000 0184 4495'
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de facturas MADRUEÑO.
        
        Las unidades están pegadas a la descripción y el importe+precio
        también están pegados sin espacio.
        """
        lineas = []
        
        # Patrón: unidades pegadas a descripción
        patron = re.compile(
            r'^(\d{1,4})\s+'              # Código
            r'(\d{1,3})'                  # Unidades (pegado)
            r'([A-ZÁÉÍÓÚÜÑa-záéíóúüñ][A-Za-z0-9\s\'\´\-\.\,ñÑáéíóúÁÉÍÓÚüÜ]+?)\s+'  # Descripción
            r'(\d{1,4}[,\.]\d{2})'        # Importe
            r'(\d{1,3}[,\.]\d{2})',       # Precio
            re.MULTILINE
        )
        
        for match in patron.finditer(texto):
            codigo, uds, descripcion, importe, precio = match.groups()
            descripcion_limpia = ' '.join(descripcion.split()).strip()
            
            # Ignorar headers/totales
            desc_upper = descripcion_limpia.upper()
            if any(x in desc_upper for x in ['ALBAR', 'TOTAL', 'BRUTO', 'SUMA', 'SIGUE', 'BASE', 'IVA']):
                continue
            
            lineas.append({
                'codigo': codigo,
                'articulo': descripcion_limpia,
                'cantidad': int(uds),
                'precio_ud': self._convertir_importe(precio),
                'iva': 21,  # Licores siempre 21%
                'base': self._convertir_importe(importe)
            })
        
        return lineas
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """
        Extrae total con patrón específico MADRUEÑO.
        Formato: TOTAL €: 890,08
        """
        patrones = [
            r'TOTAL\s*€[:\s]*(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})',  # TOTAL €: 890,08
            r'TOTAL\s*€\s*(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})',     # TOTAL € 890,08
            r'(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*€\s*\n.*?DATOS\s*BANCARIOS',  # 890,08 €\nDATOS
        ]
        
        for patron in patrones:
            match = re.search(patron, texto, re.IGNORECASE | re.MULTILINE)
            if match:
                return self._convertir_importe(match.group(1))
        
        return None
