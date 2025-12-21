"""
Extractor para LICORES MADRUEÑO S.L.

Distribuidor de licores y vinos.
CIF: B86705126
IBAN: ES21 2100 2865 5113 0088 6738

Formato factura (con pdfplumber):
CÓDIGO DESCRIPCIÓN UNIDADES PRECIO DTO % IMPORTE
1594 FEVER-TREE 24 0,80 19,20
1764 XIC DAL FONS 12 3,60 43,20

TOTAL €: 782,33

IVA: Siempre 21% (licores)

Creado: 19/12/2025
Actualizado: Migrado a pdfplumber, extrae líneas individuales con precio_ud
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar('LICORES MADRUEÑO', 'MADRUEÑO', 'MARIANO MADRUEÑO', 'LICORES MADRUENO', 'MADRUENO')
class ExtractorMadrueño(ExtractorBase):
    """Extractor para facturas de LICORES MADRUEÑO."""
    
    nombre = 'LICORES MADRUEÑO'
    cif = 'B86705126'
    iban = 'ES21 2100 2865 5113 0088 6738'
    metodo_pdf = 'pdfplumber'  # SIEMPRE pdfplumber
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas individuales de productos.
        
        Formato pdfplumber:
        1594 FEVER-TREE 24 0,80 19,20
        1764 XIC DAL FONS 12 3,60 43,20
        
        Returns:
            Lista de diccionarios con:
            - codigo: Código del producto
            - articulo: Nombre del artículo
            - cantidad: Unidades
            - precio_ud: Precio unitario
            - iva: 21 (licores siempre)
            - base: Importe (sin IVA, ya viene así en factura)
        """
        lineas = []
        
        # Patrón para líneas de producto
        # CODIGO (2-5 dígitos) DESCRIPCION UNIDADES PRECIO IMPORTE
        # Ejemplo: 1594 FEVER-TREE 24 0,80 19,20
        patron_linea = re.compile(
            r'^(\d{2,5})\s+'                              # Código (2-5 dígitos)
            r'([A-Za-záéíóúÁÉÍÓÚñÑüÜ][A-Za-z0-9áéíóúÁÉÍÓÚñÑüÜ\s\.\,\'\´\-\(\)]+?)\s+'  # Descripción
            r'(\d{1,3})\s+'                               # Unidades
            r'(\d{1,3},\d{2})\s+'                         # Precio unitario (formato europeo)
            r'(\d{1,3}(?:\.\d{3})*,\d{2})'               # Importe (formato europeo, puede tener punto de miles)
        , re.MULTILINE)
        
        for match in patron_linea.finditer(texto):
            codigo = match.group(1)
            descripcion = match.group(2).strip()
            cantidad = int(match.group(3))
            precio_str = match.group(4)
            importe_str = match.group(5)
            
            # Convertir formato europeo a float
            precio_ud = self._convertir_europeo(precio_str)
            importe = self._convertir_europeo(importe_str)
            
            # Filtrar líneas de cabecera o totales
            desc_upper = descripcion.upper()
            if any(x in desc_upper for x in [
                'DESCRIPCION', 'CÓDIGO', 'UNIDADES', 'PRECIO', 'IMPORTE',
                'TOTAL', 'BRUTO', 'SUMA', 'SIGUE', 'BASE', 'IVA', 'ALBARAN',
                'CLIENTE', 'FECHA', 'FACTURA', 'VENTA'
            ]):
                continue
            
            # Ignorar si importe muy pequeño
            if importe < 0.50:
                continue
            
            lineas.append({
                'codigo': codigo,
                'articulo': descripcion[:50],  # Limitar longitud
                'cantidad': cantidad,
                'precio_ud': round(precio_ud, 2),
                'iva': 21,  # Licores siempre 21%
                'base': round(importe, 2)
            })
        
        return lineas
    
    def _convertir_europeo(self, texto: str) -> float:
        """
        Convierte formato europeo a float.
        
        Ejemplos:
        - '0,80' → 0.80
        - '19,20' → 19.20
        - '1.234,56' → 1234.56
        """
        if not texto:
            return 0.0
        
        texto = texto.strip()
        
        # Si tiene punto Y coma, el punto es separador de miles
        if '.' in texto and ',' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            texto = texto.replace(',', '.')
        
        try:
            return float(texto)
        except:
            return 0.0
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """
        Extrae total de la factura.
        
        Formatos:
        - TOTAL €: 782,33
        - 782,33 €
        """
        patrones = [
            r'TOTAL\s*€[:\s]*(\d{1,3}(?:\.\d{3})*,\d{2})',  # TOTAL €: 782,33
            r'TOTAL[:\s]+(\d{1,3}(?:\.\d{3})*,\d{2})\s*€',  # TOTAL: 782,33 €
            r'(\d{1,3}(?:\.\d{3})*,\d{2})\s*€\s*\n.*?DATOS\s*BANCARIOS',  # 782,33 €\nDATOS
        ]
        
        for patron in patrones:
            match = re.search(patron, texto, re.IGNORECASE | re.DOTALL)
            if match:
                return self._convertir_europeo(match.group(1))
        
        return None
