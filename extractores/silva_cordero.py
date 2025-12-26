# -*- coding: utf-8 -*-
"""
Extractor para SILVA CORDERO (Quesos de Acehuche Tradicionales S.L.)

Proveedor de quesos artesanales de cabra.
CIF: B09861535
IBAN: ES4830010050785010003340 (BBVA)

Formato factura:
- Productos con precio por kg
- IVA reducido: 2% (2024) o 4% (2025) para quesos
- PORTES con IVA 21%
- Tabla: CODIGO DESCRIPCION LOTE FECHA CAJAS PIEZAS CANTIDAD PRECIO DTO IMPORTE

Actualizado: 21/12/2025
- Soporte IVA 2% (2024) y 4% (2025)
- Extraccion de PORTES con IVA 21%
- Patron mejorado para codigos con puntos (D.O.P)
- Fallback a TOTAL BRUTO si no hay lineas
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re
import pdfplumber


@registrar('SILVA CORDERO', 'QUESOS SILVA CORDERO', 'QUESOS DE ACEHUCHE', 'SILVA_CORDERO')
class ExtractorSilvaCordero(ExtractorBase):
    """Extractor para facturas de SILVA CORDERO."""
    
    nombre = 'SILVA CORDERO'
    cif = 'B09861535'
    iban = 'ES4830010050785010003340'
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae lineas de facturas SILVA CORDERO.
        
        Los quesos tienen IVA reducido (2% en 2024, 4% en 2025).
        Los PORTES tienen IVA 21%.
        """
        if not texto:
            return []
            
        lineas = []
        productos_extraidos = []
        
        # =====================================================
        # DETECTAR IVA DE PRODUCTOS
        # Formato en tabla: BASE IVA% CUOTA -> ej: "280,48 4,00 11,22"
        # =====================================================
        iva_productos = 4  # Default 2025
        iva_match = re.search(r'([\d,.]+)\s+(2|4),00\s+([\d,.]+)', texto)
        if iva_match:
            iva_productos = int(iva_match.group(2))
        
        # =====================================================
        # EXTRAER LINEAS DE PRODUCTOS
        # Patron: todo + lote + fecha + cajas + piezas + kg + precio/kg + dto + importe
        # Ejemplo: "D.O.P D.O.P QUESO DE ACEHUCHE 240608 30/09/25 1 6 4,860 17,900000€/kg. 0,00 86,99"
        # =====================================================
        patron = re.compile(
            r'^(.+?)\s+'                              # Descripcion completa
            r'(\d{6})\s+'                             # Lote (YYMMDD)
            r'(\d{2}/\d{2}/\d{2})\s+'                # Fecha caducidad
            r'(\d+)\s+'                               # Cajas
            r'(\d+)\s+'                               # Piezas
            r'([\d,]+)\s+'                            # Cantidad (kg)
            r'([\d,]+)[€/kg\.]+\s+'                  # Precio por kg
            r'([\d,]+)\s+'                            # Dto
            r'([\d,]+)$',                             # Importe
            re.MULTILINE
        )
        
        for m in patron.finditer(texto):
            desc_full = m.group(1).strip()
            cantidad = float(m.group(6).replace(',', '.'))
            precio = float(m.group(7).replace(',', '.'))
            importe = float(m.group(9).replace(',', '.'))
            
            # Ignorar cabeceras
            if 'Producto' in desc_full or 'Albaran' in desc_full:
                continue
            
            # Extraer codigo (primera palabra) y descripcion
            parts = desc_full.split(None, 1)
            codigo = parts[0] if parts else 'PROD'
            articulo = parts[1] if len(parts) > 1 else desc_full
            
            productos_extraidos.append({
                'codigo': codigo[:12],
                'articulo': articulo[:50],
                'cantidad': cantidad,
                'precio_ud': precio,
                'iva': iva_productos,
                'base': importe
            })
        
        # Si se encontraron productos, usarlos
        if productos_extraidos:
            lineas.extend(productos_extraidos)
        else:
            # Fallback: usar TOTAL BRUTO cuando no se extraen lineas
            bruto_match = re.search(r'TOTAL BRUTO\s+([\d,.]+)', texto)
            if bruto_match:
                bruto = float(bruto_match.group(1).replace('.', '').replace(',', '.'))
                lineas.append({
                    'codigo': 'PRODUCTOS',
                    'articulo': 'Quesos (total)',
                    'cantidad': 1,
                    'precio_ud': bruto,
                    'iva': iva_productos,
                    'base': bruto
                })
        
        # =====================================================
        # EXTRAER PORTES (IVA 21%)
        # =====================================================
        portes_match = re.search(r'PORTES\s+([\d,]+)', texto)
        if portes_match:
            portes = float(portes_match.group(1).replace(',', '.'))
            if portes > 0:
                lineas.append({
                    'codigo': 'PORTES',
                    'articulo': 'Gastos de envio',
                    'cantidad': 1,
                    'precio_ud': portes,
                    'iva': 21,
                    'base': portes
                })
        
        return lineas
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """Extrae el total de la factura."""
        if not texto:
            return None
        
        # Patron: TOTAL FACTURA XXX,XX €
        m = re.search(r'TOTAL FACTURA\s+([\d,.]+)', texto)
        if m:
            total_str = m.group(1).replace('.', '').replace(',', '.')
            return float(total_str)
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae la fecha de la factura."""
        if not texto:
            return None
        
        # Formato: DD/MM/YYYY
        m = re.search(r'Fecha\s+(\d{2}/\d{2}/\d{4})', texto)
        if m:
            return m.group(1)
        
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae el numero de factura."""
        if not texto:
            return None
        
        # Formato: F25/0000XXX o F24/0000XXX
        m = re.search(r'(F\d{2}/\d+)', texto)
        if m:
            return m.group(1)
        
        return None
