"""
Extractor para ECOMS SUPERMARKET / DIA.
CIF: B72738602 | Pago: Tarjeta
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict
import re


@registrar('ECOMS', 'ECOMS SUPERMARKET', 'DIA')
class ExtractorEcoms(ExtractorBase):
    nombre = 'ECOMS SUPERMARKET'
    cif = 'B72738602'
    iban = ''
    metodo_pdf = 'ocr'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        texto_upper = texto.upper()
        idx_desglose = texto_upper.find('TIPO IVA')
        if idx_desglose < 0:
            idx_desglose = texto_upper.find('DESGLOSE')
        
        if idx_desglose >= 0:
            seccion = texto[idx_desglose:idx_desglose+400]
            patron_ocr = re.compile(r'(\d{1,2})[,\.]00%\s+(\d{1,2}[,\.:\d]{2,4})\s')
            
            for m in patron_ocr.finditer(seccion):
                iva = int(m.group(1))
                base_raw = m.group(2)
                base_clean = re.sub(r'[:\.]', ',', base_raw)
                if base_clean.count(',') > 1:
                    parts = base_clean.rsplit(',', 1)
                    base_clean = parts[0].replace(',', '') + ',' + parts[1]
                
                try:
                    base = float(base_clean.replace(',', '.'))
                    if 0.05 < base < 500 and iva in [4, 10, 21]:
                        lineas.append({
                            'codigo': 'ECOMS',
                            'articulo': f'COMPRA ECOMS/DIA IVA {iva}%',
                            'iva': iva,
                            'base': round(base, 2)
                        })
                except:
                    continue
        
        if not lineas:
            patron_dia = re.compile(r'[ABC]\s+(\d{1,2})%\s+([\d,]+)\s*€')
            for m in patron_dia.finditer(texto):
                iva = int(m.group(1))
                base = self._convertir_importe(m.group(2))
                if base > 0 and iva in [4, 10, 21]:
                    lineas.append({
                        'codigo': 'ECOMS',
                        'articulo': f'COMPRA ECOMS/DIA IVA {iva}%',
                        'iva': iva,
                        'base': round(base, 2)
                    })
        
        return lineas
