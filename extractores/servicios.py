"""
Extractores para alquileres y servicios.
ALQUILERES, CONTROLPLAGA, TRUCCO, PANRUJE, ANGEL Y LOLI

Actualizado: 18/12/2025 - pdfplumber
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict
import re


@registrar('BENJAMIN ORTEGA', 'ORTEGA ALONSO')
class ExtractorAlquilerOrtega(ExtractorBase):
    nombre = 'BENJAMIN ORTEGA'
    cif = '09342596L'
    iban = 'ES31 0049 5977 5521 1606 6585'
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.search(r'(?:Importe|Base)[:\s]*([\d\.,]+)', texto, re.IGNORECASE)
        if patron:
            base = self._convertir_importe(patron.group(1))
            lineas.append({'codigo': 'ALQUILER', 'articulo': 'Alquiler local', 'iva': 21, 'base': base})
        return lineas


@registrar('JAIME FERNANDEZ', 'FERNANDEZ MORENO')
class ExtractorAlquilerFernandez(ExtractorBase):
    nombre = 'JAIME FERNANDEZ'
    cif = '07219971H'
    iban = 'ES31 0049 5977 5521 1606 6585'
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.search(r'(?:Importe|Base)[:\s]*([\d\.,]+)', texto, re.IGNORECASE)
        if patron:
            base = self._convertir_importe(patron.group(1))
            lineas.append({'codigo': 'ALQUILER', 'articulo': 'Alquiler local', 'iva': 21, 'base': base})
        return lineas


@registrar('CONTROLPLAGA', 'JAVIER ALBORES', 'JAVIER ARBORES')
class ExtractorControlplaga(ExtractorBase):
    nombre = 'CONTROLPLAGA'
    cif = '11812266H'
    iban = 'ES86 0081 7122 58 0001218325'
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.search(r'Base\s+Imponible[:\s]*([\d,]+)', texto, re.IGNORECASE)
        if patron:
            base = self._convertir_importe(patron.group(1))
            lineas.append({'codigo': 'CONTROL', 'articulo': 'Desinsectación', 'iva': 21, 'base': base})
        return lineas


@registrar('TRUCCO', 'TRUCCO COPIAS', 'ISAAC RODRIGUEZ')
class ExtractorTrucco(ExtractorBase):
    nombre = 'TRUCCO'
    cif = '05247386M'
    iban = ''
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.search(r'Base\s*Imponible[:\s]*([\d,]+)', texto, re.IGNORECASE)
        if patron:
            base = self._convertir_importe(patron.group(1))
            lineas.append({'codigo': 'TRUCCO', 'articulo': 'Imprenta/Copistería', 'iva': 21, 'base': base})
        return lineas


@registrar('PANRUJE', 'ROSQUILLAS LA ERMITA', 'LA ERMITA')
class ExtractorPanruje(ExtractorBase):
    nombre = 'PANRUJE'
    cif = 'B13858014'
    iban = 'ES19 0081 5344 2800 0261 4066'
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.compile(r'^(\d{4,6})\s+(.+?)\s+(\d+)\s+([\d,]+)\s+([\d,]+)$', re.MULTILINE)
        
        for match in patron.finditer(texto):
            codigo, desc, uds, precio, importe = match.groups()
            if 'DESCRIPCION' in desc.upper():
                continue
            lineas.append({'codigo': codigo, 'articulo': desc.strip(), 'cantidad': int(uds), 'precio_ud': self._convertir_importe(precio), 'iva': 4, 'base': self._convertir_importe(importe)})
        return lineas


@registrar('ANGEL Y LOLI', 'ALFARERIA ANGEL')
class ExtractorAngelYLoli(ExtractorBase):
    nombre = 'ANGEL Y LOLI'
    cif = '75727068M'
    iban = ''
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        lineas = []
        patron = re.search(r'Base\s*Imponible[:\s]*([\d,]+)', texto, re.IGNORECASE)
        if patron:
            base = self._convertir_importe(patron.group(1))
            lineas.append({'codigo': '', 'articulo': 'Alfarería', 'iva': 21, 'base': base})
        return lineas
