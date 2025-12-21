"""
Extractor para JIMELUZ EMPRENDEDORES S.L. (OCR)

Frutería con tickets escaneados.
CIF: B84527068
IBAN: (pago efectivo)

Actualizado: 18/12/2025 - limpieza encoding (mantiene OCR)
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict
import re


@registrar('JIMELUZ', 'JIMELUZ EMPRENDEDORES')
class ExtractorJimeluz(ExtractorBase):
    """Extractor para tickets OCR de JIMELUZ."""
    
    nombre = 'JIMELUZ'
    cif = 'B84527068'
    iban = ''
    metodo_pdf = 'ocr'  # Siempre OCR - tickets escaneados
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        
        # Buscar zona de artículos
        inicio = re.search(r'CANT\.?\s*DESCRIPCI[OÓ]N', texto, re.IGNORECASE)
        fin = re.search(r'TOTAL\s*COMPRA', texto, re.IGNORECASE)
        
        zona_articulos = texto[inicio.end():fin.start()] if inicio and fin else texto
        
        # Patrón flexible para tolerar errores OCR
        patron_linea = re.compile(
            r'^[1|lI\d]{0,2}\s*'
            r'(.+?)\s+'
            r'(4|10|21)[,\.]\d{2}\.?\s*'
            r',?(\d{1,3}[,\.]\d{1,2})',
            re.MULTILINE
        )
        
        for match in patron_linea.finditer(zona_articulos):
            desc, iva, importe_raw = match.groups()
            desc_limpia = re.sub(r'[£\*\'\"\|]+', '', desc).strip()
            desc_limpia = re.sub(r'\s+', ' ', desc_limpia)
            importe_limpio = importe_raw.replace(',', '.').replace(' ', '')
            
            try:
                importe = float(importe_limpio)
                iva_int = int(iva)
                base_sin_iva = importe / (1 + iva_int / 100)
                
                lineas.append({
                    'codigo': '',
                    'articulo': desc_limpia,
                    'iva': iva_int,
                    'base': round(base_sin_iva, 2)
                })
            except ValueError:
                continue
        
        # Fallback: Tabla IVA
        if not lineas:
            lineas = self._extraer_tabla_iva(texto)
        
        # Fallback: TOTAL FACTURA
        if not lineas:
            lineas = self._extraer_total_factura(texto)
        
        return lineas
    
    def _extraer_tabla_iva(self, texto: str) -> List[Dict]:
        lineas = []
        patron_tabla = re.compile(
            r'(4|10|21)[,\.]\d{2}%?\s+'
            r'\(?(\d{1,3}[,\.]\d{2})\)?\s+'
            r'\(?(\d{1,3}[,\.]\d{2})\)?\s+'
            r'(?:\d\s+)?'
            r'\(?(\d{1,3}[,\.]\d{2})\)?'
        )
        
        for match in patron_tabla.finditer(texto):
            iva, base, cuota, total = match.groups()
            try:
                base_val = float(base.replace(',', '.'))
                if base_val > 0:
                    lineas.append({
                        'codigo': '',
                        'articulo': f'COMPRA JIMELUZ (IVA {iva}%)',
                        'iva': int(iva),
                        'base': base_val
                    })
            except ValueError:
                continue
        return lineas
    
    def _extraer_total_factura(self, texto: str) -> List[Dict]:
        lineas = []
        total_match = re.search(
            r'TOTAL\s*(?:FACTURA|PAGADO)\s*[\|:\s]*(\d{1,3}[,\.]\d{2})',
            texto, re.IGNORECASE
        )
        if total_match:
            total = float(total_match.group(1).replace(',', '.'))
            if 0 < total < 200:
                base_estimada = total / 1.10
                lineas.append({
                    'codigo': '',
                    'articulo': 'COMPRA JIMELUZ (OCR sin desglose)',
                    'iva': 10,
                    'base': round(base_estimada, 2)
                })
        return lineas
