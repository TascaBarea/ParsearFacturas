"""
Extractor para BM SUPERMERCADOS.

Tickets de supermercado con desglose fiscal.
CIF: B20099586
IBAN: (pago tarjeta)

Formato desglose fiscal BM:
 Tipo Base Iva Req Total
------------------------------------------------
 10.00% 29.90 2.99 0.00 32.89
 21.00% 11.28 2.37 0.00 13.65
 4.00% 2.16 0.09 0.00 2.25

Actualizado: 19/12/2025 - Patrón corregido para formato real
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict
import re


@registrar('BM', 'BM SUPERMERCADOS', 'DISTRIBUCION SUPERMERCADOS')
class ExtractorBM(ExtractorBase):
    """Extractor para tickets de BM SUPERMERCADOS."""
    
    nombre = 'BM SUPERMERCADOS'
    cif = 'B20099586'
    iban = ''  # Pago tarjeta
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de tickets BM usando el desglose fiscal.
        
        Formato real:
         10.00% 29.90 2.99 0.00 32.89
         21.00% 11.28 2.37 0.00 13.65
         4.00% 2.16 0.09 0.00 2.25
        """
        lineas = []
        
        # Patrón para desglose fiscal BM
        # Formato: [espacio] IVA% BASE IVA_CUOTA REQ TOTAL
        patron_desglose = re.compile(
            r'^\s*(\d{1,2})[.,]00%\s+'     # IVA: 10.00%, 21.00%, 4.00%
            r'(\d+[.,]\d{2})\s+'            # Base
            r'(\d+[.,]\d{2})\s+'            # Cuota IVA
            r'(\d+[.,]\d{2})\s+'            # Recargo (siempre 0.00)
            r'(\d+[.,]\d{2})',              # Total
            re.MULTILINE
        )
        
        for match in patron_desglose.finditer(texto):
            iva = int(match.group(1))
            base = self._convertir_importe(match.group(2))
            
            if base > 0 and iva in [4, 10, 21]:
                if iva == 4:
                    descripcion = "PRODUCTOS IVA SUPERREDUCIDO 4%"
                elif iva == 10:
                    descripcion = "PRODUCTOS IVA REDUCIDO 10%"
                else:
                    descripcion = "PRODUCTOS IVA GENERAL 21%"
                
                lineas.append({
                    'codigo': 'BM',
                    'articulo': descripcion,
                    'iva': iva,
                    'base': round(base, 2)
                })
        
        return lineas
    
    def extraer_total(self, texto: str) -> float:
        """Extrae el total del ticket BM."""
        # Buscar TOTAL COMPRA (iva incl.) XX.XX
        patron = re.search(
            r'TOTAL\s+COMPRA\s*\(?iva\s+incl\.?\)?\s*(\d+[.,]\d{2})',
            texto, re.IGNORECASE
        )
        if patron:
            return self._convertir_importe(patron.group(1))
        
        # Alternativa: TARJETA XX.XX
        patron2 = re.search(r'^TARJETA\s+(\d+[.,]\d{2})', texto, re.MULTILINE)
        if patron2:
            return self._convertir_importe(patron2.group(1))
        
        return None
