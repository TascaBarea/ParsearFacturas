# -*- coding: utf-8 -*-
"""
Extractor para PABLO RUIZ HERRERA - LA DOLOROSA CASA DE FERMENTOS

Productos fermentados artesanales:
- Talleres/degustaciones de vermut
- Encurtidos fermentados (pepinillos, kimchi, escabeche)
- Fermentos varios

DNI: 32081620R (autónomo)
IBAN: ES27 0049 4680 8124 1609 2645

IVA: 21% (productos gourmet/servicios)

FORMATO FACTURA:
El total aparece ANTES de la palabra "TOTAL", no después:
    150,03 €
    TOTAL

Creado: 27/12/2025
Corregido: 01/01/2026 - Fix patrón extracción total
Validado: 5/5 facturas (3T25-4T25)
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar('PABLO RUIZ', 'LA DOLOROSA', 'PABLO RUIZ LA DOLOROSA', 
           'PABLO RUIZ HERRERA', 'LA DOLOROSA CASA DE FERMENTOS')
class ExtractorPabloRuiz(ExtractorBase):
    """Extractor para facturas de PABLO RUIZ - LA DOLOROSA."""
    
    nombre = 'PABLO RUIZ LA DOLOROSA'
    cif = '32081620R'  # DNI (autónomo)
    iban = 'ES27 0049 4680 8124 1609 2645'
    metodo_pdf = 'pdfplumber'
    categoria_fija = 'FERMENTOS'
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo a float."""
        if not texto:
            return 0.0
        texto = str(texto).strip().replace('€', '').strip()
        if '.' in texto and ',' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            texto = texto.replace(',', '.')
        try:
            return float(texto)
        except:
            return 0.0
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de productos.
        
        Formatos posibles:
        - Taller vermut 10/12 10 12,40 € 123,99 €
        - Apio Fermentado 200gr 5 2,90 € 14,50 €
        - Pepinillos encurtidos 1KG 1 15,00 € 15,00 €
        """
        lineas = []
        
        # Patrón general: DESCRIPCION + UNIDADES + PRECIO € + TOTAL €
        patron = re.compile(
            r'^([A-Za-záéíóúñÁÉÍÓÚÑ][A-Za-záéíóúñÁÉÍÓÚÑ0-9\s/,\.]+?)\s+'  # Descripción
            r'(\d+)\s+'                                                    # Unidades
            r'([\d,]+)\s*€\s+'                                            # Precio unitario
            r'([\d,]+)\s*€',                                              # Total línea
            re.MULTILINE
        )
        
        for match in patron.finditer(texto):
            descripcion = match.group(1).strip()
            cantidad = int(match.group(2))
            precio_ud = self._convertir_europeo(match.group(3))
            total = self._convertir_europeo(match.group(4))
            
            # Filtrar líneas vacías o de cabecera
            if total < 0.01:
                continue
            if any(x in descripcion.upper() for x in ['DESCRIPCION', 'UNIDADES', 'PRECIO']):
                continue
            
            lineas.append({
                'codigo': '',
                'articulo': descripcion[:50],
                'cantidad': cantidad,
                'precio_ud': precio_ud,
                'iva': 21,  # Siempre 21%
                'base': total,
                'categoria': self.categoria_fija
            })
        
        return lineas
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """
        Extrae total de la factura.
        
        FORMATO LA DOLOROSA:
            150,03 €
            TOTAL
        
        El número € viene ANTES de la palabra TOTAL.
        El total final es el último match de este patrón.
        """
        # Patrón: número € seguido de TOTAL (con posible salto de línea)
        matches = re.findall(r'([\d,.]+)\s*€\s*\n?\s*TOTAL', texto)
        if matches:
            # El último match es el total final
            return self._convertir_europeo(matches[-1])
        
        # Alternativa: buscar todos los importes € y tomar el mayor
        todos = re.findall(r'([\d,.]+)\s*€', texto)
        if todos:
            valores = [self._convertir_europeo(v) for v in todos]
            return max(valores)
        
        return None
    
    def extraer_base_iva(self, texto: str) -> tuple:
        """Extrae base imponible e IVA."""
        base = 0.0
        iva = 0.0
        
        # BASE: primer número € antes de TOTAL
        matches = re.findall(r'([\d,.]+)\s*€\s*\n?\s*TOTAL', texto)
        if len(matches) >= 2:
            base = self._convertir_europeo(matches[0])
        
        # IVA: buscar "IVA(21%)" o "IVA:" seguido de número
        m_iva = re.search(r'IVA\(?21%?\)?\s*:?\s*([\d,.]+)\s*€', texto)
        if m_iva:
            iva = self._convertir_europeo(m_iva.group(1))
        
        return base, iva
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de factura."""
        patron = re.search(r'Fecha\s+de\s+factura:\s*(\d{2}/\d{2}/\d{4})', texto)
        if patron:
            return patron.group(1)
        return None
    
    def extraer_referencia(self, texto: str) -> Optional[str]:
        """
        Extrae número de factura.
        Formato: "Número de factura: TB-2025-03"
        """
        # Con acento
        patron = re.search(r'Número\s+de\s+factura:\s*(TB-\d{4}-\d+)', texto, re.IGNORECASE)
        if patron:
            return patron.group(1)
        
        # Sin acento
        patron2 = re.search(r'Numero\s+de\s+factura:\s*(TB-\d{4}-\d+)', texto, re.IGNORECASE)
        if patron2:
            return patron2.group(1)
        
        return None
    
    # Alias para compatibilidad
    extraer_numero_factura = extraer_referencia
