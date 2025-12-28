"""
Extractor para DISTRIBUCIONES LAVAPIES S.COOP.MAD.

Distribuidor de bebidas, refrescos, aguas, zumos.
CIF: F88424072
IBAN: ES39 3035 0376 14 3760011213

Formato factura:
BASE IMP. AL 10% 71,76 IVA 10% 7,18
BASE IMP. AL 21% 5,22 IVA 21% 1,10
REC.DE EQUIV. 1,4% (no incluido en total)
REC.DE EQUIV. 5,2% (no incluido en total)
TOTAL 84,73 €

NOTA: El total NO incluye el Recargo de Equivalencia.
Total = Base10 + IVA10 + Base21 + IVA21

IVA:
- 10%: Bebidas no alcohólicas (refrescos, zumos, aguas)
- 21%: Otros (gaseosas, tónicas con alcohol, etc.)

Creado: 19/12/2025
Corregido: 26/12/2025 - Símbolo € y cálculo sin RE
Validado: 10/10 facturas (2T25-4T25)
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re
import pdfplumber


@registrar('DISTRIBUCIONES LAVAPIES', 'LAVAPIES')
class ExtractorLavapies(ExtractorBase):
    """Extractor para facturas de Distribuciones Lavapies."""
    
    nombre = 'DISTRIBUCIONES LAVAPIES'
    cif = 'F88424072'
    iban = 'ES39 3035 0376 14 3760011213'
    metodo_pdf = 'pdfplumber'
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo a float."""
        if not texto:
            return 0.0
        texto = str(texto).strip().replace('€', '').replace(' ', '')
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
        Extrae líneas desde el cuadro fiscal.
        
        Formato:
        BASE IMP. AL 10% 71,76 IVA 10% 7,18
        BASE IMP. AL 21% 5,22 IVA 21% 1,10
        
        NOTA IMPORTANTE: Las etiquetas del PDF a veces están INTERCAMBIADAS.
        Por eso calculamos el IVA real dividiendo cuota/base.
        
        NOTA: El Recargo de Equivalencia NO se incluye en el total.
        """
        lineas = []
        
        # Extraer base e IVA etiquetado como 10%
        m10 = re.search(
            r'BASE\s+IMP\.\s+AL\s+10%\s+([\d,]+)\s+IVA\s+10%\s+([\d,]+)',
            texto
        )
        
        if m10:
            base = self._convertir_europeo(m10.group(1))
            cuota = self._convertir_europeo(m10.group(2))
            if base > 0:
                # Calcular IVA real
                iva_real = round(cuota / base * 100)
                iva_final = iva_real if iva_real in [10, 21] else 10
                
                lineas.append({
                    'codigo': '',
                    'articulo': 'BEBIDAS Y REFRESCOS' if iva_final == 10 else 'BEBIDAS 21%',
                    'cantidad': 1,
                    'precio_ud': round(base, 2),
                    'iva': iva_final,
                    'base': round(base, 2)
                })
        
        # Extraer base e IVA etiquetado como 21%
        m21 = re.search(
            r'BASE\s+IMP\.\s+AL\s+21%\s+([\d,]+)\s+IVA\s+21%\s+([\d,]+)',
            texto
        )
        
        if m21:
            base = self._convertir_europeo(m21.group(1))
            cuota = self._convertir_europeo(m21.group(2))
            if base > 0:
                # Calcular IVA real
                iva_real = round(cuota / base * 100)
                iva_final = iva_real if iva_real in [10, 21] else 21
                
                lineas.append({
                    'codigo': '',
                    'articulo': 'BEBIDAS 21%' if iva_final == 21 else 'BEBIDAS Y REFRESCOS',
                    'cantidad': 1,
                    'precio_ud': round(base, 2),
                    'iva': iva_final,
                    'base': round(base, 2)
                })
        
        return lineas
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """
        Extrae el total de la factura.
        
        Métodos (en orden de prioridad):
        1. TOTAL directo: TOTAL 84,73 €
        2. Vencimiento: 04/12/25 330,52 € 330,52 €
        3. Calcular desde bases
        """
        # Método 1: TOTAL directo (más fiable)
        m_total = re.search(r'TOTAL\s+([\d,]+)\s*€', texto, re.IGNORECASE)
        if m_total:
            total = self._convertir_europeo(m_total.group(1))
            if total > 0:
                return total
        
        # Método 2: Buscar en vencimiento (fecha + importe + importe)
        m_venc = re.search(
            r'(\d{2}/\d{2}/\d{2})\s+([\d,]+)\s*€\s+([\d,]+)\s*€',
            texto
        )
        if m_venc:
            return self._convertir_europeo(m_venc.group(3))
        
        # Método 3: Calcular desde bases (usa IVA real)
        lineas = self.extraer_lineas(texto)
        if lineas:
            return round(sum(l['base'] * (1 + l['iva']/100) for l in lineas), 2)
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """
        Extrae fecha de la factura.
        
        Formato: 07/03/25 250150 (fecha + nº documento)
        """
        # Buscar fecha al inicio de línea seguida de número de documento
        patron = re.search(r'^(\d{2})/(\d{2})/(\d{2})\s+\d{6}', texto, re.MULTILINE)
        if patron:
            dia, mes, anio = patron.groups()
            anio_completo = f"20{anio}" if int(anio) < 50 else f"19{anio}"
            return f"{dia}/{mes}/{anio_completo}"
        
        # Alternativo: buscar FECHA
        patron2 = re.search(r'FECHA[^\d]*(\d{2})/(\d{2})/(\d{2})', texto)
        if patron2:
            dia, mes, anio = patron2.groups()
            return f"{dia}/{mes}/20{anio}"
        
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae número de factura/documento."""
        m = re.search(r'(\d{2})/(\d{2})/(\d{2})\s+(\d{6})', texto)
        if m:
            return m.group(4)
        return None
