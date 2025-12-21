"""
Extractor para LA ROSQUILLERIA S.L.U. (El Torro)

Rosquillas marineras artesanales de Santomera (Murcia)
CIF: B73814949

REQUIERE OCR - Las facturas son imágenes escaneadas

Formato factura:
- Líneas: Refer. | Descripción | Lote | Cajas | Bolsas | Tot.Bolsa | Precio | IVA | Importe
- Productos: ROSQUILLA ORIGINAL (4%)
- Gastos envío: 0% IVA

IVA:
- 4%: Rosquillas (alimentación básica)
- 0%: Gastos de envío

Categoría fija: ROSQUILLAS MARINERAS

Creado: 20/12/2025
Validado: 7/7 facturas (2T25, 3T25, 4T25)
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar('LA ROSQUILLERIA', 'ROSQUILLERIA', 'EL TORRO', 'ROSQUILLAS EL TORRO')
class ExtractorLaRosquilleria(ExtractorBase):
    """Extractor para facturas de LA ROSQUILLERIA (requiere OCR)."""
    
    nombre = 'LA ROSQUILLERIA'
    cif = 'B73814949'
    iban = ''  # Pendiente de añadir
    metodo_pdf = 'ocr'
    categoria_fija = 'ROSQUILLAS MARINERAS'
    
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
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de productos.
        
        Productos:
        - RN-1.15 ROSQUILLA ORIGINAL: IVA 4%
        - GSE GASTOS DE ENVIO: IVA 0%
        """
        lineas = []
        
        # Patrón para rosquilla
        # RN-1.15 ROSQUILLA ORIGINAL LOTE CAJAS BOLSAS TOT ... PRECIO 4% IMPORTE
        patron_rosquilla = re.compile(
            r'RN-[\d.]+\s+'                           # Referencia
            r'(ROSQUILLA\s+\w+).*?'                   # Descripción
            r'(\d+[,.]\d{2})\s*€?\s+'                 # Precio unitario
            r'4%\s+'                                   # IVA 4%
            r'(\d+[,.]\d{2})'                          # Importe
        , re.DOTALL | re.IGNORECASE)
        
        match = patron_rosquilla.search(texto)
        if match:
            descripcion = match.group(1).strip()
            precio = self._convertir_europeo(match.group(2))
            importe = self._convertir_europeo(match.group(3))
            cantidad = round(importe / precio, 0) if precio > 0 else 1
            
            lineas.append({
                'codigo': 'RN-1.15',
                'articulo': 'ROSQUILLA MARINERA',
                'cantidad': int(cantidad),
                'precio_ud': round(precio, 2),
                'iva': 4,
                'base': round(importe, 2)
            })
        
        # Patrón para gastos de envío
        # GSE / GSE 2 GASTOS DE ENVIO HASTA X CJS ... PRECIO 0% IMPORTE
        patron_envio = re.compile(
            r'GSE\s*\d*\s+'                            # Referencia GSE o GSE 2
            r'(GASTOS DE ENVIO.*?)'                    # Descripción
            r'(\d+[,.]\d{2})\s*€?\s+'                  # Precio
            r'0%\s+'                                    # IVA 0%
            r'(\d+[,.]\d{2})'                           # Importe
        , re.DOTALL | re.IGNORECASE)
        
        match_envio = patron_envio.search(texto)
        if match_envio:
            importe_envio = self._convertir_europeo(match_envio.group(3))
            
            lineas.append({
                'codigo': 'GSE',
                'articulo': 'GASTOS DE ENVIO',
                'cantidad': 1,
                'precio_ud': round(importe_envio, 2),
                'iva': 0,
                'base': round(importe_envio, 2)
            })
        
        return lineas
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo (1.234,56) a float."""
        if not texto:
            return 0.0
        texto = texto.strip().replace('€', '').strip()
        if '.' in texto and ',' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            texto = texto.replace(',', '.')
        try:
            return float(texto)
        except:
            return 0.0
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """
        Extrae total de la factura.
        
        Nota: El OCR puede fallar en el total, por lo que se prefiere
        calcular desde las líneas si hay discrepancia significativa.
        """
        # Buscar TOTAL: XX,XX €
        patron = re.search(r'TOTAL:\s*(\d+[,.]\d{2})\s*€?', texto, re.IGNORECASE)
        if patron:
            total_ocr = self._convertir_europeo(patron.group(1))
            
            # Validación: calcular total desde líneas
            lineas = self.extraer_lineas(texto)
            if lineas:
                base_rosquillas = sum(l['base'] for l in lineas if l['iva'] == 4)
                base_envio = sum(l['base'] for l in lineas if l['iva'] == 0)
                iva_calc = round(base_rosquillas * 0.04, 2)
                total_calc = round(base_rosquillas + base_envio + iva_calc, 2)
                
                # Si hay discrepancia > 10%, usar el calculado
                if abs(total_ocr - total_calc) > total_calc * 0.10:
                    return total_calc
            
            return total_ocr
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        # Formato: DD/MM/YYYY Factura
        patron = re.search(r'(\d{2}/\d{2}/\d{4})\s+Factura', texto, re.IGNORECASE)
        if patron:
            return patron.group(1)
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae número de factura."""
        patron = re.search(r'Factura\s+(\d+)', texto, re.IGNORECASE)
        if patron:
            return patron.group(1)
        return None
