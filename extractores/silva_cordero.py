# -*- coding: utf-8 -*-
"""
Extractor para QUESOS DE ACEHUCHE TRADICIONALES S.L. (SILVA CORDERO)

Queseria artesanal de Acehuche (Caceres)
CIF: B09861535
IBAN: ES48 3001 0050 7850 1000 3340

Formato factura (PDF digital):
- Lineas producto: CODIGO DESCRIPCION LOTE FEC.CADUC CAJAS PIEZAS CANTIDAD PRECIO DTO IMPORTE
- Ejemplo: MINI DOP D.O.P MINI QUESO DE ACEHUCHE 250521 20/09/26 2 12 5,940 18,900000/kg. 0,00 112,27

IVA:
- 4%: Quesos (productos)
- 21%: Portes (transporte)

Los portes se distribuyen proporcionalmente entre los productos.

Creado: 20/12/2025
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re
import pdfplumber


@registrar('SILVA CORDERO', 'QUESOS SILVA CORDERO', 'QUESOS DE ACEHUCHE', 
           'ACEHUCHE', 'SILVACORDERO')
class ExtractorSilvaCordero(ExtractorBase):
    """Extractor para facturas de SILVA CORDERO / Quesos de Acehuche."""
    
    nombre = 'SILVA CORDERO'
    cif = 'B09861535'
    iban = 'ES48 3001 0050 7850 1000 3340'
    metodo_pdf = 'pdfplumber'
    
    def extraer_texto_pdfplumber(self, pdf_path: str) -> str:
        """Extrae texto del PDF."""
        texto_completo = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    texto = page.extract_text()
                    if texto:
                        texto_completo.append(texto)
        except Exception as e:
            pass
        return '\n'.join(texto_completo)
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae lineas INDIVIDUALES de productos.
        
        Formato:
        CODIGO DESCRIPCION LOTE FEC.CADUC CAJAS PIEZAS CANTIDAD PRECIO DTO IMPORTE
        MINI DOP D.O.P MINI QUESO DE ACEHUCHE 250521 20/09/26 2 12 5,940 18,900000/kg. 0,00 112,27
        
        Nota: El codigo y descripcion pueden estar pegados (QUESOAZULQUESO LA CABRA AZUL)
        """
        lineas = []
        
        # Detectar tipo de IVA real del PDF (puede ser 2%, 4%, etc.)
        iva_quesos = self._detectar_iva_quesos(texto)
        
        # Patron para lineas de producto - formato con espacios
        patron_linea = re.compile(
            r'^([A-Z0-9\s]+?)\s+'              # Codigo + Descripcion
            r'(\d{6})\s+'                       # Lote (6 digitos)
            r'(\d{2}/\d{2}/\d{2})\s+'          # Fecha caducidad
            r'(\d+)\s+'                         # Cajas
            r'(\d+)\s+'                         # Piezas
            r'(\d+,\d{3})\s+'                   # Cantidad (kg con 3 decimales)
            r'(\d+,\d+)[^\d]*\s+'               # Precio (puede tener /kg.)
            r'(\d+,\d{2})\s+'                   # Descuento
            r'(\d+,\d{2})\s*$'                  # Importe
        , re.MULTILINE)
        
        # Patron alternativo - codigo pegado a descripcion (QUESOAZULQUESO)
        patron_alt = re.compile(
            r'^([A-Z0-9]+)([A-Z][A-Z\s]+)\s+'   # Codigo pegado + Descripcion
            r'(\d{6})\s+'                       # Lote
            r'(\d{2}/\d{2}/\d{2})\s+'          # Fecha
            r'(\d+)\s+'                         # Cajas
            r'(\d+)\s+'                         # Piezas
            r'(\d+,\d{3})\s+'                   # Cantidad
            r'(\d+,\d+)[^\d]*\s+'               # Precio
            r'(\d+,\d{2})\s+'                   # Descuento
            r'(\d+,\d{2})\s*$'                  # Importe
        , re.MULTILINE)
        
        # Intentar patron principal
        for match in patron_linea.finditer(texto):
            descripcion_raw = match.group(1).strip()
            cantidad = self._convertir_europeo(match.group(6))
            precio = self._convertir_europeo(match.group(7))
            importe = self._convertir_europeo(match.group(9))
            
            descripcion = descripcion_raw
            codigo = ''
            
            codigo_match = re.match(r'^([A-Z0-9]+)\s+(.+)$', descripcion_raw)
            if codigo_match:
                codigo = codigo_match.group(1)
                descripcion = codigo_match.group(2)
            
            descripcion = re.sub(r'^(D\.O\.P\s+)?', '', descripcion)
            descripcion = descripcion.strip()
            
            lineas.append({
                'codigo': codigo,
                'articulo': descripcion[:50],
                'cantidad': round(cantidad, 3),
                'precio_ud': round(precio, 2),
                'iva': iva_quesos,
                'base': round(importe, 2)
            })
        
        # Si no encontro lineas, intentar patron alternativo
        if not lineas:
            for match in patron_alt.finditer(texto):
                codigo = match.group(1)
                descripcion = match.group(2).strip()
                cantidad = self._convertir_europeo(match.group(7))
                precio = self._convertir_europeo(match.group(8))
                importe = self._convertir_europeo(match.group(10))
                
                lineas.append({
                    'codigo': codigo,
                    'articulo': descripcion[:50],
                    'cantidad': round(cantidad, 3),
                    'precio_ud': round(precio, 2),
                    'iva': iva_quesos,
                    'base': round(importe, 2)
                })
        
        # Extraer portes y distribuir proporcionalmente
        portes = self._extraer_portes(texto)
        if portes > 0:
            base_productos = sum(l['base'] for l in lineas)
            if base_productos > 0:
                for linea in lineas:
                    proporcion = linea['base'] / base_productos
                    linea['base'] = round(linea['base'] + (portes * proporcion), 2)
        
        return lineas
    
    def _detectar_iva_quesos(self, texto: str) -> int:
        """Detecta el tipo de IVA de quesos del PDF (puede ser 2%, 4%, etc.)."""
        # Buscar linea de IVA de quesos (la base mayor)
        # Formato: BASE % IVA CUOTA
        # 228,95 2,00 4,58  (IVA 2%)
        # 175,77 4,00 7,03  (IVA 4%)
        patron = re.search(r'(\d+,\d{2})\s+(2,00|4,00|10,00)\s+(\d+,\d{2})', texto)
        if patron:
            iva_str = patron.group(2)
            if iva_str == '2,00':
                return 2
            elif iva_str == '4,00':
                return 4
            elif iva_str == '10,00':
                return 10
        return 4  # Default
    
    def _extraer_portes(self, texto: str) -> float:
        """Extrae importe de portes."""
        patron = re.search(r'PORTES\s+(\d+,\d{2})', texto)
        if patron:
            return self._convertir_europeo(patron.group(1))
        return 0.0
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo (1.234,56) a float."""
        if not texto:
            return 0.0
        texto = texto.strip()
        # Quitar sufijos como /kg.
        texto = re.sub(r'[^\d,.]', '', texto)
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
        # Buscar TOTAL FACTURA seguido de importe
        patron = re.search(r'TOTAL\s+FACTURA\s+(\d+,\d{2})', texto)
        if patron:
            return self._convertir_europeo(patron.group(1))
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        # Formato: Fecha DD/MM/YYYY
        patron = re.search(r'Fecha\s+(\d{2}/\d{2}/\d{4})', texto)
        if patron:
            return patron.group(1)
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae numero de factura."""
        # Formato: F25/0000727 o F24/0000995
        patron = re.search(r'(F\d{2}/\d{7})', texto)
        if patron:
            return patron.group(1)
        return None
