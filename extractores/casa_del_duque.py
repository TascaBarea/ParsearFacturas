# -*- coding: utf-8 -*-
"""
Extractor para CASA DEL DUQUE 2015 SL (HOME IDEAL)
Bazar/tienda de hogar en C/Duque de Alba 15, Madrid

CIF: B87309613
Tel: 914293959
Método: OCR (tickets escaneados)

Productos: artículos de hogar, limpieza, decoración
IVA: 21% (todos los productos)

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


@registrar('CASA DEL DUQUE', 'CASA DEL DUQUE SL', 'CASA DEL DUQUE 2015 SL', 
           'HOME IDEAL', 'CASA DEL DUQUE 2015')
class ExtractorCasaDelDuque(ExtractorBase):
    """Extractor para tickets de CASA DEL DUQUE / HOME IDEAL."""
    
    nombre = 'CASA DEL DUQUE 2015 SL'
    cif = 'B87309613'
    iban = ''
    metodo_pdf = 'ocr'
    
    def extraer_texto(self, pdf_path: str) -> str:
        """Extrae texto usando método híbrido."""
        texto = self._extraer_pdfplumber(pdf_path)
        if texto and len(texto.strip()) > 100:
            return texto
        return self._extraer_ocr(pdf_path)
    
    def _extraer_pdfplumber(self, pdf_path: str) -> str:
        """Extrae texto con pdfplumber."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                texto = pdf.pages[0].extract_text()
                return texto or ''
        except:
            return ''
    
    def _extraer_ocr(self, pdf_path: str) -> str:
        """Extrae texto del PDF usando OCR (Tesseract)."""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                img_path = os.path.join(tmpdir, 'page.png')
                subprocess.run([
                    'pdftoppm', '-png', '-r', '300', '-singlefile',
                    pdf_path, os.path.join(tmpdir, 'page')
                ], capture_output=True, check=True)
                result = subprocess.run([
                    'tesseract', img_path, 'stdout', '-l', 'spa'
                ], capture_output=True, text=True)
                return result.stdout
        except:
            return ''
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de producto del ticket.
        
        Formato 1: DESCRIPCION UNDS SUMA IVA%
        Formato 2: CANx PRECIO IVA%-DESCRIPCION SUMA
        """
        lineas = []
        
        # Formato 1: DESCRIPCION UNDS SUMA 21%
        patron1 = re.compile(
            r'^([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ0-9\s/\-\.]+?)\s+'
            r'(\d+)\s+'
            r'(\d+[,\.]\d+)\s+'
            r'21%',
            re.MULTILINE
        )
        
        for match in patron1.finditer(texto):
            descripcion = match.group(1).strip()
            cantidad = int(match.group(2))
            importe = self._convertir_europeo(match.group(3))
            
            if len(descripcion) < 2 or importe < 0.10:
                continue
            if any(skip in descripcion.upper() for skip in ['DESCRIPCION', 'IMPONIBLE', 'ARTIC', 'TOTAL']):
                continue
            
            lineas.append({
                'codigo': '',
                'articulo': descripcion[:50],
                'cantidad': cantidad,
                'precio_ud': round(importe / cantidad, 2) if cantidad > 0 else importe,
                'iva': 21,
                'base': importe
            })
        
        # Formato 2: CANx PRECIO 21%-DESCRIPCION SUMA
        patron2 = re.compile(
            r'(\d+)x\s+'
            r'(\d+[,\.]\d+)\s+'
            r'21%-'
            r'(.+?)\s+'
            r'(\d+[,\.]\d+)',
            re.MULTILINE
        )
        
        for match in patron2.finditer(texto):
            cantidad = int(match.group(1))
            precio = self._convertir_europeo(match.group(2))
            descripcion = match.group(3).strip()
            importe = self._convertir_europeo(match.group(4))
            
            if importe < 0.10:
                continue
            
            lineas.append({
                'codigo': '',
                'articulo': descripcion[:50],
                'cantidad': cantidad,
                'precio_ud': precio,
                'iva': 21,
                'base': importe
            })
        
        return lineas
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """Extrae el total de la factura."""
        patrones = [
            r'ARTIC[,\.\s]*TOTAL:\s*(\d+[,\.]\d+)\s*Euro',
            r'TOTAL:\s*(\d+[,\.]\d+)\s*Euro',
            r'(\d+[,\.]\d+)\s*Euro\s*$',
            r'TOTAL:\s*(\d+[,\.]\d+)',
        ]
        
        for patron_str in patrones:
            match = re.search(patron_str, texto, re.IGNORECASE | re.MULTILINE)
            if match:
                total = self._convertir_europeo(match.group(1))
                if total > 1.0:
                    return total
        
        # Alternativa: calcular desde cuadro fiscal
        cuadro = self._extraer_cuadro_fiscal(texto)
        if cuadro:
            return round(sum(d['base'] + d['iva'] for d in cuadro), 2)
        
        return None
    
    def _extraer_cuadro_fiscal(self, texto: str) -> List[Dict]:
        """Extrae el cuadro de desglose de IVA."""
        desglose = []
        
        patrones = [
            r'(\d+[,\.]\d+)\s+21%\s+(\d+[,\.]\d+)',
            r'(\d+[,\.]\d+)\s+21\s*%\s+(\d+[,\.]\d+)',
        ]
        
        for patron_str in patrones:
            match = re.search(patron_str, texto, re.IGNORECASE)
            if match:
                base = self._convertir_europeo(match.group(1))
                cuota = self._convertir_europeo(match.group(2))
                if base > 0:
                    desglose.append({'tipo': 21, 'base': base, 'iva': cuota})
                    break
        
        return desglose
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de emisión."""
        patrones = [
            r'Fecha\s*:?\s*(\d{2}-\d{2}-\d{4})',
            r'Fecha\s*:?\s*(\d{2}-\d{2}-202\d)',
        ]
        
        for patron_str in patrones:
            match = re.search(patron_str, texto, re.IGNORECASE)
            if match:
                fecha = match.group(1)
                fecha = re.sub(r'202[^\d]', '2025', fecha)
                return fecha.replace('-', '/')
        
        return None
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo a float."""
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
