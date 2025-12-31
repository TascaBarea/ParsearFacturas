"""
Extractor para HERNANDEZ SUMINISTROS HOSTELEROS

Suministros de menaje y cristaleria para hosteleria
CIF: B78987138
IBAN: ES49 0049 2662 97 2614316514 (Santander)

Productos (todos IVA 21%):
- Vasos (pinta, cana, sidra)
- Copas (Mencia)
- Pinzas hielo
- Cuchillos

Categoria: MENAJE : VASOS

Creado: 21/12/2025
Corregido: 30/12/2025 - Extraer TOTAL FACTURA directamente, filtrar IBAN
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar('HERNANDEZ', 'HERNANDEZ SUMINISTROS', 'SUMINISTROS HERNANDEZ',
           'HERNANDEZ HOSTELEROS', 'HERNANDEZ SUMINISTROS HOSTELEROS')
class ExtractorHernandez(ExtractorBase):
    """Extractor para facturas de HERNANDEZ SUMINISTROS HOSTELEROS."""
    
    nombre = 'HERNANDEZ SUMINISTROS'
    cif = 'B78987138'
    iban = 'ES49 0049 2662 97 2614316514'
    metodo_pdf = 'pdfplumber'
    categoria_fija = 'MENAJE : VASOS'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """Extrae lineas de producto."""
        lineas = []
        
        patron = re.compile(
            r'^([A-Z]{2}[A-Z0-9]+)\s+'
            r'(.+?)\s+'
            r'(\d+)\s+'
            r'(\d+[,\.]\d{2})\s+'
            r'(\d+[,\.]\d{2})$',
            re.MULTILINE
        )
        
        for match in patron.finditer(texto):
            codigo = match.group(1).strip()
            concepto = match.group(2).strip()
            unidades = int(match.group(3))
            pvp = float(match.group(4).replace(',', '.'))
            importe = float(match.group(5).replace(',', '.'))
            
            # Filtros de seguridad
            if 'BRUTO' in codigo or 'TOTAL' in codigo or 'IMPORTE' in codigo:
                continue
            if 'TRANSFER' in codigo.upper() or 'TRANSFER' in concepto.upper():
                continue
            if re.search(r'ES\d{2}', f"{codigo} {concepto}"):
                continue
            if importe > 500 or unidades > 1000:
                continue
            
            lineas.append({
                'codigo': codigo,
                'articulo': concepto[:40],
                'cantidad': unidades,
                'precio_ud': pvp,
                'iva': 21,
                'base': importe,
                'categoria': self.categoria_fija
            })
        
        return lineas
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """Extrae TOTAL FACTURA directamente del PDF."""
        # Metodo 1: Cuadro fiscal (BASE 21 CUOTA TOTAL)
        m = re.search(r'([\d,]+)\s+21\s+([\d,]+)\s+([\d,]+)\s*[E\u20ac]', texto)
        if m:
            return self._convertir_europeo(m.group(3))
        
        # Metodo 2: TOTAL FACTURA seguido de importe
        m = re.search(r'TOTAL\s+FACTURA[^\d]*([\d.,]+)', texto, re.IGNORECASE)
        if m:
            return self._convertir_europeo(m.group(1))
        
        # Metodo 3: Ultimo importe con euro
        matches = re.findall(r'([\d.,]+)\s*[E\u20ac]', texto)
        for val in reversed(matches):
            num = self._convertir_europeo(val)
            if 5 < num < 10000:
                return num
        
        return None
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo a float."""
        if not texto:
            return 0.0
        texto = re.sub(r'[^\d,.]', '', str(texto))
        if '.' in texto and ',' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            texto = texto.replace(',', '.')
        try:
            return float(texto)
        except:
            return 0.0
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        m = re.search(r'(\d{2}/\d{2}/\d{4})', texto)
        return m.group(1) if m else None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae numero de factura."""
        m = re.search(r'(F25/\d+)', texto)
        return m.group(1) if m else None
    
    extraer_referencia = extraer_numero_factura
