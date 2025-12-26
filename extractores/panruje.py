"""
Extractor para PANRUJE, SL (Rosquillas La Ermita)

Rosquillas artesanas.
CIF: B13858014
IVA: 4% (superreducido)
Categoría fija: ROSQUILLAS MARINERAS
Especial: Los PORTES se SUMAN al artículo (no línea separada)

Formato factura:
NOR 7  4,0 CAJAS DE ROSQUILLAS NORMALES 50 16,50 2,00 64,68
000    1,0 PORTES                              24,60     24,60

BASE IMPONIBLE: 89,28  % I.V.A.: 4,0  I.V.A.: 3,57  TOTAL: 92,85

Creado: 26/12/2025
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar('PANRUJE', 'PANRUJE SL', 'PANRUJE, SL', 'LA ERMITA', 'ROSQUILLAS ARTESANAS')
class ExtractorPanruje(ExtractorBase):
    """Extractor para facturas de PANRUJE."""
    
    nombre = 'PANRUJE'
    cif = 'B13858014'
    metodo_pdf = 'pdfplumber'
    categoria_fija = 'ROSQUILLAS MARINERAS'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """Extrae línea única con rosquillas + portes sumados."""
        lineas = []
        
        # Buscar base imponible total (incluye rosquillas + portes)
        m = re.search(r'BASE\s+IMPONIBLE\s+([\d,.]+)', texto, re.IGNORECASE)
        if not m:
            m = re.search(r'([\d,.]+)\s+[\d,.]+\s+4[,.]0\s+[\d,.]+\s+[\d,.]+\s*$', texto, re.MULTILINE)
        
        if m:
            base_total = self._convertir_europeo(m.group(1))
            
            # Buscar cantidad de cajas
            cantidad_match = re.search(r'NOR\s*7?\s+([\d,.]+)\s+CAJAS', texto, re.IGNORECASE)
            if not cantidad_match:
                cantidad_match = re.search(r'([\d,.]+)\s+CAJAS\s+DE\s+ROSQUILLAS', texto, re.IGNORECASE)
            
            cantidad = self._convertir_europeo(cantidad_match.group(1)) if cantidad_match else 1
            
            lineas.append({
                'codigo': 'NOR7',
                'articulo': 'CAJAS DE ROSQUILLAS NORMALES',
                'cantidad': cantidad,
                'precio_ud': round(base_total / cantidad, 4) if cantidad > 0 else base_total,
                'iva': 4,
                'base': round(base_total, 2),
                'categoria': self.categoria_fija
            })
        
        return lineas
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo a float."""
        if not texto:
            return 0.0
        texto = texto.strip()
        if ',' in texto and '.' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            texto = texto.replace(',', '.')
        try:
            return float(texto)
        except:
            return 0.0
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """Extrae total de la factura."""
        # "TOTAL 92,85"
        m = re.search(r'TOTAL\s+([\d,.]+)\s*$', texto, re.MULTILINE | re.IGNORECASE)
        if m:
            return self._convertir_europeo(m.group(1))
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        # "FECHA 15/12/2025" o "15/12/2025" después de FT
        m = re.search(r'FECHA\s+(\d{2}/\d{2}/\d{4})', texto, re.IGNORECASE)
        if m:
            return m.group(1)
        m = re.search(r'FT\s+\d+\s+(\d{2}/\d{2}/\d{4})', texto)
        if m:
            return m.group(1)
        return None
    
    def extraer_referencia(self, texto: str) -> Optional[str]:
        """Extrae número de factura."""
        # "FT 197"
        m = re.search(r'FT\s+(\d+)', texto)
        if m:
            return f"FT-{m.group(1)}"
        return None
