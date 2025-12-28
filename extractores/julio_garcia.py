"""
Extractor para JULIO GARCIA VIVAS (Ay Madre!)

Verdulería del Mercado de San Fernando (Embajadores).
NIF: 02869898G

METODO: OCR (tesseract) - Las facturas son imágenes escaneadas

Formato factura:
FACTURA Nº 28693354
FECHA: 30/09/2025

ALBARÁN Nº ... DE FECHA ...    TOTAL
...

BASE IMPONIBLE    I.V.A.    R.E.
36,72    4%    1,47    0,5%    0,00
0,59    10%   0,06    1,4%    0,00
         21%         5,2%

TOTAL BASE IMPONIBLE    37,31
TOTAL I.V.A.            1,53
TOTAL R.E.              0,00
TOTAL FACTURA          38,84

IVA: Principalmente 4% (verduras), ocasionalmente 10%
Categoría fija: GENERICO PARA VERDURAS

Creado: 26/12/2025
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re
import subprocess
import tempfile
import os


@registrar('JULIO GARCIA VIVAS', 'GARCIA VIVAS JULIO', 'JULIO GARCIA', 'AY MADRE')
class ExtractorJulioGarcia(ExtractorBase):
    """Extractor para facturas de JULIO GARCIA VIVAS (OCR)."""
    
    nombre = 'JULIO GARCIA VIVAS'
    cif = '02869898G'
    iban = ''  # Pendiente
    metodo_pdf = 'ocr'
    categoria_fija = 'GENERICO PARA VERDURAS'
    
    def extraer_texto_ocr(self, pdf_path: str) -> str:
        """Extrae texto usando OCR (tesseract)."""
        try:
            from pdf2image import convert_from_path
            
            # Convertir PDF a imagen(es)
            images = convert_from_path(pdf_path, dpi=300)
            
            texto_completo = ""
            for img in images:
                # Guardar imagen temporal
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    img.save(tmp.name)
                    # OCR con tesseract
                    result = subprocess.run(
                        ['tesseract', tmp.name, 'stdout', '-l', 'eng'],
                        capture_output=True, text=True
                    )
                    texto_completo += result.stdout
                    os.unlink(tmp.name)
            
            return texto_completo
        except Exception as e:
            return ""
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas del cuadro fiscal.
        
        Formato OCR (con posibles errores):
        BASE IMPONIBLE LWA. R.E.
        36,72 4% 147 0,5% 0,00
        0,59 10% 0,06 1,4% 0,00
        """
        lineas = []
        
        # Patrón para IVA 4%: "base 4% cuota"
        # El OCR puede leer "1,47" como "147" o "1.47"
        match_4 = re.search(
            r'(\d+[.,]\d{2})\s+4%\s+(\d+[.,]?\d*)',
            texto
        )
        
        if match_4:
            base = self._convertir_europeo(match_4.group(1))
            if base > 0:
                lineas.append({
                    'codigo': '',
                    'articulo': 'VERDURAS AY MADRE',
                    'cantidad': 1,
                    'precio_ud': round(base, 2),
                    'iva': 4,
                    'base': round(base, 2),
                    'categoria': self.categoria_fija
                })
        
        # Patrón para IVA 10%: "base 10% cuota"
        match_10 = re.search(
            r'(\d+[.,]\d{2})\s+10%\s+(\d+[.,]?\d*)',
            texto
        )
        
        if match_10:
            base = self._convertir_europeo(match_10.group(1))
            if base > 0:
                lineas.append({
                    'codigo': '',
                    'articulo': 'VERDURAS AY MADRE 10%',
                    'cantidad': 1,
                    'precio_ud': round(base, 2),
                    'iva': 10,
                    'base': round(base, 2),
                    'categoria': self.categoria_fija
                })
        
        # Patrón para IVA 21% (raro, pero posible)
        match_21 = re.search(
            r'(\d+[.,]\d{2})\s+21%\s+(\d+[.,]?\d*)',
            texto
        )
        
        if match_21:
            base = self._convertir_europeo(match_21.group(1))
            if base > 0:
                lineas.append({
                    'codigo': '',
                    'articulo': 'VERDURAS AY MADRE 21%',
                    'cantidad': 1,
                    'precio_ud': round(base, 2),
                    'iva': 21,
                    'base': round(base, 2),
                    'categoria': self.categoria_fija
                })
        
        # Si no encontramos cuadro fiscal, buscar TOTAL BASE IMPONIBLE
        if not lineas:
            match_total = re.search(
                r'TOTAL\s*BASE\s*IMPONIBLE\s*(\d+[.,]\d{2})',
                texto,
                re.IGNORECASE
            )
            if match_total:
                base = self._convertir_europeo(match_total.group(1))
                if base > 0:
                    lineas.append({
                        'codigo': '',
                        'articulo': 'VERDURAS AY MADRE',
                        'cantidad': 1,
                        'precio_ud': round(base, 2),
                        'iva': 4,  # Por defecto verduras
                        'base': round(base, 2),
                        'categoria': self.categoria_fija
                    })
        
        return lineas
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo a float."""
        if not texto:
            return 0.0
        texto = texto.strip()
        # Manejar caso "1.234,56" o "1234,56" o "1234.56"
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
        # Patrón: "TOTAL FACTURA 38,84" o "TOTAL FACTURA 115,79"
        patrones = [
            r'TOTAL\s*FACTURA\s*(\d+[.,]\d{2})',
            r'TOTAL\s+(\d+[.,]\d{2})\s*$',
        ]
        
        for patron in patrones:
            m = re.search(patron, texto, re.IGNORECASE | re.MULTILINE)
            if m:
                return self._convertir_europeo(m.group(1))
        
        # Alternativa: calcular desde bases
        lineas = self.extraer_lineas(texto)
        if lineas:
            total = 0
            for l in lineas:
                total += l['base'] * (1 + l['iva'] / 100)
            return round(total, 2)
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        # Formato: "FECHA: 30/09/2025"
        m = re.search(r'FECHA[:\s]+(\d{2})/(\d{2})/(\d{4})', texto, re.IGNORECASE)
        if m:
            return f"{m.group(1)}/{m.group(2)}/{m.group(3)}"
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae número de factura."""
        m = re.search(r'FACTURA\s*N[°ºo]?\s*(\d+)', texto, re.IGNORECASE)
        return m.group(1) if m else None
