# -*- coding: utf-8 -*-
"""
Extractor para MARITA COSTA VILELA

Distribuidora de productos gourmet
NIF: 48207369J (autonoma)
Ubicacion: Valdemoro, Madrid
Tel: 665 14 06 10

Productos tipicos:
- AOVE Nobleza del Sur (4% IVA)
- Picos de Jamon Lucia (4% IVA - pan)
- Pates Lucas (10% IVA): atun, sardina
- Cookies Milola (10% IVA)
- Torreznos La Rustica (10% IVA)
- Patatas Quillo (10% IVA)

Tipos de IVA:
- 4%: Aceite de oliva virgen extra, Pan (picos de jamon)
- 10%: Alimentacion general

IBAN: ES78 2100 6398 7002 0001 9653

Creado: 20/12/2025
Actualizado: 21/12/2025 - Corregido IVA para PICOS DE JAMON (4% no 10%)
Validado: 9/9 facturas (4T24, 1T25, 2T25, 3T25, 4T25)
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re
import pdfplumber


@registrar('MARITA COSTA', 'MARITA', 'COSTA VILELA')
class ExtractorMaritaCosta(ExtractorBase):
    """Extractor para facturas de MARITA COSTA VILELA."""
    
    nombre = 'MARITA COSTA VILELA'
    cif = '48207369J'
    iban = 'ES78 2100 6398 7002 0001 9653'
    metodo_pdf = 'pdfplumber'
    categoria_fija = 'GOURMET'
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo (1.234,56) a float."""
        if not texto:
            return 0.0
        # Limpiar simbolo euro (varias formas posibles)
        texto = str(texto).strip()
        texto = texto.replace('\u20ac', '')  # Euro unicode
        texto = texto.replace('EUR', '').replace('eur', '')
        texto = texto.replace(' ', '').strip()
        
        if '.' in texto and ',' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            texto = texto.replace(',', '.')
        try:
            return float(texto)
        except:
            return 0.0
    
    def _determinar_iva(self, codigo: str, descripcion: str) -> int:
        """
        Determina el IVA segun el producto.
        
        IVA 4%:
        - AOVE (aceite de oliva)
        - PICOS DE JAMON (pan)
        
        IVA 10%:
        - Todo lo demas (pates, cookies, torreznos, patatas, etc.)
        """
        codigo_upper = codigo.upper()
        descripcion_upper = descripcion.upper()
        
        # IVA 4%: AOVE
        if 'AOVE' in codigo_upper or 'AOVE' in descripcion_upper:
            return 4
        
        # IVA 4%: Picos de jamon (pan)
        if 'PICO' in descripcion_upper and 'JAMON' in descripcion_upper:
            return 4
        if codigo_upper.startswith('PQLPJ'):  # Codigo especifico de picos
            return 4
        
        # IVA 10%: Todo lo demas
        return 10
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae lineas de producto.
        
        Formato:
        CODIGO DESCRIPCION CANTIDAD PRECIO SUBTOTAL TOTAL
        
        Ejemplo:
        AOVENOV500 AOVE NOBLEZA DEL SUR NOVO 500ML 12,00 13,2000 158,40 158,40
        """
        lineas = []
        
        # Patron para lineas de producto (sin depender del simbolo euro)
        # CODIGO DESCRIPCION CANTIDAD PRECIO SUBTOTAL [DTO] TOTAL
        patron = re.compile(
            r'^([A-Z][A-Z0-9]+)\s+'               # Codigo (empieza con letra)
            r'(.+?)\s+'                           # Descripcion
            r'(\d+[,.]?\d*)\s+'                   # Cantidad
            r'([\d,]+)[^\d\s]*\s+'                # Precio (con posible simbolo)
            r'([\d,]+)[^\d\s]*\s+'                # Subtotal
            r'([\d,]+)[^\d\s]*$',                 # Total
            re.MULTILINE
        )
        
        for m in patron.finditer(texto):
            codigo = m.group(1)
            descripcion = m.group(2).strip()
            cantidad = self._convertir_europeo(m.group(3))
            precio = self._convertir_europeo(m.group(4))
            importe = self._convertir_europeo(m.group(6))
            
            # Filtrar lineas invalidas
            if importe < 1.0:
                continue
            
            # Filtrar codigos que son fragmentos de descripcion
            if len(codigo) < 3:
                continue
            
            # Determinar IVA segun producto
            iva = self._determinar_iva(codigo, descripcion)
            
            # Limpiar descripcion (quitar lotes)
            descripcion_limpia = re.sub(r'\s*-\s*[A-Z0-9]+$', '', descripcion)
            descripcion_limpia = re.sub(r'\s*-\s*\d+$', '', descripcion_limpia)
            
            lineas.append({
                'codigo': codigo,
                'articulo': descripcion_limpia[:50],
                'cantidad': int(cantidad) if cantidad == int(cantidad) else cantidad,
                'precio_ud': precio,
                'iva': iva,
                'base': importe
            })
        
        return lineas
    
    def extraer_desglose_iva(self, texto: str) -> List[Dict]:
        """
        Extrae desglose de IVA del resumen.
        
        Formato:
        TIPO BASE I.V.A R.E. PRONTO PAGO DESC. I.R.P.F.
        10,00 188,34 18,83
        4,00 367,20 14,69
        """
        desglose = []
        
        # Patron: TIPO BASE IVA (tipo tiene decimales como 10,00 o 4,00)
        for m in re.finditer(
            r'^(\d+)[,.](\d{2})\s+([\d,.]+)\s+([\d,.]+)\s*$',
            texto,
            re.MULTILINE
        ):
            tipo = int(m.group(1))
            base = self._convertir_europeo(m.group(3))
            iva = self._convertir_europeo(m.group(4))
            if base > 0:
                desglose.append({
                    'tipo': tipo,
                    'base': base,
                    'iva': iva
                })
        
        return desglose
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """
        Extrae total de la factura.
        
        Estrategia:
        1. Buscar "TOTAL:" seguido de importe
        2. Si no, calcular desde desglose IVA (mas fiable)
        3. Si no, buscar en vencimientos
        """
        # Metodo 1: Buscar total directo (con o sin simbolo euro)
        m = re.search(r'TOTAL:\s*([\d,.]+)', texto)
        if m:
            total = self._convertir_europeo(m.group(1))
            if total > 50:
                return total
        
        # Metodo 2: Calcular desde desglose IVA (mas fiable que lineas)
        desglose = self.extraer_desglose_iva(texto)
        if desglose:
            return round(sum(d['base'] + d['iva'] for d in desglose), 2)
        
        # Metodo 3: Buscar total en vencimientos (fecha seguida de importe)
        m = re.search(r'(\d{2}/\d{2}/\d{4})\s+([\d,.]+)', texto, re.MULTILINE)
        if m:
            total = self._convertir_europeo(m.group(2))
            if total > 50:
                return total
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        # Buscar fecha en formato DD/MM/YYYY
        m = re.search(r'(\d{2}/\d{2}/\d{4})', texto)
        if m:
            return m.group(1)
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae numero de factura."""
        # Formato: "Factura ... NUMERO ... PAGINA ... FECHA"
        m = re.search(r'(\d+)\s+\d+\s+\d{2}/\d{2}/\d{4}', texto)
        if m:
            return m.group(1)
        return None
