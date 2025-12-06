#!/usr/bin/env python3
"""
CORRECTOR DE COMILLAS EN PATRONES YAML
=======================================
Cambia comillas dobles por simples en líneas con regex
para evitar errores de escape (\s, \d, etc.)

USO:
    python fix_quotes.py patterns/
"""

import re
from pathlib import Path
import shutil


def necesita_correccion(linea: str) -> bool:
    """Detecta si una línea tiene regex con comillas dobles problemáticas"""
    # Buscar líneas que tengan: regex: "..." o pattern: "..."
    # y que contengan \s, \d, \w, \b, etc.
    
    if 'regex' not in linea.lower() and 'pattern' not in linea.lower():
        return False
    
    # Tiene comillas dobles con escape characters
    if re.search(r':\s*"[^"]*\\[sdwbDSWB][^"]*"', linea):
        return True
    
    return False


def corregir_linea(linea: str) -> str:
    """Cambia comillas dobles por simples en una línea de regex"""
    
    # Patrón para encontrar: algo: "valor con \s o \d"
    # y cambiarlo por: algo: 'valor con \s o \d'
    
    def reemplazar(match):
        antes = match.group(1)  # La parte antes de las comillas (ej: "regex: ")
        contenido = match.group(2)  # El contenido entre comillas
        return f"{antes}'{contenido}'"
    
    # Buscar y reemplazar
    nueva_linea = re.sub(
        r'((?:regex|pattern)\s*:\s*)"([^"]*)"',
        reemplazar,
        linea,
        flags=re.IGNORECASE
    )
    
    return nueva_linea


def corregir_archivo(ruta: Path) -> tuple:
    """
    Corrige un archivo YAML.
    
    Returns:
        (corregido: bool, lineas_cambiadas: int)
    """
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
    except Exception as e:
        print(f"   ❌ Error leyendo {ruta.name}: {e}")
        return False, 0
    
    lineas_cambiadas = 0
    nuevas_lineas = []
    
    for i, linea in enumerate(lineas):
        if necesita_correccion(linea):
            nueva_linea = corregir_linea(linea)
            if nueva_linea != linea:
                lineas_cambiadas += 1
                print(f"   Línea {i+1}: corregida")
            nuevas_lineas.append(nueva_linea)
        else:
            nuevas_lineas.append(linea)
    
    if lineas_cambiadas > 0:
        # Crear backup
        backup = ruta.with_suffix('.yml.bak2')
        shutil.copy(ruta, backup)
        
        # Guardar archivo corregido
        with open(ruta, 'w', encoding='utf-8') as f:
            f.writelines(nuevas_lineas)
        
        return True, lineas_cambiadas
    
    return False, 0


def main(carpeta: str):
    """Corrige todos los archivos YAML de una carpeta"""
    
    carpeta_path = Path(carpeta)
    
    if not carpeta_path.exists():
        print(f"❌ Carpeta no encontrada: {carpeta}")
        return
    
    archivos = list(carpeta_path.glob('*.yml')) + list(carpeta_path.glob('*.yaml'))
    # Excluir backups
    archivos = [a for a in archivos if not a.name.endswith('.bak') and not a.name.endswith('.bak2')]
    
    print("=" * 50)
    print("CORRECTOR DE COMILLAS EN REGEX")
    print("=" * 50)
    print(f"Carpeta: {carpeta}")
    print(f"Archivos encontrados: {len(archivos)}")
    print("=" * 50)
    print()
    
    total_corregidos = 0
    total_lineas = 0
    
    for archivo in sorted(archivos):
        corregido, lineas = corregir_archivo(archivo)
        
        if corregido:
            print(f"✅ {archivo.name} - {lineas} línea(s) corregida(s)")
            total_corregidos += 1
            total_lineas += lineas
        # Solo mostrar los que se corrigieron
    
    print()
    print("=" * 50)
    print(f"RESUMEN:")
    print(f"  Archivos corregidos: {total_corregidos}")
    print(f"  Líneas modificadas:  {total_lineas}")
    print(f"  Backups creados:     {total_corregidos} (extensión .bak2)")
    print("=" * 50)
    
    if total_corregidos > 0:
        print()
        print("✅ Corrección completada. Ejecuta el validador de nuevo:")
        print("   python -m src.facturas.utils.validador patterns")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python fix_quotes.py <carpeta_patrones>")
        print("Ejemplo: python fix_quotes.py patterns/")
        sys.exit(1)
    
    main(sys.argv[1])
