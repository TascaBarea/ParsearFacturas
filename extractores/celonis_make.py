# -*- coding: utf-8 -*-
"""
Extractor para CELONIS INC. (Make.com)
Plataforma de automatización SaaS

Proveedor: Celonis Inc.
Ubicación: One World Trade Center, New York, NY 10007, USA
US EIN: 61-1797223
Email: billing@make.com

Producto: Make Core plan (10000 operations/month)
Importe fijo: $10.59 USD/mes
Moneda: USD (sin IVA - empresa americana)

Categoría: GASTOS VARIOS
Artículo: Servicios informáticos

Creado: 28/12/2025
"""
import pdfplumber
from typing import List, Dict, Optional
import re
import os


class ExtractorCelonisMake:
    """Extractor para facturas de Celonis Inc. (Make.com)."""
    
    nombre = 'CELONIS INC.'
    cif = ''  # Empresa americana - US EIN 61-1797223
    iban = ''  # Pago con tarjeta
    metodo_pdf = 'pdfplumber'
    categoria = 'GASTOS VARIOS'
    articulo = 'Servicios informáticos'
    moneda = 'USD'
    
    def extraer_texto(self, pdf_path: str) -> str:
        """Extrae texto del PDF."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                texto = pdf.pages[0].extract_text()
                return texto or ''
        except:
            return ''
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de producto.
        
        Producto único: Make Core plan
        """
        lineas = []
        
        # Buscar importe del plan Make
        patron = re.search(r'\$(\d+[,\.]\d+)\s+\$(\d+[,\.]\d+)\s*$', texto, re.MULTILINE)
        if patron:
            precio = self._convertir_numero(patron.group(1))
            importe = self._convertir_numero(patron.group(2))
            
            # Extraer período
            periodo = self._extraer_periodo(texto)
            descripcion = f"Make Core plan 10000 ops/mes"
            if periodo:
                descripcion += f" ({periodo})"
            
            lineas.append({
                'codigo': 'MAKE-CORE',
                'articulo': descripcion[:50],
                'cantidad': 1,
                'precio_ud': precio,
                'iva': 0,  # Sin IVA (empresa USA)
                'base': importe
            })
        
        return lineas
    
    def _extraer_periodo(self, texto: str) -> Optional[str]:
        """Extrae el período de facturación."""
        # Formato: "Nov 15 – Dec 15, 2025" o similar
        patron = re.search(r'([A-Z][a-z]{2}\s+\d+)\s*[–-]\s*([A-Z][a-z]{2}\s+\d+,\s*\d{4})', texto)
        if patron:
            return f"{patron.group(1)} - {patron.group(2)}"
        return None
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """
        Extrae el total de la factura.
        
        Formatos:
        - Amount due $10.59 USD
        - Amount paid $10.59
        - Total $10.59
        """
        patrones = [
            r'Amount\s+(?:due|paid)\s+\$(\d+[,\.]\d+)',
            r'Total\s+\$(\d+[,\.]\d+)',
            r'\$(\d+[,\.]\d+)\s+USD\s+due',
        ]
        
        for patron_str in patrones:
            match = re.search(patron_str, texto, re.IGNORECASE)
            if match:
                return self._convertir_numero(match.group(1))
        
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """
        Extrae número de factura.
        Formato: 556A1AE0-XXXX
        """
        # El PDF tiene caracteres nulos, buscar patrón flexible
        patron = re.search(r'Invoice\s+number\s+([A-Z0-9\-]+)', texto, re.IGNORECASE)
        if patron:
            num = patron.group(1)
            # Limpiar caracteres extraños
            num = re.sub(r'[^\w\-]', '-', num)
            return num
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """
        Extrae fecha de emisión.
        Formato: "November 15, 2025" → "15/11/2025"
        """
        meses = {
            'January': '01', 'February': '02', 'March': '03', 'April': '04',
            'May': '05', 'June': '06', 'July': '07', 'August': '08',
            'September': '09', 'October': '10', 'November': '11', 'December': '12'
        }
        
        patron = re.search(r'Date\s+(?:of\s+issue|paid)\s+([A-Z][a-z]+)\s+(\d{1,2}),\s+(\d{4})', texto)
        if patron:
            mes_nombre = patron.group(1)
            dia = patron.group(2).zfill(2)
            año = patron.group(3)
            mes = meses.get(mes_nombre, '01')
            return f"{dia}/{mes}/{año}"
        
        return None
    
    def extraer_tipo_documento(self, texto: str) -> str:
        """Determina si es Invoice o Receipt."""
        if 'Receipt' in texto:
            return 'RECEIPT'
        return 'INVOICE'
    
    def _convertir_numero(self, texto: str) -> float:
        """Convierte número americano a float."""
        if not texto:
            return 0.0
        texto = str(texto).strip()
        texto = texto.replace(',', '')  # Americano: 1,000.00
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
    
    extractor = ExtractorCelonisMake()
    
    # Buscar PDFs de CELONIS/MAKE
    if len(sys.argv) > 1:
        pdfs = sys.argv[1:]
    else:
        pdfs = glob.glob('/mnt/user-data/uploads/*CELONIS*.pdf') + \
               glob.glob('/mnt/user-data/uploads/*MAKE*.pdf')
    
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
        
        tipo_doc = extractor.extraer_tipo_documento(texto)
        fecha = extractor.extraer_fecha(texto)
        num_factura = extractor.extraer_numero_factura(texto)
        total = extractor.extraer_total(texto)
        lineas = extractor.extraer_lineas(texto)
        
        print(f"📋 Tipo: {tipo_doc}")
        print(f"📅 Fecha: {fecha}")
        print(f"📄 Nº Factura: {num_factura}")
        print(f"💰 TOTAL: ${total} USD")
        
        if lineas:
            print(f"\n📦 LÍNEAS ({len(lineas)}):")
            for i, linea in enumerate(lineas, 1):
                print(f"  {i}. {linea['articulo']}")
                print(f"     ${linea['base']} USD (sin IVA - empresa USA)")
        
        # Validación simple
        if total and total > 0:
            print(f"\n✅ VALIDACIÓN: Total extraído correctamente")
            total_ok += 1
        else:
            print(f"\n❌ No se pudo extraer total")
    
    print(f"\n{'='*60}")
    print(f"RESUMEN: {total_ok}/{total_facturas} facturas OK")
    print('='*60)
