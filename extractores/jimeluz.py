"""
Extractor para JIMELUZ EMPRENDEDORES S.L. (Carrefour Express franquicia)

Franquicia de Carrefour Express en Calle Embajadores, 50 - Madrid
CIF: B-87501243

Formato ticket (pdfplumber):
 * * CARREFOUR EXPRESS * *
 * * * * * PVP IVA INCLUIDO * * * * *
 SALMON AHUMADO 100 G 4,09
 LIMON CDC 1,19
 HIELO CUBITOS 2 KG
  5 x ( 1,25 ) 6,25
 ==========================================
 5 ART. TOTAL A PAGAR : 5,11
 ==========================================
 TIPO BASE CUOTA
 4,00% 2,51 0,10
 10,00% 2,27 0,23

Tipos de línea:
1. Simple: "LIMON CDC 1,19"
2. Con cantidad inicio: "3 BAYETAS MICROFIBRA 1,95"
3. Cantidad en línea siguiente: "HIELO CUBITOS 2 KG" + "5 x ( 1,25 ) 6,25"

IVA: 4% (frutas, verduras, pan), 10% (alimentación), 21% (droguería)
Pago: Tarjeta

Creado: 26/12/2025
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional, Tuple
import re
import pdfplumber


@registrar('JIMELUZ', 'JIMELUZ EMPRENDEDORES', 'CARREFOUR EXPRESS EMBAJADORES')
class ExtractorJimeluz(ExtractorBase):
    """Extractor para tickets de JIMELUZ (Carrefour Express)."""
    
    nombre = 'JIMELUZ'
    cif = 'B87501243'
    iban = ''  # Pago tarjeta
    metodo_pdf = 'pdfplumber'
    
    # Productos conocidos con IVA específico
    PRODUCTOS_IVA_4 = [
        'LIMON', 'LIMA', 'NARANJA', 'MANZANA', 'PERA', 'PLATANO', 'UVA',
        'MELON', 'SANDIA', 'FRESA', 'KIWI', 'PIÑA', 'MANGO',
        'TOMATE', 'LECHUGA', 'RUCULA', 'CALABACIN', 'PEPINO', 'CEBOLLA',
        'PATATA', 'ZANAHORIA', 'PIMIENTO', 'BERENJENA', 'JUDIAS',
        'PAN ', 'BARRA', 'MOLLETE', 'CHAPATA', 'HOGAZA',
        'LECHE', 'HUEVO', 'QUESO', 'YOGUR',
        'ACEITE', 'OLIVA',
        'HARINA', 'ARROZ', 'PASTA', 'LEGUMBRE',
    ]
    
    PRODUCTOS_IVA_21 = [
        'BAYETA', 'FREGONA', 'ESCOBA', 'RECOGEDOR',
        'DETERGENTE', 'SUAVIZANTE', 'LEJIA', 'LIMPIA', 'QUITAGRASA',
        'JABON', 'CHAMPU', 'GEL', 'CREMA', 'DESODORANTE',
        'PAPEL COCINA', 'PAPEL HIGIEN', 'SERVILLETA',
        'BOLSA BASURA', 'FILM', 'ALUMINIO',
        'PILA', 'BOMBILLA', 'MECHERO', 'VELA',
        'PALILLERO', 'PALILLO',
    ]
    
    def extraer_texto_pdfplumber(self, pdf_path: str) -> str:
        """Extrae texto del PDF usando pdfplumber."""
        texto_completo = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    texto = page.extract_text()
                    if texto:
                        texto_completo.append(texto)
        except Exception as e:
            pass
        return '\n'.join(texto_completo)
    
    def _extraer_cuadro_fiscal(self, texto: str) -> List[Tuple[float, float, float]]:
        """
        Extrae el cuadro fiscal del ticket.
        Retorna lista de tuplas: (tipo_iva, base, cuota)
        """
        cuadro = []
        # Patrón: "4,00% 2,51 0,10"
        patron = re.compile(r'(\d+,\d{2})%\s+(\d+,\d{2})\s+(\d+,\d{2})')
        
        for match in patron.finditer(texto):
            tipo_iva = float(match.group(1).replace(',', '.'))
            base = float(match.group(2).replace(',', '.'))
            cuota = float(match.group(3).replace(',', '.'))
            cuadro.append((tipo_iva, base, cuota))
        
        return cuadro
    
    def _determinar_iva_producto(self, descripcion: str) -> int:
        """Determina el IVA de un producto basándose en su descripción."""
        desc_upper = descripcion.upper()
        
        # Primero buscar en productos IVA 21%
        for producto in self.PRODUCTOS_IVA_21:
            if producto in desc_upper:
                return 21
        
        # Luego productos IVA 4%
        for producto in self.PRODUCTOS_IVA_4:
            if producto in desc_upper:
                return 4
        
        # Por defecto: 10% (alimentación general)
        return 10
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas individuales de productos del ticket.
        """
        lineas = []
        cuadro_fiscal = self._extraer_cuadro_fiscal(texto)
        
        # Encontrar zona de productos (entre "PVP IVA INCLUIDO" y "TOTAL A PAGAR")
        lines = texto.split('\n')
        in_productos = False
        producto_pendiente = None  # Para manejar líneas de cantidad
        
        for i, linea in enumerate(lines):
            linea = linea.strip()
            
            # Inicio zona productos
            if 'PVP IVA INCLUIDO' in linea:
                in_productos = True
                continue
            
            # Fin zona productos
            if 'TOTAL A PAGAR' in linea or '= = =' in linea:
                in_productos = False
                continue
            
            if not in_productos or not linea:
                continue
            
            # Patrón para línea de cantidad: "5 x ( 1,25 ) 6,25"
            match_cantidad = re.match(r'^(\d+)\s*x\s*\(\s*(\d+,\d{2})\s*\)\s*(\d+,\d{2})$', linea)
            if match_cantidad and producto_pendiente:
                cantidad = int(match_cantidad.group(1))
                precio_ud = float(match_cantidad.group(2).replace(',', '.'))
                importe = float(match_cantidad.group(3).replace(',', '.'))
                
                iva = self._determinar_iva_producto(producto_pendiente)
                lineas.append({
                    'codigo': '',
                    'articulo': producto_pendiente[:50],
                    'cantidad': cantidad,
                    'precio_ud': round(precio_ud, 2),
                    'iva': iva,
                    'base': round(importe / (1 + iva / 100), 2),
                    'importe_iva_inc': importe
                })
                producto_pendiente = None
                continue
            
            # Patrón: cantidad al inicio + descripción + importe
            # "3 BAYETAS MICROFIBRA 1,95"
            match_con_cantidad = re.match(r'^(\d+)\s+([A-ZÁÉÍÓÚÑa-záéíóúñ][A-ZÁÉÍÓÚÑa-záéíóúñ0-9\s\.\,\-\/\(\)]+?)\s+(\d+,\d{2})$', linea)
            if match_con_cantidad:
                cantidad = int(match_con_cantidad.group(1))
                descripcion = match_con_cantidad.group(2).strip()
                importe = float(match_con_cantidad.group(3).replace(',', '.'))
                
                # Verificar que no sea solo un número (ej: "100 G")
                if cantidad <= 20 and len(descripcion) >= 3:
                    iva = self._determinar_iva_producto(descripcion)
                    lineas.append({
                        'codigo': '',
                        'articulo': descripcion[:50],
                        'cantidad': cantidad,
                        'precio_ud': round(importe / cantidad, 2),
                        'iva': iva,
                        'base': round(importe / (1 + iva / 100), 2),
                        'importe_iva_inc': importe
                    })
                    producto_pendiente = None
                    continue
            
            # Patrón simple: descripción + importe
            # "SALMON AHUMADO 100 G 4,09"
            match_simple = re.match(r'^([A-ZÁÉÍÓÚÑa-záéíóúñ][A-ZÁÉÍÓÚÑa-záéíóúñ0-9\s\.\,\-\/\(\)]+?)\s+(\d+,\d{2})$', linea)
            if match_simple:
                descripcion = match_simple.group(1).strip()
                importe = float(match_simple.group(2).replace(',', '.'))
                
                if len(descripcion) >= 3:
                    iva = self._determinar_iva_producto(descripcion)
                    lineas.append({
                        'codigo': '',
                        'articulo': descripcion[:50],
                        'cantidad': 1,
                        'precio_ud': round(importe, 2),
                        'iva': iva,
                        'base': round(importe / (1 + iva / 100), 2),
                        'importe_iva_inc': importe
                    })
                    producto_pendiente = None
                    continue
            
            # Línea sin importe - podría ser producto con cantidad en siguiente línea
            # "HIELO CUBITOS 2 KG"
            if re.match(r'^[A-ZÁÉÍÓÚÑa-záéíóúñ][A-ZÁÉÍÓÚÑa-záéíóúñ0-9\s\.\,\-\/\(\)]+$', linea):
                if len(linea) >= 3 and not any(x in linea.upper() for x in ['ART.', 'VENTAJAS', 'CLUB', 'VENTA', 'MASTERCARD']):
                    producto_pendiente = linea
        
        # Ajustar bases con cuadro fiscal
        if cuadro_fiscal and lineas:
            lineas = self._ajustar_bases_con_cuadro_fiscal(lineas, cuadro_fiscal)
        
        # Eliminar campo temporal
        for l in lineas:
            if 'importe_iva_inc' in l:
                del l['importe_iva_inc']
        
        return lineas
    
    def _ajustar_bases_con_cuadro_fiscal(self, lineas: List[Dict], cuadro_fiscal: List[Tuple]) -> List[Dict]:
        """Ajusta las bases para que cuadren con el cuadro fiscal."""
        # Bases del cuadro fiscal
        bases_fiscales = {}
        for tipo_iva, base, cuota in cuadro_fiscal:
            iva_int = int(round(tipo_iva))
            bases_fiscales[iva_int] = bases_fiscales.get(iva_int, 0) + base
        
        # Bases extraídas
        bases_extraidas = {}
        for linea in lineas:
            iva = linea['iva']
            bases_extraidas[iva] = bases_extraidas.get(iva, 0) + linea['base']
        
        # Factores de ajuste
        factores = {}
        for iva in bases_extraidas:
            if iva in bases_fiscales and bases_extraidas[iva] > 0:
                factores[iva] = bases_fiscales[iva] / bases_extraidas[iva]
            else:
                factores[iva] = 1.0
        
        # Aplicar ajuste
        for linea in lineas:
            iva = linea['iva']
            if iva in factores:
                linea['base'] = round(linea['base'] * factores[iva], 2)
        
        return lineas
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """Extrae total de la factura."""
        # Formato: "5 ART. TOTAL A PAGAR : 5,11"
        m = re.search(r'TOTAL A PAGAR\s*:\s*(\d+,\d{2})', texto)
        if m:
            return float(m.group(1).replace(',', '.'))
        
        # Alternativa: "VENTA 5,11"
        m = re.search(r'\nVENTA\s+(\d+,\d{2})\n', texto)
        if m:
            return float(m.group(1).replace(',', '.'))
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha del ticket."""
        # Formato: "02/02/2025 12:06:14"
        m = re.search(r'(\d{2})/(\d{2})/(\d{4})\s+\d{2}:\d{2}', texto)
        if m:
            return f"{m.group(1)}/{m.group(2)}/{m.group(3)}"
        
        # Formato alternativo: "02/02/25"
        m = re.search(r'(\d{2})/(\d{2})/(\d{2})\s+\d{2}:\d{2}', texto)
        if m:
            return f"{m.group(1)}/{m.group(2)}/20{m.group(3)}"
        
        return None
