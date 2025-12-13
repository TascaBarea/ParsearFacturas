#!/usr/bin/env python3
"""
Diagnóstico de facturas de alquiler (BENJAMIN ORTEGA / JAIME FERNANDEZ)
Ejecutar en la carpeta donde está la factura.
"""
import re
from pypdf import PdfReader
import sys

def diagnostico(pdf_path):
    print(f"\n=== DIAGNÓSTICO: {pdf_path} ===\n")
    
    reader = PdfReader(pdf_path)
    texto = reader.pages[0].extract_text()
    
    print("1. TEXTO EXTRAÍDO:")
    print("-" * 40)
    print(texto)
    print("-" * 40)
    
    print("\n2. EXTRACCIÓN DE TOTAL:")
    # Patrón para retención
    patron_ret = r'RETENCION\s*\d+%?\s*-?\d+[.,]\d{2}\s*€?\s*\n?\s*TOTAL\s+(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*€?'
    match_ret = re.search(patron_ret, texto, re.IGNORECASE | re.MULTILINE)
    if match_ret:
        print(f"   ✅ Patrón RETENCIÓN encontró: {match_ret.group(1)}")
    else:
        print("   ❌ Patrón RETENCIÓN NO encontró nada")
    
    # Patrón genérico
    patron_gen = r'\bTOTAL[:\s]+(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*€'
    match_gen = re.search(patron_gen, texto, re.IGNORECASE)
    if match_gen:
        print(f"   ℹ️  Patrón genérico encontró: {match_gen.group(1)}")
    
    print("\n3. EXTRACCIÓN DE BASE:")
    patron_sub = r'SUBTOTAL\s+(\d+[.,]\d{2})'
    match_sub = re.search(patron_sub, texto, re.IGNORECASE)
    if match_sub:
        base = float(match_sub.group(1).replace(',', '.'))
        print(f"   ✅ Base (SUBTOTAL): {base}")
    else:
        print("   ❌ No encontró SUBTOTAL")
        base = 500.0
    
    print("\n4. CÁLCULO DE CUADRE:")
    total = float(match_ret.group(1).replace(',', '.')) if match_ret else 0
    iva = base * 0.21
    retencion = base * 0.19
    total_calc = base + iva - retencion
    
    print(f"   Base:       {base:.2f}")
    print(f"   IVA 21%:    {iva:.2f}")
    print(f"   Ret 19%:   -{retencion:.2f}")
    print(f"   Calculado:  {total_calc:.2f}")
    print(f"   Factura:    {total:.2f}")
    print(f"   Diferencia: {abs(total - total_calc):.2f}")
    
    if abs(total - total_calc) <= 0.05:
        print("\n   ✅ CUADRE OK")
    else:
        print("\n   ❌ DESCUADRE")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python diagnostico_alquiler.py <ruta_factura.pdf>")
        sys.exit(1)
    diagnostico(sys.argv[1])
