"""
Extractor para SABORES DE PATERNA, S.C.A.

Embutidos y chicharrones de Cadiz.
CIF: F11794542

Formato factura (pdfplumber):
TRAZABILIDAD DESCRICION UNIDADES PESO PRECIO IVA IMPORTE
CHICHARRON ESPECIAL 0,007 9,010 16,8010,0 151,37
13-01-25LOMO EN MANTECA VACIO 1KG 0,002 3,170 16,3010,0 51,67
PORTE 1,000 1,000 26,8721,0 26,87

Nota: 
- Algunas lineas tienen fecha al inicio, otras no
- PRECIO e IVA estan pegados (16,8010,0 = precio 16,80, IVA 10,0)
- Total en formato: % I.R.P.F. 297,76

IVA: 10% (embutidos), 21% (portes)

Creado: 19/12/2025
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar('SABORES DE PATERNA', 'SABORES PATERNA', 'PATERNA')
class ExtractorSaboresPaterna(ExtractorBase):
    """Extractor para facturas de SABORES DE PATERNA."""
    
    nombre = 'SABORES DE PATERNA'
    cif = 'F11794542'
    iban = ''
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae lineas individuales de productos.
        """
        lineas = []
        productos_encontrados = set()
        
        # Procesar linea por linea para evitar capturas multilinea
        for linea in texto.split('\n'):
            linea = linea.strip()
            if not linea or len(linea) < 20:
                continue
            
            # Ignorar cabeceras
            if 'DESCRICION' in linea.upper() or 'TRAZABILIDAD' in linea.upper():
                continue
            if 'BASES' in linea.upper() or 'NETO' in linea.upper():
                continue
            
            # Patron 1: Linea CON fecha al inicio
            # 13-01-25LOMO EN MANTECA VACIO 1KG 0,002 3,170 16,3010,0 51,67
            match_fecha = re.match(
                r'^(\d{2}-\d{2}-\d{2})'                     # Fecha
                r'([A-ZÑÁÉÍÓÚ][A-Za-zñáéíóúÑÁÉÍÓÚ0-9\s\.]+?)\s+'  # Descripcion
                r'(\d+,\d{3})\s+'                          # Unidades
                r'(\d+,\d{3})\s+'                          # Peso
                r'(\d+,\d{2})'                             # Precio
                r'(\d{1,2}),0\s+'                          # IVA
                r'(\d+,\d{2})$',                           # Importe
                linea
            )
            
            if match_fecha:
                descripcion = match_fecha.group(2).strip()
                peso = self._convertir_europeo(match_fecha.group(4))
                precio = self._convertir_europeo(match_fecha.group(5))
                iva = int(match_fecha.group(6))
                importe = self._convertir_europeo(match_fecha.group(7))
                
                if importe >= 1.0:
                    key = f"{descripcion}_{importe}"
                    if key not in productos_encontrados:
                        productos_encontrados.add(key)
                        lineas.append({
                            'codigo': '',
                            'articulo': descripcion[:50],
                            'cantidad': round(peso, 3),
                            'precio_ud': round(precio, 2),
                            'iva': iva,
                            'base': round(importe, 2)
                        })
                continue
            
            # Patron 2: Linea SIN fecha (productos normales)
            # CHICHARRON ESPECIAL 0,007 9,010 16,8010,0 151,37
            match_sin_fecha = re.match(
                r'^([A-ZÑÁÉÍÓÚ][A-Za-zñáéíóúÑÁÉÍÓÚ\s\.]+?)\s+'  # Descripcion (solo letras y espacios)
                r'(\d+,\d{3})\s+'                          # Unidades
                r'(\d+,\d{3})\s+'                          # Peso
                r'(\d+,\d{2})'                             # Precio
                r'(\d{1,2}),0\s+'                          # IVA
                r'(\d+,\d{2})$',                           # Importe
                linea
            )
            
            if match_sin_fecha:
                descripcion = match_sin_fecha.group(1).strip()
                peso = self._convertir_europeo(match_sin_fecha.group(3))
                precio = self._convertir_europeo(match_sin_fecha.group(4))
                iva = int(match_sin_fecha.group(5))
                importe = self._convertir_europeo(match_sin_fecha.group(6))
                
                if importe >= 1.0:
                    key = f"{descripcion}_{importe}"
                    if key not in productos_encontrados:
                        productos_encontrados.add(key)
                        lineas.append({
                            'codigo': '',
                            'articulo': descripcion[:50],
                            'cantidad': round(peso, 3),
                            'precio_ud': round(precio, 2),
                            'iva': iva,
                            'base': round(importe, 2)
                        })
                continue
            
            # Patron 3: PORTE
            # PORTE 1,000 1,000 26,8721,0 26,87
            match_porte = re.match(
                r'^PORTE\s+\d+,\d{3}\s+\d+,\d{3}\s+(\d+,\d{2})21,0\s+(\d+,\d{2})$',
                linea
            )
            
            if match_porte:
                importe_porte = self._convertir_europeo(match_porte.group(2))
                if importe_porte > 0:
                    key = f"PORTE_{importe_porte}"
                    if key not in productos_encontrados:
                        productos_encontrados.add(key)
                        lineas.append({
                            'codigo': 'PORTE',
                            'articulo': 'PORTE',
                            'cantidad': 1,
                            'precio_ud': round(importe_porte, 2),
                            'iva': 21,
                            'base': round(importe_porte, 2)
                        })
        
        return lineas
    
    def _convertir_europeo(self, texto: str) -> float:
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
        # Formato: % I.R.P.F. 297,76
        patron = re.search(r'%\s*I\.?R\.?P\.?F\.?\s*(\d+,\d{2})', texto)
        if patron:
            return self._convertir_europeo(patron.group(1))
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        # Formato: Fecha: 31-03-25
        patron = re.search(r'Fecha:\s*(\d{2})-(\d{2})-(\d{2})', texto)
        if patron:
            dia = patron.group(1)
            mes = patron.group(2)
            ano = '20' + patron.group(3)
            return f"{dia}/{mes}/{ano}"
        return None
