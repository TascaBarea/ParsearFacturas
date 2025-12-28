# -*- coding: utf-8 -*-
"""
Extractor para CELONIS INC. (Make.com)
Plataforma de automatización SaaS

Proveedor: Celonis Inc.
US EIN: 61-1797223
Producto: Make Core plan
Moneda: USD (sin IVA - empresa americana)

Creado: 28/12/2025
Corregido: 28/12/2025 - Integración con sistema
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re
import pdfplumber


@registrar('CELONIS', 'CELONIS INC', 'CELONIS INC.', 'MAKE', 'MAKE.COM')
class ExtractorCelonisMake(ExtractorBase):
    """Extractor para facturas de Celonis Inc. (Make.com)."""
    
    nombre = 'CELONIS INC.'
    cif = ''
    iban = ''
    metodo_pdf = 'pdfplumber'
    categoria_fija = 'GASTOS VARIOS'
    
    def extraer_texto(self, pdf_path: str) -> str:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                textos = []
                for page in pdf.pages:
                    texto = page.extract_text()
                    if texto:
                        textos.append(texto)
                return '\n'.join(textos)
        except:
            return ''
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        
        patrones = [
            r'\$(\d+[,\.]\d+)\s+\$(\d+[,\.]\d+)\s*$',
            r'Make\s+Core[^\n]*\$(\d+[,\.]\d+)',
            r'(\d+[,\.]\d+)\s+USD',
        ]
        
        importe = None
        for patron in patrones:
            match = re.search(patron, texto, re.MULTILINE | re.IGNORECASE)
            if match:
                importe = self._convertir_numero(match.group(match.lastindex))
                break
        
        if importe and importe > 0:
            periodo = self._extraer_periodo(texto)
            descripcion = "Make Core plan 10000 ops/mes"
            if periodo:
                descripcion += f" ({periodo})"
            
            lineas.append({
                'codigo': 'MAKE-CORE',
                'articulo': descripcion[:50],
                'cantidad': 1,
                'precio_ud': importe,
                'iva': 0,
                'base': importe
            })
        
        if not lineas:
            total = self.extraer_total(texto)
            if total and total > 0:
                lineas.append({
                    'codigo': 'MAKE',
                    'articulo': 'Suscripción Make.com',
                    'cantidad': 1,
                    'precio_ud': total,
                    'iva': 0,
                    'base': total
                })
        
        return lineas
    
    def _extraer_periodo(self, texto: str) -> Optional[str]:
        patron = re.search(r'([A-Z][a-z]{2}\s+\d+)\s*[–\-]\s*([A-Z][a-z]{2}\s+\d+,?\s*\d{4})', texto)
        if patron:
            return f"{patron.group(1)} - {patron.group(2)}"
        return None
    
    def extraer_total(self, texto: str) -> Optional[float]:
        patrones = [
            r'Amount\s+(?:due|paid)\s+\$(\d+[,\.]\d+)',
            r'Total\s+\$(\d+[,\.]\d+)',
            r'\$(\d+[,\.]\d+)\s+USD\s+(?:due|paid)',
            r'Total[:\s]+\$?(\d+[,\.]\d+)',
        ]
        
        for patron_str in patrones:
            match = re.search(patron_str, texto, re.IGNORECASE)
            if match:
                return self._convertir_numero(match.group(1))
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        meses = {
            'January': '01', 'February': '02', 'March': '03', 'April': '04',
            'May': '05', 'June': '06', 'July': '07', 'August': '08',
            'September': '09', 'October': '10', 'November': '11', 'December': '12'
        }
        
        patron = re.search(r'(?:Date|Issued)[:\s]+([A-Z][a-z]+)\s+(\d{1,2}),?\s+(\d{4})', texto, re.IGNORECASE)
        if patron:
            mes_nombre = patron.group(1)
            dia = patron.group(2).zfill(2)
            año = patron.group(3)
            mes = meses.get(mes_nombre, '01')
            return f"{dia}/{mes}/{año}"
        
        patron2 = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', texto)
        if patron2:
            return patron2.group(0)
        
        return None
    
    def _convertir_numero(self, texto: str) -> float:
        if not texto:
            return 0.0
        texto = str(texto).strip()
        texto = texto.replace(',', '').replace('$', '')
        try:
            return float(texto)
        except:
            return 0.0
