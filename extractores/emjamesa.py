"""
Extractor para EMJAMESA S.L. (Ibéricos).
CIF: B37352077 | IBAN: ES08 3016 0206 5221 8503 2527
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict
import re


@registrar('EMJAMESA')
class ExtractorEmjamesa(ExtractorBase):
    nombre = 'EMJAMESA'
    cif = 'B37352077'
    iban = 'ES08 3016 0206 5221 8503 2527'
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        
        # Preprocesar: unir líneas partidas
        lineas_texto = texto.split('\n')
        texto_unido = []
        i = 0
        while i < len(lineas_texto):
            linea = lineas_texto[i].strip()
            if re.match(r'^\d{1,4}\s+[A-Z]', linea):
                if re.search(r'\d+[.,]\d{2}\s*€(\s+\d+)?$', linea):
                    texto_unido.append(linea)
                else:
                    linea_completa = linea
                    j = i + 1
                    while j < len(lineas_texto):
                        sig = lineas_texto[j].strip()
                        if sig.startswith('Lote:') or sig.startswith('ALBARÁN') or re.match(r'^\d{1,4}\s+[A-Z]', sig):
                            break
                        linea_completa += ' ' + sig
                        if re.search(r'\d+[.,]\d{2}\s*€(\s+\d+)?$', linea_completa):
                            i = j
                            break
                        j += 1
                    texto_unido.append(linea_completa)
            else:
                texto_unido.append(linea)
            i += 1
        
        texto_procesado = '\n'.join(texto_unido)
        
        # Patrón CON columna IVA
        patron_con_iva = re.compile(
            r'^(\d{1,4})\s+(.+?)\s+(\d+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s*€\s+(\d+)$',
            re.MULTILINE
        )
        # Patrón SIN columna IVA
        patron_sin_iva = re.compile(
            r'^(\d{1,4})\s+(.+?)\s+(\d+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s*€$',
            re.MULTILINE
        )
        
        matches_con_iva = list(patron_con_iva.finditer(texto_procesado))
        matches_sin_iva = list(patron_sin_iva.finditer(texto_procesado))
        
        if len(matches_con_iva) >= len(matches_sin_iva):
            for match in matches_con_iva:
                codigo, desc, uds, kilos, precio_str, importe_str, iva_str = match.groups()
                desc = re.sub(r'\s*Lote:\s*\S+', '', desc).strip()
                lineas.append({
                    'codigo': codigo,
                    'articulo': desc.strip(),
                    'iva': int(iva_str),
                    'base': self._convertir_importe(importe_str)
                })
        else:
            for match in matches_sin_iva:
                codigo, desc, uds, kilos, precio_str, importe_str = match.groups()
                desc = re.sub(r'\s*Lote:\s*\S+', '', desc).strip()
                desc = re.sub(r'\s+[A-Z]{2,4}[-]?\d{4}$', '', desc).strip()
                iva = 21 if codigo == '01' else 10
                lineas.append({
                    'codigo': codigo,
                    'articulo': desc.strip(),
                    'iva': iva,
                    'base': self._convertir_importe(importe_str)
                })
        
        return lineas
