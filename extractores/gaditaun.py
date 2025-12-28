"""
Extractor para GADITAUN (María Linarejos Martínez Rodríguez)
Conservas, vinos y aceites de Cádiz.

Autor: Claude (ParsearFacturas v5.0)
Fecha: 27/12/2025

PECULIARIDAD: Los PDFs requieren OCR (Print to PDF desde Zoho CRM).
             El IVA se calcula desde Impuestos/Total (puede ser 4%, 10% o 21%).
             La base se calcula como: Base = Total / (1 + IVA/100)
"""

import re
from typing import List, Dict, Optional

# DESCOMENTAR estas líneas cuando integres en el proyecto:
# from extractores import registrar
# from extractores.base import ExtractorBase


# DESCOMENTAR el decorador cuando integres en el proyecto:
# @registrar('GADITAUN', 'MARILINA', 'MARIA LINAREJOS', 'MARÍA LINAREJOS', 
#            'GADITAUN MARILINA', 'MARILINA GADITAUN', 'GARDITAUN')
class ExtractorGaditaun:  # Cambiar a: class ExtractorGaditaun(ExtractorBase):
    """
    Extractor para facturas de GADITAUN.
    
    Formato: Print to PDF desde Zoho CRM (requiere OCR).
    IVA variable: 4% (aceite), 10% (conservas), 21% (vinos).
    """
    
    nombre = 'GADITAUN'
    nombre_fiscal = 'María Linarejos Martínez Rodríguez'
    nif = '34007216Z'
    iban = 'ES19 0081 0259 1000 0163 8268'
    metodo_pdf = 'ocr'  # Requiere OCR
    
    # Mapeo de productos a categorías (basado en Excel del usuario)
    CATEGORIAS = {
        'picarninas': ('CONSERVAS VEGETALES', 10),
        'berenjenas': ('CONSERVAS VEGETALES', 10),
        'picarragos': ('CONSERVAS VEGETALES', 10),
        'pate de tagarninas': ('CONSERVAS VEGETALES', 10),
        'tagarninas': ('CONSERVAS VEGETALES', 10),
        'duo vites': ('VINOS', 21),
        'relicta': ('VINOS', 21),
        'junus': ('VINOS', 21),
        'edalo': ('VINO BLANCO ZALEMA', 21),
        'aceite': ('ACEITES Y VINAGRES', 4),
        'aove': ('ACEITES Y VINAGRES', 4),
    }
    
    def extraer_texto_ocr(self, pdf_path: str) -> str:
        """Extrae texto del PDF usando OCR (Tesseract)."""
        try:
            from pdf2image import convert_from_path
            import pytesseract
            
            images = convert_from_path(pdf_path, dpi=300)
            textos = []
            for img in images:
                texto = pytesseract.image_to_string(img, lang='spa')
                textos.append(texto)
            return '\n'.join(textos)
        except Exception as e:
            print(f"Error OCR: {e}")
            return ""
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de productos de la factura.
        
        Maneja DOS formatos de OCR:
        
        FORMATO 1 (todo en una línea):
        '1 duo vites regantío viejo dv2rv 8,50 € 6 51,00€ 8,50€ 8,93€ 51,43€'
        
        FORMATO 2 (nombre y valores separados):
        '1 junus blanco regantío viejo jbrv'
        ...
        '8,85 € 6 53,10€ 8,85€ 9,290€ 53,54 €'
        """
        # Intentar primero con formato 1 (todo en una línea)
        lineas = self._extraer_formato_compacto(texto)
        
        # Si no encontramos nada, intentar formato 2 (separado)
        if not lineas:
            lineas = self._extraer_formato_separado(texto)
        
        return lineas
    
    def _extraer_formato_compacto(self, texto: str) -> List[Dict]:
        """Extrae líneas cuando todo está en una sola línea."""
        lineas = []
        
        # Patrón para inicio de línea
        patron_inicio = re.compile(
            r'^(\d)\s+'                                   # Nº de serie
            r'([a-záéíóúñ][\w\sáéíóúñ]+?)\s+'            # Nombre
            r'(\d+[.,]\d{2})\s*€?\s+'                     # Precio unidad
            r'(\d+)\s+',                                  # Cantidad
            re.IGNORECASE
        )
        
        patron_valores = re.compile(r'([\d.,/]+)\s*€')
        
        for line in texto.split('\n'):
            if not re.match(r'^\d\s+[a-záéíóúñ]', line, re.IGNORECASE):
                continue
            
            match_inicio = patron_inicio.match(line)
            if not match_inicio:
                continue
            
            # Verificar que tiene valores € (distingue de formato separado)
            valores = patron_valores.findall(line)
            if len(valores) < 4:  # Mínimo: precio, subtotal, impuestos, total
                continue
            
            num_serie, nombre, precio_str, cantidad_str = match_inicio.groups()
            cantidad = int(cantidad_str)
            
            impuestos_raw = valores[-2]
            total_raw = valores[-1]
            
            impuestos_raw = re.sub(r'[/]', '', impuestos_raw)
            impuestos = self._convertir_europeo(impuestos_raw)
            total = self._convertir_europeo(total_raw)
            
            if total < 0.01 or cantidad < 1:
                continue
            
            tipo_iva = self._detectar_iva(impuestos, total)
            base = round(total / (1 + tipo_iva / 100), 2)
            precio_ud = round(base / cantidad, 2) if cantidad > 0 else 0
            categoria = self._detectar_categoria(nombre)
            nombre_limpio = self._limpiar_nombre(nombre)
            
            lineas.append({
                'codigo': num_serie,
                'articulo': nombre_limpio[:60],
                'cantidad': cantidad,
                'precio_ud': precio_ud,
                'iva': tipo_iva,
                'base': base,
                'categoria': categoria
            })
        
        return lineas
    
    def _extraer_formato_separado(self, texto: str) -> List[Dict]:
        """
        Extrae líneas cuando nombre y valores están en líneas separadas.
        
        Formatos soportados:
        A) Nombre + valores con total en misma línea:
           '1 junus blanco...'
           '8,85 € 6 53,10€ 8,85€ 9,290€ 53,54 €'
        
        B) Nombre + valores sin total:
           '1 duo vites...'
           '8,50 € 12 102,00€ 17,00 € 17,85 €'
           ...
           'Total'
           '102,85 €'
        """
        lineas = []
        texto_lineas = texto.split('\n')
        
        # Buscar nombre del producto
        patron_nombre = re.compile(r'^(\d)\s+([a-záéíóúñ][\w\sáéíóúñ]+)$', re.IGNORECASE)
        
        # Formato A: valores con total
        patron_valores_completo = re.compile(
            r'^(\d+[.,]\d{2})\s*€\s+'    # Precio
            r'(\d+)\s+'                   # Cantidad
            r'[\d.,]+€?\s+'               # Subtotal
            r'[\d.,]+€?\s+'               # Descuento
            r'([\d.,]+)€?\s+'             # Impuestos
            r'(\d+[.,]\d{2})\s*€',        # Total
            re.IGNORECASE
        )
        
        # Formato B: valores sin total (total en línea separada)
        patron_valores_parcial = re.compile(
            r'^(\d+[.,]\d{2})\s*€\s+'    # Precio
            r'(\d+)\s+'                   # Cantidad
            r'[\d.,]+€?\s+'               # Subtotal
            r'[\d.,]+\s*€?\s+'            # Descuento
            r'([\d.,]+)\s*€?\s*$',        # Impuestos (final de línea)
            re.IGNORECASE
        )
        
        producto_actual = None
        valores_parciales = None
        
        for i, line in enumerate(texto_lineas):
            line = line.strip()
            
            # Buscar nombre de producto
            match_nombre = patron_nombre.match(line)
            if match_nombre:
                producto_actual = {
                    'num_serie': match_nombre.group(1),
                    'nombre': match_nombre.group(2).strip()
                }
                valores_parciales = None
                continue
            
            # Formato A: línea con todos los valores
            match_completo = patron_valores_completo.match(line)
            if match_completo and producto_actual:
                precio_str = match_completo.group(1)
                cantidad = int(match_completo.group(2))
                impuestos_str = match_completo.group(3)
                total_str = match_completo.group(4)
                
                impuestos = self._convertir_europeo(impuestos_str)
                total = self._convertir_europeo(total_str)
                
                if total >= 0.01 and cantidad >= 1:
                    tipo_iva = self._detectar_iva(impuestos, total)
                    base = round(total / (1 + tipo_iva / 100), 2)
                    precio_ud = round(base / cantidad, 2) if cantidad > 0 else 0
                    categoria = self._detectar_categoria(producto_actual['nombre'])
                    nombre_limpio = self._limpiar_nombre(producto_actual['nombre'])
                    
                    lineas.append({
                        'codigo': producto_actual['num_serie'],
                        'articulo': nombre_limpio[:60],
                        'cantidad': cantidad,
                        'precio_ud': precio_ud,
                        'iva': tipo_iva,
                        'base': base,
                        'categoria': categoria
                    })
                
                producto_actual = None
                valores_parciales = None
                continue
            
            # Formato B: línea con valores parciales (sin total)
            match_parcial = patron_valores_parcial.match(line)
            if match_parcial and producto_actual:
                valores_parciales = {
                    'precio': match_parcial.group(1),
                    'cantidad': int(match_parcial.group(2)),
                    'impuestos': match_parcial.group(3)
                }
                continue
            
            # Buscar total después de valores parciales
            if valores_parciales and producto_actual:
                # Ignorar esta búsqueda simple - usaremos el total de la factura
                pass
        
        # Si encontramos producto con valores parciales pero sin total de línea,
        # usar el total de la factura
        if valores_parciales and producto_actual and not lineas:
            total_factura = self.extraer_total(texto)
            if total_factura:
                impuestos = self._convertir_europeo(valores_parciales['impuestos'])
                cantidad = valores_parciales['cantidad']
                
                tipo_iva = self._detectar_iva(impuestos, total_factura)
                base = round(total_factura / (1 + tipo_iva / 100), 2)
                precio_ud = round(base / cantidad, 2) if cantidad > 0 else 0
                categoria = self._detectar_categoria(producto_actual['nombre'])
                nombre_limpio = self._limpiar_nombre(producto_actual['nombre'])
                
                lineas.append({
                    'codigo': producto_actual['num_serie'],
                    'articulo': nombre_limpio[:60],
                    'cantidad': cantidad,
                    'precio_ud': precio_ud,
                    'iva': tipo_iva,
                    'base': base,
                    'categoria': categoria
                })
        
        return lineas
    
    def _detectar_iva(self, impuestos: float, total: float) -> int:
        """
        Detecta el tipo de IVA (4, 10 o 21) desde impuestos y total.
        
        Base = Total - Impuestos
        IVA% = Impuestos / Base * 100
        
        Redondeamos al tipo más cercano: 4, 10 o 21.
        """
        if total <= 0 or impuestos <= 0:
            return 10  # Default
        
        base = total - impuestos
        if base <= 0:
            return 10
        
        iva_calculado = (impuestos / base) * 100
        
        # Determinar tipo más cercano
        tipos = [4, 10, 21]
        tipo_cercano = min(tipos, key=lambda x: abs(x - iva_calculado))
        
        return tipo_cercano
    
    def _detectar_categoria(self, nombre: str) -> str:
        """Detecta la categoría según el nombre del producto."""
        nombre_lower = nombre.lower()
        
        for clave, (categoria, _) in self.CATEGORIAS.items():
            if clave in nombre_lower:
                return categoria
        
        # Default según patrones
        if any(x in nombre_lower for x in ['vino', 'tinto', 'blanco', 'crianza', 'roble']):
            return 'VINOS'
        if any(x in nombre_lower for x in ['aceite', 'oliva', 'aove']):
            return 'ACEITES Y VINAGRES'
        
        return 'CONSERVAS VEGETALES'  # Default para GADITAUN
    
    def _limpiar_nombre(self, nombre: str) -> str:
        """Limpia el nombre del producto."""
        # Eliminar caracteres extraños de OCR
        nombre = re.sub(r'[^\w\sáéíóúñÁÉÍÓÚÑ.,/-]', '', nombre)
        nombre = ' '.join(nombre.split())
        return nombre
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae número de factura (formato: 2025-321)."""
        patron = re.search(r'Número de Factura\s*:?\s*(\d{4}-\d+)', texto, re.IGNORECASE)
        if patron:
            return patron.group(1)
        
        # Alternativa
        patron2 = re.search(r'Factura\s*:?\s*(\d{4}-\d+)', texto, re.IGNORECASE)
        if patron2:
            return patron2.group(1)
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de factura (formato: DD/MM/YYYY)."""
        patron = re.search(r'Fecha de Factura:?\s*(\d{2}/\d{2}/\d{4})', texto, re.IGNORECASE)
        if patron:
            return patron.group(1)
        
        # Alternativa con año corto
        patron2 = re.search(r'Fecha de Factura:?\s*(\d{2}/\d{2}/\d{2})', texto, re.IGNORECASE)
        if patron2:
            fecha = patron2.group(1)
            partes = fecha.split('/')
            if len(partes) == 3:
                return f"{partes[0]}/{partes[1]}/20{partes[2]}"
        
        return None
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """Extrae el total de la factura."""
        # Formato 1: "Total general 258,60 €"
        patron = re.search(r'Total\s+general\s+(\d+[.,]\d{2})\s*€?', texto, re.IGNORECASE)
        if patron:
            return self._convertir_europeo(patron.group(1))
        
        # Formato 2: Buscar en desglose "Total general" seguido de valor en línea siguiente
        patron2 = re.search(r'Total\s+general\s*\n\s*(\d+[.,]\d{2})\s*€?', texto, re.IGNORECASE)
        if patron2:
            return self._convertir_europeo(patron2.group(1))
        
        # Formato 3: "TOTAL FACTURA" o similar
        patron3 = re.search(r'TOTAL\s+FACTURA\s*:?\s*(\d+[.,]\d{2})\s*€?', texto, re.IGNORECASE)
        if patron3:
            return self._convertir_europeo(patron3.group(1))
        
        # Formato 4: Buscar último valor € grande en el documento
        todos_valores = re.findall(r'(\d+[.,]\d{2})\s*€', texto)
        if todos_valores:
            # Tomar el valor más grande como total (heurística)
            valores_float = [self._convertir_europeo(v) for v in todos_valores]
            return max(valores_float)
        
        return None
    
    def extraer_base_imponible(self, texto: str) -> Optional[float]:
        """Extrae la base imponible total."""
        patron = re.search(r'Base\s+Imponible\s+(\d+[.,]\d{2})\s*€?', texto, re.IGNORECASE)
        if patron:
            return self._convertir_europeo(patron.group(1))
        return None
    
    def extraer_iva_total(self, texto: str) -> Optional[float]:
        """Extrae el IVA total."""
        patron = re.search(r'Total\s+IVA\s+(\d+[.,]\d{2})\s*€?', texto, re.IGNORECASE)
        if patron:
            return self._convertir_europeo(patron.group(1))
        return None
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo (1.234,56) a float. Maneja errores OCR."""
        if not texto:
            return 0.0
        texto = texto.strip()
        
        # Eliminar caracteres no numéricos excepto . y ,
        texto = re.sub(r'[^\d.,]', '', texto)
        
        if not texto:
            return 0.0
        
        if '.' in texto and ',' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            texto = texto.replace(',', '.')
        elif len(texto) >= 3 and '.' not in texto:
            # Número sin decimales con 3+ dígitos (ej: "929" -> "9.29")
            # Asumimos 2 decimales
            texto = texto[:-2] + '.' + texto[-2:]
        
        try:
            return float(texto)
        except:
            return 0.0
    
    def validar_cuadre(self, lineas: List[Dict], total_factura: float) -> Dict:
        """
        Valida que la suma de líneas (con IVAs) = total factura.
        """
        total_calculado = 0.0
        detalle_iva = {}
        
        for linea in lineas:
            base = linea['base']
            iva = linea['iva']
            total_linea = round(base * (1 + iva / 100), 2)
            total_calculado += total_linea
            
            if iva not in detalle_iva:
                detalle_iva[iva] = {'base': 0, 'iva_importe': 0}
            detalle_iva[iva]['base'] += base
            detalle_iva[iva]['iva_importe'] += round(base * iva / 100, 2)
        
        total_calculado = round(total_calculado, 2)
        diferencia = round(total_factura - total_calculado, 2)
        
        return {
            'total_calculado': total_calculado,
            'total_factura': total_factura,
            'diferencia': diferencia,
            'cuadra': abs(diferencia) < 0.10,  # Tolerancia 10 céntimos por errores OCR
            'detalle_iva': detalle_iva
        }


