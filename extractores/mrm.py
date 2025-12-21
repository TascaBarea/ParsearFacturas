"""
Extractor para INDUSTRIAS CÁRNICAS MRM-2 S.A.U.

Proveedor de salmón ahumado, patés y mousses de Móstoles (Madrid)
CIF: A80280845
IVA: 10% (productos cárnicos)

Formato factura (pdfplumber):
- Líneas producto: CANTIDAD PESO CODIGO - DESCRIPCION TIPO PRECIO PRECIO IMPORTE
- Ejemplo: 6,00 1,200 1159 - PATE COCHINILLO 200 U 4,300 4,300 25,800

Creado: 19/12/2025
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar('MRM', 'MRM-2', 'MRM2', 'INDUSTRIAS CARNICAS MRM', 'MANUEL RODRIGUEZ MANZANO')
class ExtractorMRM(ExtractorBase):
    """Extractor para facturas de INDUSTRIAS CÁRNICAS MRM-2 S.A.U."""
    
    nombre = 'MRM'
    cif = 'A80280845'
    iban = ''  # No aparece en las facturas
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas INDIVIDUALES de productos.
        
        Formato:
        CANTIDAD PESO CODIGO - DESCRIPCION TIPO PRECIO PRECIO IMPORTE
        6,00 1,200 1159 - PATE COCHINILLO 200 U 4,300 4,300 25,800
        2,00 1,530 377 - SALMON AHUMADO P 35,620 35,620 54,500
        """
        lineas = []
        
        # Patrón para líneas de producto
        # CANTIDAD PESO CODIGO - DESCRIPCION (multilínea posible) TIPO PRECIO PRECIO IMPORTE
        patron_linea = re.compile(
            r'^(\d+,\d{2})\s+'                      # Cantidad (6,00)
            r'(\d+,\d{3})\s+'                       # Peso (1,200)
            r'(\d+)\s+-\s+'                         # Código (1159 -)
            r'(.+?)\s+'                             # Descripción
            r'([UP])\s+'                            # Tipo (U o P)
            r'(\d+,\d{3})\s+'                       # Precio 1
            r'(\d+,\d{3})\s+'                       # Precio 2
            r'(\d+,\d{3})\s*$'                      # Importe
        , re.MULTILINE)
        
        for match in patron_linea.finditer(texto):
            cantidad = self._convertir_europeo(match.group(1))
            peso = self._convertir_europeo(match.group(2))
            codigo = match.group(3)
            descripcion = match.group(4).strip()
            tipo = match.group(5)
            precio = self._convertir_europeo(match.group(6))
            importe = self._convertir_europeo(match.group(8))
            
            # Limpiar descripción de textos adicionales
            descripcion = re.sub(r'\s*(gr\.|grs\.|G\.|SELECT\.|SELECTOS|CASTILLA).*$', '', descripcion, flags=re.IGNORECASE)
            descripcion = descripcion.strip()
            
            # La cantidad real depende del tipo
            # U = unidades, P = peso en kg
            if tipo == 'U':
                cant_real = cantidad
            else:
                cant_real = peso
            
            lineas.append({
                'codigo': codigo,
                'articulo': descripcion[:50],
                'cantidad': cant_real,
                'precio_ud': round(precio, 3),
                'iva': 10,
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
        # Buscar "Importe Líquido :" seguido del importe
        patron = re.search(r'Importe\s+Líquido\s*:\s*(\d+,\d{2})\s*€', texto)
        if patron:
            return self._convertir_europeo(patron.group(1))
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        # Formato en cabecera: DD/MM/YYYY EURO
        patron = re.search(r'(\d{2}/\d{2}/\d{4})\s+EURO', texto)
        if patron:
            return patron.group(1)
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae número de factura."""
        # Formato: ALBARÁN / FACTURA 1-2025 -17.477
        patron = re.search(r'ALBARÁN\s*/\s*FACTURA\s+([\d-]+\s*-[\d.]+)', texto)
        if patron:
            return patron.group(1).replace(' ', '')
        return None
