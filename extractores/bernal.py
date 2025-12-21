"""
Extractor para JAMONES Y EMBUTIDOS BERNAL SLU

Jamones ibéricos y embutidos.
CIF: B67784231

Formato factura (pdfplumber):
Producto C.Sec. Unidades Precio %Des%Iva Importe
LO-JABELL JAMÓN DE BELLOTA 100% 12,00 1,000 10,0000 0,00 10,00 120,000
P-PORTES PORTES 1,00 1,000 9,4850 0,00 21,00 9,485

Total Factura: 372,25 €

IVA: 10% productos, 21% portes

Creado: 19/12/2025
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar('JAMONES BERNAL', 'BERNAL', 'JAMONES Y EMBUTIDOS BERNAL', 'EMBUTIDOS BERNAL')
class ExtractorBernal(ExtractorBase):
    """Extractor para facturas de JAMONES BERNAL."""
    
    nombre = 'JAMONES BERNAL'
    cif = 'B67784231'
    iban = 'ES49 2100 7191 2902 0003 7620'
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas individuales de productos.
        
        Formato:
        LO-JABELL JAMÓN DE BELLOTA 100% IBÉRICO LONCHEADO
        12,00 1,000 10,0000 0,00 10,00 120,000
        """
        lineas = []
        
        # Patrón para líneas de producto
        # El formato tiene código y descripción en una línea, y números en otra
        # Buscar líneas con: CANTIDAD UNIDADES PRECIO DTO IVA IMPORTE
        patron_linea = re.compile(
            r'^([A-Z]{1,3}-[A-Z]+)\s+'                 # Código (ej: LO-JABELL)
            r'(.+?)\s+'                                # Descripción
            r'(\d+,\d{2})\s+'                          # Cantidad
            r'(\d+,\d{3})\s+'                          # Unidades
            r'(\d+,\d{4})\s+'                          # Precio
            r'(\d+,\d{2})\s+'                          # Descuento
            r'(\d{1,2}),00\s+'                         # IVA
            r'(\d+,\d{3})'                             # Importe
        , re.MULTILINE)
        
        for match in patron_linea.finditer(texto):
            codigo = match.group(1)
            descripcion = match.group(2).strip()
            cantidad = self._convertir_europeo(match.group(3))
            precio = self._convertir_europeo(match.group(5))
            iva = int(match.group(7))
            importe = self._convertir_europeo(match.group(8))
            
            # Limpiar descripción
            descripcion = re.sub(r'\s*Lotes:.*$', '', descripcion, flags=re.IGNORECASE)
            descripcion = re.sub(r'\s+', ' ', descripcion).strip()
            
            if importe < 0.50:
                continue
            
            lineas.append({
                'codigo': codigo,
                'articulo': descripcion[:50],
                'cantidad': int(cantidad) if cantidad == int(cantidad) else cantidad,
                'precio_ud': round(precio, 2),
                'iva': iva,
                'base': round(importe, 2)
            })
        
        # Si no encontró líneas, usar desglose fiscal
        if not lineas:
            lineas = self._extraer_desglose(texto)
        
        return lineas
    
    def _extraer_desglose(self, texto: str) -> List[Dict]:
        """Extrae usando desglose fiscal."""
        lineas = []
        
        # Buscar: BASE IVA% CUOTA
        patron = re.compile(r'(\d+,\d{3})\s+(\d{1,2}),00\s+(\d+,\d{3})')
        
        for match in patron.finditer(texto):
            base = self._convertir_europeo(match.group(1))
            iva = int(match.group(2))
            cuota = self._convertir_europeo(match.group(3))
            
            # Validar cuota
            cuota_esperada = round(base * iva / 100, 2)
            if base > 5 and iva in [10, 21] and abs(cuota - cuota_esperada) < 2.0:
                if iva == 10:
                    articulo = 'IBERICOS BERNAL'
                else:
                    articulo = 'PORTES'
                
                lineas.append({
                    'codigo': '',
                    'articulo': articulo,
                    'cantidad': 1,
                    'precio_ud': round(base, 2),
                    'iva': iva,
                    'base': round(base, 2)
                })
        
        return lineas
    
    def _convertir_europeo(self, texto: str) -> float:
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
        patron = re.search(r'Total\s+Factura:\s*(\d+,\d{2})\s*€', texto, re.IGNORECASE)
        if patron:
            return self._convertir_europeo(patron.group(1))
        return None
