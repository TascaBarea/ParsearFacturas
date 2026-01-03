"""
Extractor para JIMELUZ EMPRENDEDORES S.L.

Supermercado / Autoservicio en Calle Embajadores, 50 - 28005 Madrid.
Venta de frutas, verduras, limpieza, hielo, etc.

CIF: (pendiente confirmar)
IBAN: (pendiente - pago en efectivo/tarjeta)

IMPORTANTE: Las facturas de JIMELUZ son tickets escaneados (imágenes).
Este extractor requiere OCR (Tesseract) para funcionar.

Productos típicos:
- Frutas/verduras (IVA 4%): limón, naranja, rúcula, lima
- Alimentación (IVA 10%): hielo, agua, chocolate
- Limpieza (IVA 21%): papel higiénico, bayetas, lejía, bolsas

Estructura del ticket:
- Cabecera con datos fiscales
- Líneas de productos: CANT DESCRIPCION %IVA IMPORTE
- Cuadro fiscal: %IVA BASE CUOTA TOTAL
- TOTAL COMPRA / TOTAL PAGADO / TOTAL FACTURA

Creado: 01/01/2026
Validado: 8/10 facturas (2 con OCR muy malo)
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re
from collections import Counter

# Intentar importar OCR
try:
    from pdf2image import convert_from_path
    import pytesseract
    OCR_DISPONIBLE = True
except ImportError:
    OCR_DISPONIBLE = False


@registrar('JIMELUZ', 'JIMELUZ EMPRENDEDORES', 'JIMELUZ EMPRENDEDORES S.L.',
           'JIMELUZ EMPRENDEDORES SL', 'IMELUZ', 'JIME LUZ')
class ExtractorJimeluz(ExtractorBase):
    """Extractor para tickets escaneados de JIMELUZ (requiere OCR)."""
    
    nombre = 'JIMELUZ EMPRENDEDORES S.L.'
    cif = ''  # Pendiente confirmar
    iban = ''  # Pago en efectivo/tarjeta
    metodo_pdf = 'ocr'  # Requiere OCR
    
    def _convertir_importe(self, texto: str) -> float:
        """Convierte texto a float (formato europeo)."""
        if not texto:
            return 0.0
        texto = str(texto).strip().replace(' ', '')
        texto = re.sub(r'[^\d,.]', '', texto)
        if '.' in texto and ',' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            texto = texto.replace(',', '.')
        try:
            return float(texto)
        except:
            return 0.0
    
    def _extraer_texto_ocr(self, pdf_path: str) -> str:
        """Extrae texto del PDF usando OCR."""
        if not OCR_DISPONIBLE:
            return ""
        
        try:
            images = convert_from_path(pdf_path, dpi=300)
            texto_completo = []
            for img in images:
                texto = pytesseract.image_to_string(img)
                texto_completo.append(texto)
            return '\n'.join(texto_completo)
        except Exception as e:
            print(f"Error OCR: {e}")
            return ""
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """
        Extrae TOTAL del ticket.
        
        Estrategia optimizada para OCR de tickets escaneados:
        1. TOTAL FACTURA con número
        2. TOTAL PAGADO con número
        3. Número que aparece 2+ veces (total aparece en COMPRA/PAGADO/FACTURA)
        4. TOTAL COMPRA con número
        5. Línea con FACTURA/PAGADO + número al final
        """
        texto_norm = texto.upper()
        
        # 1. TOTAL FACTURA
        m1 = re.search(r'TOTAL\s*FACTURA[^\d]*([\d]+[,.][\d]{2})', texto_norm)
        if m1:
            return self._convertir_importe(m1.group(1))
        
        # 2. TOTAL PAGADO
        m2 = re.search(r'TOTAL\s*PAGADO[^\d]*([\d]+[,.][\d]{2})', texto_norm)
        if m2:
            return self._convertir_importe(m2.group(1))
        
        # 3. Número que aparece 2+ veces (el total aparece en múltiples lugares)
        todos = re.findall(r'([\d]+[,.][\d]{2})', texto)
        if todos:
            valores = [self._convertir_importe(v) for v in todos]
            # Filtrar %IVA y valores pequeños
            valores_filtrados = [v for v in valores if v not in [21.0, 10.0, 4.0, 0.0] and v > 2]
            if valores_filtrados:
                contador = Counter(valores_filtrados)
                mas_comun = contador.most_common(1)
                if mas_comun and mas_comun[0][1] >= 2:
                    return mas_comun[0][0]
        
        # 4. TOTAL COMPRA (con espacios en números)
        m4 = re.search(r'TOTAL\s*COMPRA[^\d]*([\d]+[,.\s]?[\d]{2})', texto_norm)
        if m4:
            return self._convertir_importe(m4.group(1).replace(' ', ''))
        
        # 5. Líneas con FACTURA/PAGADO + número al final
        for line in texto.split('\n'):
            line_upper = line.upper()
            if ('FACTURA' in line_upper or 'PAGADO' in line_upper) and '%' not in line:
                m = re.search(r'([\d]+[,.\s]?[\d]{2})\s*$', line.strip())
                if m:
                    val = self._convertir_importe(m.group(1).replace(' ', ''))
                    if 1 < val < 500:
                        return val
        
        return None
    
    def extraer_cuadro_fiscal(self, texto: str) -> List[Dict]:
        """
        Extrae cuadro fiscal con múltiples tipos de IVA.
        
        Formato: %IVA BASE CUOTA TOTAL
        Ej: "4,00% 2,34 0,10 2,44"
        """
        cuadros = []
        
        patron = re.compile(
            r'(\d{1,2})[,.]?(\d{0,2})\s*%\s+'
            r'([\d]+[,.][\d]{2})\s+'
            r'([\d]+[,.][\d]{2})\s+'
            r'([\d]+[,.][\d]{2})',
            re.IGNORECASE
        )
        
        for m in patron.finditer(texto):
            iva_entero = int(m.group(1))
            iva_decimal = m.group(2) or '0'
            iva = float(f"{iva_entero}.{iva_decimal}")
            base = self._convertir_importe(m.group(3))
            cuota = self._convertir_importe(m.group(4))
            total = self._convertir_importe(m.group(5))
            
            cuadros.append({
                'iva': iva,
                'base': base,
                'cuota': cuota,
                'total': total
            })
        
        return cuadros
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de productos del ticket.
        
        Formato: CANT DESCRIPCION %IVA IMPORTE
        Ej: "2 RUCULA CRF BL/50GR 4,00 1,50"
        """
        lineas = []
        
        patron = re.compile(
            r'^(\d+)\s+'                           # Cantidad
            r'([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ0-9\s/,\.]+?)\s+'  # Descripción
            r'(\d{1,2}[,.]00)\s+'                  # %IVA (4,00 / 10,00 / 21,00)
            r'([\d]+[,.][\d]{2})',                 # Importe
            re.MULTILINE
        )
        
        for m in patron.finditer(texto):
            cantidad = int(m.group(1))
            descripcion = m.group(2).strip()
            iva = int(self._convertir_importe(m.group(3)))
            importe = self._convertir_importe(m.group(4))
            
            # Determinar categoría por IVA
            if iva == 4:
                categoria = 'FRUTAS Y VERDURAS'
            elif iva == 10:
                categoria = 'ALIMENTACION'
            else:
                categoria = 'LIMPIEZA'
            
            lineas.append({
                'codigo': '',
                'articulo': descripcion[:50],
                'cantidad': cantidad,
                'precio_ud': importe / cantidad if cantidad > 0 else importe,
                'iva': iva,
                'base': importe / (1 + iva/100),  # Calcular base desde importe con IVA
                'categoria': categoria
            })
        
        return lineas
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha del ticket."""
        # Formato: "FECHA FACTURA: 04/01/2025" o "FECHA: 04/01/2025"
        m = re.search(r'FECHA[:\s]*(\d{2}/\d{2}/\d{4})', texto, re.IGNORECASE)
        if m:
            return m.group(1)
        return None
    
    def extraer_referencia(self, texto: str) -> Optional[str]:
        """Extrae número de factura."""
        # Formato: "FACTURA N.: A250000005" o "FAC URA N : A250000146"
        m = re.search(r'FA?C?T?U?RA?\s*N[.:]?\s*:?\s*([A-Z]?\d{6,12})', texto, re.IGNORECASE)
        if m:
            return m.group(1)
        return None
