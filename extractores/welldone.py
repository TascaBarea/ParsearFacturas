"""
Extractor para WELLDONE LACTICOS / RODOLFO DEL RIO

Quesero artesanal - quesos franceses de cabra
NIF: 27292516A (autonomo)
IBAN: ES55 2100 5789 1202 0015 7915 (Caixabank)
Direccion: Camilo Jose Cela 2, 41807 Espartinas (Sevilla)

METODO HIBRIDO: pdfplumber + OCR (algunas facturas escaneadas)

Productos (IVA 4% - quesos):
- LORETO, NORDUMANI, BRIQUETTE, PYRAMIDE RUAN
- ALJARAFE, CHEVRO, CARTUJO

Portes: SEUR - SE DISTRIBUYEN PROPORCIONALMENTE entre los productos

Creado: 21/12/2025
Validado: 4/4 facturas (1T25, 2T25, 4T25)
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar('WELLDONE', 'WELLDONE LACTICOS', 'RODOLFO DEL RIO', 
           'RODOLFO DEL RIO LAMEYER', 'WELL DONE')
class ExtractorWelldone(ExtractorBase):
    """Extractor para facturas de WELLDONE LACTICOS (hibrido pdfplumber + OCR)."""
    
    nombre = 'WELLDONE LACTICOS'
    cif = '27292516A'  # Autonomo
    iban = 'ES55 2100 5789 1202 0015 7915'
    metodo_pdf = 'hibrido'
    categoria_fija = 'QUESOS'
    
    def extraer_texto(self, pdf_path: str) -> str:
        """Extrae texto con pdfplumber, fallback a OCR."""
        import pdfplumber
        
        texto = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    texto += t + "\n"
        
        # Si no hay texto suficiente, usar OCR
        if not texto.strip() or len(texto) < 200:
            texto = self.extraer_texto_ocr(pdf_path)
        
        return texto
    
    def extraer_texto_ocr(self, pdf_path: str) -> str:
        """Extrae texto usando OCR."""
        try:
            from pdf2image import convert_from_path
            import pytesseract
            from PIL import ImageEnhance
            
            images = convert_from_path(pdf_path, dpi=300)
            texto = ""
            for img in images:
                gray = img.convert('L')
                enhancer = ImageEnhance.Contrast(gray)
                enhanced = enhancer.enhance(1.5)
                texto += pytesseract.image_to_string(enhanced, lang='eng', 
                    config='--psm 4') + "\n"
            return texto
        except:
            return ""
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae lineas de producto con portes distribuidos.
        
        Los portes se distribuyen proporcionalmente entre los productos.
        """
        productos = []
        portes_total_con_iva = 0.0
        
        # Patron para lineas de producto
        patron = re.compile(
            r'^(Q[A-Z]\d{4}|Porte)\s+'     # Codigo
            r'(.+?)\s+'                     # Descripcion
            r'(wD\d+)?\s*'                  # Lote (opcional)
            r'(\d+[.,]\d+)\s+'              # Cantidad
            r'(\d+[.,]\d+)\s+'              # Precio sin IVA
            r'(\d+[.,]\d+)\s+'              # Precio con IVA
            r'(\d+[.,]\d+)',                # Total con IVA
            re.MULTILINE
        )
        
        for match in patron.finditer(texto):
            codigo = match.group(1)
            descripcion = match.group(2).strip()
            cantidad = float(match.group(4).replace(',', '.'))
            precio_sin_iva = float(match.group(5).replace(',', '.'))
            total_con_iva = float(match.group(7).replace(',', '.'))
            
            # Si es porte, guardar para distribuir
            if 'Porte' in codigo or 'SEUR' in descripcion.upper():
                portes_total_con_iva = total_con_iva
            else:
                # Producto normal (queso al 4%)
                base = round(total_con_iva / 1.04, 2)
                productos.append({
                    'codigo': codigo,
                    'articulo': descripcion[:40],
                    'cantidad': int(cantidad) if cantidad == int(cantidad) else cantidad,
                    'precio_ud': precio_sin_iva,
                    'iva': 4,
                    'base': base
                })
        
        # Si OCR y no hay productos, buscar base imponible
        if len(productos) == 0:
            m_base = re.search(r'4[,.]00\s*\|?\s*([\d,.]+)', texto)
            if m_base:
                base_str = m_base.group(1).replace('.', '').replace(',', '.')
                base_str = re.sub(r'[^\d.]', '', base_str)
                try:
                    base_4 = float(base_str)
                    if base_4 > 30:
                        productos.append({
                            'codigo': '',
                            'articulo': 'QUESOS ARTESANOS',
                            'cantidad': 1,
                            'precio_ud': base_4,
                            'iva': 4,
                            'base': base_4
                        })
                except:
                    pass
        
        # DISTRIBUIR PORTES proporcionalmente
        if portes_total_con_iva > 0 and len(productos) > 0:
            # Convertir total portes a base equivalente al 4%
            portes_base_equiv = round(portes_total_con_iva / 1.04, 2)
            
            total_bases = sum(p['base'] for p in productos)
            for p in productos:
                proporcion = p['base'] / total_bases
                incremento = round(portes_base_equiv * proporcion, 2)
                p['base'] = round(p['base'] + incremento, 2)
                if p['cantidad'] > 0:
                    p['precio_ud'] = round(p['base'] / p['cantidad'], 4)
        
        return productos
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """Calcula total desde lineas (con portes distribuidos)."""
        lineas = self.extraer_lineas(texto)
        if lineas:
            total = sum(l['base'] * 1.04 for l in lineas)
            return round(total, 2)
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        m = re.search(r'Factura\s+\d+\s+\d+\s+(\d{2}/\d{2}/\d{4})', texto)
        if m:
            return m.group(1)
        m = re.search(r'(\d{2}/\d{2}/\d{4})\s+Tasca', texto)
        return m.group(1) if m else None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae numero de factura."""
        m = re.search(r'Factura\s+(\d+\s+\d+)', texto)
        if m:
            return m.group(1).replace(' ', '')
        m = re.search(r'(\d+)\s+\d{2}/\d{2}/\d{4}', texto)
        return m.group(1) if m else None
