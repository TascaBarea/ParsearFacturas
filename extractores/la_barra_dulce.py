"""
Extractor para LA BARRA DULCE S.L.

Pasteleria y bolleria.
CIF: B19981141

Formato factura (pdfplumber):
LA BARRA DULCE S.L. Fecha
CIF: B19981141 31.01.2025
...
Descripcion Unidades Precio Unitario
Minipalmeritas 1 29,28 29,28
Fresas con chocolate 12 0,70 8,40
...
Base Imponible 29,28
TOTAL FACTURA 32,20€

IVA: 10% (pasteleria)

Creado: 19/12/2025
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar('LA BARRA DULCE', 'BARRA DULCE')
class ExtractorBarraDulce(ExtractorBase):
    """Extractor para facturas de LA BARRA DULCE."""
    
    nombre = 'LA BARRA DULCE'
    cif = 'B19981141'
    iban = 'ES76 2100 5606 4802 0017 4138'
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae lineas individuales de productos.
        
        Formato:
        Minipalmeritas 1 29,28 29,28
        Fresas con chocolate 12 0,70 8,40
        """
        lineas = []
        
        for linea_texto in texto.split('\n'):
            linea_texto = linea_texto.strip()
            if not linea_texto or len(linea_texto) < 5:
                continue
            
            # Ignorar cabeceras y lineas no deseadas
            upper = linea_texto.upper()
            if any(x in upper for x in [
                'DESCRIPCION', 'UNIDADES', 'PRECIO UNITARIO', 'BASE', 'IVA',
                'TOTAL', 'FACTURA', 'CLIENTE', 'CIF', 'CALLE', 'TELEFONO',
                'OBSERVACIONES', 'PROTECCION', 'DATOS', 'CAIXA', 'TRANSFERENCIA',
                'BARRA DULCE', 'MESON', 'MADRID', 'FORMA DE PAGO', 'INFORMACION'
            ]):
                continue
            
            # Patron: DESCRIPCION CANTIDAD PRECIO IMPORTE
            # Minipalmeritas 1 29,28 29,28
            match = re.match(
                r'^([A-Za-zñáéíóúÑÁÉÍÓÚ][A-Za-zñáéíóúÑÁÉÍÓÚ\s]+?)\s+'  # Descripcion
                r'(\d{1,3})\s+'                             # Cantidad
                r'(\d+,\d{2})\s+'                           # Precio
                r'(\d+,\d{2})$',                            # Importe
                linea_texto
            )
            
            if match:
                descripcion = match.group(1).strip()
                cantidad = int(match.group(2))
                precio = self._convertir_europeo(match.group(3))
                importe = self._convertir_europeo(match.group(4))
                
                if importe < 0.50 or len(descripcion) < 3:
                    continue
                
                lineas.append({
                    'codigo': '',
                    'articulo': descripcion[:50],
                    'cantidad': cantidad,
                    'precio_ud': round(precio, 2),
                    'iva': 10,  # Pasteleria siempre 10%
                    'base': round(importe, 2)
                })
        
        return lineas
    
    def _convertir_europeo(self, texto: str) -> float:
        if not texto:
            return 0.0
        texto = texto.strip().replace('.', '').replace(',', '.')
        try:
            return float(texto)
        except:
            return 0.0
    
    def extraer_total(self, texto: str) -> Optional[float]:
        # Formato: TOTAL FACTURA 32,20€
        patron = re.search(r'TOTAL\s+FACTURA\s+(\d+,\d{2})\s*€', texto, re.IGNORECASE)
        if patron:
            return self._convertir_europeo(patron.group(1))
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        # Formato en linea: CIF: B19981141 31.01.2025
        patron = re.search(r'CIF:\s*B\d+\s+(\d{2})\.(\d{2})\.(\d{4})', texto)
        if patron:
            return f"{patron.group(1)}/{patron.group(2)}/{patron.group(3)}"
        
        # Alternativo: buscar directamente DD.MM.YYYY
        patron2 = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', texto)
        if patron2:
            return f"{patron2.group(1)}/{patron2.group(2)}/{patron2.group(3)}"
        
        return None
