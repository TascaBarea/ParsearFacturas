"""
Extractor para CONSERVAS LA ALACENA, S.L.U

Conservas gourmet de Almansa (Albacete).
CIF: B02488054

Formato factura (pdfplumber):
Cantidad  Lote      Artículo                              Precio  IVA    Subtotal
12,00     2L041 25  POLLITO PICANTON EN ESCABECHE LATA    4,85    10,00  58,20
12,00     1L175 25  POLLITO PICANTON EN ESCABECHE         4,65    10,00  55,80
6,00      1L261 25  PERDIZ ROJA DE CAMPO DESHUESADA       9,20    10,00  55,20

IVA: 10% (conservas alimenticias)
Sin categoría fija (se busca en diccionario)

Creado: 26/12/2025
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar('LA ALACENA', 'CONSERVAS LA ALACENA', 'ALACENA')
class ExtractorLaAlacena(ExtractorBase):
    """Extractor para facturas de CONSERVAS LA ALACENA."""
    
    nombre = 'LA ALACENA'
    cif = 'B02488054'
    iban = ''  # Pago anticipado transferencia
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de productos.
        
        Formato:
        12,00 2L041 25 POLLITO PICANTON EN ESCABECHE LATA OVAL. 4,85 10,00 58,20
        """
        lineas = []
        
        for linea in texto.split('\n'):
            linea = linea.strip()
            if not linea:
                continue
            
            # Ignorar cabeceras y totales
            if any(x in linea.upper() for x in ['CANTIDAD', 'LOTE', 'ARTÍCULO', 
                                                  'PRECIO', 'SUBTOTAL', 'DESCRIPCIÓN',
                                                  'CONSERVAS LA ALACENA', 'FACTURA',
                                                  'NÚMERO', 'FECHA', 'REFERENCIA',
                                                  'TASCA BAREA', 'LUGAR DE ENTREGA',
                                                  'ALBARÁN', 'DESCUENTO', 'DTO',
                                                  'BASE IMPONIBLE', 'IMPORTE IVA',
                                                  'TOTAL FACTURA', 'FORMA DE PAGO',
                                                  'VENCIMIENTOS', 'TRANS.', 'PAGO',
                                                  'C.I.F', 'PANADEROS', 'ALMANSA']):
                continue
            
            # Patrón principal: CANTIDAD LOTE DESCRIPCION PRECIO IVA SUBTOTAL
            # "12,00 2L041 25 POLLITO PICANTON EN ESCABECHE LATA OVAL. 4,85 10,00 58,20"
            match = re.match(
                r'^(\d+[.,]\d{2})\s+'                               # Cantidad
                r'(\d?[A-Z]\d+\s+\d+)\s+'                           # Lote (2L041 25)
                r'(.+?)\s+'                                          # Descripción
                r'(\d+[.,]\d{2})\s+'                                 # Precio
                r'(\d+[.,]\d{2})\s+'                                 # IVA (10,00)
                r'(\d+[.,]\d{2})$',                                  # Subtotal
                linea
            )
            
            if match:
                cantidad = self._convertir_europeo(match.group(1))
                lote = match.group(2)
                descripcion = match.group(3).strip()
                precio = self._convertir_europeo(match.group(4))
                iva = int(self._convertir_europeo(match.group(5)))
                subtotal = self._convertir_europeo(match.group(6))
                
                if subtotal > 0 and len(descripcion) >= 3:
                    lineas.append({
                        'codigo': lote.split()[0] if lote else '',
                        'articulo': descripcion[:50],
                        'cantidad': int(cantidad) if cantidad == int(cantidad) else cantidad,
                        'precio_ud': round(precio, 2),
                        'iva': iva if iva in [4, 10, 21] else 10,
                        'base': round(subtotal, 2)
                    })
                continue
            
            # Patrón alternativo con descuento
            # "3,00 1L021 25 CARRILLADA DE CERDO EN SALSA 7,05 100,00 10,00"
            match2 = re.match(
                r'^(\d+[.,]\d{2})\s+'                               # Cantidad
                r'(\d?[A-Z]\d+\s+\d+)\s+'                           # Lote
                r'(.+?)\s+'                                          # Descripción
                r'(\d+[.,]\d{2})\s+'                                 # Precio
                r'(\d+[.,]\d{2})\s+'                                 # Dto o IVA
                r'(\d+[.,]\d{2})$',                                  # IVA o Subtotal
                linea
            )
            
            if match2:
                cantidad = self._convertir_europeo(match2.group(1))
                lote = match2.group(2)
                descripcion = match2.group(3).strip()
                precio = self._convertir_europeo(match2.group(4))
                
                # Calcular subtotal
                subtotal = round(cantidad * precio, 2)
                
                if subtotal > 0 and len(descripcion) >= 3:
                    lineas.append({
                        'codigo': lote.split()[0] if lote else '',
                        'articulo': descripcion[:50],
                        'cantidad': int(cantidad) if cantidad == int(cantidad) else cantidad,
                        'precio_ud': round(precio, 2),
                        'iva': 10,
                        'base': round(subtotal, 2)
                    })
        
        return lineas
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo a float."""
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
        # Formato: "TOTAL FACTURA 527,67 €"
        m = re.search(r'TOTAL\s*FACTURA\s*(\d+[.,]\d{2})\s*€?', texto, re.IGNORECASE)
        if m:
            return self._convertir_europeo(m.group(1))
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        # Formato: "Fecha 07/10/2025"
        m = re.search(r'Fecha\s+(\d{2})/(\d{2})/(\d{4})', texto)
        if m:
            return f"{m.group(1)}/{m.group(2)}/{m.group(3)}"
        
        return None
