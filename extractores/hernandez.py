"""
Extractor para HERNANDEZ SUMINISTROS HOSTELEROS

Suministros de menaje y cristaleria para hosteleria
CIF: B78987138
IBAN: ES49 0049 2662 97 2614316514 (Santander)
Direccion: Humilladero 14 / Plaza La Cebada 14, 28005 Madrid

METODO HIBRIDO: pdfplumber + OCR (algunas facturas escaneadas)

Productos (todos IVA 21%):
- Vasos (pinta, cana, sidra)
- Copas (Mencia)
- Pinzas hielo
- Bombas vacio vino
- Cuchillos

Categoria: MENAJE : VASOS

Creado: 21/12/2025
Validado: 4/6 facturas (1T25, 2T25, 3T25, 4T25)
Nota: 2 facturas escaneadas de baja calidad requieren proceso manual
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
    metodo_pdf = 'hibrido'
    categoria_fija = 'MENAJE : VASOS'
    
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
        if len(texto) < 300:
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
    
    def _es_ocr(self, pdf_path: str) -> bool:
        """Detecta si el PDF requiere OCR."""
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t and len(t) > 300:
                    return False
        return True
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae lineas de producto.
        
        Formato pdfplumber:
        ACVASO PINTA VASO AGUA DE 36 CL.PINTA 12 0,79 9,48
        (CODIGO + CONCEPTO + UNIDADES + PVP + IMPORTE)
        """
        lineas = []
        
        # Patron para lineas de producto
        patron = re.compile(
            r'^([A-Z]{2}[A-Z0-9\s]+?)\s+'     # Codigo (ACVASO, DXCOPA, etc)
            r'(.+?)\s+'                        # Concepto
            r'(\d+)\s+'                        # Unidades
            r'(\d+[,\.]\d{2})\s+'             # PVP
            r'(\d+[,\.]\d{2})$',              # Importe (base)
            re.MULTILINE
        )
        
        for match in patron.finditer(texto):
            codigo = match.group(1).strip()
            concepto = match.group(2).strip()
            unidades = int(match.group(3))
            pvp = float(match.group(4).replace(',', '.'))
            importe = float(match.group(5).replace(',', '.'))
            
            # Ignorar lineas de totales
            if 'BRUTO' in codigo or 'TOTAL' in codigo:
                continue
            
            lineas.append({
                'codigo': codigo,
                'articulo': concepto[:40],
                'cantidad': unidades,
                'precio_ud': pvp,
                'iva': 21,
                'base': importe
            })
        
        # Si no hay lineas (OCR), buscar base imponible
        if len(lineas) == 0:
            # Buscar: BASE 21 IVA
            m_base = re.search(r'(\d+[,\.]\d{2})\s+21\s+(\d+[,\.]\d{2})', texto)
            if m_base:
                base = float(m_base.group(1).replace(',', '.'))
                if base > 5:
                    lineas.append({
                        'codigo': '',
                        'articulo': 'MENAJE VASOS',
                        'cantidad': 1,
                        'precio_ud': base,
                        'iva': 21,
                        'base': base
                    })
            else:
                # Buscar numeros aislados (rango razonable)
                numeros = re.findall(r'(\d+[,\.]\d{2})', texto)
                for n in numeros:
                    val = float(n.replace(',', '.'))
                    if 10 < val < 200:
                        lineas.append({
                            'codigo': '',
                            'articulo': 'MENAJE VASOS',
                            'cantidad': 1,
                            'precio_ud': val,
                            'iva': 21,
                            'base': val
                        })
                        break
        
        return lineas
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """Calcula total desde lineas."""
        lineas = self.extraer_lineas(texto)
        if lineas:
            suma = sum(l['base'] for l in lineas)
            return round(suma * 1.21, 2)
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        # Formato: DD/MM/YYYY F25/
        m = re.search(r'(\d{2}/\d{2}/\d{4})\s+F25/', texto)
        if m:
            return m.group(1)
        m = re.search(r'(\d{2}/\d{2}/\d{4})', texto)
        return m.group(1) if m else None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae numero de factura."""
        # Formato: F25/XXXX
        m = re.search(r'(F25/\d+)', texto)
        return m.group(1) if m else None
