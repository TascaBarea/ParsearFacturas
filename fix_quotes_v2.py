#!/usr/bin/env python3
"""
CORRECTOR DE COMILLAS v2
========================
Cambia TODAS las comillas dobles por simples en líneas que parezcan regex.
Más agresivo que la versión anterior.

USO:
    python fix_quotes_v2.py patterns/
"""

import re
from pathlib import Path
import shutil


def corregir_archivo(ruta: Path) -> tuple:
    """
    Corrige un archivo YAML cambiando comillas dobles por simples
    en cualquier línea que contenga patrones regex.
    
    Returns:
        (corregido: bool, lineas_cambiadas: int)
    """
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            contenido = f.read()
    except Exception as e:
        print(f"   ❌ Error leyendo {ruta.name}: {e}")
        return False, 0
    
    original = contenido
    lineas_cambiadas = 0
    
    # Patrón para encontrar valores entre comillas dobles que parecen regex
    # Busca: "algo que contenga \s, \d, \w, \., \(, \), etc."
    
    def reemplazar_comillas(match):
        nonlocal lineas_cambiadas
        contenido_interno = match.group(1)
        # Si contiene caracteres de escape típicos de regex, cambiar comillas
        if re.search(r'\\[sdwbDSWB.()[\]{}+*?^$|]', contenido_interno):
            lineas_cambiadas += 1
            return f"'{contenido_interno}'"
        # También si parece una regex compleja
        if re.search(r'[\^$.*+?\[\](){}|]', contenido_interno) and '\\' in contenido_interno:
            lineas_cambiadas += 1
            return f"'{contenido_interno}'"
        return match.group(0)  # No cambiar
    
    # Buscar y reemplazar todas las cadenas entre comillas dobles
    contenido = re.sub(r'"([^"]*)"', reemplazar_comillas, contenido)
    
    if contenido != original:
        # Crear backup
        backup = ruta.with_suffix('.yml.backup')
        if not backup.exists():  # Solo crear backup si no existe
            shutil.copy(ruta, backup)
        
        # Guardar archivo corregido
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
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
    archivos = [a for a in archivos if '.bak' not in a.name and '.backup' not in a.name]
    
    print("=" * 50)
    print("CORRECTOR DE COMILLAS v2")
    print("=" * 50)
    print(f"Carpeta: {carpeta}")
    print(f"Archivos a revisar: {len(archivos)}")
    print("=" * 50)
    print()
    
    total_corregidos = 0
    total_lineas = 0
    
    for archivo in sorted(archivos):
        corregido, lineas = corregir_archivo(archivo)
        
        if corregido:
            print(f"✅ {archivo.name} - {lineas} corrección(es)")
            total_corregidos += 1
            total_lineas += lineas
    
    print()
    print("=" * 50)
    print(f"RESUMEN:")
    print(f"  Archivos corregidos: {total_corregidos}")
    print(f"  Correcciones:        {total_lineas}")
    print("=" * 50)
    
    if total_corregidos > 0:
        print()
        print("✅ Ejecuta el validador de nuevo:")
        print("   python -m src.facturas.utils.validador patterns")
    else:
        print()
        print("No se encontraron más comillas dobles que corregir.")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python fix_quotes_v2.py <carpeta_patrones>")
        print("Ejemplo: python fix_quotes_v2.py patterns/")
        sys.exit(1)
    
    main(sys.argv[1])
