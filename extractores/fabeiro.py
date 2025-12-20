"""
Extractor para FABEIRO S.L. (ibéricos y quesos)

Formato de factura:
- Tabla con: Artículo | Concepto | I.V.A. | Cantidad | P. Unidad | De. | Importe
- Desglose fiscal al final con BASE IMPONIBLE y TOTAL
- Total en formato europeo: 1.119,70 € (punto miles, coma decimal)
- CIF: B-79/992079 (formato especial con /)

Actualizado: 18/12/2025 - pdfplumber + formato europeo
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict
import re


@registrar('FABEIRO', 'FABEIRO S.L', 'FABEIRO SL', 'FABEIRO IBERICO', 'FABEIROIBERICO')
class ExtractorFabeiro(ExtractorBase):
    nombre = 'FABEIRO'
    cif = 'B79992079'
    iban = 'ES21 0182 5906 8702 0151 7643'
    metodo_pdf = 'pdfplumber'
    
    def _convertir_importe_fabeiro(self, texto: str) -> float:
        """
        Convierte importes en formato FABEIRO (europeo).
        Ejemplos: '1.119,70' -> 1119.70, '288,00' -> 288.00
        """
        if not texto:
            return 0.0
        
        texto = texto.strip().replace('€', '').replace(' ', '')
        
        # Si tiene punto Y coma, el punto es separador de miles
        if '.' in texto and ',' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            texto = texto.replace(',', '.')
        
        try:
            return float(texto)
        except:
            return 0.0
    
    def extraer_total(self, texto: str) -> float:
        """Extrae el total de la factura FABEIRO."""
        patron = re.search(r'TOTAL\s+([\d.,]+)\s*€', texto, re.IGNORECASE)
        if patron:
            return self._convertir_importe_fabeiro(patron.group(1))
        
        patron2 = re.search(r'TOTAL\s+([\d.,]+)', texto, re.IGNORECASE)
        if patron2:
            return self._convertir_importe_fabeiro(patron2.group(1))
        
        return None
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de factura FABEIRO.
        
        Formato tabla:
        CODIGO  DESCRIPCION  IVA%  CANTIDAD  P.UNIDAD  DESC  IMPORTE
        CA0005  ANCHOA OLIVA...  10,00%  12,0000  24,0000      288,00
        """
        lineas = []
        
        # Patrón para líneas de producto
        patron = re.compile(
            r'^([A-Z]{2}\d{4})\s+'           # Código: CA0005, SA0011, AL0007, ZA0010, LE0003
            r'(.+?)\s+'                       # Descripción
            r'(\d{1,2}),00%\s+'               # IVA: 10,00% o 4,00%
            r'([\d,]+)\s+'                    # Cantidad: 12,0000 o 3,1600
            r'([\d,]+)\s+'                    # Precio unitario: 24,0000
            r'([\d,]+)$',                     # Importe: 288,00
            re.MULTILINE
        )
        
        for match in patron.finditer(texto):
            codigo = match.group(1)
            desc = match.group(2).strip()
            iva = int(match.group(3))
            cantidad = self._convertir_importe(match.group(4))
            precio = self._convertir_importe(match.group(5))
            importe = self._convertir_importe(match.group(6))
            
            # Limpiar descripción (quitar códigos de lote al final)
            desc_limpia = re.sub(r'\s*-\s*\d+[A-Z]*\s*$', '', desc)
            desc_limpia = re.sub(r'\s*-\s*[A-Z0-9]+\s*$', '', desc_limpia)
            
            if importe > 0:
                lineas.append({
                    'codigo': codigo,
                    'articulo': desc_limpia,
                    'cantidad': cantidad,
                    'precio_ud': precio,
                    'iva': iva,
                    'base': round(importe, 2)
                })
        
        # Si no encontramos líneas, usar desglose fiscal
        if not lineas:
            lineas = self._extraer_desde_desglose(texto)
        
        return lineas
    
    def _extraer_desde_desglose(self, texto: str) -> List[Dict]:
        """
        Extrae líneas desde el desglose fiscal.
        Formato: BASE IVA% CUOTA
        Ejemplo: 1.291,12 10% 129,11
                 161,65 4% 6,47
        """
        lineas = []
        
        patron = re.compile(r'([\d.,]+)\s+(\d{1,2})%\s+([\d.,]+)')
        
        for match in patron.finditer(texto):
            base = self._convertir_importe_fabeiro(match.group(1))
            iva = int(match.group(2))
            cuota = self._convertir_importe_fabeiro(match.group(3))
            
            # Validar: cuota ≈ base × iva / 100 (tolerancia 0.15€)
            cuota_esperada = base * iva / 100
            if base > 0 and iva in [4, 10, 21] and abs(cuota - cuota_esperada) < 0.15:
                lineas.append({
                    'codigo': '',
                    'articulo': f'PRODUCTOS IVA {iva}%',
                    'iva': iva,
                    'base': round(base, 2)
                })
        
        return lineas
