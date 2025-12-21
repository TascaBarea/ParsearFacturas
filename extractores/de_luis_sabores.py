"""
Extractor para DE LUIS SABORES ÚNICOS S.L.

Quesos Cañarejal.
CIF: B86249711

Formato factura (pdfplumber):
Línea Artículo Cantidad Kilos Precio % Dto. Total
1 O760 CREMA DE QUESO "CAÑAREJAL" 200 GR. 6 6 7,19 43,14 4%

T O T A L Fra. 347,51

IVA: 4% (quesos)

Creado: 19/12/2025
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar('DE LUIS SABORES', 'DE LUIS', 'SABORES UNICOS', 'CAÑAREJAL', 'JAMONES LIEBANA')
class ExtractorDeLuisSabores(ExtractorBase):
    """Extractor para facturas de DE LUIS SABORES ÚNICOS."""
    
    nombre = 'DE LUIS SABORES ÚNICOS'
    cif = 'B86249711'
    iban = 'ES53 0049 1920 1021 1019 2545'
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas individuales de productos.
        
        Formato:
        1 O760 CREMA DE QUESO "CAÑAREJAL" 200 GR. 6 6 7,19 43,14 4%
        """
        lineas = []
        
        # Patrón: LINEA CODIGO DESCRIPCION CANTIDAD KILOS PRECIO TOTAL IVA%
        patron_linea = re.compile(
            r'^(\d+)\s+'                               # Línea
            r'([A-Z]\d{3})\s+'                         # Código (ej: O760)
            r'(.+?)\s+'                                # Descripción
            r'(\d+)\s+'                                # Cantidad
            r'(\d+(?:,\d+)?)\s+'                       # Kilos
            r'(\d+,\d{2})\s+'                          # Precio
            r'(\d+,\d{2})\s+'                          # Total
            r'(\d+)%'                                  # IVA%
        , re.MULTILINE)
        
        for match in patron_linea.finditer(texto):
            codigo = match.group(2)
            descripcion = match.group(3).strip()
            cantidad = int(match.group(4))
            precio = self._convertir_europeo(match.group(6))
            importe = self._convertir_europeo(match.group(7))
            iva = int(match.group(8))
            
            # Limpiar descripción
            descripcion = re.sub(r'\s*Lotes\s+\d+.*$', '', descripcion, flags=re.IGNORECASE)
            descripcion = re.sub(r'\s+', ' ', descripcion).strip()
            
            if importe < 1.0:
                continue
            
            lineas.append({
                'codigo': codigo,
                'articulo': descripcion[:50],
                'cantidad': cantidad,
                'precio_ud': round(precio, 2),
                'iva': iva,
                'base': round(importe, 2)
            })
        
        # Si no encontró líneas, usar desglose fiscal
        if not lineas:
            lineas = self._extraer_desglose(texto)
        
        return lineas
    
    def _extraer_desglose(self, texto: str) -> List[Dict]:
        """Extrae usando desglose fiscal."""
        lineas = []
        
        # Buscar: BASE IVA% CUOTA
        patron = re.compile(r'(\d+,\d{2})\s+(\d{1,2})%\s+(\d+,\d{2})')
        
        for match in patron.finditer(texto):
            base = self._convertir_europeo(match.group(1))
            iva = int(match.group(2))
            cuota = self._convertir_europeo(match.group(3))
            
            # Validar cuota
            cuota_esperada = round(base * iva / 100, 2)
            if base > 5 and iva in [4, 10, 21] and abs(cuota - cuota_esperada) < 1.0:
                lineas.append({
                    'codigo': '',
                    'articulo': f'QUESOS CAÑAREJAL IVA {iva}%',
                    'cantidad': 1,
                    'precio_ud': round(base, 2),
                    'iva': iva,
                    'base': round(base, 2)
                })
        
        return lineas
    
    def _convertir_europeo(self, texto: str) -> float:
        if not texto:
            return 0.0
        texto = texto.strip()
        if '.' in texto and ',' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            texto = texto.replace(',', '.')
        try:
            return float(texto)
        except:
            return 0.0
    
    def extraer_total(self, texto: str) -> Optional[float]:
        # Buscar T O T A L Fra. o TOTAL Fra.
        patrones = [
            r'T\s*O\s*T\s*A\s*L\s+Fra\.?\s*(\d+,\d{2})',
            r'TOTAL\s+Fra\.?\s*(\d+,\d{2})',
        ]
        for patron in patrones:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                return self._convertir_europeo(match.group(1))
        return None
