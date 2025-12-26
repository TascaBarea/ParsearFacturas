#!/usr/bin/env python3
"""
PARSEAR FACTURAS v4.0
=====================
Sistema modular para extraccion y procesamiento de facturas.

Uso:
    python main.py -i "carpeta_facturas" [-o archivo.xlsx] [-d diccionario.xlsx]

Ejemplo:
    python main.py -i "C:\Facturas\3 TRI 2025"
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import re

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
from extractores import obtener_extractor, listar_extractores
from extractores.generico import ExtractorGenerico
from salidas import generar_excel, generar_log, imprimir_resumen


def cargar_diccionario(ruta: Path) -> tuple:
    """
    Carga el diccionario de categorias.
    
    Returns:
        (articulos_df, patrones_df, indice_proveedores)
    """
    import pandas as pd
    
    try:
        xlsx = pd.ExcelFile(ruta)
        articulos = pd.read_excel(xlsx, sheet_name='Articulos')
        
        # Intentar cargar patrones
        try:
            patrones = pd.read_excel(xlsx, sheet_name='Patrones especificos')
        except:
            try:
                patrones = pd.read_excel(xlsx, sheet_name='Patrones')
            except:
                patrones = pd.DataFrame()
        
        # Crear indice por proveedor
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


def categorizar_linea(linea: LineaFactura, proveedor: str, indice: dict) -> None:
    """
    Asigna categoria a una linea segun el diccionario.
    """
    prov_upper = proveedor.upper().strip() if proveedor else ''
    
    if prov_upper in indice:
        articulo_upper = linea.articulo.upper() if linea.articulo else ''
        
        for entry in indice[prov_upper]:
            patron = entry['articulo'].upper()
            if patron in articulo_upper or articulo_upper in patron:
                linea.categoria = entry['categoria']
                linea.id_categoria = entry.get('id_categoria', '')
                return
    
    # Si no se encuentra, marcar como pendiente
    if not linea.categoria:
        linea.categoria = 'PENDIENTE'


def procesar_factura(ruta_pdf: Path, indice: dict) -> Factura:
    """
    Procesa una factura PDF.
    
    Args:
        ruta_pdf: Ruta al archivo PDF
        indice: Diccionario de categorias por proveedor
        
    Returns:
        Objeto Factura con los datos extraidos
    """
    # Parsear nombre del archivo
    info = parsear_nombre_archivo(ruta_pdf.name)
    
    # Crear factura
    factura = Factura(
        archivo=ruta_pdf.name,
        numero=info.get('numero', ''),
        ruta=ruta_pdf,
        proveedor=info.get('proveedor', 'DESCONOCIDO')
    )
    
    # Obtener extractor adecuado
    extractor = obtener_extractor(factura.proveedor)
    
    if extractor is None:
        extractor = ExtractorGenerico()
    
    # Extraer texto del PDF
    metodo = extractor.metodo_pdf if extractor else 'pypdf'
    texto = extraer_texto_pdf(ruta_pdf, metodo=metodo, fallback=True)
    factura.texto_raw = texto
    factura.metodo_pdf = metodo
    
    if not texto:
        factura.agregar_error('PDF_VACIO')
        factura.cuadre = 'SIN_TEXTO'
        return factura
    
    # Extraer fecha (usar extractor si tiene metodo propio)
    if extractor and hasattr(extractor, 'extraer_fecha'):
        factura.fecha = extractor.extraer_fecha(texto)
    if not factura.fecha:
        factura.fecha = extraer_fecha(texto)
    
    # Extraer CIF e IBAN
    factura.cif = extractor.cif if extractor and extractor.cif else extraer_cif(texto)
    factura.iban = extractor.iban if extractor and extractor.iban else extraer_iban(texto)
    
    # Extraer referencia (usar extractor si tiene metodo propio)
    if extractor and hasattr(extractor, 'extraer_referencia'):
        factura.referencia = extractor.extraer_referencia(texto)
    if not factura.referencia:
        factura.referencia = extraer_referencia(texto)
    
    # Extraer total (usar extractor si tiene metodo propio)
    if extractor and hasattr(extractor, 'extraer_total'):
        factura.total = extractor.extraer_total(texto)
    if factura.total is None:
        factura.total = extraer_total(texto, factura.proveedor)
    
    # Extraer lineas usando el extractor
    try:
        lineas_raw = extractor.extraer_lineas(texto) if extractor else []
    except Exception as e:
        factura.agregar_error(f'EXTRACTOR_ERROR: {str(e)[:50]}')
        lineas_raw = []
    
    # Convertir lineas raw a objetos LineaFactura
    for linea_raw in lineas_raw:
        # Si ya es LineaFactura, usarlo directamente
        if isinstance(linea_raw, LineaFactura):
            linea = linea_raw
        # Si es diccionario, convertir
        elif isinstance(linea_raw, dict):
            # Obtener IVA - cuidado con iva=0 que es valido
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
            # Tipo desconocido, saltar
            continue
        
        # Categorizar
        categorizar_linea(linea, factura.proveedor, indice)
        
        factura.agregar_linea(linea)
    
    # Validar cuadre
    factura.cuadre = validar_cuadre(factura.lineas, factura.total)
    
    # Validar factura completa
    errores = validar_factura(factura)
    for error in errores:
        factura.agregar_error(error)
    
    return factura


def detectar_trimestre(carpeta_nombre: str) -> str:
    """
    Detecta el trimestre del nombre de la carpeta.
    
    Busca patrones como "1 TRI", "2TRI", "3 TRIMESTRE", etc.
    Evita falsos positivos con el año (2025 contiene 2).
    
    Args:
        carpeta_nombre: Nombre de la carpeta en mayusculas
        
    Returns:
        Codigo de trimestre (1T25, 2T25, etc.) o fecha actual
    """
    # Patron para detectar trimestre: numero seguido de TRI
    # Ejemplos: "1 TRI", "1TRI", "2 TRIMESTRE", "4 TRI 2025"
    match = re.search(r'(\d)\s*TRI', carpeta_nombre)
    if match:
        num_tri = match.group(1)
        if num_tri in '1234':
            return f'{num_tri}T25'
    
    # Patron alternativo: "TRI" seguido de numero
    match = re.search(r'TRI\w*\s*(\d)', carpeta_nombre)
    if match:
        num_tri = match.group(1)
        if num_tri in '1234':
            return f'{num_tri}T25'
    
    # Si no se detecta, usar fecha actual
    return datetime.now().strftime('%Y%m%d')


def main():
    """Funcion principal."""
    parser = argparse.ArgumentParser(
        description=f'ParsearFacturas v{VERSION}',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main.py -i "C:\\Facturas\\3 TRI 2025"
  python main.py -i facturas/ -o resultado.xlsx
  python main.py --listar-extractores
        """
    )
    
    parser.add_argument('--input', '-i', help='Carpeta de facturas PDF')
    parser.add_argument('--output', '-o', default=None, 
                        help='Archivo Excel de salida (default: outputs/Facturas_[trimestre].xlsx)')
    parser.add_argument('--diccionario', '-d', default=DICCIONARIO_DEFAULT,
                        help=f'DiccionarioProveedoresCategoria.xlsx')
    parser.add_argument('--listar-extractores', action='store_true',
                        help='Listar extractores disponibles y salir')
    parser.add_argument('--version', '-v', action='version', version=f'v{VERSION}')
    
    args = parser.parse_args()
    
    # Listar extractores
    if args.listar_extractores:
        extractores = listar_extractores()
        print(f"\nEXTRACTORES DISPONIBLES ({len(extractores)}):\n")
        for nombre, clase in sorted(extractores.items()):
            print(f"  - {nombre}")
        print()
        return
    
    # Verificar input
    if not args.input:
        parser.print_help()
        print("\nERROR: Debes especificar una carpeta con -i")
        sys.exit(1)
    
    carpeta = Path(args.input)
    if not carpeta.exists():
        print(f"ERROR: No existe la carpeta: {carpeta}")
        sys.exit(1)
    
    # Verificar diccionario
    diccionario_path = Path(args.diccionario)
    if not diccionario_path.exists():
        print(f"Aviso: Diccionario no encontrado: {diccionario_path}")
        print("   Continuando sin categorizacion...")
        indice = {}
    else:
        print(f"\nCargando diccionario...")
        _, _, indice = cargar_diccionario(diccionario_path)
        print(f"   {len(indice)} proveedores indexados")
    
    # Cabecera
    print("\n" + "="*60)
    print(f"PARSEAR FACTURAS v{VERSION}")
    print("="*60)
    
    # Determinar carpeta de salida
    script_dir = Path(__file__).parent
    outputs_dir = script_dir / 'outputs'
    outputs_dir.mkdir(exist_ok=True)
    
    # Determinar nombre del archivo de salida
    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute() and output_path.parent == Path('.'):
            ruta_excel = outputs_dir / output_path.name
        else:
            ruta_excel = output_path
    else:
        # Detectar trimestre del nombre de carpeta (corregido)
        carpeta_nombre = carpeta.name.upper()
        trimestre = detectar_trimestre(carpeta_nombre)
        ruta_excel = outputs_dir / f'Facturas_{trimestre}.xlsx'
    
    # Buscar PDFs
    archivos = list(carpeta.glob('*.pdf'))
    print(f"\nCarpeta: {carpeta}")
    print(f"   Archivos PDF: {len(archivos)}")
    
    if not archivos:
        print("ERROR: No se encontraron archivos PDF")
        sys.exit(1)
    
    # Procesar facturas
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
    
    # Generar salidas
    print(f"\nGenerando Excel...")
    total_filas = generar_excel(facturas, ruta_excel)
    print(f"   {ruta_excel}: {total_filas} filas")
    
    ruta_log = outputs_dir / f"log_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    generar_log(facturas, ruta_log)
    print(f"   {ruta_log}")
    
    # Resumen
    imprimir_resumen(facturas)
    
    print("Proceso completado\n")


if __name__ == '__main__':
    main()
