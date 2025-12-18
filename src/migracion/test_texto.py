from migracion_historico_2025_v3_55 import *
from pathlib import Path

pdf = r"C:\Users\jaime\Dropbox\File inviati\TASCA BAREA S.L.L\CONTABILIDAD\FACTURAS 2025\FACTURAS RECIBIDAS\2 TRI 2025\2082 2T25 0505 MANIPULADOS ABELLAN TF.pdf"
texto = extraer_texto_pdf(Path(pdf), 'MANIPULADOS ABELLAN')
print("=== TEXTO OCR ===")
print(texto)
print("\n=== LINEAS EXTRAIDAS ===")
lineas = extraer_lineas_manipulados_abellan(texto)
for l in lineas:
    print(f"  {l['base']:>6.2f} - {l['articulo']}")
print(f"\nTotal lineas: {len(lineas)}, Suma bases: {sum(l['base'] for l in lineas):.2f}")
