"""
Extractor para PANRUJE SL (Rosquillas Artesanas La Ermita)

Fabricante de rosquillas artesanas en Cieza (Murcia)
Productos: Cajas de rosquillas normales + Portes
CIF: B-13.858.014

Formato factura (pdfplumber):
- Líneas de producto: CODIGO CANTIDAD DESCRIPCION [LOTE] PRECIO [DTO] IMPORTE
- Desglose fiscal: TOTAL_BRUTO BASE_IMPONIBLE %IVA IVA TOTAL

IVA: 4% (todo incluido portes)

Creado: 20/12/2025
Validado: 6/6 facturas (1T25, 3T25, 4T25)
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re
import pdfplumber


@registrar('PANRUJE', 'PANRUJE SL', 'ROSQUILLAS LA ERMITA', 'LA ERMITA', 
           'ROSQUILLAS ARTESANAS LA ERMITA')
class ExtractorPanruje(ExtractorBase):
    """Extractor para facturas de PANRUJE (Rosquillas La Ermita)."""
    
    nombre = 'PANRUJE'
    cif = 'B13858014'
    iban = 'ES1900815344280002614066'
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
        Extrae líneas de productos.
        
        Formatos posibles:
        - NOR 7 4,0 CAJAS DE ROSQUILLAS NORMALES 50 16,50 2,00 64,68 (con lote y dto)
        - NOR 7 2,0 CAJAS DE ROSQUILLAS NORMALES 16,50 33,00 (sin lote ni dto)
        - 000 1,0 PORTES 24,60 24,60
        - POR 1,0 PORTES 11,77 11,77
        
        Todo va al 4% (portes incluidos en misma base).
        """
        lineas = []
        
        # Patrón para rosquillas con descuento (tiene lote y dto)
        # NOR 7 4,0 CAJAS DE ROSQUILLAS NORMALES 50 16,50 2,00 64,68
        patron_rosquillas_dto = re.compile(
            r'^(NOR\s*\d?|NOR)\s+'           # Código (NOR 7, NOR)
            r'(\d+[,.]?\d*)\s+'               # Cantidad
            r'(.+?)\s+'                       # Descripción
            r'(\d+)\s+'                       # Lote
            r'(\d+[,.]\d{2})\s+'              # Precio
            r'(\d+[,.]\d{2})\s+'              # Descuento %
            r'(\d+[,.]\d{2})$'                # Importe
        , re.MULTILINE)
        
        # Patrón para rosquillas sin descuento
        # NOR 7 2,0 CAJAS DE ROSQUILLAS NORMALES 16,50 33,00
        patron_rosquillas = re.compile(
            r'^(NOR\s*\d?|NOR)\s+'           # Código
            r'(\d+[,.]?\d*)\s+'               # Cantidad
            r'(.+?)\s+'                       # Descripción
            r'(\d+[,.]\d{2})\s+'              # Precio
            r'(\d+[,.]\d{2})$'                # Importe
        , re.MULTILINE)
        
        # Patrón para portes
        # 000 1,0 PORTES 24,60 24,60
        # POR 1,0 PORTES 11,77 11,77
        patron_portes = re.compile(
            r'^(000|POR)\s+'                  # Código
            r'(\d+[,.]?\d*)\s+'               # Cantidad
            r'(PORTES)\s+'                    # Descripción
            r'(\d+[,.]\d{2})\s+'              # Precio
            r'(\d+[,.]\d{2})$'                # Importe
        , re.MULTILINE)
        
        # Buscar rosquillas con descuento
        for match in patron_rosquillas_dto.finditer(texto):
            codigo = match.group(1).strip().replace(' ', '')
            cantidad = self._convertir_europeo(match.group(2))
            descripcion = match.group(3).strip()
            precio = self._convertir_europeo(match.group(5))
            importe = self._convertir_europeo(match.group(7))
            
            lineas.append({
                'codigo': codigo,
                'articulo': descripcion[:50],
                'cantidad': cantidad,
                'precio_ud': round(precio, 2),
                'iva': 4,
                'base': round(importe, 2)
            })
        
        # Si no se encontraron con descuento, buscar sin descuento
        if not any('ROSQUILLAS' in l['articulo'].upper() for l in lineas):
            for match in patron_rosquillas.finditer(texto):
                codigo = match.group(1).strip().replace(' ', '')
                cantidad = self._convertir_europeo(match.group(2))
                descripcion = match.group(3).strip()
                precio = self._convertir_europeo(match.group(4))
                importe = self._convertir_europeo(match.group(5))
                
                lineas.append({
                    'codigo': codigo,
                    'articulo': descripcion[:50],
                    'cantidad': cantidad,
                    'precio_ud': round(precio, 2),
                    'iva': 4,
                    'base': round(importe, 2)
                })
        
        # Buscar portes
        for match in patron_portes.finditer(texto):
            codigo = match.group(1).strip()
            cantidad = self._convertir_europeo(match.group(2))
            descripcion = match.group(3).strip()
            precio = self._convertir_europeo(match.group(4))
            importe = self._convertir_europeo(match.group(5))
            
            lineas.append({
                'codigo': codigo,
                'articulo': descripcion[:50],
                'cantidad': cantidad,
                'precio_ud': round(precio, 2),
                'iva': 4,  # Portes también al 4%
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
        # Buscar última línea con formato: BASE BASE %IVA IVA TOTAL
        # 89,28 89,28 4,0 3,57 92,85
        patron = re.search(
            r'(\d+[,.]\d{2})\s+(\d+[,.]\d{2})\s+4[,.]0\s+(\d+[,.]\d{2})\s+(\d+[,.]\d{2})$', 
            texto, re.MULTILINE
        )
        if patron:
            return self._convertir_europeo(patron.group(4))
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        # Formato: 43.025 FT 197 15/12/2025
        patron = re.search(r'(\d{2}/\d{2}/\d{4})', texto)
        if patron:
            return patron.group(1)
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae número de factura."""
        # Formato: 43.025 FT 197 15/12/2025
        patron = re.search(r'FT\s+(\d+)\s+\d{2}/\d{2}/\d{4}', texto)
        if patron:
            return patron.group(1)
        return None
