"""
Extractores para distribuidores y carnes.
LAVAPIES, FABEIRO, SERRIN, MRM, DISBER, LIDL, MAKRO
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict
import re


@registrar('LAVAPIES', 'DISTRIBUCIONES LAVAPIES')
class ExtractorLavapies(ExtractorBase):
    nombre = 'DISTRIBUCIONES LAVAPIES'
    cif = 'F88424072'
    iban = 'ES39 3035 0376 1437 6001 1213'
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.compile(r'^(\d{4,6})\s+(.+?)\s+(\d+)\s+([\d,]+)\s+([\d,]+)\s+(\d+)$', re.MULTILINE)
        
        for match in patron.finditer(texto):
            codigo, desc, uds, precio, importe, iva = match.groups()
            if 'DESCRIPCION' in desc.upper():
                continue
            lineas.append({'codigo': codigo, 'articulo': desc.strip(), 'cantidad': int(uds), 'precio_ud': self._convertir_importe(precio), 'iva': int(iva), 'base': self._convertir_importe(importe)})
        return lineas


@registrar('FABEIRO')
class ExtractorFabeiro(ExtractorBase):
    nombre = 'FABEIRO'
    cif = 'B79992079'
    iban = 'ES70 0182 1292 2202 0150 5065'
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.compile(r'^(\d{4,6})\s+(.+?)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)$', re.MULTILINE)
        
        for match in patron.finditer(texto):
            codigo, desc, cantidad, precio, importe = match.groups()
            if 'DESCRIPCION' in desc.upper():
                continue
            lineas.append({'codigo': codigo, 'articulo': desc.strip(), 'cantidad': self._convertir_importe(cantidad), 'precio_ud': self._convertir_importe(precio), 'iva': 10, 'base': self._convertir_importe(importe)})
        return lineas


@registrar('SERRIN', 'SERRÍN', 'SERRIN NO CHAN')
class ExtractorSerrin(ExtractorBase):
    nombre = 'SERRIN'
    cif = 'B87214755'
    iban = 'ES88 0049 6650 1329 1001 8834'
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.compile(r'^(\d{4,6})\s+(.+?)\s+(\d+)\s+([\d,]+)\s+([\d,]+)$', re.MULTILINE)
        
        for match in patron.finditer(texto):
            codigo, desc, uds, precio, importe = match.groups()
            if 'DESCRIPCION' in desc.upper():
                continue
            lineas.append({'codigo': codigo, 'articulo': desc.strip(), 'cantidad': int(uds), 'precio_ud': self._convertir_importe(precio), 'iva': 21, 'base': self._convertir_importe(importe)})
        return lineas


@registrar('MRM', 'MRM-2', 'INDUSTRIAS CARNICAS MRM')
class ExtractorMRM(ExtractorBase):
    nombre = 'MRM'
    cif = 'A80280845'
    iban = 'ES28 2100 8662 5702 0004 8824'
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.compile(r'^(\d{4,8})\s+(.+?)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)$', re.MULTILINE)
        
        for match in patron.finditer(texto):
            codigo, desc, cantidad, precio, importe = match.groups()
            if 'DESCRIPCION' in desc.upper():
                continue
            lineas.append({'codigo': codigo, 'articulo': desc.strip(), 'cantidad': self._convertir_importe(cantidad), 'precio_ud': self._convertir_importe(precio), 'iva': 10, 'base': self._convertir_importe(importe)})
        return lineas


@registrar('DISBER', 'GRUPO DISBER')
class ExtractorDisber(ExtractorBase):
    nombre = 'DISBER'
    cif = 'B46144424'
    iban = 'ES39 2100 8617 1502 0002 4610'
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.compile(r'^(\d{4,8})\s+(.+?)\s+(\d+)\s+([\d,]+)\s+([\d,]+)$', re.MULTILINE)
        
        for match in patron.finditer(texto):
            codigo, desc, uds, precio, importe = match.groups()
            if 'DESCRIPCION' in desc.upper():
                continue
            lineas.append({'codigo': codigo, 'articulo': desc.strip(), 'cantidad': int(uds), 'precio_ud': self._convertir_importe(precio), 'iva': 10, 'base': self._convertir_importe(importe)})
        return lineas


@registrar('LIDL')
class ExtractorLidl(ExtractorBase):
    nombre = 'LIDL'
    cif = 'A60195278'
    iban = ''
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.compile(r'^(\d{1,2})[,\.](\d{2})%\s+([\d,]+)\s+([\d,]+)\s+[\d,]+\s+([\d,]+)', re.MULTILINE)
        
        for match in patron.finditer(texto):
            iva_ent, iva_dec, base, cuota, total = match.groups()
            iva = int(iva_ent)
            base_val = self._convertir_importe(base)
            if base_val > 0:
                lineas.append({'codigo': 'LIDL', 'articulo': f'COMPRA LIDL IVA {iva}%', 'iva': iva, 'base': base_val})
        return lineas


@registrar('MAKRO')
class ExtractorMakro(ExtractorBase):
    nombre = 'MAKRO'
    cif = 'A28647451'
    iban = ''
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.compile(r'(\d{1,2})%\s+([\d,]+)\s+([\d,]+)', re.MULTILINE)
        
        for match in patron.finditer(texto):
            iva, base, cuota = match.groups()
            iva_int = int(iva)
            base_val = self._convertir_importe(base)
            if base_val > 0 and iva_int in [4, 10, 21]:
                lineas.append({'codigo': 'MAKRO', 'articulo': f'COMPRA MAKRO IVA {iva_int}%', 'iva': iva_int, 'base': base_val})
        return lineas
