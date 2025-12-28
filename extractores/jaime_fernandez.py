"""
Extractor para JAIME FERNANDEZ MORENO

Alquiler local Calle Rodas 2 (persona física)
NIF: 07219971H
Dirección: Abades 16 3ºC, 28012 Madrid

METODO: pdfplumber (PDF texto)

Factura mensual:
- Base: 500€
- IVA 21%: 105€
- Retención IRPF 19%: -95€
- Total a pagar: 510€

Categoría: ALQUILER

Creado: 21/12/2025
Corregido: 26/12/2025 - Símbolo €
Validado: 4/4 facturas (1T25-3T25)
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re
import pdfplumber


@registrar('JAIME FERNANDEZ', 'JAIME FERNANDEZ MORENO', 'FERNANDEZ MORENO')
class ExtractorJaimeFernandez(ExtractorBase):
    """Extractor para facturas de alquiler de JAIME FERNANDEZ MORENO."""
    
    nombre = 'JAIME FERNANDEZ MORENO'
    cif = '07219971H'  # NIF persona física
    iban = ''  # PENDIENTE
    metodo_pdf = 'pdfplumber'
    categoria_fija = 'ALQUILER'
    tiene_retencion = True
    
    def extraer_texto_pdfplumber(self, pdf_path: str) -> str:
        """Extrae texto con pdfplumber."""
        texto = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    texto += t + "\n"
        return texto
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae línea de alquiler.
        
        Formato factura:
        DESCRIPCIÓN                    IMPORTE
        Alquiler mensual local...      500,00 €
        SUBTOTAL                       500,00 €
        IVA AL 21%                     105,00 €
        RETENCION 19%                  -95,00 €
        TOTAL                          510,00 €
        """
        lineas = []
        
        # Base (SUBTOTAL)
        m_base = re.search(r'SUBTOTAL\s*([\d.,]+)\s*€', texto)
        if m_base:
            base = float(m_base.group(1).replace('.', '').replace(',', '.'))
            lineas.append({
                'codigo': '',
                'articulo': 'ALQUILER LOCAL RODAS 2',
                'cantidad': 1,
                'precio_ud': base,
                'iva': 21,
                'base': base
            })
        
        return lineas
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """
        Extrae total de la factura.
        Total = Base + IVA - Retención
        """
        m_total = re.search(r'^TOTAL\s+([\d.,]+)\s*€', texto, re.MULTILINE)
        if m_total:
            return float(m_total.group(1).replace('.', '').replace(',', '.'))
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        m = re.search(r'Fecha:\s*(\d{2})-(\d{2})-(\d{2,4})', texto)
        if m:
            dia, mes, año = m.groups()
            if len(año) == 2:
                año = '20' + año
            return f"{dia}/{mes}/{año}"
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae número de factura."""
        m = re.search(r'N\.º de factura:\s*(\d+-\d+)', texto)
        return m.group(1) if m else None
    
    def extraer_retencion(self, texto: str) -> Optional[float]:
        """Extrae importe de retención IRPF."""
        m = re.search(r'RETENCION.*?-?\s*(\d+[.,]\d{2})\s*€', texto)
        if m:
            return float(m.group(1).replace(',', '.'))
        return None
