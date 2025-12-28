# -*- coding: utf-8 -*-
"""
Extractor para MARITA COSTA VILELA

Distribuidora de productos gourmet
NIF: 48207369J (autónoma)
Ubicación: Valdemoro, Madrid
Tel: 665 14 06 10

Productos típicos:
- AOVE Nobleza del Sur (4% IVA)
- Picos de Jamón Lucía (4% IVA - pan)
- Patés Lucas (10% IVA)
- Cookies Milola (10% IVA)
- Torreznos La Rústica (10% IVA)
- Patatas Quillo (10% IVA)

IBAN: ES78 2100 6398 7002 0001 9653

Creado: 20/12/2025
Corregido: 28/12/2025 - Integración con sistema
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re
import pdfplumber


@registrar('MARITA COSTA', 'MARITA', 'COSTA VILELA', 'MARITA COSTA VILELA')
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
        texto = str(texto).strip()
        texto = texto.replace('\u20ac', '').replace('€', '')
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
        """Determina el IVA según el producto."""
        codigo_upper = codigo.upper()
        descripcion_upper = descripcion.upper()
        
        # IVA 4%: AOVE
        if 'AOVE' in codigo_upper or 'AOVE' in descripcion_upper:
            return 4
        
        # IVA 4%: Picos de jamón (pan)
        if 'PICO' in descripcion_upper and 'JAM' in descripcion_upper:
            return 4
        if codigo_upper.startswith('PQLPJ'):
            return 4
        
        # IVA 10%: Todo lo demás
        return 10
    
    def extraer_texto(self, pdf_path: str) -> str:
        """Extrae texto del PDF."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                texto = pdf.pages[0].extract_text()
                return texto or ''
        except:
            return ''
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de producto.
        
        Formatos soportados:
        1. Código sin espacios: AOVENOV500 AOVE NOBLEZA... 12,00 13,2000€ 158,40€
        2. Código con espacios: LR 010 LA RUSTICA... 10,00 3,5500€ 35,50€
        """
        lineas = []
        lineas_texto = texto.split('\n')
        
        patron = re.compile(
            r'^(.+?)\s+'                     # Código + Descripción
            r'(\d+[,.]?\d*)\s+'              # Cantidad
            r'([\d,]+)€\s+'                  # Precio unitario
            r'([\d,]+)€\s+'                  # Subtotal
            r'([\d,]+)€$'                    # Total
        )
        
        ultimo_codigo = None
        
        for linea in lineas_texto:
            linea = linea.strip()
            
            if not linea or 'TOTAL:' in linea or 'Albarán:' in linea:
                continue
            if 'Vencimientos' in linea or 'ARTÍCULO' in linea:
                continue
            if '€' not in linea:
                continue
            
            match = patron.match(linea)
            if match:
                prefijo = match.group(1).strip()
                cantidad = self._convertir_europeo(match.group(2))
                precio = self._convertir_europeo(match.group(3))
                importe = self._convertir_europeo(match.group(5))
                
                if importe < 1.0:
                    continue
                
                codigo, descripcion = self._separar_codigo_descripcion(prefijo)
                
                if not codigo:
                    codigo = ultimo_codigo or 'CONT'
                    descripcion = prefijo
                else:
                    ultimo_codigo = codigo
                
                descripcion = self._limpiar_descripcion(descripcion)
                iva = self._determinar_iva(codigo, descripcion)
                
                lineas.append({
                    'codigo': codigo,
                    'articulo': descripcion[:50],
                    'cantidad': int(cantidad) if cantidad == int(cantidad) else cantidad,
                    'precio_ud': precio,
                    'iva': iva,
                    'base': importe
                })
        
        return lineas
    
    def _separar_codigo_descripcion(self, prefijo: str) -> tuple:
        """Separa código de descripción."""
        # Caso 1: Código con espacio (ej: "LR 010")
        match_espacio = re.match(r'^([A-Z]{2,3}\s+\d{3,4})\s+(.+)$', prefijo)
        if match_espacio:
            return match_espacio.group(1), match_espacio.group(2)
        
        # Caso 2: Código normal
        match_normal = re.match(r'^([A-Z][A-Z0-9]{2,})\s+(.+)$', prefijo)
        if match_normal:
            codigo = match_normal.group(1)
            resto = match_normal.group(2)
            if 4 <= len(codigo) <= 15:
                return codigo, resto
        
        # Caso 3: Línea de continuación
        if prefijo[0].isdigit() or not prefijo[0].isupper():
            return None, prefijo
        
        # Caso 4: Intentar separar por primer espacio
        partes = prefijo.split(' ', 1)
        if len(partes) == 2 and len(partes[0]) >= 4:
            return partes[0], partes[1]
        
        return None, prefijo
    
    def _limpiar_descripcion(self, desc: str) -> str:
        """Limpia la descripción de lotes y caracteres extra."""
        desc = re.sub(r'\s*-\s*[A-Z0-9]+$', '', desc)
        desc = re.sub(r'\s*-\s*L\d+[A-Z]?$', '', desc)
        desc = re.sub(r'\s*-\s*\d{6}$', '', desc)
        desc = ' '.join(desc.split())
        return desc
    
    def extraer_desglose_iva(self, texto: str) -> List[Dict]:
        """Extrae desglose de IVA del resumen."""
        desglose = []
        
        for m in re.finditer(
            r'^(\d+)[,.](\d{2})\s+([\d,.]+)\s+([\d,.]+)\s*$',
            texto,
            re.MULTILINE
        ):
            tipo = int(m.group(1))
            base = self._convertir_europeo(m.group(3))
            iva = self._convertir_europeo(m.group(4))
            if base > 0 and tipo in [4, 10, 21]:
                desglose.append({'tipo': tipo, 'base': base, 'iva': iva})
        
        return desglose
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """Extrae total de la factura."""
        m = re.search(r'TOTAL:\s*([\d,.]+)€?', texto)
        if m:
            total = self._convertir_europeo(m.group(1))
            if total > 10:
                return total
        
        desglose = self.extraer_desglose_iva(texto)
        if desglose:
            return round(sum(d['base'] + d['iva'] for d in desglose), 2)
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        m = re.search(r'(\d{2}/\d{2}/\d{4})', texto)
        if m:
            return m.group(1)
        return None
