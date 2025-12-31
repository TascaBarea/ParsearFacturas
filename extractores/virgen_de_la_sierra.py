# -*- coding: utf-8 -*-
"""
Extractor para BODEGA VIRGEN DE LA SIERRA S.COOP.
Bodega cooperativa en Villarroya de la Sierra, Zaragoza

CIF: F50019868
Método: pdfplumber (funciona perfecto, no necesita OCR)

Productos: vinos (Albada, Vendimia Seleccionada), portes
IVA: 21% (bebidas alcohólicas)

VERSIÓN DEFINITIVA: 28/12/2025
Validado contra 7 facturas reales
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re
import pdfplumber


@registrar('VIRGEN DE LA SIERRA', 'BODEGA VIRGEN DE LA SIERRA', 'VIRGEN SIERRA', 
           'BODEGA VIRGEN DE LA SIERRA S.COOP.', 'BODEGAS VIRGEN DE LA SIERRA')
class ExtractorVirgenDeLaSierra(ExtractorBase):
    """Extractor para facturas de Bodega Virgen de la Sierra."""
    
    nombre = 'BODEGA VIRGEN DE LA SIERRA'
    cif = 'F50019868'
    iban = ''
    metodo_pdf = 'pdfplumber'
    
    def extraer_texto(self, pdf_path: str) -> str:
        """Extrae texto del PDF con pdfplumber."""
        try:
            texto_completo = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    texto = page.extract_text()
                    if texto:
                        texto_completo.append(texto)
            return '\n'.join(texto_completo)
        except Exception as e:
            print(f"[VIRGEN] Error extrayendo texto: {e}")
            return ''
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de productos.
        
        Formato real del PDF:
        201-02023 C.P. VENDIMIA SELECCIONADA 2023 48,00 4,600000 220,80
        202-00025 ALBADA PARAJE CAÑADILLA 2,00 8,000000 16,00
        115-10004 PORTES TRANSPORTE 1,00 25,000000 25,00
        """
        lineas = []
        
        if not texto:
            return lineas
        
        # Patrón para líneas de producto
        # Código: XXX-XXXXX (3 dígitos - 5 dígitos)
        # Descripción: texto variable
        # Cantidad: XX,XX
        # Precio: XX,XXXXXX (6 decimales)
        # Importe: XXX,XX
        patron_linea = re.compile(
            r'^(\d{3}-\d{5})\s+'              # Código
            r'(.+?)\s+'                        # Descripción
            r'(\d+,\d{2})\s+'                  # Cantidad
            r'(\d+,\d{6})\s+'                  # Precio (6 decimales)
            r'(\d+,\d{2})$',                   # Importe
            re.MULTILINE
        )
        
        for match in patron_linea.finditer(texto):
            codigo = match.group(1)
            descripcion = match.group(2).strip()
            cantidad = self._convertir_europeo(match.group(3))
            precio = self._convertir_europeo(match.group(4))
            importe = self._convertir_europeo(match.group(5))
            
            # Limpiar descripción
            descripcion = self._limpiar_descripcion(descripcion)
            
            if importe > 0:
                lineas.append({
                    'codigo': codigo,
                    'articulo': descripcion[:50],
                    'cantidad': cantidad,
                    'precio_ud': round(precio, 4),
                    'iva': 21,  # Vinos siempre 21%
                    'base': round(importe, 2)
                })
        
        return lineas
    
    def _limpiar_descripcion(self, desc: str) -> str:
        """Limpia la descripción del producto."""
        # Quitar "Uds. X" si aparece
        desc = re.sub(r'\s+Uds\.\s*\d+', '', desc)
        # Normalizar espacios
        desc = ' '.join(desc.split())
        return desc
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """Extrae el total de la factura."""
        if not texto:
            return None
        
        # Buscar formato XXX,XX€ (sin espacio)
        patron1 = re.search(r'(\d+,\d{2})€', texto)
        if patron1:
            return self._convertir_europeo(patron1.group(1))
        
        # Buscar formato XXX,XX € (con espacio)
        patron2 = re.search(r'(\d+,\d{2})\s*€', texto)
        if patron2:
            return self._convertir_europeo(patron2.group(1))
        
        # Calcular desde cuadro fiscal: BASE + IVA
        patron_fiscal = re.search(
            r'(\d+,\d{2})\s+21,00\s+(\d+,\d{2})',
            texto
        )
        if patron_fiscal:
            base = self._convertir_europeo(patron_fiscal.group(1))
            iva = self._convertir_europeo(patron_fiscal.group(2))
            return round(base + iva, 2)
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de emisión (formato DD-MM-YYYY -> DD/MM/YYYY)."""
        if not texto:
            return None
        
        patron = re.search(r'(\d{2})-(\d{2})-(\d{4})', texto)
        if patron:
            return f"{patron.group(1)}/{patron.group(2)}/{patron.group(3)}"
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae número de factura (formato FV00250XXX)."""
        if not texto:
            return None
        
        patron = re.search(r'(FV\d{8,})', texto)
        if patron:
            return patron.group(1)
        return None
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo (1.234,56) a float."""
        if not texto:
            return 0.0
        texto = str(texto).strip()
        # Si tiene punto y coma, es formato europeo completo
        if '.' in texto and ',' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        # Si solo tiene coma, la coma es decimal
        elif ',' in texto:
            texto = texto.replace(',', '.')
        try:
            return float(texto)
        except:
            return 0.0
