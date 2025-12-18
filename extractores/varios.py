"""
Extractores varios restantes.
MARITA COSTA, PILAR RODRIGUEZ, PANIFIESTO, JULIO GARCIA VIVAS, LA BARRA DULCE, 
PORVAZ, MARTIN ABENZA, CARRASCAL, BIELLEBI, FERRIOL, ABBATI, MIGUEZ CAL, 
ROSQUILLERIA, MANIPULADOS ABELLAN, PC COMPONENTES, OPENAI, AMAZON
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict
import re


@registrar('MARITA COSTA')
class ExtractorMaritaCosta(ExtractorBase):
    nombre = 'MARITA COSTA'
    cif = '48207369J'
    iban = 'ES08 0182 7036 0902 0151 9833'
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


@registrar('PILAR RODRIGUEZ', 'EL MAJADAL', 'HUEVOS EL MAJADAL')
class ExtractorPilarRodriguez(ExtractorBase):
    nombre = 'PILAR RODRIGUEZ'
    cif = '06582655D'
    iban = 'ES30 5853 0199 2810 0235 62'
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.compile(r'^(.+?)\s+(\d+)\s+([\d,]+)\s+([\d,]+)$', re.MULTILINE)
        for match in patron.finditer(texto):
            desc, uds, precio, importe = match.groups()
            if 'DESCRIPCION' in desc.upper() or len(desc.strip()) < 3:
                continue
            lineas.append({'codigo': '', 'articulo': desc.strip(), 'cantidad': int(uds), 'precio_ud': self._convertir_importe(precio), 'iva': 4, 'base': self._convertir_importe(importe)})
        return lineas


@registrar('PANIFIESTO', 'PANIFIESTO LAVAPIES')
class ExtractorPanifiesto(ExtractorBase):
    nombre = 'PANIFIESTO'
    cif = 'B87874327'
    iban = ''
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.compile(r'^(.+?)\s+(\d+)\s+([\d,]+)\s+([\d,]+)$', re.MULTILINE)
        for match in patron.finditer(texto):
            desc, uds, precio, importe = match.groups()
            if 'DESCRIPCION' in desc.upper() or len(desc.strip()) < 3:
                continue
            lineas.append({'codigo': '', 'articulo': desc.strip(), 'cantidad': int(uds), 'precio_ud': self._convertir_importe(precio), 'iva': 4, 'base': self._convertir_importe(importe)})
        return lineas


@registrar('JULIO GARCIA VIVAS', 'GARCIA VIVAS')
class ExtractorJulioGarciaVivas(ExtractorBase):
    nombre = 'JULIO GARCIA VIVAS'
    cif = '02869898G'
    iban = ''
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.search(r'Base\s*Imponible[:\s]*([\d,]+)', texto, re.IGNORECASE)
        if patron:
            base = self._convertir_importe(patron.group(1))
            lineas.append({'codigo': '', 'articulo': 'Verduras', 'iva': 4, 'base': base})
        return lineas


@registrar('LA BARRA DULCE', 'BARRA DULCE')
class ExtractorBarraDulce(ExtractorBase):
    nombre = 'LA BARRA DULCE'
    cif = 'B19981141'
    iban = 'ES76 2100 5606 4802 0017 4138'
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


@registrar('PORVAZ', 'PORVAZ VILAGARCIA', 'CONSERVAS TITO', 'TITO')
class ExtractorPorvaz(ExtractorBase):
    nombre = 'PORVAZ'
    cif = 'B36281087'
    iban = 'ES63 0049 5368 0625 1628 3321'
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


@registrar('MARTIN ABENZA', 'MARTIN ARBENZA', 'EL MODESTO')
class ExtractorMartinAbenza(ExtractorBase):
    nombre = 'MARTIN ABENZA'
    cif = '74305431K'
    iban = 'ES37 0049 6193 4128 9534 3887'
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.search(r'Base\s*Imponible[:\s]*([\d,]+)', texto, re.IGNORECASE)
        if patron:
            base = self._convertir_importe(patron.group(1))
            lineas.append({'codigo': '', 'articulo': 'Aceite de oliva', 'iva': 4, 'base': base})
        return lineas


@registrar('CARRASCAL', 'EL CARRASCAL', 'JOSE LUIS SANCHEZ')
class ExtractorCarrascal(ExtractorBase):
    nombre = 'EL CARRASCAL'
    cif = '07951036M'
    iban = 'ES59 0049 0344 98 2510368354'
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.search(r'Base\s*Imponible[:\s]*([\d,]+)', texto, re.IGNORECASE)
        if patron:
            base = self._convertir_importe(patron.group(1))
            lineas.append({'codigo': '', 'articulo': 'Aceite de oliva', 'iva': 4, 'base': base})
        return lineas


@registrar('BIELLEBI', 'BIELLEBI SRL')
class ExtractorBiellebi(ExtractorBase):
    nombre = 'BIELLEBI'
    cif = '06089700725'
    iban = 'IT68B0306941603100000001003'
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.compile(r'^(.+?)\s+(\d+)\s+([\d,]+)\s+([\d,]+)$', re.MULTILINE)
        for match in patron.finditer(texto):
            desc, uds, precio, importe = match.groups()
            if 'DESCRIPCION' in desc.upper() or len(desc.strip()) < 3:
                continue
            lineas.append({'codigo': '', 'articulo': desc.strip(), 'cantidad': int(uds), 'precio_ud': self._convertir_importe(precio), 'iva': 0, 'base': self._convertir_importe(importe)})
        return lineas


@registrar('EMBUTIDOS FERRIOL', 'EMBOTITS FERRIOL', 'FERRIOL')
class ExtractorFerriol(ExtractorBase):
    nombre = 'FERRIOL'
    cif = 'B57955098'
    iban = 'ES22 2100 0088 0502 0014 6500'
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


@registrar('ABBATI CAFFE', 'ABBATI')
class ExtractorAbbati(ExtractorBase):
    nombre = 'ABBATI'
    cif = 'B82567876'
    iban = ''
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.search(r'Base\s*Imponible[:\s]*([\d,]+)', texto, re.IGNORECASE)
        if patron:
            base = self._convertir_importe(patron.group(1))
            lineas.append({'codigo': '', 'articulo': 'Café', 'iva': 10, 'base': base})
        return lineas


@registrar('MIGUEZ CAL', 'FORPLAN')
class ExtractorMiguezCal(ExtractorBase):
    nombre = 'MIGUEZ CAL'
    cif = 'B79868006'
    iban = 'ES96 2085 9748 9203 0003 9285'
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.search(r'Base\s*Imponible[:\s]*([\d,]+)', texto, re.IGNORECASE)
        if patron:
            base = self._convertir_importe(patron.group(1))
            lineas.append({'codigo': '', 'articulo': 'Formación/Consultoría', 'iva': 21, 'base': base})
        return lineas


@registrar('LA ROSQUILLERIA', 'ROSQUILLERIA')
class ExtractorRosquilleria(ExtractorBase):
    nombre = 'LA ROSQUILLERIA'
    cif = 'B73814949'
    iban = 'ES16 0487 0061 1320 0700 2940'
    metodo_pdf = 'ocr'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.search(r'Base\s*Imponible[:\s]*([\d,]+)', texto, re.IGNORECASE)
        if patron:
            base = self._convertir_importe(patron.group(1))
            lineas.append({'codigo': '', 'articulo': 'Rosquillas artesanas', 'iva': 4, 'base': base})
        return lineas


@registrar('MANIPULADOS ABELLAN', 'ABELLAN', 'EL LABRADOR')
class ExtractorManipuladosAbellan(ExtractorBase):
    nombre = 'MANIPULADOS ABELLAN'
    cif = 'B30473326'
    iban = 'ES06 2100 8321 0413 0018 3503'
    metodo_pdf = 'ocr'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.compile(r'^(.+?)\s+(\d+)\s+([\d,]+)\s+([\d,]+)$', re.MULTILINE)
        for match in patron.finditer(texto):
            desc, uds, precio, importe = match.groups()
            if 'DESCRIPCION' in desc.upper() or len(desc.strip()) < 3:
                continue
            lineas.append({'codigo': '', 'articulo': desc.strip(), 'cantidad': int(uds), 'precio_ud': self._convertir_importe(precio), 'iva': 10, 'base': self._convertir_importe(importe)})
        return lineas


@registrar('PC COMPONENTES')
class ExtractorPCComponentes(ExtractorBase):
    nombre = 'PC COMPONENTES'
    cif = 'B73347494'
    iban = ''
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.search(r'Base\s*Imponible[:\s]*([\d,]+)', texto, re.IGNORECASE)
        if patron:
            base = self._convertir_importe(patron.group(1))
            lineas.append({'codigo': '', 'articulo': 'Material informático', 'iva': 21, 'base': base})
        return lineas


@registrar('OPENAI')
class ExtractorOpenAI(ExtractorBase):
    nombre = 'OPENAI'
    cif = ''
    iban = ''
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.search(r'(?:Subtotal|Amount)[:\s]*\$?([\d,\.]+)', texto, re.IGNORECASE)
        if patron:
            base = self._convertir_importe(patron.group(1))
            lineas.append({'codigo': '', 'articulo': 'Servicios API OpenAI', 'iva': 21, 'base': base})
        return lineas


@registrar('AMAZON')
class ExtractorAmazon(ExtractorBase):
    nombre = 'AMAZON'
    cif = 'W0184081H'
    iban = ''
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.search(r'Base\s*Imponible[:\s]*([\d,]+)', texto, re.IGNORECASE)
        if patron:
            base = self._convertir_importe(patron.group(1))
            lineas.append({'codigo': '', 'articulo': 'Compra Amazon', 'iva': 21, 'base': base})
        return lineas
