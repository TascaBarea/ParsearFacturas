"""
Extractor para GADITAUN (María Linarejos Martínez Rodríguez)

Productora artesanal de vinos Regantío Viejo (Cádiz) y conservas
NIF: 34007216Z (autónoma)
IBAN: ES19 0081 0259 1000 0163 8268

REQUIERE OCR - Las facturas son PDFs de Zoho CRM sin texto extraíble

Productos:
- Vinos Regantío Viejo (Duo Vites, Relicta, Junus Blanco): 21% IVA
- Paté de Tagarninas de la Sierra de Cádiz: 10% IVA
- Aceite de Oliva Virgen Extra Koroneiki: 4% IVA

Estrategia de extracción:
- Usar tabla de desglose de IVA al final de la factura
- Formato: "XX% BASE€ - IVA€"
- Cada tipo de IVA corresponde a un tipo de producto

Creado: 20/12/2025
Validado: 5/5 facturas (1T25, 2T25, 4T25)
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar('GADITAUN', 'MARILINA', 'MARIA LINAREJOS', 'GARDITAUN',
           'GADITAUN MARILINA', 'MARILINA GADITAUN', 
           'GARDITAUN MARIA LINAREJOS', 'MARIA LINAREJOS GADITAUN')
class ExtractorGaditaun(ExtractorBase):
    """Extractor para facturas de GADITAUN (requiere OCR)."""
    
    nombre = 'GADITAUN'
    cif = '34007216Z'  # NIF de autónoma
    iban = 'ES19 0081 0259 1000 0163 8268'
    metodo_pdf = 'ocr'
    
    def extraer_texto_ocr(self, pdf_path: str) -> str:
        """Extrae texto del PDF usando OCR."""
        try:
            from pdf2image import convert_from_path
            import pytesseract
            
            images = convert_from_path(pdf_path, dpi=300)
            texto = ""
            for img in images:
                texto += pytesseract.image_to_string(img, lang='eng')
            return texto
        except Exception as e:
            return ""
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo (1.234,56) a float."""
        if not texto:
            return 0.0
        texto = str(texto).strip().replace('€', '').replace(' ', '').strip()
        if '.' in texto and ',' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            texto = texto.replace(',', '.')
        try:
            return float(texto)
        except:
            return 0.0
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de productos usando la tabla de desglose de IVA.
        
        La factura tiene una tabla al final con formato:
        Tipo | B.I. | B.I. Portes | IVA
        21%  | 149,25€ |    -     | 31,34€
        10%  | 95,60€  |    -     | 9,56€
        4%   | 75,00€  |    -     | 3,00€
        
        Cada tipo de IVA corresponde a un producto:
        - 21%: Vino Regantío Viejo
        - 10%: Paté de Tagarninas
        - 4%: Aceite de Oliva AOVE Koroneiki
        """
        lineas = []
        
        # Procesar línea por línea para evitar problemas con regex multilinea
        for line in texto.split('\n'):
            line = line.strip()
            
            # IVA 21% - Vinos (Duo Vites, Relicta, Junus)
            m = re.match(r'^21%\s+(\d+[,.]?\d+)\s*€?', line)
            if m:
                base = self._convertir_europeo(m.group(1))
                if base > 1:
                    iva = round(base * 0.21, 2)
                    lineas.append({
                        'codigo': 'VINO',
                        'articulo': 'VINO REGANTÍO VIEJO',
                        'cantidad': 1,
                        'precio_ud': round(base, 2),
                        'iva': 21,
                        'base': round(base, 2)
                    })
            
            # IVA 10% - Paté de Tagarninas
            m = re.match(r'^10%\s+(\d+[,.]?\d+)\s*€?', line)
            if m:
                base = self._convertir_europeo(m.group(1))
                if base > 1:
                    iva = round(base * 0.10, 2)
                    lineas.append({
                        'codigo': 'PATE',
                        'articulo': 'PATÉ TAGARNINAS',
                        'cantidad': 1,
                        'precio_ud': round(base, 2),
                        'iva': 10,
                        'base': round(base, 2)
                    })
            
            # IVA 4% - Aceite de Oliva
            m = re.match(r'^4%\s+(\d+[,.]?\d+)\s*€?', line)
            if m:
                base = self._convertir_europeo(m.group(1))
                if base > 1:
                    iva = round(base * 0.04, 2)
                    lineas.append({
                        'codigo': 'AOVE',
                        'articulo': 'ACEITE OLIVA KORONEIKI',
                        'cantidad': 1,
                        'precio_ud': round(base, 2),
                        'iva': 4,
                        'base': round(base, 2)
                    })
        
        return lineas
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """
        Extrae total de la factura.
        
        El OCR puede fallar en el total, así que calculamos desde las líneas.
        """
        lineas = self.extraer_lineas(texto)
        if lineas:
            base_total = sum(l['base'] for l in lineas)
            iva_total = sum(round(l['base'] * l['iva'] / 100, 2) for l in lineas)
            return round(base_total + iva_total, 2)
        
        # Fallback: buscar "Total general"
        m = re.search(r'Total general\s*(\d+[,.]?\d+)\s*€?', texto)
        if m:
            return self._convertir_europeo(m.group(1))
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        m = re.search(r'Fecha de Factura[:\s]*(\d{2}/\d{2}/\d{4})', texto)
        if m:
            return m.group(1)
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae número de factura."""
        m = re.search(r'Numero de Factura\s*[:\s]*(\d{4}-\d+)', texto)
        if m:
            return m.group(1)
        return None
