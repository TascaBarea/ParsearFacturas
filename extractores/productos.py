"""
Extractores para productos varios.
MOLLETES, ZUBELZU, IBARRAKO, PRODUCTOS ADELL, ECOFICUS, ANA CABALLO, GRUPO CAMPERO
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict
import re


@registrar('MOLLETES', 'MOLLETES ARTESANOS')
class ExtractorMolletes(ExtractorBase):
    nombre = 'MOLLETES ARTESANOS'
    cif = 'B93662708'
    iban = 'ES34 0049 4629 5323 1715 7896'
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.compile(r'^(\d{5})\s+(.+?)(?:\s+-\s+CAD\.?:\s*\d{2}/\d{2}/\d{4})?\s+(\d+)\s+([\d,]+)\s+([\d,]+)\s+[\d,]+\s+([\d,]+)$', re.MULTILINE)
        
        for match in patron.finditer(texto):
            codigo, desc, cajas, uds, precio, importe = match.groups()
            if 'DESCRIPCIÓN' in desc:
                continue
            lineas.append({'codigo': codigo, 'articulo': desc.strip(), 'iva': 4, 'base': self._convertir_importe(importe)})
        return lineas


@registrar('ZUBELZU', 'ZUBELZU PIPARRAK')
class ExtractorZubelzu(ExtractorBase):
    nombre = 'ZUBELZU'
    cif = 'B75079608'
    iban = 'ES61 3035 0141 8214 1001 9635'
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.compile(r'^(.+?)\s+(\d+)\s+([\d,]+)\s+([\d,]+)$', re.MULTILINE)
        
        for match in patron.finditer(texto):
            desc, uds, precio, importe = match.groups()
            if 'DESCRIPCION' in desc.upper() or len(desc.strip()) < 3:
                continue
            lineas.append({'codigo': '', 'articulo': desc.strip(), 'cantidad': int(uds), 'precio_ud': self._convertir_importe(precio), 'iva': 10, 'base': self._convertir_importe(importe)})
        return lineas


@registrar('IBARRAKO PIPARRAK', 'IBARRAKO PIPARRA', 'IBARRAKO')
class ExtractorIbarrako(ExtractorBase):
    nombre = 'IBARRAKO PIPARRAK'
    cif = 'F20532297'
    iban = 'ES69 2095 5081 9010 6181 7077'
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.compile(r'^(\d{2,4})\s+(.+?)\s+(\d+)\s+([\d,]+)\s+([\d,]+)$', re.MULTILINE)
        
        for match in patron.finditer(texto):
            codigo, desc, uds, precio, importe = match.groups()
            if 'DESCRIPCION' in desc.upper():
                continue
            lineas.append({'codigo': codigo, 'articulo': desc.strip(), 'cantidad': int(uds), 'precio_ud': self._convertir_importe(precio), 'iva': 10, 'base': self._convertir_importe(importe)})
        return lineas


@registrar('PRODUCTOS ADELL', 'CROQUELLANAS')
class ExtractorProductosAdell(ExtractorBase):
    nombre = 'PRODUCTOS ADELL'
    cif = 'B12711636'
    iban = 'ES62 3058 7413 2127 2000 8367'
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.compile(r'^(\d{4,6})\s+(.+?)\s+(\d+)\s+([\d,]+)\s+([\d,]+)$', re.MULTILINE)
        
        for match in patron.finditer(texto):
            codigo, desc, uds, precio, importe = match.groups()
            if 'DESCRIPCION' in desc.upper():
                continue
            lineas.append({'codigo': codigo, 'articulo': desc.strip(), 'cantidad': int(uds), 'precio_ud': self._convertir_importe(precio), 'iva': 10, 'base': self._convertir_importe(importe)})
        return lineas


@registrar('ECOFICUS')
class ExtractorEcoficus(ExtractorBase):
    nombre = 'ECOFICUS'
    cif = 'B10214021'
    iban = 'ES23 2103 7136 4700 3002 4378'
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.compile(r'^(.+?)\s+(\d+)\s+([\d,]+)\s+([\d,]+)$', re.MULTILINE)
        
        for match in patron.finditer(texto):
            desc, uds, precio, importe = match.groups()
            if 'DESCRIPCION' in desc.upper() or len(desc.strip()) < 3:
                continue
            lineas.append({'codigo': '', 'articulo': desc.strip(), 'cantidad': int(uds), 'precio_ud': self._convertir_importe(precio), 'iva': 10, 'base': self._convertir_importe(importe)})
        return lineas


@registrar('ANA CABALLO', 'ANA CABALLO VERMOUTH')
class ExtractorAnaCaballo(ExtractorBase):
    nombre = 'ANA CABALLO'
    cif = 'B87925970'
    iban = 'ES75 2100 1360 2202 0006 0355'
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.compile(r'^(.+?)\s+(\d+)\s+([\d,]+)\s+([\d,]+)$', re.MULTILINE)
        
        for match in patron.finditer(texto):
            desc, uds, precio, importe = match.groups()
            if 'DESCRIPCION' in desc.upper() or len(desc.strip()) < 3:
                continue
            lineas.append({'codigo': '', 'articulo': desc.strip(), 'cantidad': int(uds), 'precio_ud': self._convertir_importe(precio), 'iva': 21, 'base': self._convertir_importe(importe)})
        return lineas


@registrar('GRUPO TERRITORIO CAMPERO', 'TERRITORIO CAMPERO', 'GRUPO CAMPERO')
class ExtractorGrupoCampero(ExtractorBase):
    nombre = 'GRUPO CAMPERO'
    cif = 'B16690141'
    iban = 'ES71 0049 3739 4027 1401 6466'
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.compile(r'^(\d{4,6})\s+(.+?)\s+(\d+)\s+([\d,]+)\s+([\d,]+)$', re.MULTILINE)
        
        for match in patron.finditer(texto):
            codigo, desc, uds, precio, importe = match.groups()
            if 'DESCRIPCION' in desc.upper():
                continue
            lineas.append({'codigo': codigo, 'articulo': desc.strip(), 'cantidad': int(uds), 'precio_ud': self._convertir_importe(precio), 'iva': 10, 'base': self._convertir_importe(importe)})
        return lineas
