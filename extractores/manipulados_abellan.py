"""
Extractor para PRODUCTOS MANIPULADOS ABELLAN S.L.

Marca comercial: El Labrador / Pepejo
Productor de conservas vegetales artesanales
CIF: B30473326
Ubicación: El Raal, Murcia
Web: pepejolabrador.com

REQUIERE OCR - Las facturas son imágenes escaneadas

Productos (todos 10% IVA - conservas vegetales):
- Tomate asado leña 720ml (1,95€)
- Tomate rallado especial tostadas 720ml (1,85€)
- Tomate confitado 370ml (3,40€)
- Mermelada de tomate 370ml (2,15€)
- Mermelada de higos 370ml (2,15€)
- Tomates secos con aceite de oliva 370ml (3,50€)
- Pisto murciano 370ml (1,90€)
- Tomate frito con huevo 370ml (1,90€)
- Tomate frito 370ml (1,36€)

IBAN: ES06 2100 8321 0413 0018 3503 (CaixaBank)

Creado: 20/12/2025
Validado: 6/6 facturas (1T25, 2T25, 3T25, 4T25)
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar('MANIPULADOS ABELLAN', 'ABELLAN', 'EL LABRADOR', 'PEPEJO', 
           'PEPEJOLABRADOR', 'PRODUCTOS MANIPULADOS')
class ExtractorManipuladosAbellan(ExtractorBase):
    """Extractor para facturas de MANIPULADOS ABELLAN (requiere OCR)."""
    
    nombre = 'MANIPULADOS ABELLAN'
    cif = 'B30473326'
    iban = 'ES06 2100 8321 0413 0018 3503'
    metodo_pdf = 'ocr'
    categoria_fija = 'CONSERVAS VEGETALES'
    
    def extraer_texto_ocr(self, pdf_path: str) -> str:
        """Extrae texto del PDF usando OCR."""
        try:
            from pdf2image import convert_from_path
            import pytesseract
            
            images = convert_from_path(pdf_path, dpi=300)
            texto = ""
            for img in images:
                texto += pytesseract.image_to_string(img, lang='eng')
            return texto
        except Exception as e:
            return ""
    
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
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de producto.
        
        Formato OCR típico:
        TOMATE ASADO LENA 720 ML EL LABRADOR 1,9500 70,20
        
        Los productos son conservas vegetales al 10% IVA.
        """
        lineas = []
        
        # Buscar líneas con precio y total (2 números decimales al final)
        for line in texto.split('\n'):
            # Patrón: PRODUCTO PRECIO IMPORTE
            m = re.search(
                r'([A-Z][A-Z\s]+(?:ML|GR)?)\s+'  # Nombre producto
                r'(\d+[,.]?\d*)\s+'               # Precio unitario
                r'(\d+[,.]?\d+)$',                # Importe total
                line.strip()
            )
            if m:
                articulo = m.group(1).strip()
                precio = self._convertir_europeo(m.group(2))
                importe = self._convertir_europeo(m.group(3))
                
                # Calcular cantidad
                if precio > 0:
                    cantidad = round(importe / precio)
                else:
                    cantidad = 1
                
                # Normalizar nombre de producto
                if 'ASADO' in articulo and 'LENA' in articulo:
                    articulo = 'TOMATE ASADO LEÑA 720ML'
                elif 'RALLADO' in articulo and 'TOSTADAS' in articulo:
                    articulo = 'TOMATE RALLADO TOSTADAS 720ML'
                elif 'CONFITADO' in articulo:
                    articulo = 'TOMATE CONFITADO 370ML'
                elif 'MERMELADA' in articulo and 'TOMATE' in articulo:
                    articulo = 'MERMELADA DE TOMATE 370ML'
                elif 'MERMELADA' in articulo and 'HIGO' in articulo:
                    articulo = 'MERMELADA DE HIGOS 370ML'
                elif 'SECOS' in articulo and 'ACEITE' in articulo:
                    articulo = 'TOMATES SECOS EN ACEITE 370ML'
                elif 'PISTO' in articulo:
                    articulo = 'PISTO MURCIANO 370ML'
                elif 'FRITO' in articulo and 'HUEVO' in articulo:
                    articulo = 'TOMATE FRITO CON HUEVO 370ML'
                elif 'FRITO' in articulo:
                    articulo = 'TOMATE FRITO 370ML'
                
                lineas.append({
                    'codigo': '',
                    'articulo': articulo,
                    'cantidad': cantidad,
                    'precio_ud': precio,
                    'iva': 10,
                    'base': importe
                })
        
        return lineas
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """
        Extrae total de la factura.
        
        Formatos de resumen fiscal (OCR variable):
        1. "BASE 10 IVA TOTAL" en misma línea
        2. "SUMA BASE 10 IVA" + TOTAL en línea siguiente
        3. "BASE 10" + total en línea siguiente
        """
        lines = texto.split('\n')
        
        for i, line in enumerate(lines):
            # Formato 1: BASE 10 IVA TOTAL (4 números)
            m = re.search(r'([\d,.]+)\s+10\s+([\d,.]+)\s+([\d,.]+)', line)
            if m:
                base = self._convertir_europeo(m.group(1))
                iva = self._convertir_europeo(m.group(2))
                total = self._convertir_europeo(m.group(3))
                if base > 50 and total > base:
                    return total
            
            # Formato 2: "BASE BASE 10 IVA" sin total
            m = re.search(r'([\d,.]+)\s+([\d,.]+)\s+10\s+([\d,.]+)$', line.strip())
            if m:
                base = self._convertir_europeo(m.group(2))
                iva = self._convertir_europeo(m.group(3))
                # Buscar total en siguientes líneas
                for j in range(i+1, min(len(lines), i+5)):
                    nums = re.findall(r'^([\d,.]+)$', lines[j].strip())
                    for n in nums:
                        total = self._convertir_europeo(n)
                        if abs(total - (base + iva)) < 1:
                            return total
                return round(base + iva, 2)
            
            # Formato 3: "BASE 10" solo
            m = re.search(r'([\d,.]+)\s+10$', line.strip())
            if m:
                base = self._convertir_europeo(m.group(1))
                if base > 50:
                    # Buscar total en siguientes líneas
                    total_esperado = round(base * 1.10, 2)
                    for j in range(i+1, min(len(lines), i+5)):
                        nums = re.findall(r'([\d,.]+)', lines[j])
                        for n in nums:
                            val = self._convertir_europeo(n)
                            if abs(val - total_esperado) < 1:
                                return val
                    return total_esperado
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        m = re.search(r'(\d{2}/\d{2}/\d{4})', texto)
        if m:
            return m.group(1)
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae número de factura."""
        m = re.search(r'F25/\d+', texto)
        if m:
            return m.group(0)
        return None
