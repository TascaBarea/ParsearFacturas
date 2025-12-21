"""
Extractor para FISHGOURMET S.L.

Ahumados de pescado gourmet
CIF: B85975126
IBAN: ES57 2100 2127 1502 0045 4128 (LA CAIXA)
Dirección: C/ Romero 7, Pol. Ind. La Mata, 28440 Guadarrama (Madrid)
Tel: 620429972

Productos típicos (todos 10% IVA):
- Salmón ahumado tarrina 350g
- Bacalao ahumado tarrina 350g
- Lomitos de arenque al dulce de vinagre 350g
- Anchoa Cantábrico 00 - tarrina 20 lomos

Nota: Las facturas son imágenes PDF, requieren OCR.

Creado: 20/12/2025
Validado: 5/5 facturas (1T25, 2T25, 3T25)
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar('FISHGOURMET', 'FISH GOURMET')
class ExtractorFishgourmet(ExtractorBase):
    """Extractor para facturas de FISHGOURMET S.L."""
    
    nombre = 'FISHGOURMET'
    cif = 'B85975126'
    iban = 'ES57 2100 2127 1502 0045 4128'
    metodo_pdf = 'ocr'  # Las facturas son imágenes
    categoria_fija = 'AHUMADOS PESCADO'
    
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
    
    def extraer_texto_ocr(self, pdf_path: str) -> str:
        """Extrae texto usando OCR (Tesseract)."""
        try:
            from pdf2image import convert_from_path
            import pytesseract
            
            images = convert_from_path(pdf_path, dpi=300)
            if images:
                return pytesseract.image_to_string(images[0], lang='eng')
        except:
            pass
        return ""
    
    def extraer_texto(self, pdf_path: str) -> str:
        """Extrae texto con OCR (las facturas son imágenes)."""
        return self.extraer_texto_ocr(pdf_path)
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de producto.
        
        Formato (OCR puede variar):
        DESCRIPCION
        CODIGO                      Cajas Unidades Precio Importe %IVA
        
        Ejemplo:
        SALMON AHUMADO TARRINA 350 G
        VL201285458104642005         0    1,000    17,50   17,50  10,0
        """
        lineas = []
        
        # Productos conocidos
        productos = {
            'SALMON': 'SALMON AHUMADO TARRINA 350G',
            'BACALAO': 'BACALAO AHUMADO TARRINA 350G',
            'LOMITOS': 'LOMITOS DE ARENQUE AL DULCE DE VINAGRE 350G',
            'ANCHOA': 'ANCHOA CANTABRICO 00 - TARRINA 20 LOMOS',
            'ARENQUE': 'LOMITOS DE ARENQUE AL DULCE DE VINAGRE 350G',
        }
        
        # Buscar líneas con precio e importe
        # Formato aproximado: 0 CANTIDAD PRECIO IMPORTE IVA
        for m in re.finditer(
            r'0\s+'                          # Cajas (siempre 0)
            r'([\d,]+)\s+'                   # Unidades
            r'([\d,]+)\s+'                   # Precio
            r'([\d,]+)\s+'                   # Importe
            r'10[,.]0',                      # IVA 10%
            texto
        ):
            cantidad = self._convertir_europeo(m.group(1))
            precio = self._convertir_europeo(m.group(2))
            importe = self._convertir_europeo(m.group(3))
            
            lineas.append({
                'codigo': '',
                'articulo': 'PRODUCTO AHUMADO',
                'cantidad': int(cantidad) if cantidad == int(cantidad) else cantidad,
                'precio_ud': precio,
                'iva': 10,
                'base': importe
            })
        
        return lineas
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """
        Extrae total de la factura.
        
        Busca: "TOTAL FACTURA XXX,XX €"
        """
        m = re.search(r'TOTAL FACTURA\s+([\d,.]+)\s*€', texto)
        if m:
            return self._convertir_europeo(m.group(1))
        
        # Alternativa: calcular desde base + IVA
        m_base = re.search(r'BASE IMPONIBLE\s+([\d,.]+)\s*€', texto)
        m_iva = re.search(r'TOTAL\s+[IL]\.?V\.?A\.?\s+([\d,.]+)\s*€', texto)
        if m_base and m_iva:
            base = self._convertir_europeo(m_base.group(1))
            iva = self._convertir_europeo(m_iva.group(1))
            return round(base + iva, 2)
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        # Formato: DD/MM/YYYY seguido de número de factura
        m = re.search(r'(\d{2}/\d{2}/\d{4})\s+\d+', texto)
        if m:
            return m.group(1)
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae número de factura."""
        # Formato: fecha seguida de número
        m = re.search(r'\d{2}/\d{2}/\d{4}\s+(\d+)', texto)
        if m:
            return m.group(1)
        return None
