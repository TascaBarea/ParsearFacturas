# -*- coding: utf-8 -*-
"""
Extractor para ECOMS SUPERMARKET S.L.
Supermercado local en C/ Huertas 72, Madrid

CIF: B72738602
Método: Híbrido (pdfplumber + OCR fallback)

Creado: 28/12/2025
Corregido: 28/12/2025 - Integración con sistema
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re
import subprocess
import tempfile
import os
import pdfplumber


@registrar('ECOMS', 'ECOMS SUPERMARKET SL', 'ECOMS SUPERMARKET S.L.', 'ECOMS S', 'ECOMS SUPERMARKET')
class ExtractorEcoms(ExtractorBase):
    """Extractor para tickets de ECOMS SUPERMARKET."""
    
    nombre = 'ECOMS SUPERMARKET'
    cif = 'B72738602'
    iban = ''
    metodo_pdf = 'hibrido'
    
    def extraer_texto(self, pdf_path: str) -> str:
        texto = self._extraer_pdfplumber(pdf_path)
        if texto and len(texto.strip()) > 100:
            return texto
        return self._extraer_ocr(pdf_path)
    
    def _extraer_pdfplumber(self, pdf_path: str) -> str:
        try:
            texto_completo = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    texto = page.extract_text()
                    if texto:
                        texto_completo.append(texto)
            return '\n'.join(texto_completo)
        except:
            return ''
    
    def _extraer_ocr(self, pdf_path: str) -> str:
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                img_path = os.path.join(tmpdir, 'page.png')
                subprocess.run(['pdftoppm', '-png', '-r', '300', '-singlefile',
                    pdf_path, os.path.join(tmpdir, 'page')], capture_output=True, check=True)
                result = subprocess.run(['tesseract', img_path, 'stdout', '-l', 'spa'],
                    capture_output=True, text=True)
                return result.stdout
        except:
            return ''
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron_linea = re.compile(
            r'^([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ0-9\s\-\.]+?)\s+'
            r'(\d+[,\.]\d+)\s+'
            r'(\d+)[,\.]00%',
            re.MULTILINE
        )
        
        for match in patron_linea.finditer(texto):
            descripcion = match.group(1).strip()
            importe_str = match.group(2)
            iva = int(match.group(3))
            
            if len(descripcion) < 3:
                continue
            if any(skip in descripcion for skip in ['TIPO IVA', 'TOTALES', 'FACTURA', 'DATOS', 'FISCALES']):
                continue
            
            importe = self._convertir_europeo(importe_str)
            
            if importe > 0:
                lineas.append({
                    'codigo': '',
                    'articulo': re.sub(r'[|¿¡\[\]{}]', '', descripcion)[:50],
                    'cantidad': 1,
                    'precio_ud': importe,
                    'iva': iva,
                    'base': importe
                })
        
        if not lineas:
            lineas = self._extraer_desde_cuadro_fiscal(texto)
        
        return lineas
    
    def _extraer_desde_cuadro_fiscal(self, texto: str) -> List[Dict]:
        lineas = []
        cuadro = self._extraer_cuadro_fiscal(texto)
        for item in cuadro:
            lineas.append({
                'codigo': '',
                'articulo': f'COMPRA IVA {item["tipo"]}%',
                'cantidad': 1,
                'precio_ud': item['base'],
                'iva': item['tipo'],
                'base': item['base']
            })
        return lineas
    
    def _extraer_cuadro_fiscal(self, texto: str) -> List[Dict]:
        desglose = []
        patron = re.compile(r'(\d+)[,\.]00%\s+(\d+[,\.]\d+)\s+(\d+[,\.]\d+)', re.MULTILINE)
        for match in patron.finditer(texto):
            tipo = int(match.group(1))
            base = self._convertir_europeo(match.group(2))
            cuota = self._convertir_europeo(match.group(3))
            if tipo in [4, 10, 21] and base > 0:
                desglose.append({'tipo': tipo, 'base': base, 'iva': cuota})
        return desglose
    
    def extraer_total(self, texto: str) -> Optional[float]:
        patrones = [
            r'TOTAL\s+FACTURA\s+(\d+[,\.]\d+)',
            r'TOTAL\s+FAÉTURA\s+(\d+[,\.]\d+)',
            r'TOTAL\s+FACT[UÚ]RA\s+(\d+[,\.]\d+)',
            r'TOTAL[:\s]+(\d+[,\.]\d+)\s*€',
        ]
        for patron in patrones:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                return self._convertir_europeo(match.group(1))
        cuadro = self._extraer_cuadro_fiscal(texto)
        if cuadro:
            return round(sum(d['base'] + d['iva'] for d in cuadro), 2)
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        patron = re.search(r'EMITIDA:?\s*(\d{2}-\d{2}-\d{4})', texto, re.IGNORECASE)
        if patron:
            return patron.group(1).replace('-', '/')
        patron2 = re.search(r'(\d{2}/\d{2}/\d{4})', texto)
        if patron2:
            return patron2.group(1)
        return None
    
    def _convertir_europeo(self, texto: str) -> float:
        if not texto:
            return 0.0
        texto = str(texto).strip()
        if ',' in texto and '.' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            texto = texto.replace(',', '.')
        try:
            return float(texto)
        except:
            return 0.0
