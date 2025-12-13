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

def extraer_lineas_ceres_v38(texto):
    """Extractor CERES v3.38 con SOUSAS y PLASTICO."""
    resultado = {'productos': [], 'envases': [], 'sousas': [], 'plastico': [], 'cla': None, 'total_extraido': None}
    
    # Patron 1: Productos normales (IVA pegado al precio)
    patron_productos = re.compile(
        r'^([A-Z0-9]{5,6})\s+([A-Z][A-Z0-9\s\'/\-\.]+?)\s+(-?\d+)\s+(\d{1,2})(\d+[,\.]\d+)\s+(\d+[,\.]?\d*)\s+(-?\d+[,\.]\d+)',
        re.MULTILINE)
    
    # Patron 2: Envases
    patron_envases = re.compile(
        r'^(CE\d{5,6})\s+(ENVASE\s+\d+\s*lit\.?)\s+(-?\d+)\s+(\d{1,2})(\d+)\s+(-?\d+[,\.]\d+)',
        re.MULTILINE)
    
    # Patron 3: IVA separado (SOUSAS, etc.)
    patron_iva_separado = re.compile(
        r'^(\d{6})\s+([A-Z][A-Z0-9\s\'/\-\.]+?)\s+(\d+)\s+(\d+[,\.]\d{2})\s+(\d{1,2})\s+(\d+[,\.]\d{2})',
        re.MULTILINE)
    
    # Patron 4: PLASTICO
    patron_plastico = re.compile(
        r'^(CE990\d{3})\s+(PLASTICO[A-Z0-9\s/\-]*?)\s+(\d+)\s+(\d+)\s+(\d{1,2})\s+(\d+[,\.]\d{2})',
        re.MULTILINE)
    
    for match in patron_productos.finditer(texto):
        codigo, descripcion, uds, iva, precio, dto, importe = match.groups()
        descripcion_limpia = descripcion.strip()
        if 'ENVASE' in descripcion_limpia.upper() or 'REAJUSTE' in descripcion_limpia.upper():
            continue
        if 'SOUSAS' in descripcion_limpia.upper():
            continue
        resultado['productos'].append({
            'codigo': codigo, 'articulo': descripcion_limpia, 'uds': int(uds),
            'iva': int(iva), 'importe': float(importe.replace(',', '.'))
        })
    
    for match in patron_envases.finditer(texto):
        codigo, descripcion, uds, iva, precio, importe = match.groups()
        resultado['envases'].append({
            'codigo': codigo, 'articulo': descripcion.strip(), 'uds': int(uds),
            'iva': int(iva), 'importe': float(importe.replace(',', '.'))
        })
    
    for match in patron_iva_separado.finditer(texto):
        codigo, descripcion, uds, precio, iva, importe = match.groups()
        importe_val = float(importe.replace(',', '.'))
        if importe_val > 0:
            resultado['sousas'].append({
                'codigo': codigo, 'articulo': descripcion.strip(), 'uds': int(uds),
                'iva': int(iva), 'importe': importe_val
            })
    
    for match in patron_plastico.finditer(texto):
        codigo, descripcion, uds, precio, iva, importe = match.groups()
        resultado['plastico'].append({
            'codigo': codigo, 'articulo': descripcion.strip(), 'uds': int(uds),
            'iva': int(iva), 'importe': float(importe.replace(',', '.'))
        })
    
    cla_match = re.search(r'CLA:\s*(\d+)', texto)
    if cla_match:
        resultado['cla'] = int(cla_match.group(1))
    
    total_match = re.search(r'Importe\s*TOTAL[\s\S]*?(\d{2,}[.,]\d{2})\s*\n', texto, re.IGNORECASE)
    if total_match:
        resultado['total_extraido'] = float(total_match.group(1).replace(',', '.'))
    
    return resultado

