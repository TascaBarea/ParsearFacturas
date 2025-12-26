#!/usr/bin/env python3
"""
PARSEAR FACTURAS v5.1
=====================
Sistema modular para extraccion y procesamiento de facturas.

CAMBIOS v5.1 (26/12/2025):
- Mejorada normalización de proveedor usando alias de extractores
- Búsqueda en diccionario con múltiples variantes del nombre

CAMBIOS v5.0 (26/12/2025):
- Prorrateo automático de PORTE/TRANSPORTE/SERVICIO URGENTE
- Distribuye portes proporcionalmente al importe de cada artículo

CAMBIOS v4.5 (22/12/2025):
- Añadido fuzzy matching para categorización (80% similitud)

Uso:
    python main.py -i "carpeta_facturas" [-o archivo.xlsx] [-d diccionario.xlsx]
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import re
from difflib import SequenceMatcher

# Anadir el directorio del script al path
sys.path.insert(0, str(Path(__file__).parent))

# Importar modulos del proyecto
from config.settings import VERSION, CIF_PROPIO, DICCIONARIO_DEFAULT
from nucleo.factura import Factura, LineaFactura
from nucleo.pdf import extraer_texto_pdf
from nucleo.parser import (
    parsear_nombre_archivo,
    extraer_fecha,
    extraer_cif,
    extraer_iban,
    extraer_total,
    extraer_referencia
)
from nucleo.validacion import validar_cuadre, validar_factura
from extractores import obtener_extractor, listar_extractores, EXTRACTORES
from extractores.generico import ExtractorGenerico
from salidas import generar_excel, generar_log, imprimir_resumen


# ============================================================================
# CONSTANTES PARA PRORRATEO
# ============================================================================

KEYWORDS_PRORRATEO = [
    'SERVICIO URGENTE',
    'PORTE',
    'PORTES',
    'TRANSPORTE',
    'ENVIO',
    'ENVÍO',
    'GASTOS ENVIO',
    'GASTOS ENVÍO',
    'GASTOS DE ENVIO',
    'GASTOS DE ENVÍO',
]

KEYWORDS_EXCLUIR_PRORRATEO = [
    'ENVASE',
    'CAJA RETORNABLE',
    'FIANZA',
    'DEPOSITO',
    'DEPÓSITO',
]


# ============================================================================
# MAPEO DE ALIAS PARA NORMALIZACIÓN
# ============================================================================

# Mapeo manual de nombres de factura → nombre en diccionario
ALIAS_DICCIONARIO = {
    # SABORES DE PATERNA
    'SABORES DE PATERNA': 'SABORES PATERNA',
    'PATERNA': 'SABORES PATERNA',
    # FELISA
    'FELISA GOURMET': 'FELISA',
    'PESCADOS DON FELIX': 'FELISA',
    # ZUCCA
    'QUESERIA ZUCCA': 'ZUCCA',
    'FORMAGGIARTE': 'ZUCCA',
    # SERRIN
    'SERRIN NOCHAO': 'SERRIN NO CHAO',
    'SERRIN NO CHAN': 'SERRIN NO CHAO',
    'SERRIN': 'SERRIN NO CHAO',
    # DE LUIS
    'DE LUIS': 'DE LUIS SABORES UNICOS',
    # BERZAL
    'BERZAL': 'BERZAL HERMANOS',
    # CONSERVAS TITO
    'PORVAZ': 'CONSERVAS TITO',
    'PORVAZ VILLAGARCIA': 'CONSERVAS TITO',
    'PORVAZ TITO': 'CONSERVAS TITO',
    # EMBUTIDOS BERNAL
    'JAMONES BERNAL': 'EMBUTIDOS BERNAL',
    'JAMONES Y EMBUTIDOS BERNAL': 'EMBUTIDOS BERNAL',
    'BERNAL': 'EMBUTIDOS BERNAL',
    # SILVA CORDERO
    'QUESOS SILVA CORDERO': 'SILVA CORDERO',
    'QUESOS DE ACEHUCHE': 'SILVA CORDERO',
    # QUESERIA NAVAS
    'CARLOS NAVAS': 'QUESERIA NAVAS',
    'QUESOS NAVAS': 'QUESERIA NAVAS',
    # LA ALACENA
    'CONSERVAS LA ALACENA': 'LA ALACENA',
    # GADITAUN
    'MARILINA GADITAUN': 'GADITAUN',
    'GARDITAUN MARIA LINAREJOS': 'GADITAUN',
    'MARILINA': 'GADITAUN',
    # BORBOTON
    'BODEGAS BORBOTON': 'BORBOTON',
    # ARTESANOS DEL MOLLETE
    'ARTESANOS DEL MOLLETE': 'MOLLETES ARTESANOS',
    'MOLLETES ARTESANOS DE ANTEQUERA': 'MOLLETES ARTESANOS',
    # ZUBELZU
    'ZUBELZU PIPARRAK': 'ZUBELZU',
    'IBARRAKO': 'ZUBELZU',
    'IBARRAKO PIPARRAK': 'ZUBELZU',
    # LA MOLIENDA VERDE
    'MOLIENDA VERDE': 'LA MOLIENDA VERDE',
    # DISTRIBUCIONES LAVAPIES
    'LAVAPIES': 'DISTRIBUCIONES LAVAPIES',
    # GRUPO DISBER
    'DISBER': 'GRUPO DISBER',
    'GRUPO DISBER': 'DISBER',
    # MRM
    'INDUSTRIAS CARNICAS MRM': 'MRM',
    # PILAR RODRIGUEZ
    'EL MAJADAL': 'PILAR RODRIGUEZ',
    # TERRITORIO CAMPERO
    'GRUPO TERRITORIO CAMPERO': 'TERRITORIO CAMPERO',
    # MARITA
    'MARITA COSTA': 'MARITA',
    # LA BARRA DULCE
    'BARRA DULCE': 'LA BARRA DULCE',
    # MIGUEZ CAL
    'FORPLAN': 'MIGUEZ CAL',
    # MARTIN ABENZA
    'CONSERVAS EL MODESTO': 'MARTIN ABENZA',
    # WELLDONE
    'RODOLFO DEL RIO': 'WELLDONE',
    'WELLDONE LACTICOS': 'WELLDONE',
    # MANIPULADOS ABELLAN
    'EL LABRADOR': 'MANIPULADOS ABELLAN',
    'ABELLAN': 'MANIPULADOS ABELLAN',
    # LA ROSQUILLERIA  
    'EL TORRO': 'LA ROSQUILLERIA',
    # PANRUJE
    'ROSQUILLAS LA ERMITA': 'PANRUJE',
    # LICORES MADRUEÑO
    'MADRUEÑO': 'LICORES MADRUEÑO',
    # VINOS DE ARGANZA
    'ARGANZA': 'VINOS DE ARGANZA',
    # CVNE
    'BODEGAS CVNE': 'CVNE',
    # LA PURISIMA
    'BODEGAS LA PURISIMA': 'LA PURISIMA',
    # FRANCISCO GUERRA
    'GUERRA': 'FRANCISCO GUERRA',
    # FISHGOURMET
    'FISH GOURMET': 'FISHGOURMET',
    # ECOFICUS
    'ECO FICUS': 'ECOFICUS',
    # LOS GREDALES
    'GREDALES': 'LOS GREDALES',
    'LOS GREDALES DEL TOBOSO': 'LOS GREDALES',
}


# ============================================================================
# FUNCIÓN: Normalizar nombre de proveedor
# ============================================================================

def normalizar_proveedor(nombre: str) -> str:
    """
    Normaliza nombre de proveedor:
    1. Quita prefijos de fecha/referencia (ej: "4T25 1031")
    2. Quita sufijos numéricos (ej: " 2")
    3. Aplica mapeo de alias conocidos
    """
    if not nombre:
        return ""
    
    # Paso 1: Quitar prefijos tipo "4T25 1031 " o "1T25 0331 "
    nombre = re.sub(r'^\d[TQ]\d{2}\s+\d{3,4}\s+', '', nombre)
    
    # Quitar sufijos numéricos tipo " 2" o " 3"
    nombre = re.sub(r'\s+\d+$', '', nombre)
    
    nombre = nombre.strip().upper()
    
    # Paso 2: Aplicar mapeo de alias
    if nombre in ALIAS_DICCIONARIO:
        return ALIAS_DICCIONARIO[nombre]
    
    return nombre


def buscar_en_diccionario(proveedor: str, indice: dict) -> str:
    """
    Busca el nombre del proveedor en el diccionario.
    Prueba múltiples variantes: exacto, alias, parcial.
    
    Returns:
        Nombre como está en el diccionario, o el original si no se encuentra
    """
    prov_upper = proveedor.upper().strip()
    
    # 1. Búsqueda exacta
    if prov_upper in indice:
        return prov_upper
    
    # 2. Buscar via alias
    if prov_upper in ALIAS_DICCIONARIO:
        alias = ALIAS_DICCIONARIO[prov_upper]
        if alias in indice:
            return alias
    
    # 3. Búsqueda parcial (substring)
    for nombre_dic in indice.keys():
        if nombre_dic in prov_upper or prov_upper in nombre_dic:
            return nombre_dic
    
    # 4. Búsqueda parcial en alias
    for alias_from, alias_to in ALIAS_DICCIONARIO.items():
        if alias_from in prov_upper or prov_upper in alias_from:
            if alias_to in indice:
                return alias_to
    
    return prov_upper


# ============================================================================
# FUNCIÓN: Prorratear portes/transporte entre productos
# ============================================================================

def prorratear_portes(lineas: list) -> list:
    """
    Prorratea los portes/transporte proporcionalmente entre los productos.
    """
    if not lineas:
        return lineas
    
    lineas_porte = []
    lineas_producto = []
    lineas_excluidas = []
    
    for linea in lineas:
        articulo_upper = (linea.articulo or '').upper()
        
        es_porte = any(kw in articulo_upper for kw in KEYWORDS_PRORRATEO)
        es_excluida = any(kw in articulo_upper for kw in KEYWORDS_EXCLUIR_PRORRATEO)
        
        if es_porte:
            lineas_porte.append(linea)
        elif es_excluida:
            lineas_excluidas.append(linea)
        else:
            lineas_producto.append(linea)
    
    if not lineas_porte:
        return lineas
    
    total_porte = sum(linea.base for linea in lineas_porte if linea.base)
    
    if total_porte <= 0:
        return lineas
    
    total_productos = sum(linea.base for linea in lineas_producto if linea.base and linea.base > 0)
    
    if total_productos <= 0:
        return lineas
    
    for linea in lineas_producto:
        if linea.base and linea.base > 0:
            proporcion = linea.base / total_productos
            porte_linea = total_porte * proporcion
            linea.base = round(linea.base + porte_linea, 2)
            if linea.cantidad and linea.cantidad > 0:
                linea.precio_ud = round(linea.base / linea.cantidad, 4)
    
    return lineas_producto + lineas_excluidas


# ============================================================================
# FUNCIÓN: cargar_diccionario
# ============================================================================

def cargar_diccionario(ruta: Path) -> tuple:
    """
    Carga el diccionario de categorias.
    """
    import pandas as pd
    
    try:
        xlsx = pd.ExcelFile(ruta)
        articulos = pd.read_excel(xlsx, sheet_name='Articulos')
        
        try:
            patrones = pd.read_excel(xlsx, sheet_name='Patrones especificos')
        except:
            try:
                patrones = pd.read_excel(xlsx, sheet_name='Patrones')
            except:
                patrones = pd.DataFrame()
        
        indice = {}
        for _, row in articulos.iterrows():
            prov = str(row.get('PROVEEDOR', '')).upper().strip()
            if prov and prov != 'NAN':
                if prov not in indice:
                    indice[prov] = []
                indice[prov].append({
                    'articulo': str(row.get('ARTICULO', '')),
                    'categoria': str(row.get('CATEGORIA', 'PENDIENTE')),
                    'id_categoria': row.get('ID_CATEGORIA', '')
                })
        
        return articulos, patrones, indice
        
    except Exception as e:
        print(f"Aviso: Error cargando diccionario: {e}")
        return None, None, {}


# ============================================================================
# FUNCIÓN: categorizar_linea con FUZZY MATCHING y normalización mejorada
# ============================================================================

def categorizar_linea(linea: LineaFactura, proveedor: str, indice: dict) -> None:
    """
    Asigna categoria a una linea segun el diccionario.
    """
    # Normalizar proveedor
    prov_normalizado = normalizar_proveedor(proveedor)
    
    # Buscar en diccionario con múltiples estrategias
    prov_diccionario = buscar_en_diccionario(prov_normalizado, indice)
    
    # Lista de proveedores a probar
    proveedores_a_probar = [prov_diccionario]
    if prov_normalizado != prov_diccionario:
        proveedores_a_probar.append(prov_normalizado)
    prov_original = proveedor.upper().strip() if proveedor else ''
    if prov_original and prov_original not in proveedores_a_probar:
        proveedores_a_probar.append(prov_original)
    
    articulo_upper = linea.articulo.upper() if linea.articulo else ''
    
    mejor_match = None
    mejor_similitud = 0
    mejor_tipo = None
    
    for prov_test in proveedores_a_probar:
        if prov_test not in indice:
            continue
            
        for entry in indice[prov_test]:
            patron = entry['articulo'].upper()
            
            # 1. Match exacto (substring)
            if patron in articulo_upper or articulo_upper in patron:
                linea.categoria = entry['categoria']
                linea.id_categoria = entry.get('id_categoria', '')
                linea.match_info = 'EXACTO'
                return
            
            # 2. Fuzzy matching
            similitud = SequenceMatcher(None, patron, articulo_upper).ratio()
            
            if similitud > mejor_similitud and similitud >= 0.80:
                mejor_similitud = similitud
                mejor_match = entry
                mejor_tipo = f'FUZZY_{int(similitud*100)}%'
    
    if mejor_match:
        linea.categoria = mejor_match['categoria']
        linea.id_categoria = mejor_match.get('id_categoria', '')
        linea.match_info = mejor_tipo
        return
    
    if not linea.categoria:
        linea.categoria = 'PENDIENTE'
        linea.match_info = 'SIN_MATCH'


# ============================================================================
# FUNCIÓN: procesar_factura
# ============================================================================

def procesar_factura(ruta_pdf: Path, indice: dict) -> Factura:
    """
    Procesa una factura PDF.
    """
    info = parsear_nombre_archivo(ruta_pdf.name)
    
    factura = Factura(
        archivo=ruta_pdf.name,
        numero=info.get('numero', ''),
        ruta=ruta_pdf,
        proveedor=info.get('proveedor', 'DESCONOCIDO')
    )
    
    extractor = obtener_extractor(factura.proveedor)
    
    if extractor is None:
        extractor = ExtractorGenerico()
    
    metodo = extractor.metodo_pdf if extractor else 'pypdf'
    texto = extraer_texto_pdf(ruta_pdf, metodo=metodo, fallback=True)
    factura.texto_raw = texto
    factura.metodo_pdf = metodo
    
    if not texto:
        factura.agregar_error('PDF_VACIO')
        factura.cuadre = 'SIN_TEXTO'
        return factura
    
    if extractor and hasattr(extractor, 'extraer_fecha'):
        factura.fecha = extractor.extraer_fecha(texto)
    if not factura.fecha:
        factura.fecha = extraer_fecha(texto)
    
    factura.cif = extractor.cif if extractor and extractor.cif else extraer_cif(texto)
    factura.iban = extractor.iban if extractor and extractor.iban else extraer_iban(texto)
    
    if extractor and hasattr(extractor, 'extraer_referencia'):
        factura.referencia = extractor.extraer_referencia(texto)
    if not factura.referencia:
        factura.referencia = extraer_referencia(texto)
    
    if extractor and hasattr(extractor, 'extraer_total'):
        factura.total = extractor.extraer_total(texto)
    if factura.total is None:
        factura.total = extraer_total(texto, factura.proveedor)
    
    try:
        lineas_raw = extractor.extraer_lineas(texto) if extractor else []
    except Exception as e:
        factura.agregar_error(f'EXTRACTOR_ERROR: {str(e)[:50]}')
        lineas_raw = []
    
    lineas_convertidas = []
    for linea_raw in lineas_raw:
        if isinstance(linea_raw, LineaFactura):
            linea = linea_raw
        elif isinstance(linea_raw, dict):
            iva_raw = linea_raw.get('iva')
            if iva_raw is None:
                iva_valor = 21
            else:
                iva_valor = int(iva_raw)
            
            linea = LineaFactura(
                articulo=linea_raw.get('articulo', ''),
                base=float(linea_raw.get('base', 0.0) or 0),
                iva=iva_valor,
                codigo=str(linea_raw.get('codigo', '') or ''),
                cantidad=linea_raw.get('cantidad'),
                precio_ud=linea_raw.get('precio_ud'),
                categoria=linea_raw.get('categoria', ''),
                id_categoria=str(linea_raw.get('id_categoria', '') or '')
            )
        else:
            continue
        
        lineas_convertidas.append(linea)
    
    # Prorratear portes
    lineas_prorrateadas = prorratear_portes(lineas_convertidas)
    
    # Categorizar cada línea
    for linea in lineas_prorrateadas:
        categorizar_linea(linea, factura.proveedor, indice)
        factura.agregar_linea(linea)
    
    factura.cuadre = validar_cuadre(factura.lineas, factura.total)
    
    errores = validar_factura(factura)
    for error in errores:
        factura.agregar_error(error)
    
    return factura


# ============================================================================
# FUNCIÓN: detectar_trimestre
# ============================================================================

def detectar_trimestre(carpeta_nombre: str) -> str:
    """
    Detecta el trimestre del nombre de la carpeta.
    """
    match = re.search(r'(\d)\s*TRI', carpeta_nombre)
    if match:
        num_tri = match.group(1)
        if num_tri in '1234':
            return f'{num_tri}T25'
    
    match = re.search(r'TRI\w*\s*(\d)', carpeta_nombre)
    if match:
        num_tri = match.group(1)
        if num_tri in '1234':
            return f'{num_tri}T25'
    
    return datetime.now().strftime('%Y%m%d')


# ============================================================================
# FUNCIÓN: main
# ============================================================================

def main():
    """Funcion principal."""
    parser = argparse.ArgumentParser(
        description='ParsearFacturas v5.1',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main.py -i "C:\\Facturas\\4 TRI 2025"
  python main.py -i facturas/ -o resultado.xlsx
  python main.py --listar-extractores
        """
    )
    
    parser.add_argument('--input', '-i', help='Carpeta de facturas PDF')
    parser.add_argument('--output', '-o', default=None, 
                        help='Archivo Excel de salida')
    parser.add_argument('--diccionario', '-d', default=DICCIONARIO_DEFAULT,
                        help='DiccionarioProveedoresCategoria.xlsx')
    parser.add_argument('--listar-extractores', action='store_true',
                        help='Listar extractores disponibles y salir')
    parser.add_argument('--version', '-v', action='version', version='v5.1')
    
    args = parser.parse_args()
    
    if args.listar_extractores:
        extractores = listar_extractores()
        print(f"\nEXTRACTORES DISPONIBLES ({len(extractores)}):\n")
        for nombre, clase in sorted(extractores.items()):
            print(f"  - {nombre}")
        print()
        return
    
    if not args.input:
        parser.print_help()
        print("\nERROR: Debes especificar una carpeta con -i")
        sys.exit(1)
    
    carpeta = Path(args.input)
    if not carpeta.exists():
        print(f"ERROR: No existe la carpeta: {carpeta}")
        sys.exit(1)
    
    diccionario_path = Path(args.diccionario)
    if not diccionario_path.exists():
        print(f"Aviso: Diccionario no encontrado: {diccionario_path}")
        print("   Continuando sin categorizacion...")
        indice = {}
    else:
        print(f"\nCargando diccionario...")
        _, _, indice = cargar_diccionario(diccionario_path)
        print(f"   {len(indice)} proveedores indexados")
    
    print("\n" + "="*60)
    print("PARSEAR FACTURAS v5.1")
    print("="*60)
    
    script_dir = Path(__file__).parent
    outputs_dir = script_dir / 'outputs'
    outputs_dir.mkdir(exist_ok=True)
    
    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute() and output_path.parent == Path('.'):
            ruta_excel = outputs_dir / output_path.name
        else:
            ruta_excel = output_path
    else:
        carpeta_nombre = carpeta.name.upper()
        trimestre = detectar_trimestre(carpeta_nombre)
        ruta_excel = outputs_dir / f'Facturas_{trimestre}.xlsx'
    
    archivos = list(carpeta.glob('*.pdf'))
    print(f"\nCarpeta: {carpeta}")
    print(f"   Archivos PDF: {len(archivos)}")
    
    if not archivos:
        print("ERROR: No se encontraron archivos PDF")
        sys.exit(1)
    
    facturas = []
    for i, archivo in enumerate(sorted(archivos), 1):
        nombre_corto = archivo.name[:45] + '...' if len(archivo.name) > 48 else archivo.name
        print(f"   [{i:3d}/{len(archivos)}] {nombre_corto}", end=" ")
        
        try:
            factura = procesar_factura(archivo, indice)
            facturas.append(factura)
            
            if factura.errores:
                print(f"AVISO: {factura.errores[0][:30]}")
            elif factura.lineas:
                print(f"OK: {len(factura.lineas)} lineas, {factura.cuadre}")
            else:
                print("AVISO: SIN_LINEAS")
                
        except Exception as e:
            print(f"ERROR: {str(e)[:40]}")
            factura = Factura(archivo=archivo.name, numero='', ruta=archivo, proveedor='ERROR')
            factura.agregar_error(f'EXCEPCION: {str(e)[:50]}')
            facturas.append(factura)
    
    print(f"\nGenerando Excel...")
    total_filas = generar_excel(facturas, ruta_excel)
    print(f"   {ruta_excel}: {total_filas} filas")
    
    ruta_log = outputs_dir / f"log_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    generar_log(facturas, ruta_log)
    print(f"   {ruta_log}")
    
    imprimir_resumen(facturas)
    
    print("Proceso completado\n")


if __name__ == '__main__':
    main()
