"""
Extractor para ECOMS SUPERMARKET S.L. (Supermercados DIA)

Operador de franquicias DIA
CIF: B72738602
Ubicación: CL Huertas 72, 28014 Madrid

DOS FORMATOS DE FACTURA:
1. DIA Digital (pdfplumber) - Tickets modernos exportados digitalmente
   → Funciona 100%
2. TPV Escaneado (OCR) - Tickets térmicos fotografiados/escaneados
   → Funciona si la imagen tiene buena calidad

Productos típicos:
- Frutas y verduras (4% IVA): Naranjas, limones, lima, rúcula
- Alimentación general (10% IVA): Hielo, leche, caramelos
- Droguería (21% IVA): Papel higiénico, jabón, servilletas

Sistema IVA por letras (formato DIA digital):
- A = 4% (frutas, verduras, pan, leche)
- B = 10% (alimentación general)
- C = 21% (droguería, no alimentario)

Creado: 20/12/2025
Validado: 6/8 facturas (5/5 digitales OK, 1/3 OCR OK)
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional, Tuple
import re


@registrar('ECOMS', 'ECOMS SUPERMARKET', 'DIA', 'SUPERMERCADOS DIA')
class ExtractorEcoms(ExtractorBase):
    """Extractor para facturas de ECOMS SUPERMARKET (DIA)."""
    
    nombre = 'ECOMS SUPERMARKET'
    cif = 'B72738602'
    iban = None  # Pago en efectivo/tarjeta
    metodo_pdf = 'hibrido'  # pdfplumber + OCR fallback
    categoria_fija = 'SUPERMERCADO'
    
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
    
    def extraer_texto(self, pdf_path: str) -> Tuple[str, str]:
        """
        Extrae texto con pdfplumber, fallback a OCR.
        Returns: (texto, metodo)
        """
        import pdfplumber
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if len(pdf.pages) > 0:
                    texto = pdf.pages[0].extract_text()
                    if texto and len(texto) > 100:
                        return texto, 'pdfplumber'
        except:
            pass
        
        # Fallback OCR
        try:
            from pdf2image import convert_from_path
            import pytesseract
            
            images = convert_from_path(pdf_path, dpi=300)
            if images:
                return pytesseract.image_to_string(images[0], lang='eng'), 'ocr'
        except:
            pass
        
        return "", None
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de producto.
        
        Formato DIA digital:
        DESCRIPCIÓN CANTIDADud/kg PRECIO€ TOTAL€ LETRA
        
        Ejemplo:
        BOLSA DE HIELO 2 KG 2 ud 0,99 € 1,98 € B
        NARANJA SELECCIÓN 0,765kg 2,69 €/kg 2,06 € A
        """
        lineas = []
        
        # Patrón para formato DIA digital
        for m in re.finditer(
            r'([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s\d]+?)\s+'  # Descripción
            r'(\d+)\s*(?:ud|kg)\s+'                # Cantidad
            r'([\d,]+)\s*€[/kg]*\s+'               # Precio
            r'([\d,]+)\s*€\s+'                     # Total
            r'([ABC])',                             # Letra IVA
            texto
        ):
            articulo = m.group(1).strip()
            cantidad = int(m.group(2))
            precio = self._convertir_europeo(m.group(3))
            importe = self._convertir_europeo(m.group(4))
            iva_letra = m.group(5)
            
            # Mapear letra a porcentaje
            iva_map = {'A': 4, 'B': 10, 'C': 21}
            iva = iva_map.get(iva_letra, 10)
            
            lineas.append({
                'codigo': '',
                'articulo': articulo,
                'cantidad': cantidad,
                'precio_ud': precio,
                'iva': iva,
                'base': importe
            })
        
        return lineas
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """
        Extrae total de la factura.
        
        Formatos:
        1. DIA digital: "Total a pagar..................... X,XX €"
        2. TPV antiguo: "TOTAL FACTURA    X,XX"
        """
        # Formato DIA digital
        m = re.search(r'Total a pagar[.\s]+([\d,]+)\s*€', texto)
        if m:
            return self._convertir_europeo(m.group(1))
        
        # Formato TPV (OCR)
        m = re.search(r'TOTAL FACTURA\s+([\d,]+)', texto)
        if m:
            return self._convertir_europeo(m.group(1))
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """
        Extrae fecha de la factura.
        
        Formatos:
        1. DIA digital: "04/10/2025 15:31"
        2. TPV: "EMITIDA: 04-07-2025"
        """
        # Formato DIA digital
        m = re.search(r'(\d{2}/\d{2}/\d{4})\s+\d{2}:\d{2}', texto)
        if m:
            return m.group(1)
        
        # Formato TPV
        m = re.search(r'[EA]MITIDA[:\s]+(\d{2}[-/]\d{2}[-/]\d{4})', texto)
        if m:
            return m.group(1).replace('-', '/')
        
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """
        Extrae número de factura.
        
        Formatos:
        1. DIA digital: "por la factura Nº FT139080300468"
        2. TPV: "N.FACTURA: FT 139080200016"
        """
        # Formato DIA digital
        m = re.search(r'factura\s+N[ºo°]\s*(FT\d+)', texto, re.IGNORECASE)
        if m:
            return m.group(1)
        
        # Formato TPV
        m = re.search(r'N\.?FACTURA[:\s]+(FT\s*\d+)', texto)
        if m:
            return m.group(1).replace(' ', '')
        
        # ID alternativo
        m = re.search(r'ES-\d+-\d+-\d+-\d+-\d+', texto)
        if m:
            return m.group(0)
        
        return None
