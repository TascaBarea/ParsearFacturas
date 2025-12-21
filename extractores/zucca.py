"""
Extractor para QUESERIA ZUCCA / FORMAGGIARTE SL

Quesería artesanal italiana en Portillo (Valladolid)
Productos: Burrata, Ciliegine, Scamorza, Yogur de Oveja
CIF: B42861948

Formato factura (pdfplumber):
- Múltiples albaranes por factura
- Líneas: CODIGO DESCRIPCION CANTIDAD PRECIO SUBTOTAL TOTAL
- Desglose fiscal al final por tipo IVA

IVA:
- 4%: Quesos (Burrata, Ciliegine, Scamorza) + PORTES
- 10%: Yogur de Oveja

IMPORTANTE: Este proveedor incluye los portes en la base del 4%,
no los separa al 21% como es habitual.

Creado: 20/12/2025
Validado: 7/7 facturas (2T25, 3T25, 4T25)
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re
import pdfplumber


@registrar('QUESERIA ZUCCA', 'ZUCCA', 'FORMAGGIARTE', 'FORMAGGIARTE SL', 
           'ZUCCA FORMAGGIARTE', 'FORMAGGIARTE ZUCCA')
class ExtractorZucca(ExtractorBase):
    """Extractor para facturas de QUESERIA ZUCCA / FORMAGGIARTE."""
    
    nombre = 'QUESERIA ZUCCA'
    cif = 'B42861948'
    iban = 'ES0515500001200011577624'
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
        Extrae líneas INDIVIDUALES de productos.
        
        IVA por producto:
        - 00015 Yogur de Oveja → 10%
        - Todo lo demás (quesos + portes) → 4%
        
        El proveedor incluye los portes en la base del 4%.
        """
        lineas = []
        
        # Patrón para líneas de producto
        # Formato: CODIGO DESCRIPCION CANTIDAD PRECIO SUBTOTAL TOTAL
        # Ejemplos:
        # 00042 Burrata Individual SN 10,00 3,40 34,00 34,00
        # 00029 Scamorza Ahumada Kg 0,85 17,58 14,94 14,94
        # 07 Scamorza Ahumada 2,00 5,41 10,82 10,82
        # 00017 Eenvio SEUR Frio 13:30 1,00 10,50 10,50 10,50
        patron_linea = re.compile(
            r'^(\d{2,5})\s+'                    # Código (2-5 dígitos)
            r'(.+?)\s+'                          # Descripción
            r'(\d+,\d{2})\s+'                    # Cantidad
            r'(\d+,\d{2})\s+'                    # Precio unitario
            r'(\d+,\d{2})\s+'                    # Subtotal
            r'(\d+,\d{2})$'                      # Total
        , re.MULTILINE)
        
        for match in patron_linea.finditer(texto):
            codigo = match.group(1).strip()
            descripcion = match.group(2).strip()
            cantidad = self._convertir_europeo(match.group(3))
            precio = self._convertir_europeo(match.group(4))
            importe = self._convertir_europeo(match.group(6))  # Columna TOTAL
            
            # Filtrar cabeceras y líneas inválidas
            if any(x in descripcion.upper() for x in ['DESCRIPCION', 'ARTÍCULO', 'TIPO']):
                continue
            
            if importe < 0.01:
                continue
            
            # IVA según producto:
            # - Yogur = 10%
            # - Todo lo demás (quesos + portes) = 4%
            if 'YOGUR' in descripcion.upper() or codigo == '00015':
                iva = 10
            else:
                iva = 4
            
            lineas.append({
                'codigo': codigo,
                'articulo': descripcion[:50],
                'cantidad': cantidad,
                'precio_ud': round(precio, 2),
                'iva': iva,
                'base': round(importe, 2)
            })
        
        return lineas
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo (1.234,56) a float."""
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
        """Extrae total de la factura."""
        patron = re.search(r'TOTAL:\s*(\d+,\d{2})', texto, re.IGNORECASE)
        if patron:
            return self._convertir_europeo(patron.group(1))
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura (fecha del documento, no de albarán)."""
        # Buscar fecha en formato DD/MM/YYYY después de "Factura 1 XXXXXX 1"
        patron = re.search(r'Factura\s+1\s+\d+\s+1\s+(\d{2}/\d{2}/\d{4})', texto)
        if patron:
            return patron.group(1)
        # Alternativa: buscar en cabecera
        patron = re.search(r'(\d{2}/\d{2}/\d{4})', texto)
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
