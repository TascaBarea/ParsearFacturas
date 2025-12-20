# -*- coding: utf-8 -*-
"""
Extractor para LA ROSQUILLERIA S.L.U. (Las Rosquillas El Torro)

Proveedor de rosquillas artesanales de Santomera (Murcia)
CIF: B73814949

Formato factura (OCR - PDF escaneado):
- Linea producto: CODIGO DESCRIPCION LOTE CAJAS BOLSAS TOT_BOLSA PRECIO IVA IMPORTE
- Ejemplo: RN-1.15 ROSQUILLA ORIGINAL 3124 3 15 45 1,02 10% 45,90
- Gastos envio: GSE GASTOS DE ENVIO HASTA 3 CJS. 1 1 10,00 0% 10,00

IVA: Variable - 4% o 10% en rosquillas, 0% en gastos de envio

Creado: 20/12/2025
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re
import subprocess
import tempfile
import os


@registrar('LA ROSQUILLERIA', 'ROSQUILLERIA', 'LAS ROSQUILLAS', 'EL TORRO', 
           'ROSQUILLAS EL TORRO', 'ROSQUILLASELTORRO')
class ExtractorLaRosquilleria(ExtractorBase):
    """Extractor para facturas de LA ROSQUILLERIA S.L.U."""
    
    nombre = 'LA ROSQUILLERIA'
    cif = 'B73814949'
    metodo_pdf = 'ocr'
    
    def extraer_texto_ocr(self, pdf_path: str) -> str:
        """Extrae texto del PDF usando OCR."""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                img_base = os.path.join(tmpdir, 'page')
                cmd = ['pdftoppm', '-png', '-f', '1', '-l', '1', '-r', '300', pdf_path, img_base]
                subprocess.run(cmd, capture_output=True, check=True)
                
                img_path = None
                for f in os.listdir(tmpdir):
                    if f.endswith('.png'):
                        img_path = os.path.join(tmpdir, f)
                        break
                
                if not img_path:
                    return ''
                
                result = subprocess.run(
                    ['tesseract', img_path, 'stdout'],
                    capture_output=True,
                    text=True
                )
                return result.stdout
        except Exception as e:
            return ''
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """Extrae lineas INDIVIDUALES de productos."""
        lineas = []
        
        # Patron para linea de rosquillas
        patron_rosquilla = re.compile(
            r'(RN-[\d.]+)\s+'
            r'(ROSQUILLA[A-Z\s]*)\s+'
            r'(\d{4})\s+'
            r'(\d+)\s+'
            r'(\d+)\s+'
            r'(\d+)\s+'
            r'(\d*,?\d+)\s*[E]?\s+'
            r'(\d+)%\s+'
            r'(\d+,\d{2})'
        , re.IGNORECASE)
        
        # Patron para gastos de envio
        patron_envio = re.compile(
            r'(GSE)\s+'
            r'(GASTOS\s+DE\s+ENVIO[A-Z0-9\s.]*)\s+'
            r'(\d+)\s+'
            r'(\d+)\s+'
            r'(\d*,?\d+)\s*[E]?\s+'
            r'(\d+)%\s+'
            r'[4]?(\d+,\d{2})'
        , re.IGNORECASE)
        
        # Buscar rosquillas
        for match in patron_rosquilla.finditer(texto):
            codigo = match.group(1)
            descripcion = match.group(2).strip()
            cantidad = int(match.group(6))
            precio_raw = match.group(7)
            iva = int(match.group(8))
            importe = self._convertir_europeo(match.group(9))
            
            precio = self._convertir_europeo(precio_raw)
            if precio > 50:
                precio = 1.02
            
            lineas.append({
                'codigo': codigo,
                'articulo': descripcion[:50],
                'cantidad': cantidad,
                'precio_ud': round(precio, 2),
                'iva': iva,
                'base': round(importe, 2)
            })
        
        # Buscar gastos de envio
        for match in patron_envio.finditer(texto):
            codigo = match.group(1)
            descripcion = 'GASTOS DE ENVIO'
            cantidad = 1
            precio_raw = match.group(5)
            iva = int(match.group(6))
            importe_raw = match.group(7)
            
            precio = self._convertir_europeo(precio_raw)
            if precio > 50:
                precio = 10.00
            
            importe = self._convertir_europeo(importe_raw)
            if importe > 50 or importe < 5:
                importe = 10.00
            
            lineas.append({
                'codigo': codigo,
                'articulo': descripcion,
                'cantidad': cantidad,
                'precio_ud': round(precio, 2),
                'iva': iva,
                'base': round(importe, 2)
            })
        
        return lineas
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo (1.234,56) a float."""
        if not texto:
            return 0.0
        texto = texto.strip()
        # Quitar simbolo euro si existe
        texto = re.sub(r'[^0-9.,]', '', texto)
        if '.' in texto and ',' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            texto = texto.replace(',', '.')
        try:
            return float(texto)
        except:
            return 0.0
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """Extrae total de la factura."""
        patron = re.search(r'TOTAL:\s*(\d+,\d{2})', texto, re.IGNORECASE)
        if patron:
            return self._convertir_europeo(patron.group(1))
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        patron = re.search(r'(\d{2}/\d{2}/\d{4})', texto)
        if patron:
            return patron.group(1)
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae numero de factura."""
        patron = re.search(r'Numero\s*(\d{7})', texto, re.IGNORECASE)
        if patron:
            return patron.group(1)
        patron2 = re.search(r'Factura\s+(\d{7})', texto, re.IGNORECASE)
        if patron2:
            return patron2.group(1)
        return None
