# -*- coding: utf-8 -*-
"""
Extractor para PRODUCTOS MANIPULADOS ABELLAN S.L. (El Labrador / Pepejo)

Proveedor de conservas vegetales de El Raal (Murcia)
CIF: B30473326
IBAN: ES06 2100 8321 0413 0018 3503

Formato factura (OCR - PDF escaneado):
- Lineas producto: CANTIDAD DESCRIPCION PRECIO IMPORTE
- Ejemplo: 24,00 TOMATE ASADO LENA 720 ML EL LABRADOR 1,9500 46,80
- IVA: 10% (conservas vegetales)

Creado: 19/12/2025
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re
import subprocess
import tempfile
import os


@registrar('MANIPULADOS ABELLAN', 'ABELLAN', 'EL LABRADOR', 'PEPEJO', 'PEPEJOLABRADOR',
           'PRODUCTOS MANIPULADOS ABELLAN')
class ExtractorManipuladosAbellan(ExtractorBase):
    """Extractor para facturas de MANIPULADOS ABELLAN S.L."""
    
    nombre = 'MANIPULADOS ABELLAN'
    cif = 'B30473326'
    iban = 'ES06 2100 8321 0413 0018 3503'
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
        
        # Patron para lineas de producto
        patron_linea = re.compile(
            r'^(\d+,\d{2})\s+'
            r'([A-Z][A-Z\s\d./-]+?)\s+'
            r'(\d+,\d{4})\s+'
            r'(\d+,\d{2})\s*$'
        , re.MULTILINE)
        
        for match in patron_linea.finditer(texto):
            cantidad = self._convertir_europeo(match.group(1))
            descripcion = match.group(2).strip()
            precio = self._convertir_europeo(match.group(3))
            importe = self._convertir_europeo(match.group(4))
            
            descripcion = re.sub(r'\s+', ' ', descripcion)
            descripcion = re.sub(r'\s*(EL LABRADOR|LABRADOR|ML|370|720)\s*$', '', descripcion)
            descripcion = descripcion.strip()
            
            lineas.append({
                'codigo': '',
                'articulo': descripcion[:50],
                'cantidad': cantidad,
                'precio_ud': round(precio, 4),
                'iva': 10,
                'base': round(importe, 2)
            })
        
        return lineas
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo (1.234,56) a float."""
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
        """Extrae total de la factura."""
        patron = re.search(
            r'(\d+,\d{2})\s+(\d+,\d{2})\s+10\s+(\d+,\d{2})\s+(\d+,\d{2})\s*$',
            texto,
            re.MULTILINE
        )
        if patron:
            return self._convertir_europeo(patron.group(4))
        
        patron_alt = re.search(r'TOTAL\s*FACTURA\s*\n\s*[\d,\s]+\s+(\d+,\d{2})\s*$', texto, re.MULTILINE)
        if patron_alt:
            return self._convertir_europeo(patron_alt.group(1))
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        patron = re.search(r'(\d{2}/\d{2}/\d{4})', texto)
        if patron:
            return patron.group(1)
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae numero de factura."""
        patron = re.search(r'(F\d+/\d+)', texto)
        if patron:
            return patron.group(1)
        return None
