# -*- coding: utf-8 -*-
"""
Extractor para DIA / ECOMS SUPERMARKET S.L.
Franquiciado DIA en C/ Embajadores 29, Madrid

CIF: B72738602
Método: pdfplumber

IMPORTANTE: Los tickets dicen "DIA" pero el CIF es de ECOMS SUPERMARKET S.L.
Los archivos se nombran "DIA" así que necesitamos ese alias.

Formato ticket:
- Productos con letra A/B/C que indica tipo IVA
- A = 4% (alimentación básica)
- B = 10% (alimentación elaborada)  
- C = 21% (no alimentación)
- Precios con IVA incluido
- Cuadro fiscal al final con Base y Cuota por tipo

Creado: 28/12/2025
Corregido: 01/01/2026 - Añadido alias DIA, patrón cuadro fiscal corregido
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar(
    'DIA',                      # ← NUEVO: alias principal por nombre archivo
    'ECOMS', 
    'ECOMS SUPERMARKET SL', 
    'ECOMS SUPERMARKET S.L.', 
    'ECOMS S', 
    'ECOMS SUPERMARKET',
    'DIA ECOMS',
    'GRUPO DIA'
)
class ExtractorDiaEcoms(ExtractorBase):
    """Extractor para tickets de DIA / ECOMS SUPERMARKET."""
    
    nombre = 'DIA ECOMS'
    cif = 'B72738602'
    iban = ''
    metodo_pdf = 'pdfplumber'
    
    # Mapeo letra → tipo IVA
    LETRA_IVA = {'A': 4, 'B': 10, 'C': 21}
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """Extrae líneas de productos.
        
        ESTRATEGIA: El cuadro fiscal es más fiable que los productos individuales
        porque las letras A/B/C no tienen mapeo fijo (depende del ticket).
        Usamos cuadro fiscal para el cuadre y productos solo para descripciones.
        """
        if not texto:
            return []
        
        # MÉTODO 1: Cuadro fiscal (más fiable)
        cuadro = self._extraer_cuadro_fiscal(texto)
        if cuadro:
            # Intentar obtener descripciones de productos
            productos = self._extraer_productos_individuales(texto)
            return self._combinar_cuadro_con_productos(cuadro, productos)
        
        # MÉTODO 2: Fallback a productos individuales
        return self._extraer_productos_individuales(texto)
    
    def _combinar_cuadro_con_productos(self, cuadro: List[Dict], productos: List[Dict]) -> List[Dict]:
        """Combina cuadro fiscal (bases correctas) con productos (descripciones)."""
        lineas = []
        
        # Si no hay productos, usar cuadro fiscal directamente
        if not productos:
            for item in cuadro:
                lineas.append({
                    'codigo': '',
                    'articulo': f'COMPRA DIA IVA {item["tipo"]}%',
                    'cantidad': 1,
                    'precio_ud': item['base'],
                    'iva': item['tipo'],
                    'base': item['base']
                })
            return lineas
        
        # Si hay productos, agrupar descripciones por tipo IVA aproximado
        # y usar las bases del cuadro fiscal
        for item in cuadro:
            tipo_iva = item['tipo']
            base = item['base']
            
            # Buscar productos que podrían corresponder a este IVA
            # Usar descripción genérica pero precisa
            lineas.append({
                'codigo': '',
                'articulo': f'PRODUCTOS DIA IVA {tipo_iva}%',
                'cantidad': 1,
                'precio_ud': base,
                'iva': tipo_iva,
                'base': base
            })
        
        return lineas
    
    def _extraer_productos_individuales(self, texto: str) -> List[Dict]:
        """Intenta extraer productos individuales del ticket."""
        lineas = []
        
        # El formato es complicado porque las descripciones están fragmentadas
        # Patrón: buscar líneas con "X ud PRECIO € TOTAL € LETRA"
        patron_linea = re.compile(
            r'(\d+)\s+ud\s+(\d+[,\.]\d+)\s*€?\s+(\d+[,\.]\d+)\s*€?\s+([ABC])',
            re.IGNORECASE
        )
        
        # Palabras a ignorar en descripciones
        IGNORAR = [
            'productos vendidos', 'descripción', 'cantidad', 'precio', 'total',
            'forma de pago', 'resumen', 'desglose', 'tipo iva', 'iva incluido',
            'ecoms', 'supermarket', 'documento', 'compra en', 'tienda'
        ]
        
        lineas_texto = texto.split('\n')
        
        for i, linea in enumerate(lineas_texto):
            linea = linea.strip()
            
            # Buscar línea de cantidad/precio
            match = patron_linea.search(linea)
            if match:
                cantidad = int(match.group(1))
                precio_ud = self._convertir_europeo(match.group(2))
                total = self._convertir_europeo(match.group(3))
                letra = match.group(4).upper()
                iva = self.LETRA_IVA.get(letra, 10)
                
                # Buscar descripción en líneas anteriores (máximo 2)
                partes_desc = []
                for j in range(max(0, i-2), i):
                    linea_anterior = lineas_texto[j].strip()
                    
                    # Validar que sea descripción de producto
                    if not linea_anterior or len(linea_anterior) < 3:
                        continue
                    if re.search(r'\d+\s+ud', linea_anterior, re.IGNORECASE):
                        continue
                    if re.search(r'^\d+[,\.]\d+\s*€', linea_anterior):
                        continue
                    if any(ig in linea_anterior.lower() for ig in IGNORAR):
                        continue
                    # Solo texto alfanumérico básico
                    if re.match(r'^[A-ZÁÉÍÓÚÑ0-9\s\-\.]+$', linea_anterior, re.IGNORECASE):
                        partes_desc.append(linea_anterior)
                
                # Construir descripción
                if partes_desc:
                    desc = ' '.join(partes_desc)
                else:
                    desc = f"PRODUCTO DIA IVA {iva}%"
                
                # Limpiar descripción
                desc = re.sub(r'[|¿¡\[\]{}]', '', desc)
                desc = ' '.join(desc.split())[:50]
                
                # Convertir precio IVA incluido a base
                base = round(total / (1 + iva / 100), 2)
                
                lineas.append({
                    'codigo': '',
                    'articulo': desc,
                    'cantidad': cantidad,
                    'precio_ud': precio_ud,
                    'iva': iva,
                    'base': base
                })
        
        return lineas
    
    def _extraer_cuadro_fiscal(self, texto: str) -> List[Dict]:
        """Extrae cuadro de IVA del ticket."""
        desglose = []
        
        # PATRÓN CORREGIDO: "A 4% 0,86 € 0,03 €"
        patron = re.compile(
            r'([ABC])\s+(\d+)%\s+(\d+[,\.]\d+)\s*€?\s+(\d+[,\.]\d+)',
            re.MULTILINE
        )
        
        for match in patron.finditer(texto):
            letra = match.group(1).upper()
            tipo = int(match.group(2))
            base = self._convertir_europeo(match.group(3))
            cuota = self._convertir_europeo(match.group(4))
            
            if tipo in [4, 10, 21] and base > 0:
                desglose.append({
                    'tipo': tipo, 
                    'base': base, 
                    'iva': cuota
                })
        
        return desglose
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """Extrae el total del ticket."""
        if not texto:
            return None
        
        patrones = [
            r'Total a pagar[\.]+\s*(\d+[,\.]\d+)\s*€',
            r'Total a pagar\s*(\d+[,\.]\d+)\s*€',
            r'Total venta Dia[\.]+\s*(\d+[,\.]\d+)\s*€',
            r'TOTAL\s+FACTURA\s+(\d+[,\.]\d+)',
        ]
        
        for patron in patrones:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                return self._convertir_europeo(match.group(1))
        
        # Fallback: calcular desde cuadro fiscal
        cuadro = self._extraer_cuadro_fiscal(texto)
        if cuadro:
            return round(sum(d['base'] + d['iva'] for d in cuadro), 2)
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae la fecha del ticket."""
        if not texto:
            return None
        
        # Formato: "11/10/2025 12:52"
        patron = re.search(r'(\d{2}/\d{2}/\d{4})\s+\d{2}:\d{2}', texto)
        if patron:
            return patron.group(1)
        
        # Formato alternativo
        patron2 = re.search(r'(\d{2}/\d{2}/\d{4})', texto)
        if patron2:
            return patron2.group(1)
        
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae el número de factura."""
        if not texto:
            return None
        
        # Formato: "factura Nº FT139080200206"
        patron = re.search(r'factura\s+N[ºo°]\s*([A-Z0-9]+)', texto, re.IGNORECASE)
        if patron:
            return patron.group(1)
        
        # Formato: "Nº de documento V90000013"
        patron2 = re.search(r'N[ºo°]\s+de\s+documento\s+([A-Z0-9]+)', texto, re.IGNORECASE)
        if patron2:
            return patron2.group(1)
        
        return None
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo a float."""
        if not texto:
            return 0.0
        texto = str(texto).strip()
        if ',' in texto and '.' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            texto = texto.replace(',', '.')
        try:
            return float(texto)
        except:
            return 0.0
