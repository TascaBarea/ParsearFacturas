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

def extraer_lineas_ceres_v39(texto):
    """Extractor CERES v3.39."""
    lineas = []
    codigos_capturados = set()
    debug_info = {'con_dto': [], 'sin_dto': [], 'envases': []}
    
    # Patron 1: Productos CON descuento
    patron_con_descuento = re.compile(
        r'^([A-Z0-9]{5,8})\s+([A-Z][A-Z0-9\s\'/\-\.]+?)\s+(-?\d+)\s+(\d{1,2})(\d+[,\.]\d+)\s+(\d+[,\.]?\d*)\s+(-?\d+[,\.]\d+)',
        re.MULTILINE)
    
    # Patron 2: Productos SIN descuento
    patron_sin_descuento = re.compile(
        r'^([A-Z0-9]{6,8})\s+([A-Z][A-Z0-9\s\'/\-\.]+?)\s+(\d+)\s+(\d{1,2})(\d+[,\.]?\d*)\s+(\d+[,\.]\d{2})$',
        re.MULTILINE)
    
    # Patron 3: Envases
    patron_envases = re.compile(
        r'^(CE99\d{4})\s+(ENVASE\s+\d+\s*lit\.?)\s+(-?\d+)\s+(\d{1,2})(\d+)\s+(-?\d+[,\.]\d+)',
        re.MULTILINE)
    
    for match in patron_con_descuento.finditer(texto):
        codigo, descripcion, uds, iva, precio, dto, importe = match.groups()
        descripcion_limpia = descripcion.strip()
        if 'ENVASE' in descripcion_limpia.upper() or 'REAJUSTE' in descripcion_limpia.upper():
            continue
        key = (codigo, float(importe.replace(',', '.')))
        if key in codigos_capturados:
            continue
        codigos_capturados.add(key)
        debug_info['con_dto'].append({'codigo': codigo, 'articulo': descripcion_limpia, 
            'iva': int(iva), 'importe': float(importe.replace(',', '.'))})
        lineas.append({'codigo': codigo, 'articulo': descripcion_limpia,
            'iva': int(iva), 'base': float(importe.replace(',', '.'))})
    
    for match in patron_sin_descuento.finditer(texto):
        codigo, descripcion, uds, iva, precio, importe = match.groups()
        descripcion_limpia = descripcion.strip()
        if 'ENVASE' in descripcion_limpia.upper():
            continue
        key = (codigo, float(importe.replace(',', '.')))
        if key in codigos_capturados:
            continue
        importe_val = float(importe.replace(',', '.'))
        if importe_val <= 0:
            continue
        codigos_capturados.add(key)
        debug_info['sin_dto'].append({'codigo': codigo, 'articulo': descripcion_limpia,
            'iva': int(iva), 'importe': importe_val})
        lineas.append({'codigo': codigo, 'articulo': descripcion_limpia,
            'iva': int(iva), 'base': importe_val})
    
    for match in patron_envases.finditer(texto):
        codigo, descripcion, uds, iva, precio, importe = match.groups()
        debug_info['envases'].append({'codigo': codigo, 'articulo': descripcion.strip(),
            'iva': int(iva), 'importe': float(importe.replace(',', '.'))})
        lineas.append({'codigo': codigo, 'articulo': descripcion.strip(),
            'iva': int(iva), 'base': float(importe.replace(',', '.'))})
    
    cla = None
    cla_match = re.search(r'CLA:\s*(\d+)', texto)
    if cla_match:
        cla = int(cla_match.group(1))
        if cla > 0:
            lineas.append({'codigo': 'CLA', 'articulo': 'CAJA RETORNABLE', 'iva': 21, 'base': float(cla)})
    
    total = None
    total_match = re.search(r'Importe\s*TOTAL[\s\S]*?(\d{2,}[.,]\d{2})\s*\n', texto, re.IGNORECASE)
    if total_match:
        total = float(total_match.group(1).replace(',', '.'))
    
    return lineas, cla, total, debug_info

def calcular_total(lineas):
    return round(sum(l['base'] * (1 + l['iva']/100) for l in lineas), 2)

def main():
    if len(sys.argv) < 2:
        print("USO: python diagnostico_ceres_v39.py RUTA_CARPETA")
        sys.exit(1)
    
    carpeta = Path(sys.argv[1])
    archivos = [f for f in carpeta.glob('*.pdf') if 'CERES' in f.name.upper()]
    
    print("\n" + "=" * 70)
    print("DIAGNOSTICO CERES v3.39 -", len(archivos), "facturas")
    print("=" * 70)
    
    ok, descuadre, sin_total = 0, 0, 0
    
    for archivo in sorted(archivos):
        print("\n[%s]" % archivo.name)
        print("-" * 60)
        
        texto = extraer_texto_pdf(archivo)
        if not texto:
            print("   ERROR: Sin texto")
            continue
        
        lineas, cla, total_fac, debug = extraer_lineas_ceres_v39(texto)
        
        print("   CON_DTO (%d):" % len(debug['con_dto']))
        for p in debug['con_dto']:
            print("      %s | %-28s | IVA %2d%% | %8.2f" % (p['codigo'], p['articulo'][:28], p['iva'], p['importe']))
        
        print("   SIN_DTO (%d):" % len(debug['sin_dto']))
        for p in debug['sin_dto']:
            print("      %s | %-28s | IVA %2d%% | %8.2f" % (p['codigo'], p['articulo'][:28], p['iva'], p['importe']))
        
        print("   ENVASES (%d):" % len(debug['envases']))
        for e in debug['envases']:
            print("      %s | %-28s | IVA %2d%% | %8.2f" % (e['codigo'], e['articulo'], e['iva'], e['importe']))
        
        if cla:
            print("   CLA: %d EUR" % cla)
        
        total_calc = calcular_total(lineas)
        print("\n   Calculado: %.2f | Factura: %s" % (total_calc, "%.2f" % total_fac if total_fac else "N/A"))
        
        if total_fac:
            diff = total_calc - total_fac
            if abs(diff) < 0.05:
                print("   >> OK")
                ok += 1
            else:
                print("   >> DESCUADRE: %+.2f" % diff)
                descuadre += 1
        else:
            print("   >> SIN_TOTAL")
            sin_total += 1
    
    print("\n" + "=" * 70)
    print("RESUMEN: OK=%d | DESCUADRE=%d | SIN_TOTAL=%d" % (ok, descuadre, sin_total))
    print("=" * 70)

if __name__ == '__main__':
    main()