# ============================================================
# CÓDIGO DE PRUEBA
# ============================================================

if __name__ == '__main__':
    import sys
    
    extractor = ExtractorGaditaun()
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = '/mnt/user-data/uploads/4078_4T25_1031_GARDITAUN_MARIA_LINAREJOS_TF.pdf'
    
    print(f"\n{'='*60}")
    print(f"PROBANDO EXTRACTOR GADITAUN")
    print(f"{'='*60}")
    print(f"Archivo: {pdf_path}\n")
    
    # Extraer texto con OCR
    texto = extractor.extraer_texto_ocr(pdf_path)
    
    if not texto:
        print("❌ No se pudo extraer texto del PDF")
        sys.exit(1)
    
    # Extraer datos
    fecha = extractor.extraer_fecha(texto)
    num_factura = extractor.extraer_numero_factura(texto)
    total = extractor.extraer_total(texto)
    base = extractor.extraer_base_imponible(texto)
    iva_total = extractor.extraer_iva_total(texto)
    lineas = extractor.extraer_lineas(texto)
    
    print(f"📅 Fecha: {fecha}")
    print(f"📄 Nº Factura: {num_factura}")
    print(f"💰 Base imponible: {base}€")
    print(f"💰 IVA total: {iva_total}€")
    print(f"💰 TOTAL: {total}€")
    print(f"\n📦 LÍNEAS ({len(lineas)}):")
    print("-" * 80)
    
    for i, linea in enumerate(lineas, 1):
        print(f"  {i}. [{linea['codigo']}] {linea['articulo']}")
        print(f"     Cant: {linea['cantidad']} x {linea['precio_ud']}€ = {linea['base']}€ (IVA {linea['iva']}%)")
        print(f"     Categoría: {linea['categoria']}")
    
    print("-" * 80)
    
    # Validar cuadre
    if total:
        cuadre = extractor.validar_cuadre(lineas, total)
        print(f"\n✅ VALIDACIÓN DE CUADRE:")
        print(f"   Total calculado: {cuadre['total_calculado']}€")
        print(f"   Total factura:   {cuadre['total_factura']}€")
        print(f"   Diferencia:      {cuadre['diferencia']}€")
        print(f"   {'✅ CUADRA' if cuadre['cuadra'] else '❌ DESCUADRE'}")
        
        print(f"\n   Desglose IVA:")
        for iva, datos in cuadre['detalle_iva'].items():
            print(f"     {iva}%: Base {round(datos['base'],2)}€, IVA {round(datos['iva_importe'],2)}€")
