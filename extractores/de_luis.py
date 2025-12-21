"""
Extractor para DE LUIS SABORES UNICOS S.L.

Distribuidor de quesos artesanales Cañarejal (Zamora)
CIF: B86249711
Ubicación: Pinto, Madrid
Web: jamonesliebana.com

Productos (todos 4% IVA - quesos):
- O711: QUESO OVEJA CURADO "CAÑAREJAL" - €/kg (14,90€/kg)
- O760: CREMA DE QUESO "CAÑAREJAL" 200 GR. - €/ud (7,19€/ud)
- O765: QUESO OVEJA MANTECOSO RULO "CAÑAREJAL" - €/kg (17,25€/kg)

Método: pdfplumber con fallback a OCR
Las facturas agrupan múltiples albaranes en una sola factura

IBAN: ES53 0049 1920 1021 1019 2545 (Banco Santander)

Creado: 20/12/2025
Validado: 5/5 facturas (2T25, 3T25, 4T25)
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional, Tuple
import re


@registrar('DE LUIS', 'DE LUIS SABORES', 'DE LUIS SABORES UNICOS', 
           'JAMONES LIEBANA', 'CAÑAREJAL')
class ExtractorDeLuis(ExtractorBase):
    """Extractor para facturas de DE LUIS SABORES UNICOS."""
    
    nombre = 'DE LUIS SABORES UNICOS'
    cif = 'B86249711'
    iban = 'ES53 0049 1920 1021 1019 2545'
    metodo_pdf = 'hibrido'  # pdfplumber + OCR fallback
    categoria_fija = 'QUESOS'
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo (1.234,56) a float."""
        if not texto:
            return 0.0
        texto = str(texto).strip().replace('€', '').replace(' ', '').strip()
        if '.' in texto and ',' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            texto = texto.replace(',', '.')
        try:
            return float(texto)
        except:
            return 0.0
    
    def extraer_texto(self, pdf_path: str) -> Tuple[str, str]:
        """
        Extrae texto con pdfplumber, fallback a OCR.
        Returns: (texto, metodo)
        """
        import pdfplumber
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if len(pdf.pages) > 0:
                    texto = pdf.pages[0].extract_text()
                    if texto:
                        return texto, 'pdfplumber'
        except:
            pass
        
        # Fallback OCR
        try:
            from pdf2image import convert_from_path
            import pytesseract
            
            images = convert_from_path(pdf_path, dpi=300)
            if images:
                return pytesseract.image_to_string(images[0], lang='eng'), 'ocr'
        except:
            pass
        
        return "", None
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de producto.
        
        Formato: N CODIGO ARTICULO CANTIDAD KILOS PRECIO TOTAL %
        Ejemplo: 1 O760 CREMA DE QUESO "CAÑAREJAL" 200 GR. 6 6 7,19 43,14 4%
        
        Productos:
        - O711: Queso Oveja Curado Cañarejal (€/kg)
        - O760: Crema de Queso Cañarejal 200gr (€/ud)
        - O765: Queso Oveja Mantecoso Rulo Cañarejal (€/kg)
        """
        lineas = []
        
        for line in texto.split('\n'):
            # Patrón flexible: acepta O o 0 como prefijo del código
            m = re.match(
                r'^(\d+)\s+'                    # Número línea
                r'([O0]\d{3})\s+'               # Código (O711, 0760, etc)
                r'(.+?)\s+'                     # Artículo
                r'(\d+)\s+'                     # Cantidad
                r'([\d,]+)\s+'                  # Kilos
                r'([\d,]+)\s+'                  # Precio
                r'([\d,]+)\s+'                  # Total
                r'(\d+)%',                      # IVA
                line
            )
            if m:
                codigo = m.group(2)
                # Normalizar código: primer caracter siempre O
                if codigo[0] == '0':
                    codigo = 'O' + codigo[1:]
                
                articulo_raw = m.group(3).strip()
                cantidad = int(m.group(4))
                kilos = self._convertir_europeo(m.group(5))
                precio = self._convertir_europeo(m.group(6))
                importe = self._convertir_europeo(m.group(7))
                iva_pct = int(m.group(8))
                
                # Normalizar nombre de artículo
                if 'CREMA' in articulo_raw.upper():
                    articulo = 'CREMA DE QUESO CAÑAREJAL 200GR'
                elif 'MANTECOSO' in articulo_raw.upper() or 'RULO' in articulo_raw.upper():
                    articulo = 'QUESO OVEJA MANTECOSO RULO CAÑAREJAL'
                elif 'CURADO' in articulo_raw.upper():
                    articulo = 'QUESO OVEJA CURADO CAÑAREJAL'
                else:
                    articulo = articulo_raw.upper()
                
                lineas.append({
                    'codigo': codigo,
                    'articulo': articulo,
                    'cantidad': cantidad,
                    'kilos': kilos,
                    'precio_ud': precio,
                    'iva': iva_pct,
                    'base': importe
                })
        
        return lineas
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """
        Extrae total calculándolo desde las líneas.
        Más fiable que buscar en el resumen.
        """
        lineas = self.extraer_lineas(texto)
        if lineas:
            base_total = sum(l['base'] for l in lineas)
            iva_total = round(base_total * 0.04, 2)  # Todo al 4%
            return round(base_total + iva_total, 2)
        
        # Fallback: usar base del resumen
        m = re.search(r'([\d,.]+)\s+([\d,.]+)\s+4%\s+([\d,.]+)', texto)
        if m:
            base = self._convertir_europeo(m.group(2))
            iva = self._convertir_europeo(m.group(3))
            return round(base + iva, 2)
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        m = re.search(r'Fecha\s+(\d{2}/\d{2}/\d{4})', texto)
        if m:
            return m.group(1)
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae número de factura."""
        m = re.search(r'[Nn][uú]mero\s+(\d+\s*-\s*\d+)', texto)
        if m:
            return m.group(1).replace(' ', '')
        return None
