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

def extraer_lineas_felisa_v40(texto):
    """Extractor FELISA v3.40."""
    lineas = []
    
    patron = re.compile(
        r'^([A-Z][A-Z0-9\s]+?)\s+'
        r'(\d+,\d{4})\s+'
        r'(\d+,\d{2})'
        r'([A-Z][A-Z0-9]+)\s+'
        r'([\d,]+)\s+'
        r'(?:Unidades|Kilos)',
        re.MULTILINE
    )
    
    for match in patron.finditer(texto):
        desc, precio, importe, codigo, cantidad = match.groups()
        desc_limpia = desc.strip()
        if 'Albaran' in desc_limpia or 'Lote:' in desc_limpia or 'TOTAL' in desc_limpia:
            continue
        if len(desc_limpia) < 5:
            continue
        lineas.append({
            'codigo': codigo, 'articulo': desc_limpia,
            'iva': 10, 'base': float(importe.replace(',', '.'))
        })
    
    # TRANSPORTE
    if 'TRANSPORTE' in texto:
        match_transp = re.search(r'TRANSPORTE\n[\d,]+\n([\d,]+)', texto)
        if match_transp:
            lineas.append({
                'codigo': 'TRANSP', 'articulo': 'TRANSPORTE',
                'iva': 21, 'base': float(match_transp.group(1).replace(',', '.'))
            })
        else:
            match_transp2 = re.search(r'(\d+,\d{2})\s+21\s*%', texto)
            if match_transp2:
                valor = float(match_transp2.group(1).replace(',', '.'))
                if valor < 20:
                    lineas.append({
                        'codigo': 'TRANSP', 'articulo': 'TRANSPORTE',
                        'iva': 21, 'base': valor
                    })
    
    # Total factura
    total = None
    match_total = re.search(r'Total Factura\s+([\d,]+)', texto)
    if match_total:
        total = float(match_total.group(1).replace(',', '.'))
    
    return lineas, total

def calcular_total_con_prorrateo(lineas):
    """Calcula total CON prorrateo de transporte."""
    productos = [l for l in lineas if l['articulo'] != 'TRANSPORTE']
    transporte = [l for l in lineas if l['articulo'] == 'TRANSPORTE']
    
    if not transporte or not productos:
        return round(sum(l['base'] * (1 + l['iva']/100) for l in lineas), 2)
    
    # Prorratear transporte
    transp_base = transporte[0]['base']
    transp_iva = transporte[0]['iva']
    transp_total = transp_base * (1 + transp_iva/100)
    
    total_bases_prod = sum(p['base'] for p in productos)
    
    total = 0
    for p in productos:
        proporcion = p['base'] / total_bases_prod
        incremento = transp_total * proporcion / (1 + p['iva']/100)
        base_ajustada = p['base'] + incremento
        total += base_ajustada * (1 + p['iva']/100)
    
    return round(total, 2)

def main():
    if len(sys.argv) < 2:
        print("USO: python diagnostico_felisa.py RUTA_CARPETA")
        sys.exit(1)
    
    carpeta = Path(sys.argv[1])
    archivos = [f for f in carpeta.glob('*.pdf') if 'FELISA' in f.name.upper()]
    
    print("\n" + "=" * 70)
    print("DIAGNOSTICO FELISA v3.40 -", len(archivos), "facturas")
    print("=" * 70)
    
    for archivo in sorted(archivos):
        print("\n[%s]" % archivo.name)
        print("-" * 50)
        
        texto = extraer_texto_pdf(archivo)
        if not texto:
            print("   ERROR: Sin texto")
            continue
        
        lineas, total_fac = extraer_lineas_felisa_v40(texto)
        
        productos = [l for l in lineas if l['articulo'] != 'TRANSPORTE']
        transporte = [l for l in lineas if l['articulo'] == 'TRANSPORTE']
        
        print("   PRODUCTOS (%d):" % len(productos))
        for p in productos:
            print("      %s | %-30s | IVA %2d%% | %8.2f" % (
                p['codigo'], p['articulo'][:30], p['iva'], p['base']))
        
        print("   TRANSPORTE (%d):" % len(transporte))
        for t in transporte:
            print("      %s | IVA %d%% | %.2f" % (t['codigo'], t['iva'], t['base']))
        
        total_calc = calcular_total_con_prorrateo(lineas)
        print("\n   Calculado: %.2f | Factura: %s" % (
            total_calc, "%.2f" % total_fac if total_fac else "N/A"))
        
        if total_fac:
            diff = total_calc - total_fac
            if abs(diff) < 0.05:
                print("   >> OK")
            else:
                print("   >> DESCUADRE: %+.2f" % diff)

if __name__ == '__main__':
    main()
