"""
Extractor para LA ROSQUILLERIA S.L.U. (El Torro)

Rosquillas marineras artesanales de Santomera (Murcia)
CIF: B73814949

REQUIERE OCR - Las facturas son imágenes escaneadas

MÉTODO ESPECIAL DE CÁLCULO:
- BASE = TOTAL / 1,04 (incluye portes prorrateados)
- Si hay múltiples productos, prorratear BASE según importe de cada línea
- IVA siempre 4%
- Los portes NO se extraen como línea separada (ya están en el total)

Categoría fija: ROSQUILLAS MARINERAS

Creado: 20/12/2025
Corregido: 27/12/2025 - Método especial Total/1,04
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re
import subprocess
import tempfile
import os


@registrar('LA ROSQUILLERIA', 'ROSQUILLERIA', 'EL TORRO', 'ROSQUILLAS EL TORRO')
class ExtractorLaRosquilleria(ExtractorBase):
    """Extractor para facturas de LA ROSQUILLERIA (requiere OCR)."""
    
    nombre = 'LA ROSQUILLERIA'
    cif = 'B73814949'
    iban = ''
    metodo_pdf = 'ocr'
    categoria_fija = 'ROSQUILLAS MARINERAS'
    
    def extraer_texto(self, pdf_path: str) -> str:
        """Extrae texto del PDF usando OCR (tesseract)."""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                # Convertir PDF a imagen
                subprocess.run(
                    ['pdftoppm', '-png', '-r', '300', pdf_path, f'{tmpdir}/page'],
                    capture_output=True
                )
                
                # OCR cada imagen
                texto = ""
                for img in sorted(os.listdir(tmpdir)):
                    if img.endswith('.png'):
                        result = subprocess.run(
                            ['tesseract', f'{tmpdir}/{img}', 'stdout', '-l', 'eng'],
                            capture_output=True, text=True
                        )
                        texto += result.stdout
                return texto
        except Exception as e:
            return ""
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de productos con método especial.
        
        ALGORITMO:
        1. Extraer TOTAL de la factura
        2. BASE_TOTAL = TOTAL / 1,04
        3. Extraer productos (cantidad + importe_linea)
        4. Prorratear BASE_TOTAL entre productos según importe_linea
        5. Precio_ud = base_prorrateada / cantidad
        6. IVA = 4% siempre
        7. Portes NO se extraen (ya incluidos en total)
        """
        lineas = []
        
        # 1. Extraer TOTAL
        total = self.extraer_total(texto)
        if not total or total == 0:
            return []
        
        # 2. Calcular BASE TOTAL
        base_total = round(total / 1.04, 2)
        
        # 3. Extraer productos (no portes)
        productos_raw = []
        
        # Patrón para líneas de producto con IVA 4%
        # RN-X.XX DESCRIPCION ... TOT_BOLSA ... PRECIO 4% IMPORTE
        patron_producto = re.compile(
            r'RN-[\d.]+\s+'                        # Código RN-X.XX
            r'([A-Z]+(?:\s+[A-Z]+)?)\s+'           # Descripción
            r'.*?'                                  # Lote, cajas, bolsas...
            r'(\d+)\s+'                             # Tot. Bolsa (cantidad)
            r'[\d.,]+[€]?\s+'                       # Precio unitario (ignorar)
            r'4%\s+'                                # IVA 4%
            r'([\d.,]+)'                            # Importe
        , re.DOTALL)
        
        for match in patron_producto.finditer(texto):
            descripcion = match.group(1).strip()
            cantidad = int(match.group(2))
            importe = self._convertir_europeo(match.group(3))
            
            if cantidad > 0 and importe > 0:
                productos_raw.append({
                    'descripcion': descripcion,
                    'cantidad': cantidad,
                    'importe_linea': importe
                })
        
        if not productos_raw:
            return []
        
        # 4. Prorratear BASE_TOTAL entre productos
        suma_importes = sum(p['importe_linea'] for p in productos_raw)
        
        for p in productos_raw:
            proporcion = p['importe_linea'] / suma_importes
            base_prorrateada = round(base_total * proporcion, 2)
            precio_ud = round(base_prorrateada / p['cantidad'], 4)
            
            # Mejorar nombre del artículo
            articulo = p['descripcion']
            if articulo == 'ROSQUILLA':
                articulo = 'ROSQUILLA ORIGINAL'
            
            lineas.append({
                'codigo': 'RN-1.15',
                'articulo': articulo,
                'cantidad': p['cantidad'],
                'precio_ud': precio_ud,
                'iva': 4,
                'base': base_prorrateada
            })
        
        return lineas
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo (1.234,56) a float."""
        if not texto:
            return 0.0
        texto = str(texto).strip().replace('€', '').replace(' ', '')
        if ',' in texto:
            texto = texto.replace(',', '.')
        try:
            return float(texto)
        except:
            return 0.0
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """Extrae total de la factura."""
        patron = re.search(r'TOTAL:\s*([\d.,]+)\s*[€]?', texto, re.IGNORECASE)
        if patron:
            return self._convertir_europeo(patron.group(1))
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        # Formato: DD/MM/YYYY Factura
        patron = re.search(r'(\d{2}/\d{2}/\d{4})\s+Factura', texto, re.IGNORECASE)
        if patron:
            return patron.group(1)
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae número de factura."""
        patron = re.search(r'Factura\s+(\d+)', texto, re.IGNORECASE)
        if patron:
            return patron.group(1)
        return None
