"""
Extractor para WELLDONE LÁCTICOS (Rodolfo del Río Lameyer)
Quesos artesanos de Sevilla.

Autor: Claude (ParsearFacturas v5.0)
Fecha: 27/12/2025

PECULIARIDADES:
- IVA 4% para quesos
- Portes con IVA 21% - deben prorratearse entre productos
- El TOTAL de línea incluye IVA (cantidad × precio_con_iva)
- La BASE se calcula como cantidad × precio_unidad
"""

import re
from typing import List, Dict, Optional

# DESCOMENTAR para integrar en proyecto:
# from extractores import registrar
# from extractores.base import ExtractorBase


# @registrar('WELLDONE', 'WELLDONE LACTICOS', 'WELLDONE LÁCTICOS', 
#            'RODOLFO DEL RIO', 'RODOLFO DEL RÍO', 'RODOLFO DEL RIO LAMEYER')
class ExtractorWelldone:  # (ExtractorBase):
    """
    Extractor para facturas de WELLDONE LÁCTICOS.
    
    Formato línea:
    CÓDIGO DESCRIPCIÓN LOTE CANTIDAD PRECIO_UNIDAD PRECIO_CON_IVA TOTAL
    QA0006 ALJARAFE wD140925 4,00 7,37 7,6648 30,66
    """
    
    nombre = 'WELLDONE LACTICOS'
    nombre_fiscal = 'Rodolfo del Rio Lameyer'
    nif = '27292516A'
    iban = 'ES55 2100 5789 1202 0015 7915'
    metodo_pdf = 'pdfplumber'
    categoria_fija = 'QUESOS'
    iva_quesos = 4
    iva_portes = 21
    
    def extraer_texto_pdfplumber(self, pdf_path: str) -> str:
        """Extrae texto del PDF usando pdfplumber."""
        import pdfplumber
        texto_completo = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    texto = page.extract_text()
                    if texto:
                        texto_completo.append(texto)
        except Exception as e:
            print(f"Error extrayendo texto: {e}")
        return '\n'.join(texto_completo)
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de productos.
        
        Formato:
        CÓDIGO DESCRIPCIÓN LOTE CANTIDAD PRECIO_UNIDAD PRECIO_CON_IVA TOTAL
        QA0006 ALJARAFE wD140925 4,00 7,37 7,6648 30,66
        
        IMPORTANTE: 
        - Base = cantidad × precio_unidad
        - Los portes NO se prorratean - se tratan por separado con IVA 21%
        """
        lineas = []
        
        # Patrón para productos (código empieza con Q)
        patron_producto = re.compile(
            r'^(Q[A-Z]\d{4})\s+'           # Código (QA0006, QF0003, etc.)
            r'([A-ZÀ-Ü][A-ZÀ-Ü\s]+?)\s+'   # Descripción (incluye acentos)
            r'wD\d+\s+'                     # Lote (ignorar)
            r'(\d+[.,]\d+)\s+'              # Cantidad
            r'(\d+[.,]\d+)\s+'              # Precio unidad
            r'(\d+[.,]\d+)\s+'              # Precio con IVA (ignorar)
            r'(\d+[.,]\d+)',                # Total con IVA (ignorar)
            re.MULTILINE
        )
        
        # Extraer productos
        for match in patron_producto.finditer(texto):
            codigo = match.group(1)
            descripcion = match.group(2).strip()
            cantidad = self._convertir_europeo(match.group(3))
            precio_ud = self._convertir_europeo(match.group(4))
            
            # Calcular base = cantidad × precio_unidad
            base = round(cantidad * precio_ud, 2)
            
            if base < 0.01 or cantidad < 0.01:
                continue
            
            lineas.append({
                'codigo': codigo,
                'articulo': descripcion[:50],
                'cantidad': cantidad,
                'precio_ud': precio_ud,
                'iva': self.iva_quesos,
                'base': base,
                'categoria': self.categoria_fija
            })
        
        return lineas
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae número de factura."""
        patron = re.search(r'Factura\s+\d\s+(\d{6})', texto)
        if patron:
            return patron.group(1)
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de factura."""
        patron = re.search(r'Factura\s+\d\s+\d{6}\s+(\d{2}/\d{2}/\d{4})', texto)
        if patron:
            return patron.group(1)
        return None
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """Extrae total de la factura."""
        patron = re.search(r'TOTAL:\s*(\d+[.,]\d{2})', texto)
        if patron:
            return self._convertir_europeo(patron.group(1))
        return None
    
    def extraer_base_imponible(self, texto: str) -> Dict[int, float]:
        """
        Extrae bases imponibles por tipo de IVA.
        Retorna dict {iva: base}
        
        Formato en factura SIN portes:
        21,00
        10,00
        4,00 181,31 7,25
        
        Formato en factura CON portes:
        21,00 11,96 11,96 2,51
        10,00
        4,00 142,90 5,72
        """
        bases = {}
        
        # Procesar línea por línea
        for linea in texto.split('\n'):
            linea = linea.strip()
            
            # Buscar base al 4%
            match_4 = re.match(r'^4[.,]00\s+(\d+[.,]\d+)\s+\d+[.,]\d+', linea)
            if match_4:
                bases[4] = self._convertir_europeo(match_4.group(1))
            
            # Buscar base al 21% (solo si hay 3 valores después)
            match_21 = re.match(r'^21[.,]00\s+(\d+[.,]\d+)\s+(\d+[.,]\d+)\s+(\d+[.,]\d+)', linea)
            if match_21:
                # El segundo valor es la base de portes
                bases[21] = self._convertir_europeo(match_21.group(2))
        
        return bases
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo a float."""
        if not texto:
            return 0.0
        texto = texto.strip()
        if '.' in texto and ',' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            texto = texto.replace(',', '.')
        try:
            return float(texto)
        except:
            return 0.0
    
    def validar_cuadre(self, lineas: List[Dict], total_factura: float, 
                       bases_factura: Dict[int, float] = None) -> Dict:
        """Valida cuadre de la factura."""
        suma_bases = sum(l['base'] for l in lineas)
        iva_4 = round(suma_bases * 0.04, 2)
        
        # Si hay portes al 21%, añadir su IVA
        iva_21 = 0
        base_portes = 0
        if bases_factura and 21 in bases_factura:
            base_portes = bases_factura[21]
            iva_21 = round(base_portes * 0.21, 2)
        
        total_calculado = round(suma_bases + iva_4 + base_portes + iva_21, 2)
        diferencia = round(total_factura - total_calculado, 2)
        
        return {
            'suma_bases': round(suma_bases, 2),
            'iva_4': iva_4,
            'base_portes': base_portes,
            'iva_21': iva_21,
            'total_calculado': total_calculado,
            'total_factura': total_factura,
            'diferencia': diferencia,
            'cuadra': abs(diferencia) < 0.10
        }


