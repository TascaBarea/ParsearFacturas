# -*- coding: utf-8 -*-
"""
Extractor para ECOMS SUPERMARKET S.L.
Supermercado local en C/ Huertas 72, Madrid

CIF: B72738602
Método: pdfplumber (corregido de 'hibrido')

Creado: 28/12/2025
Corregido: 29/12/2025 - metodo_pdf = 'pdfplumber'
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re
import pdfplumber


@registrar('ECOMS', 'ECOMS SUPERMARKET SL', 'ECOMS SUPERMARKET S.L.', 'ECOMS S', 'ECOMS SUPERMARKET')
class ExtractorEcoms(ExtractorBase):
    """Extractor para tickets de ECOMS SUPERMARKET."""
    
    nombre = 'ECOMS SUPERMARKET'
    cif = 'B72738602'
    iban = ''
    metodo_pdf = 'pdfplumber'  # CORREGIDO de 'hibrido'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """Extrae líneas de productos."""
        if not texto:
            return []
        
        lineas = []
        
        # Patrón: DESCRIPCION IMPORTE IVA%
        patron_linea = re.compile(
            r'^([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ0-9\s\-\.]+?)\s+'
            r'(\d+[,\.]\d+)\s+'
            r'(\d+)[,\.]00%',
            re.MULTILINE
        )
        
        for match in patron_linea.finditer(texto):
            descripcion = match.group(1).strip()
            importe_str = match.group(2)
            iva = int(match.group(3))
            
            if len(descripcion) < 3:
                continue
            if any(skip in descripcion for skip in ['TIPO IVA', 'TOTALES', 'FACTURA', 'DATOS', 'FISCALES']):
                continue
            
            importe = self._convertir_europeo(importe_str)
            
            if importe > 0:
                lineas.append({
                    'codigo': '',
                    'articulo': re.sub(r'[|¿¡\[\]{}]', '', descripcion)[:50],
                    'cantidad': 1,
                    'precio_ud': importe,
                    'iva': iva,
                    'base': importe
                })
        
        # Fallback: extraer desde cuadro fiscal
        if not lineas:
            lineas = self._extraer_desde_cuadro_fiscal(texto)
        
        return lineas
    
    def _extraer_desde_cuadro_fiscal(self, texto: str) -> List[Dict]:
        """Extrae desde cuadro fiscal."""
        lineas = []
        cuadro = self._extraer_cuadro_fiscal(texto)
        for item in cuadro:
            lineas.append({
                'codigo': '',
                'articulo': f'COMPRA IVA {item["tipo"]}%',
                'cantidad': 1,
                'precio_ud': item['base'],
                'iva': item['tipo'],
                'base': item['base']
            })
        return lineas
    
    def _extraer_cuadro_fiscal(self, texto: str) -> List[Dict]:
        """Extrae cuadro de IVA."""
        desglose = []
        patron = re.compile(r'(\d+)[,\.]00%\s+(\d+[,\.]\d+)\s+(\d+[,\.]\d+)', re.MULTILINE)
        for match in patron.finditer(texto):
            tipo = int(match.group(1))
            base = self._convertir_europeo(match.group(2))
            cuota = self._convertir_europeo(match.group(3))
            if tipo in [4, 10, 21] and base > 0:
                desglose.append({'tipo': tipo, 'base': base, 'iva': cuota})
        return desglose
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """Extrae el total."""
        if not texto:
            return None
        
        patrones = [
            r'TOTAL\s+FACTURA\s+(\d+[,\.]\d+)',
            r'TOTAL\s+FAÉTURA\s+(\d+[,\.]\d+)',
            r'TOTAL\s+FACT[UÚ]RA\s+(\d+[,\.]\d+)',
            r'TOTAL[:\s]+(\d+[,\.]\d+)\s*€',
        ]
        for patron in patrones:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                return self._convertir_europeo(match.group(1))
        
        # Calcular desde cuadro fiscal
        cuadro = self._extraer_cuadro_fiscal(texto)
        if cuadro:
            return round(sum(d['base'] + d['iva'] for d in cuadro), 2)
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae la fecha."""
        if not texto:
            return None
        
        patron = re.search(r'EMITIDA:?\s*(\d{2}-\d{2}-\d{4})', texto, re.IGNORECASE)
        if patron:
            return patron.group(1).replace('-', '/')
        patron2 = re.search(r'(\d{2}/\d{2}/\d{4})', texto)
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
