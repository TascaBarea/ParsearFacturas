# -*- coding: utf-8 -*-
"""
Extractor para BODEGA VIRGEN DE LA SIERRA S.COOP.
Bodega cooperativa en Villarroya de la Sierra, Zaragoza

CIF: F50019868
Método: pdfplumber (PDFs con texto)

Productos: vinos (Albada, Vendimia Seleccionada), portes
IVA: 21% (bebidas alcohólicas)

Creado: 28/12/2025
"""
import pdfplumber
from typing import List, Dict, Optional
import re
import os
import subprocess
import tempfile


class ExtractorVirgenDeLaSierra:
    """Extractor para facturas de Bodega Virgen de la Sierra."""
    
    nombre = 'BODEGA VIRGEN DE LA SIERRA'
    cif = 'F50019868'
    iban = ''  # Por determinar - usa RECIBO o TRANSFERENCIA
    metodo_pdf = 'hibrido'  # pdfplumber + OCR fallback
    
    def extraer_texto(self, pdf_path: str) -> str:
        """
        Extrae texto del PDF usando método híbrido:
        1. Primero intenta pdfplumber (PDFs con texto)
        2. Si no hay texto, usa OCR (PDFs escaneados)
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
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de productos del ticket.
        
        Formato típico:
        201-02023 C.P. VENDIMIA SELECCIONADA 2023 48,00 4,600000 220,80
        202-00025 ALBADA PARAJE CAÑADILLA 2,00 8,000000 16,00
        115-10004 PORTES TRANSPORTE 1,00 25,000000 25,00
        """
        lineas = []
        
        # Patrón para líneas de producto con código
        # CODIGO DESCRIPCION CANTIDAD PRECIO IMPORTE
        patron_linea = re.compile(
            r'^(\d{3}-\d{5})\s+'           # Código (ej: 201-02023)
            r'(.+?)\s+'                     # Descripción
            r'(\d+[,\.]\d+)\s+'             # Cantidad
            r'(\d+[,\.]\d+)\s+'             # Precio unitario
            r'(\d+[,\.]\d+)$',              # Importe
            re.MULTILINE
        )
        
        for match in patron_linea.finditer(texto):
            codigo = match.group(1)
            descripcion = match.group(2).strip()
            cantidad = self._convertir_europeo(match.group(3))
            precio = self._convertir_europeo(match.group(4))
            importe = self._convertir_europeo(match.group(5))
            
            # Limpiar descripción (quitar años duplicados, etc.)
            descripcion = self._limpiar_descripcion(descripcion)
            
            if importe > 0:
                lineas.append({
                    'codigo': codigo,
                    'articulo': descripcion[:50],
                    'cantidad': cantidad,
                    'precio_ud': precio,
                    'iva': 21,  # Vinos siempre 21%
                    'base': importe
                })
        
        return lineas
    
    def _limpiar_descripcion(self, desc: str) -> str:
        """Limpia la descripción de caracteres extra."""
        # Eliminar "Uds. X" que aparece en algunas líneas
        desc = re.sub(r'\s+Uds\.\s*\d+', '', desc)
        # Normalizar espacios
        desc = ' '.join(desc.split())
        return desc
    
    def extraer_cuadro_fiscal(self, texto: str) -> List[Dict]:
        """
        Extrae el cuadro de desglose de IVA.
        
        Formato:
        Base imponible % IVA Importe IVA Recargo
        288,80 21,00 60,65
        """
        desglose = []
        
        # Buscar línea con base, tipo IVA y cuota
        patron = re.compile(
            r'(\d+[,\.]\d+)\s+'       # Base imponible
            r'21[,\.]00\s+'           # Tipo IVA (siempre 21%)
            r'(\d+[,\.]\d+)',         # Cuota IVA
            re.MULTILINE
        )
        
        match = patron.search(texto)
        if match:
            base = self._convertir_europeo(match.group(1))
            cuota = self._convertir_europeo(match.group(2))
            
            desglose.append({
                'tipo': 21,
                'base': base,
                'iva': cuota
            })
        
        return desglose
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """Extrae el total de la factura."""
        # Buscar formato XXX,XX€
        patron1 = re.search(r'(\d+[,\.]\d+)€', texto)
        if patron1:
            return self._convertir_europeo(patron1.group(1))
        
        # Alternativa: "Total" seguido de importe
        patron2 = re.search(r'Total\s+(\d+[,\.]\d+)', texto, re.IGNORECASE)
        if patron2:
            return self._convertir_europeo(patron2.group(1))
        
        # Calcular desde cuadro fiscal
        cuadro = self.extraer_cuadro_fiscal(texto)
        if cuadro:
            return round(sum(d['base'] + d['iva'] for d in cuadro), 2)
        
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """
        Extrae número de factura.
        Formato: FV00250XXX
        """
        patron = re.search(r'(FV\d{8,})', texto)
        if patron:
            return patron.group(1)
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """
        Extrae fecha de emisión.
        Formato en PDF: DD-MM-YYYY
        """
        # Buscar fecha después de "Fecha" o al principio
        patron = re.search(r'(\d{2}-\d{2}-\d{4})', texto)
        if patron:
            # Convertir de DD-MM-YYYY a DD/MM/YYYY
            fecha = patron.group(1).replace('-', '/')
            return fecha
        return None
    
    def extraer_metodo_pago(self, texto: str) -> Optional[str]:
        """Extrae el método de pago."""
        if 'TRANSFERENCIA' in texto.upper():
            return 'TRANSFERENCIA'
        elif 'RECIBO' in texto.upper():
            return 'RECIBO'
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
    
    extractor = ExtractorVirgenDeLaSierra()
    
    # Buscar PDFs de VIRGEN DE LA SIERRA
    if len(sys.argv) > 1:
        pdfs = sys.argv[1:]
    else:
        pdfs = glob.glob('/mnt/user-data/uploads/*VIRGEN*.pdf')[:5]
    
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
        metodo_pago = extractor.extraer_metodo_pago(texto)
        lineas = extractor.extraer_lineas(texto)
        cuadro = extractor.extraer_cuadro_fiscal(texto)
        
        print(f"📅 Fecha: {fecha}")
        print(f"📄 Nº Factura: {num_factura}")
        print(f"💳 Método pago: {metodo_pago}")
        print(f"💰 TOTAL: {total}€")
        
        if lineas:
            print(f"\n📦 LÍNEAS ({len(lineas)}):")
            suma_bases = 0
            for i, linea in enumerate(lineas, 1):
                print(f"  {i}. [{linea['codigo']}] {linea['articulo']}")
                print(f"     {linea['cantidad']} x {linea['precio_ud']}€ = {linea['base']}€")
                suma_bases += linea['base']
            
            print(f"\n   Suma bases: {round(suma_bases, 2)}€")
            
            # Validación
            if cuadro and total:
                base_cuadro = cuadro[0]['base']
                iva_cuadro = cuadro[0]['iva']
                total_calculado = base_cuadro + iva_cuadro
                diff = abs(total - total_calculado)
                cuadra = diff < 0.10
                
                print(f"\n✅ VALIDACIÓN:")
                print(f"   Base imponible: {base_cuadro}€")
                print(f"   IVA 21%: {iva_cuadro}€")
                print(f"   Total calculado: {round(total_calculado, 2)}€")
                print(f"   Total factura: {total}€")
                print(f"   {'✅ CUADRA' if cuadra else f'❌ Diferencia: {diff:.2f}€'}")
                
                # Verificar suma de líneas vs base
                diff_lineas = abs(suma_bases - base_cuadro)
                if diff_lineas < 0.10:
                    print(f"   ✅ Líneas cuadran con base")
                else:
                    print(f"   ⚠️ Diferencia líneas vs base: {diff_lineas:.2f}€")
                
                if cuadra:
                    total_ok += 1
        else:
            print("❌ No se extrajeron líneas")
    
    print(f"\n{'='*60}")
    print(f"RESUMEN: {total_ok}/{total_facturas} facturas OK")
    print('='*60)
