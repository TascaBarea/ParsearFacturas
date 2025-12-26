"""
Extractor para DISTRIBUCIONES LAVAPIES S.COOP.MAD.

Bebidas y refrescos.
CIF: F88424072
IVA: Por línea (10% y 21%)
Categoría: Por diccionario

Formato factura:
Nº ALBARÁN REF. DESCRIPCIÓN CANT. DTO. IMPORTE TOTAL
631/2025 AGUVIC AGUA VICHY CATALAN 300 ML 48 0,84 40,32 €

BASE IMP. AL 10%    IVA 10%    BASE IMP. AL 21%    IVA 21%
163,98              34,44      120,09              12,01

TOTAL: 330,52 €

Creado: 26/12/2025
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar('DISTRIBUCIONES LAVAPIES', 'LAVAPIES', 'DISTRIBUCIONES LAVAPIES S.COOP.MAD.')
class ExtractorLavapies(ExtractorBase):
    """Extractor para facturas de DISTRIBUCIONES LAVAPIES."""
    
    nombre = 'DISTRIBUCIONES LAVAPIES'
    cif = 'F88424072'
    metodo_pdf = 'pdfplumber'
    usa_diccionario = True
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """Extrae líneas de productos de DISTRIBUCIONES LAVAPIES."""
        lineas = []
        
        # Buscar bases imponibles para determinar IVA
        bases_10 = 0.0
        bases_21 = 0.0
        m10 = re.search(r'BASE\s+IMP\.\s+AL\s+10%.*?([\d,.]+)', texto)
        m21 = re.search(r'BASE\s+IMP\.\s+AL\s+21%.*?([\d,.]+)', texto)
        if m10:
            bases_10 = self._convertir_europeo(m10.group(1))
        if m21:
            bases_21 = self._convertir_europeo(m21.group(1))
        
        # Patrón para líneas de producto
        # Formato: ALBARAN REF DESCRIPCION CANT PRECIO IMPORTE
        patron = re.compile(
            r'(\d+/\d+)\s+'                    # Albarán
            r'(\w+)\s+'                         # REF
            r'([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ0-9\s/.,]+?)'  # Descripción
            r'\s+(\d+)\s+'                      # Cantidad
            r'([\d,.]+)\s+'                     # Precio
            r'([\d,.]+)\s*€'                    # Importe
        )
        
        for match in patron.finditer(texto):
            ref = match.group(2)
            descripcion = match.group(3).strip()
            cantidad = float(match.group(4))
            precio = self._convertir_europeo(match.group(5))
            importe = self._convertir_europeo(match.group(6))
            
            # Determinar IVA basado en tipo de producto
            # Bebidas azucaradas = 21%, agua/zumos = 10%
            if any(x in descripcion.upper() for x in ['COLA', 'REFRESCO', 'LIMON']):
                iva = 21
            else:
                iva = 10
            
            if importe > 0:
                lineas.append({
                    'codigo': ref,
                    'articulo': descripcion,
                    'cantidad': cantidad,
                    'precio_ud': precio,
                    'iva': iva,
                    'base': round(importe, 2),
                    'categoria': ''  # Se asignará por diccionario
                })
        
        return lineas
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo a float."""
        if not texto:
            return 0.0
        texto = texto.strip()
        if ',' in texto and '.' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            texto = texto.replace(',', '.')
        try:
            return float(texto)
        except:
            return 0.0
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """Extrae total de la factura."""
        m = re.search(r'TOTAL\s+([\d,.]+)\s*€', texto, re.IGNORECASE)
        if m:
            return self._convertir_europeo(m.group(1))
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        m = re.search(r'FECHA\s+N[ºo°]\s*DOCUMENTO.*?(\d{2}/\d{2}/\d{2})', texto, re.DOTALL)
        if m:
            fecha = m.group(1)
            # Convertir año de 2 dígitos a 4
            partes = fecha.split('/')
            if len(partes) == 3 and len(partes[2]) == 2:
                partes[2] = '20' + partes[2]
            return '/'.join(partes)
        return None
    
    def extraer_referencia(self, texto: str) -> Optional[str]:
        """Extrae número de factura."""
        m = re.search(r'N[ºo°]\s*DOCUMENTO\s*(\d+)', texto)
        if m:
            return m.group(1)
        return None