def calcular_total_lineas(resultado):
    total = 0.0
    for prod in resultado['productos']:
        total += prod['importe'] * (1 + prod['iva']/100)
    for env in resultado['envases']:
        total += env['importe'] * (1 + env['iva']/100)
    for s in resultado['sousas']:
        total += s['importe'] * (1 + s['iva']/100)
    for p in resultado['plastico']:
        total += p['importe'] * (1 + p['iva']/100)
    if resultado['cla']:
        total += resultado['cla'] * 1.21
    return round(total, 2)

def main():
    if len(sys.argv) < 2:
        print("USO: python diagnostico_ceres_v38.py RUTA_CARPETA")
        sys.exit(1)
    
    carpeta = Path(sys.argv[1])
    archivos_ceres = [f for f in carpeta.glob('*.pdf') if 'CERES' in f.name.upper()]
    
    if not archivos_ceres:
        print("No se encontraron facturas CERES en", carpeta)
        sys.exit(1)
    
    print("")
    print("=" * 70)
    print("DIAGNOSTICO FACTURAS CERES v3.38 -", len(archivos_ceres), "encontradas")
    print("=" * 70)
    
    ok_count = 0
    descuadre_count = 0
    sin_total_count = 0
    
    for archivo in sorted(archivos_ceres):
        print("\n[FACTURA]", archivo.name)
        print("-" * 60)
        
        texto = extraer_texto_pdf(archivo)
        if not texto:
            print("   ERROR: No se pudo extraer texto del PDF")
            continue
        
        resultado = extraer_lineas_ceres_v38(texto)
        
        print("\n   PRODUCTOS (" + str(len(resultado['productos'])) + "):")
        for p in resultado['productos']:
            print("      %s | %-30s | %3d uds | IVA %2d%% | %8.2f EUR" % (
                p['codigo'], p['articulo'][:30], p['uds'], p['iva'], p['importe']))
        
        print("\n   ENVASES (" + str(len(resultado['envases'])) + "):")
        if resultado['envases']:
            for e in resultado['envases']:
                print("      %s | %-30s | %3d uds | IVA %2d%% | %8.2f EUR" % (
                    e['codigo'], e['articulo'], e['uds'], e['iva'], e['importe']))
        else:
            print("      (ninguno)")
        
        print("\n   SOUSAS/IVA_SEPARADO (" + str(len(resultado['sousas'])) + "):")
        if resultado['sousas']:
            for s in resultado['sousas']:
                print("      %s | %-30s | %3d uds | IVA %2d%% | %8.2f EUR" % (
                    s['codigo'], s['articulo'][:30], s['uds'], s['iva'], s['importe']))
        else:
            print("      (ninguno)")
        
        print("\n   PLASTICO (" + str(len(resultado['plastico'])) + "):")
        if resultado['plastico']:
            for p in resultado['plastico']:
                print("      %s | %-30s | %3d uds | IVA %2d%% | %8.2f EUR" % (
                    p['codigo'], p['articulo'], p['uds'], p['iva'], p['importe']))
        else:
            print("      (ninguno)")
        
        if resultado['cla']:
            print("\n   CLA:", resultado['cla'], "EUR")
        
        total_calculado = calcular_total_lineas(resultado)
        total_factura = resultado['total_extraido']
        
        print("\n   TOTALES:")
        print("      Total calculado (lineas): %.2f EUR" % total_calculado)
        if total_factura:
            print("      Total factura (extraido): %.2f EUR" % total_factura)
            diferencia = total_calculado - total_factura
            if abs(diferencia) < 0.05:
                print("      >> CUADRA OK")
                ok_count += 1
            else:
                print("      >> DESCUADRE: %+.2f EUR" % diferencia)
                descuadre_count += 1
        else:
            print("      Total factura: NO ENCONTRADO")
            sin_total_count += 1
    
    print("\n" + "=" * 70)
    print("RESUMEN v3.38:")
    print("   OK:         %d" % ok_count)
    print("   DESCUADRE:  %d" % descuadre_count)
    print("   SIN_TOTAL:  %d" % sin_total_count)
    print("=" * 70)

if __name__ == '__main__':
    main()
