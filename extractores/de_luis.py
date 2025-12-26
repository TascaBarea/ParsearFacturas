"""
Extractor para DE LUIS SABORES UNICOS S.L.

Distribuidor de quesos Cañarejal (Zamora).
CIF: B86249711
IBAN: ES58 3085 0023 6226 2926 3126 (Caja Rural)
      ES53 0049 1920 1021 1019 2545 (Banco Santander)

Formato factura (pdfplumber):
Línea  Artículo                              Cantidad  Kilos  Precio  % Dto.  Total
1 O760 CREMA DE QUESO "CAÑAREJAL" 200 GR.    6         6      7,19            43,14 4%
2 O765 QUESO OVEJA MANTECOSO RULO "CAÑAREJAL" 6        3,1    17,25           53,48 4%

IVA: 4% (quesos)
Categoría fija: QUESOS

Creado: 26/12/2025
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar('DE LUIS SABORES UNICOS', 'DE LUIS', 'JAMONES LIEBANA')
class ExtractorDeLuis(ExtractorBase):
    """Extractor para facturas de DE LUIS SABORES UNICOS."""
    
    nombre = 'DE LUIS SABORES UNICOS'
    cif = 'B86249711'
    iban = 'ES58 3085 0023 6226 2926 3126'
    metodo_pdf = 'pdfplumber'
    categoria_fija = 'QUESOS'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de productos.
        
        Formato:
        1 O760 CREMA DE QUESO "CAÑAREJAL" 200 GR. 6 6 7,19 43,14 4%
        """
        lineas = []
        productos_encontrados = set()
        
        for linea in texto.split('\n'):
            linea = linea.strip()
            if not linea:
                continue
            
            # Ignorar líneas de cabecera, albarán, lotes
            if any(x in linea.upper() for x in ['LÍNEA', 'ARTÍCULO', 'CANTIDAD', 
                                                  'ALBARÁN:', 'LOTES', 'FECHA',
                                                  'OBSERVACIONES', 'IMPORTE BRUTO',
                                                  'PORTES', 'DESCUENTO', 'B. IMPONIBLE',
                                                  'CUOTA IVA', 'TOTAL', 'VENCIMIENTO',
                                                  'BANCO', 'CAJA RURAL', 'CONCEPTO',
                                                  'INSCRITA', 'DEVOLUCIONES']):
                continue
            
            # Patrón: NUM_LINEA CODIGO DESCRIPCION CANTIDAD KILOS PRECIO IMPORTE IVA%
            # "1 O760 CREMA DE QUESO "CAÑAREJAL" 200 GR. 6 6 7,19 43,14 4%"
            match = re.match(
                r'^\d+\s+'                                          # Número línea
                r'([A-Z]\d+)\s+'                                    # Código (O760, O765, O711)
                r'(.+?)\s+'                                         # Descripción
                r'(\d+)\s+'                                         # Cantidad
                r'(\d+[.,]?\d*)\s+'                                 # Kilos
                r'(\d+[.,]\d{2})\s+'                                # Precio
                r'(\d+[.,]\d{2})\s+'                                # Importe
                r'(\d+)%',                                          # IVA
                linea
            )
            
            if match:
                codigo = match.group(1)
                descripcion = match.group(2).strip()
                cantidad = int(match.group(3))
                kilos = self._convertir_europeo(match.group(4))
                precio = self._convertir_europeo(match.group(5))
                importe = self._convertir_europeo(match.group(6))
                iva = int(match.group(7))
                
                # Limpiar descripción (quitar comillas extras)
                descripcion = descripcion.replace('"', '').replace('"', '').strip()
                
                if importe > 0:
                    key = f"{descripcion}_{importe}"
                    if key not in productos_encontrados:
                        productos_encontrados.add(key)
                        lineas.append({
                            'codigo': codigo,
                            'articulo': descripcion[:50],
                            'cantidad': round(kilos, 3) if kilos else cantidad,
                            'precio_ud': round(precio, 2),
                            'iva': iva,
                            'base': round(importe, 2),
                            'categoria': self.categoria_fija
                        })
                continue
            
            # Patrón alternativo más flexible
            # Para capturar líneas que puedan tener formato ligeramente diferente
            match2 = re.match(
                r'^\d+\s+([A-Z]\d+)\s+(.+?)\s+(\d+[.,]\d{2})\s+(\d+)%',
                linea
            )
            
            if match2:
                codigo = match2.group(1)
                resto = match2.group(2)
                importe = self._convertir_europeo(match2.group(3))
                iva = int(match2.group(4))
                
                # Extraer descripción y precio del resto
                # El resto tiene: "DESCRIPCION CANTIDAD KILOS PRECIO"
                partes = resto.rsplit(None, 3)  # Dividir desde el final
                if len(partes) >= 2:
                    descripcion = ' '.join(partes[:-3]) if len(partes) > 3 else partes[0]
                    descripcion = descripcion.replace('"', '').strip()
                    
                    if importe > 0 and len(descripcion) >= 3:
                        key = f"{descripcion}_{importe}"
                        if key not in productos_encontrados:
                            productos_encontrados.add(key)
                            lineas.append({
                                'codigo': codigo,
                                'articulo': descripcion[:50],
                                'cantidad': 1,
                                'precio_ud': round(importe, 2),
                                'iva': iva,
                                'base': round(importe, 2),
                                'categoria': self.categoria_fija
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
        # Formato: "T O T A L Fra. 269,41"
        m = re.search(r'T\s*O\s*T\s*A\s*L\s*Fra\.?\s*(\d+[.,]\d{2})', texto)
        if m:
            return self._convertir_europeo(m.group(1))
        
        # Alternativa: "TOTAL FACTURA 269,41"
        m = re.search(r'TOTAL\s*FACTURA\s*(\d+[.,]\d{2})', texto, re.IGNORECASE)
        if m:
            return self._convertir_europeo(m.group(1))
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        # Formato: "Fecha 30/09/2025"
        m = re.search(r'Fecha\s+(\d{2})/(\d{2})/(\d{4})', texto)
        if m:
            return f"{m.group(1)}/{m.group(2)}/{m.group(3)}"
        
        return None
