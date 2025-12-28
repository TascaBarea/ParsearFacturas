# -*- coding: utf-8 -*-
"""
Extractor para ECOMS SUPERMARKET S.L.
Supermercado local en C/ Huertas 72, Madrid

CIF: B72738602
Método: OCR (tickets escaneados)

Productos: alimentación general, limpieza, frescos
IVA: 4% (básicos), 10% (procesados), 21% (no alimentarios)

Creado: 28/12/2025
"""
# from extractores.base import ExtractorBase
# from extractores import registrar
from typing import List, Dict, Optional
import re
import subprocess
import tempfile
import os
import pdfplumber


# @registrar('ECOMS', 'ECOMS SUPERMARKET', 'ECOMS SUPERMARKET S.L.')
class ExtractorEcoms:  # (ExtractorBase):
    """Extractor para tickets de ECOMS SUPERMARKET."""
    
    nombre = 'ECOMS SUPERMARKET'
    cif = 'B72738602'
    iban = ''  # Pago en efectivo/tarjeta
    metodo_pdf = 'hibrido'  # pdfplumber + OCR fallback
    
    def extraer_texto(self, pdf_path: str) -> str:
        """
        Extrae texto del PDF usando método híbrido:
        1. Primero intenta pdfplumber (PDFs con texto)
        2. Si no hay texto, usa OCR (tickets escaneados)
        """
        # Método 1: pdfplumber (rápido)
        texto = self._extraer_pdfplumber(pdf_path)
        
        # Si hay texto suficiente, usarlo
        if texto and len(texto.strip()) > 100:
            return texto
        
        # Método 2: OCR (fallback para escaneados)
        return self._extraer_ocr(pdf_path)
    
    def _extraer_pdfplumber(self, pdf_path: str) -> str:
        """Extrae texto con pdfplumber."""
        try:
            texto_completo = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    texto = page.extract_text()
                    if texto:
                        texto_completo.append(texto)
            return '\n'.join(texto_completo)
        except Exception as e:
            return ''
    
    def _extraer_ocr(self, pdf_path: str) -> str:
        """Extrae texto del PDF usando OCR (Tesseract)."""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                img_path = os.path.join(tmpdir, 'page.png')
                
                # Convertir PDF a imagen alta resolución
                subprocess.run([
                    'pdftoppm', '-png', '-r', '300', '-singlefile',
                    pdf_path, os.path.join(tmpdir, 'page')
                ], capture_output=True, check=True)
                
                # OCR con Tesseract en español
                result = subprocess.run([
                    'tesseract', img_path, 'stdout', '-l', 'spa'
                ], capture_output=True, text=True)
                
                return result.stdout
        except Exception as e:
            return ''
    
    # Alias para compatibilidad
    def extraer_texto_ocr(self, pdf_path: str) -> str:
        """Alias para compatibilidad."""
        return self.extraer_texto(pdf_path)
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de productos del ticket.
        
        Formato típico:
        DESCRIPCION                    IMPORTE IVA%
        CANTIDAD DTO. DESCUENTO
        
        Ejemplo:
        LIMONES MALLA                  1,43269 4,00%
        1,91346X1 DTO. 0,48077
        """
        lineas = []
        
        # Patrón para líneas de producto
        # DESCRIPCION + IMPORTE + IVA%
        patron_linea = re.compile(
            r'^([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ0-9\s\-\.]+?)\s+'  # Descripción
            r'(\d+[,\.]\d+)\s+'                          # Importe
            r'(\d+)[,\.]00%',                            # IVA (4, 10, 21)
            re.MULTILINE
        )
        
        for match in patron_linea.finditer(texto):
            descripcion = match.group(1).strip()
            importe_str = match.group(2)
            iva = int(match.group(3))
            
            # Filtrar líneas no válidas
            if len(descripcion) < 3:
                continue
            if any(skip in descripcion for skip in ['TIPO IVA', 'TOTALES', 'FACTURA', 'DATOS', 'FISCALES']):
                continue
            
            importe = self._convertir_europeo(importe_str)
            
            if importe > 0:
                lineas.append({
                    'codigo': '',
                    'articulo': self._limpiar_descripcion(descripcion)[:50],
                    'cantidad': 1,
                    'precio_ud': importe,
                    'iva': iva,
                    'base': importe
                })
        
        # Si no encontramos líneas, intentar extraer del cuadro fiscal
        if not lineas:
            lineas = self._extraer_desde_cuadro_fiscal(texto)
        
        return lineas
    
    def _extraer_desde_cuadro_fiscal(self, texto: str) -> List[Dict]:
        """Extrae información mínima desde el cuadro fiscal."""
        lineas = []
        cuadro = self.extraer_cuadro_fiscal(texto)
        
        for item in cuadro:
            lineas.append({
                'codigo': '',
                'articulo': f'COMPRA IVA {item["tipo"]}%',
                'cantidad': 1,
                'precio_ud': item['base'],
                'iva': item['tipo'],
                'base': item['base']
            })
        
        return lineas
    
    def _limpiar_descripcion(self, desc: str) -> str:
        """Limpia la descripción de caracteres OCR erróneos."""
        # Eliminar caracteres extraños comunes en OCR
        desc = re.sub(r'[|¿¡\[\]{}]', '', desc)
        # Normalizar espacios
        desc = ' '.join(desc.split())
        return desc
    
    def extraer_cuadro_fiscal(self, texto: str) -> List[Dict]:
        """
        Extrae el cuadro de desglose de IVA.
        
        Formato:
        TIPO IVA    BASE    CUOTA
        4,00%       3,26    0,13
        10,00%      2,26    0,23
        21,00%      3,76    0,79
        """
        desglose = []
        
        # Buscar líneas del cuadro fiscal
        patron = re.compile(
            r'(\d+)[,\.]00%\s+'    # Tipo IVA (4, 10, 21)
            r'(\d+[,\.]\d+)\s+'    # Base
            r'(\d+[,\.]\d+)',      # Cuota
            re.MULTILINE
        )
        
        for match in patron.finditer(texto):
            tipo = int(match.group(1))
            base = self._convertir_europeo(match.group(2))
            cuota = self._convertir_europeo(match.group(3))
            
            if tipo in [4, 10, 21] and base > 0:
                desglose.append({
                    'tipo': tipo,
                    'base': base,
                    'iva': cuota
                })
        
        return desglose
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """Extrae el total de la factura."""
        # Buscar TOTAL FACTURA seguido de importe
        patrones = [
            r'TOTAL\s+FACTURA\s+(\d+[,\.]\d+)',
            r'TOTAL\s+FAÉTURA\s+(\d+[,\.]\d+)',  # Error OCR común
            r'TOTAL\s+FACT[UÚ]RA\s+(\d+[,\.]\d+)',
        ]
        
        for patron in patrones:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                return self._convertir_europeo(match.group(1))
        
        # Alternativa: calcular desde cuadro fiscal
        cuadro = self.extraer_cuadro_fiscal(texto)
        if cuadro:
            return round(sum(d['base'] + d['iva'] for d in cuadro), 2)
        
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """
        Extrae número de factura.
        Formato: FT 139080XXXXXX
        """
        patron = re.search(r'N\.?\s*FACTURA:?\s*(FT\s*\d+)', texto, re.IGNORECASE)
        if patron:
            # Limpiar espacios
            return patron.group(1).replace(' ', '')
        
        # Alternativa sin FT
        patron2 = re.search(r'FACTURA:?\s*(\d{12,})', texto, re.IGNORECASE)
        if patron2:
            return f'FT{patron2.group(1)}'
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de emisión."""
        patron = re.search(r'EMITIDA:?\s*(\d{2}-\d{2}-\d{4})', texto, re.IGNORECASE)
        if patron:
            # Convertir de DD-MM-YYYY a DD/MM/YYYY
            fecha = patron.group(1).replace('-', '/')
            return fecha
        return None
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo a float."""
        if not texto:
            return 0.0
        texto = str(texto).strip()
        # Manejar tanto coma como punto decimal
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
    
    extractor = ExtractorEcoms()
    
    # Buscar PDFs de ECOMS
    if len(sys.argv) > 1:
        pdfs = sys.argv[1:]
    else:
        pdfs = glob.glob('/mnt/user-data/uploads/*ECOMS*.pdf')[:5]
    
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
        
        # Indicar método usado
        metodo_usado = "pdfplumber" if len(extractor._extraer_pdfplumber(pdf_path).strip()) > 100 else "OCR"
        print(f"📝 Método: {metodo_usado}")
        
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
                print(f"  {i}. {linea['articulo']} - {linea['base']}€ (IVA {linea['iva']}%)")
                suma_bases += linea['base']
            
            # Validación
            if cuadro and total:
                total_cuadro = sum(d['base'] + d['iva'] for d in cuadro)
                diff = abs(total - total_cuadro)
                cuadra = diff < 0.10
                
                print(f"\n✅ VALIDACIÓN:")
                print(f"   Total factura: {total}€")
                print(f"   Total cuadro:  {round(total_cuadro, 2)}€")
                print(f"   {'✅ CUADRA' if cuadra else f'❌ Diferencia: {diff:.2f}€'}")
                
                if cuadra:
                    total_ok += 1
        else:
            print("❌ No se extrajeron líneas")
    
    print(f"\n{'='*60}")
    print(f"RESUMEN: {total_ok}/{total_facturas} facturas OK")
    print('='*60)
