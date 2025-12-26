#!/usr/bin/env python3
"""
generar_proveedores.py - Genera PROVEEDORES.md automáticamente

Lee todos los extractores de la carpeta extractores/ y genera
un archivo Markdown con la lista completa de proveedores.

Uso:
    python generar_proveedores.py

Salida:
    docs/PROVEEDORES.md
"""

import os
import re
from datetime import datetime
from pathlib import Path


def extraer_info_extractor(filepath: str) -> dict:
    """Extrae información de un archivo de extractor."""
    info = {
        'archivo': os.path.basename(filepath),
        'nombres': [],
        'cif': '',
        'iban': '',
        'metodo': 'pdfplumber',
        'categoria_fija': '',
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            contenido = f.read()
    except:
        return None
    
    # Buscar @registrar('NOMBRE', 'VARIANTE1', ...)
    match_registrar = re.search(r"@registrar\s*\(\s*([^)]+)\s*\)", contenido)
    if match_registrar:
        nombres_str = match_registrar.group(1)
        # Extraer strings entre comillas
        nombres = re.findall(r"['\"]([^'\"]+)['\"]", nombres_str)
        info['nombres'] = nombres
    
    # Buscar cif = 'X'
    match_cif = re.search(r"cif\s*=\s*['\"]([^'\"]+)['\"]", contenido)
    if match_cif:
        info['cif'] = match_cif.group(1)
    
    # Buscar iban = 'X'
    match_iban = re.search(r"iban\s*=\s*['\"]([^'\"]+)['\"]", contenido)
    if match_iban:
        info['iban'] = match_iban.group(1)
    
    # Buscar metodo_pdf = 'X'
    match_metodo = re.search(r"metodo_pdf\s*=\s*['\"]([^'\"]+)['\"]", contenido)
    if match_metodo:
        info['metodo'] = match_metodo.group(1)
    
    # Buscar categoria_fija = 'X'
    match_cat = re.search(r"categoria_fija\s*=\s*['\"]([^'\"]+)['\"]", contenido)
    if match_cat:
        info['categoria_fija'] = match_cat.group(1)
    
    return info if info['nombres'] else None


def generar_markdown(extractores: list) -> str:
    """Genera el contenido Markdown."""
    
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    total = len(extractores)
    
    # Contar estadísticas
    con_iban = sum(1 for e in extractores if e['iban'])
    con_categoria_fija = sum(1 for e in extractores if e['categoria_fija'])
    ocr = sum(1 for e in extractores if e['metodo'] == 'ocr')
    hibrido = sum(1 for e in extractores if e['metodo'] == 'hibrido')
    
    md = f"""# 📋 PROVEEDORES - Lista de Extractores

**Generado automáticamente:** {fecha}  
**Script:** `python generar_proveedores.py`

---

## 📊 RESUMEN

| Métrica | Valor |
|---------|-------|
| Total extractores | **{total}** |
| Con IBAN | {con_iban} ({round(con_iban/total*100) if total else 0}%) |
| Con categoría fija | {con_categoria_fija} |
| Método OCR | {ocr} |
| Método híbrido | {hibrido} |
| Método pdfplumber | {total - ocr - hibrido} |

---

## 📑 LISTA COMPLETA

| # | Proveedor | CIF | Método | Cat. Fija | IBAN |
|---|-----------|-----|--------|-----------|------|
"""
    
    # Ordenar por nombre principal
    extractores_ordenados = sorted(extractores, key=lambda x: x['nombres'][0] if x['nombres'] else '')
    
    for i, ext in enumerate(extractores_ordenados, 1):
        nombre = ext['nombres'][0] if ext['nombres'] else '?'
        cif = ext['cif'] or '-'
        metodo = ext['metodo']
        cat = ext['categoria_fija'][:20] + '...' if len(ext['categoria_fija']) > 20 else ext['categoria_fija'] or '-'
        iban = '✅' if ext['iban'] else '❌'
        
        md += f"| {i} | {nombre} | {cif} | {metodo} | {cat} | {iban} |\n"
    
    md += f"""
---

## 🔍 DETALLE POR EXTRACTOR

"""
    
    for ext in extractores_ordenados:
        nombre_principal = ext['nombres'][0] if ext['nombres'] else '?'
        md += f"### {nombre_principal}\n\n"
        md += f"- **Archivo:** `{ext['archivo']}`\n"
        md += f"- **CIF:** {ext['cif'] or 'No especificado'}\n"
        md += f"- **Método:** {ext['metodo']}\n"
        
        if len(ext['nombres']) > 1:
            variantes = ', '.join(ext['nombres'][1:])
            md += f"- **Variantes:** {variantes}\n"
        
        if ext['categoria_fija']:
            md += f"- **Categoría fija:** {ext['categoria_fija']}\n"
        
        if ext['iban']:
            # Ocultar parte del IBAN por seguridad
            iban_oculto = ext['iban'][:8] + '...' + ext['iban'][-4:] if len(ext['iban']) > 12 else ext['iban']
            md += f"- **IBAN:** {iban_oculto}\n"
        
        md += "\n"
    
    md += f"""---

## 📝 NOTAS

- Este archivo se genera automáticamente con `python generar_proveedores.py`
- No editar manualmente - los cambios se perderán
- Para añadir/modificar proveedores, editar los archivos en `extractores/`

---

*Generado: {fecha}*
"""
    
    return md


def main():
    # Determinar rutas
    script_dir = Path(__file__).parent
    extractores_dir = script_dir / 'extractores'
    docs_dir = script_dir / 'docs'
    
    # Crear docs/ si no existe
    docs_dir.mkdir(exist_ok=True)
    
    # Archivos a ignorar
    ignorar = {'__init__.py', 'base.py', '_plantilla.py', '__pycache__'}
    
    # Leer todos los extractores
    extractores = []
    
    if not extractores_dir.exists():
        print(f"❌ No se encuentra la carpeta: {extractores_dir}")
        print("   Ejecuta este script desde la raíz del proyecto")
        return
    
    for archivo in extractores_dir.glob('*.py'):
        if archivo.name in ignorar:
            continue
        
        info = extraer_info_extractor(str(archivo))
        if info:
            extractores.append(info)
    
    print(f"📂 Encontrados {len(extractores)} extractores")
    
    # Generar Markdown
    markdown = generar_markdown(extractores)
    
    # Guardar
    salida = docs_dir / 'PROVEEDORES.md'
    with open(salida, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"✅ Generado: {salida}")
    print(f"   Total: {len(extractores)} proveedores")


if __name__ == '__main__':
    main()
