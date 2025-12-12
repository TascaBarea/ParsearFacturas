import sys
import re
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader

def extraer_texto_pdf(ruta):
    try:
        reader = PdfReader(str(ruta))
        texto = ""
        for page in reader.pages:
            texto += page.extract_text() or ""
        return texto
    except:
        return ""

def extraer_lineas_disber_v41(texto):
    """Extractor DISBER v3.41."""
    lineas = []
    iva = 10 if 'IVA 10%' in texto else 21
    
    patron_producto = re.compile(r'\[([A-Z0-9]+)\]\s*([^\[]+?)(?=\[|Base\s+Tipo|$)', re.DOTALL)
    
    for match in patron_producto.finditer(texto):
        codigo = match.group(1)
        desc_raw = match.group(2)
        desc = ' '.join(desc_raw.split())
        desc = re.sub(r'\s+[\d,\.]+\s*€?\s*$', '', desc)
        desc = re.sub(r'\s+\d+,\d+\s+\d+,\d+\s+\d+,\d+.*$', '', desc)
        desc = desc.strip()
        if len(desc) < 5:
            continue
        lineas.append({'codigo': codigo, 'articulo': desc[:60], 'iva': iva, 'base': 0})
    
    match_base = re.search(r'(\d+,\d{2})\s*€?\s*IVA\s*\d+%', texto)
    if match_base and lineas:
        base_total = float(match_base.group(1).replace(',', '.'))
        base_por_producto = round(base_total / len(lineas), 2)
        for linea in lineas:
            linea['base'] = base_por_producto
        if lineas:
            suma = sum(l['base'] for l in lineas[:-1])
            lineas[-1]['base'] = round(base_total - suma, 2)
    
    # Total factura
    total = None
    match_total = re.search(r'Total\s+([\d,]+)\s*€', texto)
    if match_total:
        total = float(match_total.group(1).replace(',', '.'))
    
    return lineas, total

def extraer_lineas_adell_v41(texto):
    """Extractor ADELL v3.41."""
    lineas = []
    
    patron = re.compile(
        r'(\d+[,.]\d{3})'
        r'([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s\d]+?)\s+'
        r'(\d+[,.]\d{3})\s+'
        r'(\d+[,.]\d{2})\s+'
        r'(\d+[,.]\d{2})'
        r'(\d{6})\s*-\s*\d{2}/\d{2}/\d{4}',
        re.MULTILINE
    )
    
    for match in patron.finditer(texto):
        cantidad, descripcion, precio, iva, subtotal, lote = match.groups()
        lineas.append({
            'codigo': '',
            'articulo': descripcion.strip()[:50],
            'iva': int(float(iva.replace(',', '.'))),
            'base': round(float(subtotal.replace(',', '.')), 2)
        })
    
    # Total factura
    total = None
    match_total = re.search(r'TOTAL FACTURA\s*\n?([\d,]+)\s*€', texto)
    if not match_total:
        match_total = re.search(r'([\d,]+)\s*€\s*$', texto, re.MULTILINE)
    if match_total:
        total = float(match_total.group(1).replace(',', '.'))
    
    return lineas, total

def calcular_total(lineas):
    return round(sum(l['base'] * (1 + l['iva']/100) for l in lineas), 2)

def main():
    archivos = [
        ("/mnt/user-data/uploads/1011_1T25_0109_GRUPO_DISBER_2_TF.pdf", "DISBER"),
        ("/mnt/user-data/uploads/1012_1T25_0109_GRUPO_DISBER_TF.pdf", "DISBER"),
        ("/mnt/user-data/uploads/1014_1T25_0109_PRODUCTOS_ADELL_TF.pdf", "ADELL"),
        ("/mnt/user-data/uploads/1082_1T25_0219_PRODUCTOS_ADELL_TF.pdf", "ADELL"),
    ]
    
    print("\n" + "="*70)
    print("DIAGNOSTICO DISBER/ADELL v3.41")
    print("="*70)
    
    for ruta, tipo in archivos:
        nombre = ruta.split('/')[-1]
        print(f"\n[{nombre}]")
        print("-"*50)
        
        texto = extraer_texto_pdf(ruta)
        if not texto:
            print("   ERROR: Sin texto")
            continue
        
        if tipo == "DISBER":
            lineas, total_fac = extraer_lineas_disber_v41(texto)
        else:
            lineas, total_fac = extraer_lineas_adell_v41(texto)
        
        print(f"   PRODUCTOS ({len(lineas)}):")
        for p in lineas:
            print(f"      {p.get('codigo',''):8s} | {p['articulo'][:35]:35s} | IVA {p['iva']:2d}% | {p['base']:8.2f}")
        
        total_calc = calcular_total(lineas)
        print(f"\n   Calculado: {total_calc:.2f} | Factura: {total_fac if total_fac else 'N/A'}")
        
        if total_fac:
            diff = total_calc - total_fac
            if abs(diff) < 0.05:
                print("   >> OK")
            else:
                print(f"   >> DESCUADRE: {diff:+.2f}")

if __name__ == '__main__':
    main()
