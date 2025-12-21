"""
Extractor para MARITA COSTA VILELA

Distribuidora de productos gourmet
NIF: 48207369J (autónoma)
Ubicación: Valdemoro, Madrid
Tel: 665 14 06 10

Productos típicos:
- AOVE Nobleza del Sur (4% IVA)
- Patés Luças (10% IVA): atún, sardina
- Cookies Milola (10% IVA)
- Picos de Jamón Lucía (4%/10% IVA)
- Torreznos La Rústica (10% IVA)
- Patatas Quillo (10% IVA)
- Vinagres Badia (10% IVA)
- Risotto Urdet (10% IVA)

Tipos de IVA:
- 4%: Aceite de oliva virgen extra
- 10%: Alimentación general
- 2%: Casos especiales (recargo equivalencia histórico)

Creado: 20/12/2025
Validado: 9/9 facturas (4T24, 1T25, 2T25, 3T25, 4T25)
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar('MARITA COSTA', 'MARITA', 'COSTA VILELA')
class ExtractorMaritaCosta(ExtractorBase):
    """Extractor para facturas de MARITA COSTA VILELA."""
    
    nombre = 'MARITA COSTA VILELA'
    cif = '48207369J'
    iban = None  # Transferencia bancaria (sin IBAN en factura)
    metodo_pdf = 'pdfplumber'
    categoria_fija = 'GOURMET'
    
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
    
    def extraer_texto(self, pdf_path: str) -> str:
        """Extrae texto con pdfplumber."""
        import pdfplumber
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if len(pdf.pages) > 0:
                    return pdf.pages[0].extract_text()
        except:
            pass
        return ""
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de producto.
        
        Formato:
        CODIGO DESCRIPCIÓN CANTIDAD PRECIO€ SUBTOTAL€ DTO. TOTAL€
        
        Ejemplo:
        AOVENOV500 AOVE NOBLEZA DEL SUR NOVO 500ML 12,00 13,2000€ 158,40€ 158,40€
        """
        lineas = []
        
        # Patrón para líneas de producto
        for m in re.finditer(
            r'^([A-Z0-9]+)\s+'                    # Código
            r'(.+?)\s+'                           # Descripción
            r'(\d+[,.]?\d*)\s+'                   # Cantidad
            r'([\d,]+)€\s+'                       # Precio
            r'([\d,]+)€\s+'                       # Subtotal
            r'([\d,]+)€$',                        # Total
            texto,
            re.MULTILINE
        ):
            codigo = m.group(1)
            articulo = m.group(2).strip()
            cantidad = self._convertir_europeo(m.group(3))
            precio = self._convertir_europeo(m.group(4))
            importe = self._convertir_europeo(m.group(6))
            
            # Determinar IVA según producto
            if 'AOVE' in codigo or 'AOVE' in articulo:
                iva = 4
            else:
                iva = 10
            
            lineas.append({
                'codigo': codigo,
                'articulo': articulo,
                'cantidad': int(cantidad) if cantidad == int(cantidad) else cantidad,
                'precio_ud': precio,
                'iva': iva,
                'base': importe
            })
        
        return lineas
    
    def extraer_desglose_iva(self, texto: str) -> List[Dict]:
        """
        Extrae desglose de IVA.
        
        Formato:
        TIPO BASE I.V.A R.E. PRONTO PAGO DESC. I.R.P.F.
        21,00
        10,00 188,34 18,83
        4,00 367,20 14,69
        """
        desglose = []
        
        for m in re.finditer(
            r'^(\d+)[,.](\d{2})\s+([\d,.]+)\s+([\d,.]+)\s*$',
            texto,
            re.MULTILINE
        ):
            tipo = int(m.group(1))
            base = self._convertir_europeo(m.group(3))
            iva = self._convertir_europeo(m.group(4))
            if base > 0:
                desglose.append({
                    'tipo': tipo,
                    'base': base,
                    'iva': iva
                })
        
        return desglose
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """
        Extrae total de la factura.
        
        Estrategia:
        1. Buscar "TOTAL: XXX,XX€"
        2. Si no, calcular desde desglose IVA
        """
        # Método directo
        m = re.search(r'TOTAL:\s*([\d,.]+)€', texto)
        if m:
            return self._convertir_europeo(m.group(1))
        
        # Calcular desde desglose
        desglose = self.extraer_desglose_iva(texto)
        if desglose:
            return round(sum(d['base'] + d['iva'] for d in desglose), 2)
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        # Buscar fecha en formato DD/MM/YYYY
        m = re.search(r'(\d{2}/\d{2}/\d{4})', texto)
        if m:
            return m.group(1)
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae número de factura."""
        m = re.search(r'Factura\s+\d+\s+(\d+)', texto)
        if m:
            return m.group(1)
        return None
