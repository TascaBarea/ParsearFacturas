"""
Extractor para JIMELUZ EMPRENDEDORES S.L. (OCR)

Frutería con tickets escaneados.
CIF: B84527068
IBAN: (pago efectivo)

Formato factura:
- Tickets escaneados (requiere OCR)
- Tabla IVA al final del ticket
- IVA 4%, 10% o 21%

Estrategia v3.57:
1. Extrae líneas individuales con patrón flexible (tolera OCR malo)
2. Usa tabla IVA como fallback cuando OCR es muy malo
3. Fallback a TOTAL FACTURA si todo falla

Creado: 18/12/2025
Migrado de: migracion_historico_2025_v3_57.py (líneas 6412-6555)
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict
import re


@registrar('JIMELUZ', 'JIMELUZ EMPRENDEDORES')
class ExtractorJimeluz(ExtractorBase):
    """Extractor para tickets OCR de JIMELUZ."""
    
    nombre = 'JIMELUZ'
    cif = 'B84527068'
    iban = ''  # Pago efectivo
    metodo_pdf = 'ocr'  # Siempre OCR
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de tickets JIMELUZ (OCR).
        
        Doble estrategia:
        1. Extraer líneas individuales
        2. Usar tabla IVA como fallback
        """
        lineas = []
        
        # === MÉTODO 1: Extraer líneas individuales ===
        
        # Buscar zona de artículos
        inicio = re.search(r'CANT\.?\s*DESCRIPCI[OÓ]N', texto, re.IGNORECASE)
        fin = re.search(r'TOTAL\s*COMPRA', texto, re.IGNORECASE)
        
        if inicio and fin:
            zona_articulos = texto[inicio.end():fin.start()]
        else:
            zona_articulos = texto
        
        # Patrón flexible para tolerar errores OCR
        patron_linea = re.compile(
            r'^[1|lI\d]{0,2}\s*'                 # Cantidad (puede faltar)
            r'(.+?)\s+'                          # Descripción
            r'(4|10|21)[,\.]\d{2}\.?\s*'         # IVA
            r',?(\d{1,3}[,\.]\d{1,2})',          # Importe
            re.MULTILINE
        )
        
        for match in patron_linea.finditer(zona_articulos):
            desc, iva, importe_raw = match.groups()
            
            # Limpiar descripción
            desc_limpia = re.sub(r'[£\*\'\"\|]+', '', desc).strip()
            desc_limpia = re.sub(r'\s+', ' ', desc_limpia)
            
            # Limpiar importe
            importe_limpio = importe_raw.replace(',', '.').replace(' ', '')
            
            try:
                importe = float(importe_limpio)
                iva_int = int(iva)
                
                # El importe es CON IVA, calcular base
                base_sin_iva = importe / (1 + iva_int / 100)
                
                lineas.append({
                    'codigo': '',
                    'articulo': desc_limpia,
                    'iva': iva_int,
                    'base': round(base_sin_iva, 2)
                })
            except ValueError:
                continue
        
        # === MÉTODO 2: Tabla IVA como fallback ===
        
        tabla_iva = {}
        patron_tabla = re.compile(
            r'(4|10|21)[,\.]\d{2}%?\s+'
            r'\(?(\d{1,3}[,\.]\d{2})\)?\s+'      # BASE
            r'\(?(\d{1,3}[,\.]\d{2})\)?\s+'      # CUOTA
            r'(?:\d\s+)?'                         # RUIDO OCR
            r'\(?(\d{1,3}[,\.]\d{2})\)?'         # TOTAL
        )
        
        for match in patron_tabla.finditer(texto):
            iva, base, cuota, total = match.groups()
            try:
                tabla_iva[int(iva)] = {
                    'base': float(base.replace(',', '.')),
                    'cuota': float(cuota.replace(',', '.')),
                    'total': float(total.replace(',', '.'))
                }
            except ValueError:
                continue
        
        # Si no hay líneas pero sí tabla IVA
        if not lineas and tabla_iva:
            for iva, datos in sorted(tabla_iva.items()):
                if datos['total'] > 0:
                    lineas.append({
                        'codigo': '',
                        'articulo': f'COMPRA JIMELUZ (IVA {iva}%)',
                        'iva': iva,
                        'base': datos['base']
                    })
        
        # Si hay líneas pero no cuadran con tabla IVA
        elif lineas and tabla_iva:
            suma_lineas = sum(l['base'] * (1 + l['iva']/100) for l in lineas)
            suma_tabla = sum(d['total'] for d in tabla_iva.values())
            
            if suma_tabla > 0 and abs(suma_lineas - suma_tabla) / suma_tabla > 0.05:
                lineas = []
                for iva, datos in sorted(tabla_iva.items()):
                    if datos['total'] > 0:
                        lineas.append({
                            'codigo': '',
                            'articulo': f'COMPRA JIMELUZ (IVA {iva}%)',
                            'iva': iva,
                            'base': datos['base']
                        })
        
        # === MÉTODO 3: Fallback a TOTAL FACTURA ===
        
        if not lineas:
            total_match = re.search(
                r'TOTAL\s*(?:FACTURA|PAGADO)\s*[\|:\s]*(\d{1,3}[,\.]\d{2})',
                texto, re.IGNORECASE
            )
            if total_match:
                total = float(total_match.group(1).replace(',', '.'))
                if 0 < total < 200:
                    base_estimada = total / 1.10  # ~10% IVA promedio
                    lineas.append({
                        'codigo': '',
                        'articulo': 'COMPRA JIMELUZ (OCR sin desglose)',
                        'iva': 10,
                        'base': round(base_estimada, 2)
                    })
        
        return lineas
