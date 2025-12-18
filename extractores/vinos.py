"""
Extractores para facturas de vinos.
ARGANZA, PURISIMA, CVNE, MUÑOZ MARTIN
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict
import re


@registrar('VINOS DE ARGANZA', 'ARGANZA')
class ExtractorArganza(ExtractorBase):
    nombre = 'VINOS DE ARGANZA'
    cif = 'B24416869'
    iban = 'ES92 0081 5385 6500 0121 7327'
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron_ocr = re.compile(r'^([A-Z][A-Z0-9]{1,5})\s+(.+?)\s+(\d{1,3}[,\.]\d{2})$', re.MULTILINE)
        
        for match in patron_ocr.finditer(texto):
            codigo = match.group(1)
            desc_raw = match.group(2)
            importe = self._convertir_importe(match.group(3))
            desc = re.sub(r'[\d,\.]+\s+[\d,\.]+\s+[\d,\.]+$', '', desc_raw).strip()
            
            if 'DESCRIPCION' in desc.upper() or codigo in ['IMPORTE', 'CODIGO', 'TOTAL']:
                continue
            
            lineas.append({'codigo': codigo, 'articulo': desc[:50], 'iva': 21, 'base': importe})
        return lineas


@registrar('LA PURISIMA', 'PURISIMA')
class ExtractorPurisima(ExtractorBase):
    nombre = 'LA PURISIMA'
    cif = 'F30005193'
    iban = 'ES78 0081 0259 1000 0184 4495'
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.compile(r'^(\d{9})([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ\s\d.]+?)\s+(\d+)\s+([\d,]+)\s+([\d,]+)$', re.MULTILINE)
        
        for match in patron.finditer(texto):
            codigo, desc, uds, precio, importe = match.groups()
            if 'DESCRIPCIÓN' in desc or 'Lote:' in desc:
                continue
            lineas.append({'codigo': codigo, 'articulo': desc.strip(), 'iva': 21, 'base': self._convertir_importe(importe)})
        return lineas


@registrar('CVNE', 'COMPAÑIA VINICOLA')
class ExtractorCvne(ExtractorBase):
    nombre = 'CVNE'
    cif = 'A48002893'
    iban = 'ES09 2100 9144 3102 0002 5176'
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.compile(r'^(\d{6,8})\s+(.+?)\s+(\d+)\s+([\d,]+)\s+([\d,]+)$', re.MULTILINE)
        
        for match in patron.finditer(texto):
            codigo, desc, uds, precio, importe = match.groups()
            if 'DESCRIPCION' in desc.upper():
                continue
            lineas.append({'codigo': codigo, 'articulo': desc.strip(), 'cantidad': int(uds), 'precio_ud': self._convertir_importe(precio), 'iva': 21, 'base': self._convertir_importe(importe)})
        return lineas


@registrar('BODEGAS MUÑOZ MARTIN', 'MUÑOZ MARTIN')
class ExtractorMunozMartin(ExtractorBase):
    nombre = 'BODEGAS MUÑOZ MARTIN'
    cif = 'E83182683'
    iban = 'ES62 0049 5184 11 2016002766'
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.compile(r'(\d+)\s+([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ\s]+?)\s+(\d+)\s+([\d,]+)\s+([\d,]+)', re.MULTILINE)
        
        for match in patron.finditer(texto):
            codigo, desc, uds, precio, importe = match.groups()
            if 'CANTIDAD' in desc.upper() or 'DESCRIPCION' in desc.upper():
                continue
            lineas.append({'codigo': codigo, 'articulo': desc.strip(), 'cantidad': int(uds), 'precio_ud': self._convertir_importe(precio), 'iva': 21, 'base': self._convertir_importe(importe)})
        return lineas