# ============================================================
# CÓDIGO DE PRUEBA
# ============================================================

if __name__ == '__main__':
    import sys
    import pdfplumber
    
    extractor = ExtractorWelldone()
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = '/mnt/user-data/uploads/4038_4T25_1016_RODOLFO_DEL_RIO_TJ.pdf'
    
    print(f"\n{'='*60}")
    print(f"PROBANDO EXTRACTOR WELLDONE LÁCTICOS")
    print(f"{'='*60}")
    print(f"Archivo: {pdf_path}\n")
    
    texto = extractor.extraer_texto_pdfplumber(pdf_path)
    
    fecha = extractor.extraer_fecha(texto)
    num_factura = extractor.extraer_numero_factura(texto)
    total = extractor.extraer_total(texto)
    bases = extractor.extraer_base_imponible(texto)
    lineas = extractor.extraer_lineas(texto)
    
    print(f"📅 Fecha: {fecha}")
    print(f"📄 Nº Factura: {num_factura}")
    print(f"💰 Bases: {bases}")
    print(f"💰 TOTAL: {total}€")
    print(f"\n📦 LÍNEAS ({len(lineas)}):")
    print("-" * 80)
    
    for i, linea in enumerate(lineas, 1):
        print(f"  {i}. [{linea['codigo']}] {linea['articulo']}")
        print(f"     Cant: {linea['cantidad']} x {linea['precio_ud']}€ = {linea['base']}€ (IVA {linea['iva']}%)")
    
    print("-" * 80)
    
    if total:
        cuadre = extractor.validar_cuadre(lineas, total, bases)
        print(f"\n✅ VALIDACIÓN DE CUADRE:")
        print(f"   Suma bases quesos: {cuadre['suma_bases']}€")
        print(f"   IVA 4%:            {cuadre['iva_4']}€")
        if cuadre['base_portes'] > 0:
            print(f"   Base portes:       {cuadre['base_portes']}€")
            print(f"   IVA 21% portes:    {cuadre['iva_21']}€")
        print(f"   Total calculado:   {cuadre['total_calculado']}€")
        print(f"   Total factura:     {cuadre['total_factura']}€")
        print(f"   Diferencia:        {cuadre['diferencia']}€")
        print(f"   {'✅ CUADRA' if cuadre['cuadra'] else '❌ DESCUADRE'}")
