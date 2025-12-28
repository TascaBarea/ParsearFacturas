# -*- coding: utf-8 -*-
"""
Extractor para BODEGA VIRGEN DE LA SIERRA S.COOP.
Bodega cooperativa en Villarroya de la Sierra, Zaragoza

CIF: F50019868
Método: Híbrido (pdfplumber + OCR fallback)

Productos: vinos (Albada, Vendimia Seleccionada), portes
IVA: 21% (bebidas alcohólicas)

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


@registrar('VIRGEN DE LA SIERRA', 'BODEGA VIRGEN DE LA SIERRA', 'VIRGEN SIERRA', 
           'BODEGA VIRGEN DE LA SIERRA S.COOP.')
class ExtractorVirgenDeLaSierra(ExtractorBase):
    """Extractor para facturas de Bodega Virgen de la Sierra."""
    
    nombre = 'BODEGA VIRGEN DE LA SIERRA'
    cif = 'F50019868'
    iban = ''
    metodo_pdf = 'hibrido'
    
    def extraer_texto(self, pdf_path: str) -> str:
        """Extrae texto del PDF usando método híbrido."""
        texto = self._extraer_pdfplumber(pdf_path)
        if texto and len(texto.strip()) > 100:
            return texto
        return self._extraer_ocr(pdf_path)
    
    def _extraer_pdfplumber(self, pdf_path: str) -> str:
        """Extrae texto con pdfplumber."""
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
        Extrae líneas de productos.
        
        Formato: CODIGO DESCRIPCION CANTIDAD PRECIO IMPORTE
        Ejemplo: 201-02023 C.P. VENDIMIA SELECCIONADA 2023 48,00 4,600000 220,80
        """
        lineas = []
        
        patron_linea = re.compile(
            r'^(\d{3}-\d{5})\s+'           # Código (ej: 201-02023)
            r'(.+?)\s+'                     # Descripción
            r'(\d+[,\.]\d+)\s+'             # Cantidad
            r'(\d+[,\.]\d+)\s+'             # Precio unitario
            r'(\d+[,\.]\d+)$',              # Importe
            re.MULTILINE
        )
        
        for match in patron_linea.finditer(texto):
            codigo = match.group(1)
            descripcion = match.group(2).strip()
            cantidad = self._convertir_europeo(match.group(3))
            precio = self._convertir_europeo(match.group(4))
            importe = self._convertir_europeo(match.group(5))
            
            descripcion = self._limpiar_descripcion(descripcion)
            
            if importe > 0:
                lineas.append({
                    'codigo': codigo,
                    'articulo': descripcion[:50],
                    'cantidad': cantidad,
                    'precio_ud': precio,
                    'iva': 21,  # Vinos siempre 21%
                    'base': importe
                })
        
        return lineas
    
    def _limpiar_descripcion(self, desc: str) -> str:
        """Limpia la descripción."""
        desc = re.sub(r'\s+Uds\.\s*\d+', '', desc)
        desc = ' '.join(desc.split())
        return desc
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """Extrae el total de la factura."""
        # Buscar formato XXX,XX€
        patron1 = re.search(r'(\d+[,\.]\d+)\s*€', texto)
        if patron1:
            return self._convertir_europeo(patron1.group(1))
        
        # Alternativa: "Total" seguido de importe
        patron2 = re.search(r'Total\s+(\d+[,\.]\d+)', texto, re.IGNORECASE)
        if patron2:
            return self._convertir_europeo(patron2.group(1))
        
        # Calcular desde cuadro fiscal
        cuadro = self._extraer_cuadro_fiscal(texto)
        if cuadro:
            return round(sum(d['base'] + d['iva'] for d in cuadro), 2)
        
        return None
    
    def _extraer_cuadro_fiscal(self, texto: str) -> List[Dict]:
        """Extrae el cuadro de desglose de IVA."""
        desglose = []
        
        patron = re.compile(
            r'(\d+[,\.]\d+)\s+'       # Base imponible
            r'21[,\.]00\s+'           # Tipo IVA (siempre 21%)
            r'(\d+[,\.]\d+)',         # Cuota IVA
            re.MULTILINE
        )
        
        match = patron.search(texto)
        if match:
            base = self._convertir_europeo(match.group(1))
            cuota = self._convertir_europeo(match.group(2))
            desglose.append({'tipo': 21, 'base': base, 'iva': cuota})
        
        return desglose
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de emisión."""
        patron = re.search(r'(\d{2}-\d{2}-\d{4})', texto)
        if patron:
            return patron.group(1).replace('-', '/')
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
