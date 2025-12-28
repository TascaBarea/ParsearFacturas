# -*- coding: utf-8 -*-
"""
Extractor para PABLO RUIZ HERRERA - LA DOLOROSA CASA DE FERMENTOS

Productos fermentados artesanales:
- Degustaciones de vermut
- Encurtidos fermentados
- Fermentos varios

DNI: 32081620R (autónomo)
IBAN: ES27 0049 4680 8124 1609 2645

IVA: 21% (productos gourmet/servicios)

Creado: 27/12/2025
"""
# from extractores.base import ExtractorBase
# from extractores import registrar
from typing import List, Dict, Optional
import re
import pdfplumber


# @registrar('PABLO RUIZ', 'LA DOLOROSA', 'PABLO RUIZ LA DOLOROSA', 
#            'PABLO RUIZ HERRERA', 'LA DOLOROSA CASA DE FERMENTOS')
class ExtractorPabloRuiz:  # (ExtractorBase):
    """Extractor para facturas de PABLO RUIZ - LA DOLOROSA."""
    
    nombre = 'PABLO RUIZ LA DOLOROSA'
    cif = '32081620R'  # DNI (autónomo)
    iban = 'ES27 0049 4680 8124 1609 2645'
    metodo_pdf = 'pdfplumber'
    
    def extraer_texto_pdfplumber(self, pdf_path: str) -> str:
        """Extrae texto del PDF."""
        texto_completo = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    texto = page.extract_text()
                    if texto:
                        texto_completo.append(texto)
        except Exception as e:
            pass
        return '\n'.join(texto_completo)
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de productos.
        
        Formato:
        Descripción Unidades Precio Unitario Total
        Degustación Vermut 7/10 3 12,40 € 37,20 €
        Degustacion Encurtidos 15/10 13 12,40 € 161,20 €
        """
        lineas = []
        
        # Patrón para líneas de producto
        # DESCRIPCION + UNIDADES + PRECIO € + TOTAL €
        patron = re.compile(
            r'^(Degustaci[oó]n\s+[A-Za-záéíóúñ]+(?:\s+\d+/\d+)?)\s+'  # Descripción con fecha opcional
            r'(\d+)\s+'                                                # Unidades
            r'(\d+[.,]\d{2})\s*€\s+'                                   # Precio unitario
            r'(\d+[.,]\d{2})\s*€',                                     # Total
            re.MULTILINE | re.IGNORECASE
        )
        
        for match in patron.finditer(texto):
            descripcion = match.group(1).strip()
            cantidad = int(match.group(2))
            precio_ud = self._convertir_europeo(match.group(3))
            total = self._convertir_europeo(match.group(4))
            
            if total < 0.01:
                continue
            
            lineas.append({
                'codigo': '',
                'articulo': descripcion[:50],
                'cantidad': cantidad,
                'precio_ud': precio_ud,
                'iva': 21,  # Siempre 21%
                'base': total,
                'categoria': 'FERMENTOS'
            })
        
        return lineas
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """
        Extrae número de factura.
        Formato: "Número de factura: TB-2025-03"
        """
        patron = re.search(r'Número\s+de\s+factura:\s*(TB-\d{4}-\d+)', texto, re.IGNORECASE)
        if patron:
            return patron.group(1)
        
        # Alternativa sin acento
        patron2 = re.search(r'Numero\s+de\s+factura:\s*(TB-\d{4}-\d+)', texto, re.IGNORECASE)
        if patron2:
            return patron2.group(1)
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de factura."""
        patron = re.search(r'Fecha\s+de\s+factura:\s*(\d{2}/\d{2}/\d{4})', texto)
        if patron:
            return patron.group(1)
        return None
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """
        Extrae total de la factura.
        El total final está en una línea sola antes del segundo "TOTAL".
        Formato: "405,11 €" seguido de "TOTAL"
        """
        # Buscar importe seguido de € en línea sola (el mayor)
        importes = re.findall(r'^(\d+[.,]\d{2})\s*€\s*$', texto, re.MULTILINE)
        if importes:
            return self._convertir_europeo(importes[-1])
        
        # Alternativa: buscar todos los importes y tomar el mayor
        todos = re.findall(r'(\d+[.,]\d{2})\s*€', texto)
        if todos:
            valores = [self._convertir_europeo(v) for v in todos]
            return max(valores)
        
        return None
    
    def extraer_base_total(self, texto: str) -> Optional[float]:
        """
        Extrae base imponible.
        Formato: "Comentarios adicionales: 334,80 €" o "TOTAL 334,80 €"
        """
        patron = re.search(r'Comentarios\s+adicionales:\s*(\d+[.,]\d{2})\s*€', texto)
        if patron:
            return self._convertir_europeo(patron.group(1))
        return None
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo a float."""
        if not texto:
            return 0.0
        texto = texto.strip().replace('€', '').strip()
        if '.' in texto and ',' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            texto = texto.replace(',', '.')
        try:
            return float(texto)
        except:
            return 0.0


# ============================================================
# CÓDIGO DE PRUEBA
# ============================================================

if __name__ == '__main__':
    import sys
    
    extractor = ExtractorPabloRuiz()
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = '/mnt/user-data/uploads/4071_4T25_1030_PABLO_RUIZ_LA_DOLOROSA_TF.pdf'
    
    print(f"\n{'='*60}")
    print(f"PROBANDO EXTRACTOR PABLO RUIZ - LA DOLOROSA")
    print(f"{'='*60}")
    print(f"Archivo: {pdf_path}\n")
    
    texto = extractor.extraer_texto_pdfplumber(pdf_path)
    
    fecha = extractor.extraer_fecha(texto)
    num_factura = extractor.extraer_numero_factura(texto)
    total = extractor.extraer_total(texto)
    base_total = extractor.extraer_base_total(texto)
    lineas = extractor.extraer_lineas(texto)
    
    print(f"📅 Fecha: {fecha}")
    print(f"📄 Nº Factura: {num_factura}")
    print(f"💰 Base: {base_total}€")
    print(f"💰 TOTAL: {total}€")
    print(f"\n📦 LÍNEAS ({len(lineas)}):")
    print("-" * 80)
    
    suma_bases = 0
    for i, linea in enumerate(lineas, 1):
        print(f"  {i}. {linea['articulo']}")
        print(f"     Cant: {linea['cantidad']} x {linea['precio_ud']}€ = {linea['base']}€ (IVA {linea['iva']}%)")
        suma_bases += linea['base']
    
    print("-" * 80)
    
    if total:
        iva_calculado = round(suma_bases * 0.21, 2)
        total_calculado = round(suma_bases + iva_calculado, 2)
        diferencia = round(total - total_calculado, 2)
        cuadra = abs(diferencia) < 0.10
        
        print(f"\n✅ VALIDACIÓN DE CUADRE:")
        print(f"   Suma bases:      {round(suma_bases, 2)}€")
        print(f"   IVA 21%:         {iva_calculado}€")
        print(f"   Total calculado: {total_calculado}€")
        print(f"   Total factura:   {total}€")
        print(f"   Diferencia:      {diferencia}€")
        print(f"   {'✅ CUADRA' if cuadra else '❌ DESCUADRE'}")
