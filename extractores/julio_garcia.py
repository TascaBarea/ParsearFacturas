"""
Extractor para JULIO GARCIA VIVAS (Ay Madre!)

Verdulería del Mercado de San Fernando (Embajadores).
NIF: 02869898G

Formato factura (pdfplumber):
DESCRIPCIÓN                              CANTIDAD  PRECIO  TOTAL
ALBARÁN Nº 28706692 DE FECHA 06/11/2025                    10,64
ALBARÁN Nº 28707466 DE FECHA 11/11/2025                    1,73
...

Cuadro fiscal:
BASE IMPONIBLE  I.V.A.    R.E.
65,87           4%  2,65  0,5%  0,00
                10% 1,4%
                21% 5,2%

IVA: Principalmente 4% (verduras), ocasionalmente 10% o 21%
Categoría fija: GENERICO PARA VERDURAS
NOTA: Se genera UNA línea por tipo de IVA con artículo "VERDURAS AY MADRE"

Creado: 26/12/2025
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar('JULIO GARCIA VIVAS', 'GARCIA VIVAS JULIO', 'JULIO GARCIA', 'AY MADRE')
class ExtractorJulioGarcia(ExtractorBase):
    """Extractor para facturas de JULIO GARCIA VIVAS."""
    
    nombre = 'JULIO GARCIA VIVAS'
    cif = '02869898G'
    iban = ''  # Pendiente
    metodo_pdf = 'pdfplumber'
    categoria_fija = 'GENERICO PARA VERDURAS'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae UNA línea por tipo de IVA del cuadro fiscal.
        
        Cuadro fiscal:
        BASE IMPONIBLE  I.V.A.    R.E.
        65,87           4%  2,65  0,5%  0,00
                        10% 1,4%
                        21% 5,2%
        """
        lineas = []
        
        # Buscar el cuadro fiscal con formato:
        # BASE_IMPONIBLE   4%  CUOTA_4%  0,5%  0,00
        #                  10% R.E.10%
        #                  21% R.E.21%
        
        # Patrón para IVA 4% (línea principal con base)
        match_4 = re.search(
            r'(\d+[.,]\d{2})\s+4%\s+(\d+[.,]\d{2})',
            texto
        )
        
        if match_4:
            base = self._convertir_europeo(match_4.group(1))
            if base > 0:
                lineas.append({
                    'codigo': '',
                    'articulo': 'VERDURAS AY MADRE',
                    'cantidad': 1,
                    'precio_ud': round(base, 2),
                    'iva': 4,
                    'base': round(base, 2),
                    'categoria': self.categoria_fija
                })
        
        # Buscar si hay IVA 10% con base
        # Formato alternativo cuando hay múltiples IVAs
        match_10 = re.search(
            r'(\d+[.,]\d{2})\s+10%\s+(\d+[.,]\d{2})',
            texto
        )
        
        if match_10:
            base = self._convertir_europeo(match_10.group(1))
            if base > 0:
                lineas.append({
                    'codigo': '',
                    'articulo': 'VERDURAS AY MADRE',
                    'cantidad': 1,
                    'precio_ud': round(base, 2),
                    'iva': 10,
                    'base': round(base, 2),
                    'categoria': self.categoria_fija
                })
        
        # Buscar si hay IVA 21% con base
        match_21 = re.search(
            r'(\d+[.,]\d{2})\s+21%\s+(\d+[.,]\d{2})',
            texto
        )
        
        if match_21:
            base = self._convertir_europeo(match_21.group(1))
            if base > 0:
                lineas.append({
                    'codigo': '',
                    'articulo': 'VERDURAS AY MADRE',
                    'cantidad': 1,
                    'precio_ud': round(base, 2),
                    'iva': 21,
                    'base': round(base, 2),
                    'categoria': self.categoria_fija
                })
        
        # Si no encontramos el cuadro fiscal, intentar extraer la base total
        if not lineas:
            match_total_base = re.search(
                r'TOTAL\s+BASE\s+IMPONIBLE\s+(\d+[.,]\d{2})',
                texto,
                re.IGNORECASE
            )
            if match_total_base:
                base = self._convertir_europeo(match_total_base.group(1))
                if base > 0:
                    lineas.append({
                        'codigo': '',
                        'articulo': 'VERDURAS AY MADRE',
                        'cantidad': 1,
                        'precio_ud': round(base, 2),
                        'iva': 4,  # IVA por defecto para verduras
                        'base': round(base, 2),
                        'categoria': self.categoria_fija
                    })
        
        return lineas
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo a float."""
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
        """Extrae total de la factura."""
        # Formato: "TOTAL FACTURA 68,52"
        m = re.search(r'TOTAL\s*FACTURA\s*(\d+[.,]\d{2})', texto, re.IGNORECASE)
        if m:
            return self._convertir_europeo(m.group(1))
        
        # Alternativa: última línea del cuadro "68,52"
        m = re.search(r'(\d+[.,]\d{2})\s*$', texto.strip())
        if m:
            return self._convertir_europeo(m.group(1))
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        # Formato: "FECHA: 30/11/2025"
        m = re.search(r'FECHA[:\s]+(\d{2})/(\d{2})/(\d{4})', texto, re.IGNORECASE)
        if m:
            return f"{m.group(1)}/{m.group(2)}/{m.group(3)}"
        
        return None
