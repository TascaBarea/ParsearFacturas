"""
Extractor para FORMAGGIARTE SL (Quesería ZUCCA)

Quesos italianos artesanales.
CIF: B42861948
IBAN: ES05 1555 0001 2000 1157 7624

Formato factura:
CÓDIGO DESCRIPCIÓN CANTIDAD PRECIO SUBTOTAL TOTAL

Ejemplo:
00042 Burrata Individual SN 8,00 3,40 27,20 27,20

IVA por producto:
- Quesos (Burrata, Ciliegine, Scamorza, Stracciatella) → 4%
- Yogur de Oveja → 10%
- Portes → se prorratean al 4%

IMPORTANTE: La columna TOTAL muestra BASE sin IVA.
El sistema espera el importe CON IVA para el cuadre.

Creado: 02/01/2026
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re
import pdfplumber


@registrar('QUESERIA ZUCCA', 'ZUCCA', 'FORMAGGIARTE', 'FORMAGGIARTE SL', 
           'ZUCCA FORMAGGIARTE', 'FORMAGGIARTE ZUCCA')
class ExtractorZucca(ExtractorBase):
    """Extractor para facturas de QUESERÍA ZUCCA / FORMAGGIARTE."""
    
    nombre = 'QUESERIA ZUCCA'
    cif = 'B42861948'
    iban = 'ES0515500001200011577624'  # Sin espacios como el original
    metodo_pdf = 'pdfplumber'
    
    # Productos con IVA 10% (el resto va al 4%)
    PRODUCTOS_IVA_10 = ['yogur', 'yogurt']
    
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
        Extrae líneas de productos.
        
        Formato: CÓDIGO DESCRIPCIÓN CANTIDAD PRECIO SUBTOTAL TOTAL
        """
        lineas = []
        
        # Patrón para líneas de producto
        # CODIGO (2-5 dígitos) DESCRIPCION CANTIDAD PRECIO SUBTOTAL TOTAL
        patron = re.compile(
            r'^(\d{2,5})\s+'                        # Código (00042, 07, etc.)
            r'(.+?)\s+'                              # Descripción
            r'(\d+,\d{2})\s+'                        # Cantidad
            r'(\d+,\d{2})\s+'                        # Precio unitario
            r'(\d+,\d{2})\s+'                        # Subtotal
            r'(\d+,\d{2})$'                          # Total (BASE sin IVA)
        )
        
        for linea in texto.split('\n'):
            linea = linea.strip()
            match = patron.match(linea)
            if match:
                codigo = match.group(1)
                descripcion = match.group(2).strip()
                cantidad = self._convertir_europeo(match.group(3))
                precio = self._convertir_europeo(match.group(4))
                importe_base = self._convertir_europeo(match.group(6))  # TOTAL = BASE sin IVA
                
                # Determinar IVA según producto
                desc_lower = descripcion.lower()
                if any(prod in desc_lower for prod in self.PRODUCTOS_IVA_10):
                    iva = 10
                else:
                    iva = 4  # Quesos y portes van al 4%
                
                # Filtrar líneas con importe muy bajo
                if importe_base < 0.50:
                    continue
                
                # Calcular importe CON IVA
                importe_con_iva = importe_base * (1 + iva / 100)
                
                lineas.append({
                    'codigo': codigo,
                    'articulo': descripcion[:50],
                    'cantidad': int(cantidad) if cantidad == int(cantidad) else round(cantidad, 2),
                    'precio_ud': round(precio, 2),
                    'iva': iva,
                    'base': round(importe_con_iva, 2)  # Importe CON IVA para cuadre
                })
        
        return lineas
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo (1.234,56) a float."""
        if not texto:
            return 0.0
        texto = str(texto).strip()
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
        # Buscar patrón "TOTAL: XXX,XX"
        patron = re.search(r'TOTAL:\s*([\d.,]+)', texto, re.IGNORECASE)
        if patron:
            return self._convertir_europeo(patron.group(1))
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        # Buscar en formato "Factura 1 000XXX 1 DD/MM/YYYY"
        patron = re.search(r'Factura\s+\d+\s+\d+\s+\d+\s+(\d{2}/\d{2}/\d{4})', texto)
        if patron:
            return patron.group(1)
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae número de factura."""
        # Formato: Factura 1 000407 1
        patron = re.search(r'Factura\s+1\s+(\d+)\s+1', texto)
        if patron:
            return patron.group(1)
        return None
