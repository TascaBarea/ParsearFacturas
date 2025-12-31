"""
Extractor para SILVA CORDERO (Quesos de Acehuche)

Queseria tradicional de Extremadura
CIF: B09861535
IBAN: ES48 3001 0050 78 5010003340 (BBVA)

Productos (IVA 4% - quesos):
- D.O.P Queso de Acehuche
- Mini pasta dura
- Queso sobado con manteca iberica
- Queso la cabra azul

IMPORTANTE: Los portes tienen IVA 21%, los productos IVA 4%
El prorrateo de portes lo hace main.py

Categoria: QUESO PARA TABLA

Creado: 30/12/2025
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar('SILVA CORDERO', 'QUESOS SILVA CORDERO', 'QUESOS DE ACEHUCHE',
           'SILVA', 'CORDERO')
class ExtractorSilvaCordero(ExtractorBase):
    """Extractor para facturas de SILVA CORDERO."""
    
    nombre = 'SILVA CORDERO'
    cif = 'B09861535'
    iban = 'ES48 3001 0050 78 5010003340'
    metodo_pdf = 'pdfplumber'
    categoria_fija = 'QUESO PARA TABLA'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae lineas de producto y portes.
        
        Formato productos:
        CODIGO DESCRIPCION LOTE CADUC CAJAS PIEZAS CANTIDAD PRECIO DTO IMPORTE
        Ej: 0006 MINI PASTA DURA 250717 20/09/26 1 6 3,360 18,900000E/kg. 0,00 63,50
        
        Formato portes:
        PORTES 14,90
        """
        lineas = []
        
        # Patron para productos
        # Codigo + Descripcion + ... + Importe al final
        patron_producto = re.compile(
            r'^([A-Z0-9]+)\s+'                    # Codigo
            r'(.+?)\s+'                           # Descripcion
            r'\d{6}\s+'                           # Lote (6 digitos)
            r'\d{2}/\d{2}/\d{2}\s+'              # Fecha caducidad
            r'\d+\s+\d+\s+'                       # Cajas + Piezas
            r'([\d,]+)\s+'                        # Cantidad (kg)
            r'[\d,]+(?:E|€)/kg\.\s+'             # Precio/kg
            r'[\d,]+\s+'                          # Descuento
            r'([\d,]+)$',                         # Importe
            re.MULTILINE | re.IGNORECASE
        )
        
        for match in patron_producto.finditer(texto):
            codigo = match.group(1).strip()
            descripcion = match.group(2).strip()
            cantidad_kg = float(match.group(3).replace(',', '.'))
            importe = float(match.group(4).replace(',', '.'))
            
            lineas.append({
                'codigo': codigo,
                'articulo': descripcion[:50],
                'cantidad': cantidad_kg,
                'precio_ud': round(importe / cantidad_kg, 4) if cantidad_kg > 0 else importe,
                'iva': 4,  # Quesos IVA reducido
                'base': importe,
                'categoria': self.categoria_fija
            })
        
        # Si no encontro con el patron estricto, probar patron mas flexible
        if not lineas:
            # Buscar lineas que terminen en importe tipo "0,00 XX,XX"
            patron_flex = re.compile(
                r'^(.+?)\s+\d{6}\s+\d{2}/\d{2}/\d{2}\s+.+?\s+0,00\s+([\d,]+)$',
                re.MULTILINE
            )
            for match in patron_flex.finditer(texto):
                descripcion = match.group(1).strip()
                importe = float(match.group(2).replace(',', '.'))
                
                # Limpiar descripcion de codigos al inicio
                descripcion = re.sub(r'^[A-Z0-9]+\s+', '', descripcion)
                
                lineas.append({
                    'codigo': '',
                    'articulo': descripcion[:50],
                    'cantidad': 1,
                    'precio_ud': importe,
                    'iva': 4,
                    'base': importe,
                    'categoria': self.categoria_fija
                })
        
        # Extraer PORTES (IVA 21%)
        m_portes = re.search(r'PORTES\s+([\d,]+)', texto)
        if m_portes:
            importe_porte = float(m_portes.group(1).replace(',', '.'))
            if importe_porte > 0:
                lineas.append({
                    'codigo': 'PORTE',
                    'articulo': 'PORTES',
                    'cantidad': 1,
                    'precio_ud': importe_porte,
                    'iva': 21,  # Portes IVA general
                    'base': importe_porte,
                    'categoria': 'TRANSPORTE'
                })
        
        return lineas
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """Extrae TOTAL FACTURA del PDF."""
        # Buscar "TOTAL FACTURA XXX,XX"
        m = re.search(r'TOTAL\s+FACTURA\s+([\d.,]+)\s*[E€]?', texto, re.IGNORECASE)
        if m:
            return self._convertir_europeo(m.group(1))
        
        # Buscar ultimo importe con euro
        matches = re.findall(r'([\d.,]+)\s*€', texto)
        if matches:
            return self._convertir_europeo(matches[-1])
        
        return None
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo a float."""
        if not texto:
            return 0.0
        texto = re.sub(r'[^\d,.]', '', str(texto))
        if '.' in texto and ',' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            texto = texto.replace(',', '.')
        try:
            return float(texto)
        except:
            return 0.0
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        m = re.search(r'Fecha\s+(\d{2}/\d{2}/\d{4})', texto)
        return m.group(1) if m else None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae numero de factura."""
        m = re.search(r'(F25/\d+)', texto)
        return m.group(1) if m else None
    
    extraer_referencia = extraer_numero_factura
