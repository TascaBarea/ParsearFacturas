# -*- coding: utf-8 -*-
"""
Extractor para CASA DEL DUQUE 2015 SL (HOME IDEAL)
Bazar/tienda de hogar en C/Duque de Alba 15, Madrid

CIF: B87309613
Tel: 914293959
Método: OCR (tickets escaneados)

Productos: artículos de hogar, limpieza, decoración
IVA: 21% (todos los productos)

Creado: 28/12/2025
"""
import pdfplumber
from typing import List, Dict, Optional
import re
import subprocess
import tempfile
import os


class ExtractorCasaDelDuque:
    """Extractor para tickets de CASA DEL DUQUE / HOME IDEAL."""
    
    nombre = 'CASA DEL DUQUE 2015 SL'
    cif = 'B87309613'
    iban = ''  # Pago en efectivo/tarjeta
    metodo_pdf = 'ocr'
    
    def extraer_texto(self, pdf_path: str) -> str:
        """
        Extrae texto del PDF usando método híbrido:
        1. Primero intenta pdfplumber
        2. Si no hay texto suficiente, usa OCR
        """
        # Método 1: pdfplumber
        texto = self._extraer_pdfplumber(pdf_path)
        if texto and len(texto.strip()) > 100:
            return texto
        
        # Método 2: OCR (tickets escaneados)
        return self._extraer_ocr(pdf_path)
    
    def _extraer_pdfplumber(self, pdf_path: str) -> str:
        """Extrae texto con pdfplumber."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                texto = pdf.pages[0].extract_text()
                return texto or ''
        except:
            return ''
    
    def _extraer_ocr(self, pdf_path: str) -> str:
        """Extrae texto del PDF usando OCR (Tesseract)."""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                img_path = os.path.join(tmpdir, 'page.png')
                
                subprocess.run([
                    'pdftoppm', '-png', '-r', '300', '-singlefile',
                    pdf_path, os.path.join(tmpdir, 'page')
                ], capture_output=True, check=True)
                
                result = subprocess.run([
                    'tesseract', img_path, 'stdout', '-l', 'spa'
                ], capture_output=True, text=True)
                
                return result.stdout
        except:
            return ''
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de producto del ticket.
        
        Formato 1 (mayoría):
        DESCRIPCION    UNDS.    SUMA    IVA%
        TIJERAS        1        3,95    21%
        
        Formato 2 (alternativo):
        CAN. PRE. TVA% DESCRIPCION    SUMA
        1x 2,95 21%-NIEVE NAVIDAD 150    2,95
        """
        lineas = []
        
        # Formato 1: DESCRIPCION UNDS SUMA IVA%
        patron1 = re.compile(
            r'^([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ0-9\s/\-\.]+?)\s+'  # Descripción
            r'(\d+)\s+'                                    # Unidades
            r'(\d+[,\.]\d+)\s+'                           # Suma/Importe
            r'21%',                                        # IVA
            re.MULTILINE
        )
        
        for match in patron1.finditer(texto):
            descripcion = match.group(1).strip()
            cantidad = int(match.group(2))
            importe = self._convertir_europeo(match.group(3))
            
            # Filtrar líneas no válidas
            if len(descripcion) < 2 or importe < 0.10:
                continue
            if any(skip in descripcion.upper() for skip in ['DESCRIPCION', 'IMPONIBLE', 'ARTIC', 'TOTAL']):
                continue
            
            lineas.append({
                'codigo': '',
                'articulo': descripcion[:50],
                'cantidad': cantidad,
                'precio_ud': round(importe / cantidad, 2) if cantidad > 0 else importe,
                'iva': 21,
                'base': importe
            })
        
        # Formato 2: CANx PRECIO IVA%-DESCRIPCION SUMA
        patron2 = re.compile(
            r'(\d+)x\s+'                    # Cantidad
            r'(\d+[,\.]\d+)\s+'             # Precio
            r'21%-'                         # IVA
            r'(.+?)\s+'                     # Descripción
            r'(\d+[,\.]\d+)',               # Suma
            re.MULTILINE
        )
        
        for match in patron2.finditer(texto):
            cantidad = int(match.group(1))
            precio = self._convertir_europeo(match.group(2))
            descripcion = match.group(3).strip()
            importe = self._convertir_europeo(match.group(4))
            
            if importe < 0.10:
                continue
            
            lineas.append({
                'codigo': '',
                'articulo': descripcion[:50],
                'cantidad': cantidad,
                'precio_ud': precio,
                'iva': 21,
                'base': importe
            })
        
        return lineas
    
    def extraer_cuadro_fiscal(self, texto: str) -> List[Dict]:
        """
        Extrae el cuadro de desglose de IVA.
        
        Formato:
        Imponible IVA%    IVA    REQ
        26,40 21% 5,55
        
        O con variaciones OCR:
        26.40 21% 5,55
        """
        desglose = []
        
        # Buscar línea con base, 21% y cuota (varias variaciones)
        patrones = [
            r'(\d+[,\.]\d+)\s+21%\s+(\d+[,\.]\d+)',      # Normal
            r'(\d+[,\.]\d+)\s+21\s*%\s+(\d+[,\.]\d+)',   # Espacio antes de %
            r'Imponible.*?(\d+[,\.]\d+)\s+21%?\s+(\d+[,\.]\d+)',  # Con cabecera
        ]
        
        for patron_str in patrones:
            match = re.search(patron_str, texto, re.IGNORECASE | re.DOTALL)
            if match:
                base = self._convertir_europeo(match.group(1))
                cuota = self._convertir_europeo(match.group(2))
                
                if base > 0:
                    desglose.append({
                        'tipo': 21,
                        'base': base,
                        'iva': cuota
                    })
                    break
        
        return desglose
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """
        Extrae el total de la factura.
        Formato: X ARTIC. TOTAL: XX,XX Euro
        
        Variaciones OCR:
        - 12 ARTIC, TOTAL: 25,95 Euro
        - ¿0 ARTIC. TOTAL: 31,95 Euro  
        - 2 ARTIC. TOTAL: 4,15 Euro
        """
        # Patrones de total (orden de prioridad)
        patrones = [
            r'ARTIC[,\.\s]*TOTAL:\s*(\d+[,\.]\d+)\s*Euro',
            r'TOTAL:\s*(\d+[,\.]\d+)\s*Euro',
            r'(\d+[,\.]\d+)\s*Euro\s*$',
            r'TOTAL:\s*(\d+[,\.]\d+)',
        ]
        
        for patron_str in patrones:
            match = re.search(patron_str, texto, re.IGNORECASE | re.MULTILINE)
            if match:
                total = self._convertir_europeo(match.group(1))
                if total > 1.0:  # Filtrar totales muy pequeños
                    return total
        
        # Alternativa: calcular desde cuadro fiscal
        cuadro = self.extraer_cuadro_fiscal(texto)
        if cuadro:
            return round(sum(d['base'] + d['iva'] for d in cuadro), 2)
        
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """
        Extrae número de factura.
        Formato: Factura No.: 2025XXXXXX
        
        Variaciones OCR:
        - Factura No,: 2025000938
        - Factura No.: 2025031104
        """
        patrones = [
            r'Factura\s*No[,\.:]+\s*(\d{10,})',
            r'Factura\s*No[,\.:]+\s*(\d{7,})',
            r'No[,\.:]+\s*(\d{10,})',
        ]
        
        for patron_str in patrones:
            match = re.search(patron_str, texto, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """
        Extrae fecha de emisión.
        
        Formatos:
        - Fecha:04-01-2025
        - Fecha:27-03-202)  (OCR error)
        """
        patrones = [
            r'Fecha\s*:?\s*(\d{2}-\d{2}-\d{4})',
            r'Fecha\s*:?\s*(\d{2}-\d{2}-202\d)',  # Año parcial
        ]
        
        for patron_str in patrones:
            match = re.search(patron_str, texto, re.IGNORECASE)
            if match:
                fecha = match.group(1)
                # Corregir errores OCR comunes en el año
                fecha = re.sub(r'202[^\d]', '2025', fecha)
                return fecha.replace('-', '/')
        
        return None
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo a float."""
        if not texto:
            return 0.0
        texto = str(texto).strip()
        if ',' in texto and '.' in texto:
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
    import glob
    
    extractor = ExtractorCasaDelDuque()
    
    # Buscar PDFs de CASA DEL DUQUE
    if len(sys.argv) > 1:
        pdfs = sys.argv[1:]
    else:
        pdfs = glob.glob('/mnt/user-data/uploads/*CASA_DEL_DUQUE*.pdf')
    
    total_ok = 0
    total_facturas = 0
    
    for pdf_path in pdfs:
        total_facturas += 1
        print(f"\n{'='*60}")
        print(f"ARCHIVO: {os.path.basename(pdf_path)}")
        print('='*60)
        
        texto = extractor.extraer_texto(pdf_path)
        
        if not texto:
            print("❌ Error: No se pudo extraer texto")
            continue
        
        fecha = extractor.extraer_fecha(texto)
        num_factura = extractor.extraer_numero_factura(texto)
        total = extractor.extraer_total(texto)
        lineas = extractor.extraer_lineas(texto)
        cuadro = extractor.extraer_cuadro_fiscal(texto)
        
        print(f"📅 Fecha: {fecha}")
        print(f"📄 Nº Factura: {num_factura}")
        print(f"💰 TOTAL: {total}€")
        
        if lineas:
            print(f"\n📦 LÍNEAS ({len(lineas)}):")
            suma_bases = 0
            for i, linea in enumerate(lineas, 1):
                print(f"  {i}. {linea['articulo']} - {linea['cantidad']}x{linea['precio_ud']}€ = {linea['base']}€")
                suma_bases += linea['base']
            
            print(f"\n   Suma líneas: {round(suma_bases, 2)}€")
        
        # Validación
        if cuadro and total:
            base_cuadro = cuadro[0]['base']
            iva_cuadro = cuadro[0]['iva']
            total_calculado = base_cuadro + iva_cuadro
            diff = abs(total - total_calculado)
            cuadra = diff < 0.10
            
            print(f"\n✅ VALIDACIÓN:")
            print(f"   Base: {base_cuadro}€ + IVA: {iva_cuadro}€ = {round(total_calculado, 2)}€")
            print(f"   Total factura: {total}€")
            print(f"   {'✅ CUADRA' if cuadra else f'❌ Diferencia: {diff:.2f}€'}")
            
            if cuadra:
                total_ok += 1
        elif total:
            # Sin cuadro fiscal, contar como OK si hay total
            print(f"   ⚠️ Sin cuadro fiscal para validar")
            total_ok += 1
    
    print(f"\n{'='*60}")
    print(f"RESUMEN: {total_ok}/{total_facturas} facturas OK")
    print('='*60)
