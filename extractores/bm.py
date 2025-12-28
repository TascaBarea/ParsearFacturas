"""
Extractor para BM SUPERMERCADOS (DISTRIBUCION SUPERMERCADOS, SL)

Supermercado de barrio con formato ticket.
CIF: B20099586

MEJORAS v5.2:
- Usa el cuadro fiscal del ticket para asignar IVA real
- Maneja descuentos (Vales Tarjeta)
- Diccionario de productos con IVA conocido
- Múltiples variantes de nombre consolidadas

Formato ticket:
 - SECCIÓN -
 2.75 CALABACIN VERDE 1.99 5.47  (cantidad, descripción, precio_ud, importe)
 1 AZUCAR ACOR BLANQUILLA PTE.1 1.20  (cantidad, descripción, importe)

Cuadro fiscal:
 Tipo Base Iva Req Total
 10.00% 14.65 1.47 0.00 16.12
 4.00% 2.72 0.11 0.00 2.83

IVA: 4% (pan, frutas, verduras, aceite, lácteos básicos), 
     10% (alimentación general), 
     21% (bebidas especiales, drogería)

Creado: 26/12/2025
Actualizado: 26/12/2025 - v5.2 con cuadro fiscal
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional, Tuple
import re
import pdfplumber


@registrar('BM', 'BM SUPERMERCADOS', 'BM SUPERMERCADOS 2', 'BM SUPERMERCADOS 3',
           '2 BM', 'SUPERMERCADOS BM', 'SUPERMERCADOS BM 2', 
           'DISTRIBUCION SUPERMERCADOS')
class ExtractorBM(ExtractorBase):
    """Extractor para tickets de BM SUPERMERCADOS."""
    
    nombre = 'BM'
    cif = 'B20099586'
    iban = ''  # Pago tarjeta
    metodo_pdf = 'pdfplumber'
    
    # Productos conocidos con IVA específico
    PRODUCTOS_IVA_4 = [
        'YOGUR', 'LECHE', 'QUESO', 'HUEVO',
        'PAN ', 'BARRA', 'HOGAZA', 'CHAPATA',
        'FRUTA', 'VERDURA', 'HORTALIZA',
        'CALABACIN', 'TOMATE', 'LECHUGA', 'PATATA', 'CEBOLLA', 'LIMON', 
        'NARANJA', 'MANZANA', 'PERA', 'PLATANO', 'UVA', 'MELON', 'SANDIA',
        'ACEITE', 'OLIVA', 'MENDIOLIVA',
        'AZUCAR',  # Azúcar es 10% en realidad, pero algunos son 4%
        'HARINA', 'ARROZ', 'PASTA', 'LEGUMBRE', 'GARBANZO', 'LENTEJA',
    ]
    
    PRODUCTOS_IVA_21 = [
        'KOMBUCHA', 'ENERGY', 'REDBULL', 'MONSTER',
        'CERVEZA', 'VINO', 'ALCOHOL',
        'DETERGENTE', 'SUAVIZANTE', 'LEJIA', 'LIMPIA',
        'CHAMPU', 'GEL', 'CREMA', 'DESODORANTE',
        'PILA', 'BOMBILLA', 'PILAS',
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
    
    def _extraer_cuadro_fiscal(self, texto: str) -> List[Tuple[float, float, float, float]]:
        """
        Extrae el cuadro fiscal del ticket.
        Retorna lista de tuplas: (tipo_iva, base, cuota_iva, total)
        """
        cuadro = []
        # Patrón: "10.00% 14.65 1.47 0.00 16.12"
        patron = re.compile(r'(\d+[.,]\d{2})%\s+(\d+[.,]\d{2})\s+(\d+[.,]\d{2})\s+\d+[.,]\d{2}\s+(\d+[.,]\d{2})')
        
        for match in patron.finditer(texto):
            tipo_iva = self._convertir_europeo(match.group(1))
            base = self._convertir_europeo(match.group(2))
            cuota = self._convertir_europeo(match.group(3))
            total = self._convertir_europeo(match.group(4))
            cuadro.append((tipo_iva, base, cuota, total))
        
        return cuadro
    
    def _determinar_iva_producto(self, descripcion: str, seccion: str) -> int:
        """
        Determina el IVA de un producto basándose en su descripción y sección.
        """
        desc_upper = descripcion.upper()
        
        # Primero buscar en productos conocidos IVA 21%
        for producto in self.PRODUCTOS_IVA_21:
            if producto in desc_upper:
                return 21
        
        # Luego productos conocidos IVA 4%
        for producto in self.PRODUCTOS_IVA_4:
            if producto in desc_upper:
                return 4
        
        # Por sección
        if seccion in ['FRUTERIA', 'FRUTERÍA', 'PANADERIA', 'PANADERÍA']:
            return 4
        elif seccion in ['DROGUERIA', 'DROGERÍA', 'PERFUMERIA', 'PERFUMERÍA', 'HOGAR', 'MENAJE']:
            return 21
        
        # Por defecto: 10% (alimentación general)
        return 10
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas individuales de productos del ticket.
        Usa el cuadro fiscal para validar y ajustar IVA.
        """
        lineas = []
        seccion_actual = ''
        
        # Extraer cuadro fiscal para validación
        cuadro_fiscal = self._extraer_cuadro_fiscal(texto)
        
        # Calcular totales por tipo de IVA del cuadro fiscal
        totales_por_iva = {}
        for tipo_iva, base, cuota, total in cuadro_fiscal:
            iva_int = int(round(tipo_iva))
            totales_por_iva[iva_int] = totales_por_iva.get(iva_int, 0) + total
        
        for linea in texto.split('\n'):
            linea = linea.strip()
            if not linea:
                continue
            
            # Detectar sección
            match_seccion = re.match(r'^-\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\-]+)\s*-$', linea)
            if match_seccion:
                seccion_actual = match_seccion.group(1).upper().replace('Í', 'I').replace('Ó', 'O')
                continue
            
            # Ignorar líneas no relevantes
            if any(x in linea.upper() for x in [
                'TOTAL', 'TARJETA', 'TICKET', 'FACTURA', 'CLIENTE', 'GRACIAS', 
                'COMPRA', 'BM:', 'ACUMULADO', 'PUNTO', 'COLECCION', 'CUENTA BM', 
                'APP', 'DEVOLUC', 'CAJA', 'ATENDIÓ', 'FECHA', 'HORA', 'CENTRO',
                'AUTORIZ', 'COMERCIO', 'TITULAR', 'ARC', 'AID', 'APLICACION',
                'VALIDACION', 'CHIP', 'OPER', 'IMPORTE', 'SEC.', 'CONTACTLES', 
                '---', 'Tipo', 'Base', 'Iva', 'Req', 'CIF:', 'NIF', 'DOMICILIO', 
                'POBLACIÓN', 'NOMBRE', 'EFECTIVO', 'ENTREGADO', 'CAMBIO', 
                'AHORRADO', 'UD/KG', '€/UD/KG', 'SIMPLIFICADA', 'SERVIRED',
                'NUMERO DE', 'POR COMPRAR', 'CONSEGUIDO', '****', 'COPIA PARA',
                'SE ACEPTAR', 'ADQUIRIDOS', 'GÉNERO', 'DEFECTUOSO', 'TRANSCURRIDO',
                'MANIPULADO', 'COMPROMETA', 'FRESCOS', 'REFRIGERADOS', 'CONGELADOS',
                'ESTABLECIMIENTO', 'PRODUCTO', 'N.SEC'
            ]):
                continue
            
            # Detectar descuentos (Vales Tarjeta -1.23)
            match_descuento = re.match(r'^(Vales?\s+Tarjeta|DESCUENTO|DTO)\s+(-?\d+[.,]\d{2})$', linea, re.IGNORECASE)
            if match_descuento:
                importe = self._convertir_europeo(match_descuento.group(2))
                if importe != 0:
                    lineas.append({
                        'codigo': '',
                        'articulo': 'DESCUENTO VALES',
                        'cantidad': 1,
                        'precio_ud': round(importe, 2),
                        'iva': 10,  # Los descuentos se prorratean, usar 10% como base
                        'base': round(importe / 1.10, 2)
                    })
                continue
            
            # Patrón 1: cantidad decimal + descripción + precio_ud + importe
            # "2.75 CALABACIN VERDE 1.99 5.47"
            match1 = re.match(
                r'^(\d+[.,]\d{2,3})\s+([A-ZÁÉÍÓÚÑa-záéíóúñ][A-ZÁÉÍÓÚÑa-záéíóúñ0-9\s\.\,\-\/\(\)]+?)\s+(\d+[.,]\d{2,3})\s+(\d+[.,]\d{2})$',
                linea
            )
            if match1:
                cantidad = self._convertir_europeo(match1.group(1))
                descripcion = match1.group(2).strip()
                precio_ud = self._convertir_europeo(match1.group(3))
                importe = self._convertir_europeo(match1.group(4))
                
                if importe > 0 and len(descripcion) >= 3:
                    iva = self._determinar_iva_producto(descripcion, seccion_actual)
                    lineas.append({
                        'codigo': '',
                        'articulo': descripcion[:50],
                        'cantidad': round(cantidad, 3),
                        'precio_ud': round(precio_ud, 2),
                        'iva': iva,
                        'base': round(importe / (1 + iva / 100), 2)
                    })
                continue
            
            # Patrón 2: cantidad entera + descripción + importe
            # "1 AZUCAR ACOR BLANQUILLA PTE.1 1.20"
            # "3 PIMIENTO BAIGORRI NAJERA F35 2.89 8.67"
            match2 = re.match(
                r'^(\d+)\s+([A-ZÁÉÍÓÚÑa-záéíóúñ][A-ZÁÉÍÓÚÑa-záéíóúñ0-9\s\.\,\-\/\(\)]+?)\s+(\d+[.,]\d{2})$',
                linea
            )
            if match2:
                cantidad = int(match2.group(1))
                descripcion = match2.group(2).strip()
                importe = self._convertir_europeo(match2.group(3))
                
                if importe > 0 and len(descripcion) >= 3 and cantidad <= 100:
                    iva = self._determinar_iva_producto(descripcion, seccion_actual)
                    lineas.append({
                        'codigo': '',
                        'articulo': descripcion[:50],
                        'cantidad': cantidad,
                        'precio_ud': round(importe / cantidad, 2) if cantidad else importe,
                        'iva': iva,
                        'base': round(importe / (1 + iva / 100), 2)
                    })
                continue
            
            # Patrón 2b: cantidad entera + descripción + precio_ud + importe
            # "3 PIMIENTO BAIGORRI NAJERA F35 2.89 8.67"
            match2b = re.match(
                r'^(\d+)\s+([A-ZÁÉÍÓÚÑa-záéíóúñ][A-ZÁÉÍÓÚÑa-záéíóúñ0-9\s\.\,\-\/\(\)]+?)\s+(\d+[.,]\d{2})\s+(\d+[.,]\d{2})$',
                linea
            )
            if match2b:
                cantidad = int(match2b.group(1))
                descripcion = match2b.group(2).strip()
                precio_ud = self._convertir_europeo(match2b.group(3))
                importe = self._convertir_europeo(match2b.group(4))
                
                if importe > 0 and len(descripcion) >= 3 and cantidad <= 100:
                    iva = self._determinar_iva_producto(descripcion, seccion_actual)
                    lineas.append({
                        'codigo': '',
                        'articulo': descripcion[:50],
                        'cantidad': cantidad,
                        'precio_ud': round(precio_ud, 2),
                        'iva': iva,
                        'base': round(importe / (1 + iva / 100), 2)
                    })
                continue
        
        # Si hay cuadro fiscal, ajustar bases para que cuadren
        if cuadro_fiscal and lineas:
            lineas = self._ajustar_bases_con_cuadro_fiscal(lineas, cuadro_fiscal)
        
        return lineas
    
    def _ajustar_bases_con_cuadro_fiscal(self, lineas: List[Dict], cuadro_fiscal: List[Tuple]) -> List[Dict]:
        """
        Ajusta las bases de las líneas para que cuadren con el cuadro fiscal.
        """
        # Calcular suma de bases por tipo de IVA del cuadro fiscal
        bases_fiscales = {}
        for tipo_iva, base, cuota, total in cuadro_fiscal:
            iva_int = int(round(tipo_iva))
            bases_fiscales[iva_int] = bases_fiscales.get(iva_int, 0) + base
        
        # Calcular suma de bases extraídas por tipo de IVA
        bases_extraidas = {}
        for linea in lineas:
            iva = linea['iva']
            bases_extraidas[iva] = bases_extraidas.get(iva, 0) + linea['base']
        
        # Calcular factores de ajuste por tipo de IVA
        factores = {}
        for iva in bases_extraidas:
            if iva in bases_fiscales and bases_extraidas[iva] > 0:
                factores[iva] = bases_fiscales[iva] / bases_extraidas[iva]
            else:
                factores[iva] = 1.0
        
        # Aplicar ajuste proporcional a cada línea
        for linea in lineas:
            iva = linea['iva']
            if iva in factores:
                linea['base'] = round(linea['base'] * factores[iva], 2)
        
        return lineas
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo a float."""
        if not texto:
            return 0.0
        texto = texto.strip()
        # BM usa punto como decimal
        try:
            return float(texto.replace(',', '.'))
        except:
            return 0.0
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """Extrae total de la factura."""
        # Formato: "TOTAL COMPRA (iva incl.) 35.06"
        m = re.search(r'TOTAL COMPRA.*?(\d+[.,]\d{2})', texto, re.IGNORECASE)
        if m:
            return self._convertir_europeo(m.group(1))
        
        # Alternativa: "Total Factura XX,XX€"
        m = re.search(r'Total\s+Factura\s+(\d+[.,]\d{2})', texto, re.IGNORECASE)
        if m:
            return self._convertir_europeo(m.group(1))
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha del ticket."""
        # Formato: "24/10/25 14:13" o "06/09/25 15:08"
        m = re.search(r'(\d{2})/(\d{2})/(\d{2})\s+\d{2}:\d{2}', texto)
        if m:
            dia, mes, anio = m.group(1), m.group(2), m.group(3)
            return f"{dia}/{mes}/20{anio}"
        
        # Alternativa en datos factura: "24-10-25"
        m = re.search(r'(\d{2})-(\d{2})-(\d{2})', texto)
        if m:
            dia, mes, anio = m.group(1), m.group(2), m.group(3)
            return f"{dia}/{mes}/20{anio}"
        
        return None
