# -*- coding: utf-8 -*-
"""
Script de diagnóstico para VIRGEN DE LA SIERRA
Ejecutar: python test_virgen.py
"""
import os
import sys

# Asegurar que estamos en el directorio correcto
if os.path.exists('extractores'):
    print("✓ Carpeta extractores encontrada")
else:
    print("✗ ERROR: Ejecuta desde ParsearFacturas-main")
    sys.exit(1)

# Importar el extractor
from extractores import obtener_extractor, listar_extractores
import pdfplumber

print("\n" + "="*60)
print("DIAGNÓSTICO VIRGEN DE LA SIERRA")
print("="*60)

# 1. Verificar registro
extractores = listar_extractores()
virgen_keys = [k for k in extractores if 'VIRGEN' in k]
print(f"\n1. Extractores registrados con 'VIRGEN': {virgen_keys}")

# 2. Obtener el extractor
ext = obtener_extractor('VIRGEN DE LA SIERRA')
print(f"\n2. Extractor obtenido: {ext}")
print(f"   Clase: {type(ext).__name__ if ext else 'None'}")

if not ext:
    print("\n✗ ERROR: No se pudo obtener el extractor")
    sys.exit(1)

# 3. Buscar una factura de prueba
facturas_virgen = []
for root, dirs, files in os.walk('.'):
    for f in files:
        if 'VIRGEN' in f.upper() and f.endswith('.pdf'):
            facturas_virgen.append(os.path.join(root, f))

print(f"\n3. Facturas encontradas: {len(facturas_virgen)}")

if not facturas_virgen:
    print("   No hay facturas de VIRGEN para probar")
    sys.exit(0)

# 4. Probar con la primera factura
pdf_path = facturas_virgen[0]
print(f"\n4. Probando con: {os.path.basename(pdf_path)}")

try:
    with pdfplumber.open(pdf_path) as pdf:
        texto = '\n'.join([p.extract_text() or '' for p in pdf.pages])
    print(f"   Texto extraído: {len(texto)} caracteres")
except Exception as e:
    print(f"   ✗ Error extrayendo texto: {e}")
    sys.exit(1)

# 5. Probar extraer_lineas
print("\n5. Probando extraer_lineas():")
try:
    lineas = ext.extraer_lineas(texto)
    print(f"   Líneas encontradas: {len(lineas)}")
    for l in lineas[:5]:  # Máximo 5
        print(f"   - {l.get('codigo', '')} | {l.get('articulo', '')[:30]} | {l.get('base', 0):.2f}€")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# 6. Probar extraer_total
print("\n6. Probando extraer_total():")
try:
    total = ext.extraer_total(texto)
    print(f"   Total: {total}€")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# 7. Validación
print("\n" + "="*60)
if lineas and total:
    suma_bases = sum(l.get('base', 0) for l in lineas)
    total_calculado = round(suma_bases * 1.21, 2)
    diff = abs(total - total_calculado)
    
    print(f"Suma bases: {suma_bases:.2f}€")
    print(f"Total calculado (x1.21): {total_calculado:.2f}€")
    print(f"Total PDF: {total:.2f}€")
    print(f"Diferencia: {diff:.2f}€")
    
    if diff < 0.10:
        print("\n✅ EXTRACTOR FUNCIONA CORRECTAMENTE")
    else:
        print(f"\n⚠️ DESCUADRE DE {diff:.2f}€")
else:
    if not lineas:
        print("✗ No se extrajeron líneas")
    if not total:
        print("✗ No se extrajo total")

print("="*60)
