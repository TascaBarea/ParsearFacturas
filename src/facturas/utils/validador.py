#!/usr/bin/env python3
"""
VALIDADOR DE PATRONES YAML
===========================
Comprueba que tus archivos YAML de patrones están bien escritos
ANTES de ejecutar el procesamiento.

USO:
    python -m src.facturas.utils.validador patterns/
    
    O desde código:
    from src.facturas.utils.validador import validar_patron, validar_carpeta
    
    resultado = validar_patron("patterns/BERNAL.yml")
    print(resultado)
"""

import re
import yaml
from pathlib import Path
from typing import List, Tuple


class ResultadoValidacion:
    """Resultado de validar un patrón"""
    
    def __init__(self, archivo: str):
        self.archivo = archivo
        self.errores: List[str] = []
        self.avisos: List[str] = []
    
    @property
    def valido(self) -> bool:
        return len(self.errores) == 0
    
    def __str__(self) -> str:
        nombre = Path(self.archivo).name
        if self.valido and not self.avisos:
            return f"✅ {nombre}"
        elif self.valido:
            lineas = [f"⚠️  {nombre}"]
            for aviso in self.avisos:
                lineas.append(f"   ⚠️  {aviso}")
            return "\n".join(lineas)
        else:
            lineas = [f"❌ {nombre}"]
            for error in self.errores:
                lineas.append(f"   ❌ {error}")
            for aviso in self.avisos:
                lineas.append(f"   ⚠️  {aviso}")
            return "\n".join(lineas)


def validar_regex(patron_regex: str, nombre_campo: str) -> Tuple[bool, str]:
    """Comprueba si una expresión regular es válida."""
    try:
        re.compile(patron_regex)
        return True, ""
    except re.error as e:
        return False, f"Regex inválida en '{nombre_campo}': {e}"


def buscar_regex_en_dict(d: dict, path: str = "") -> List[Tuple[str, str]]:
    """Busca recursivamente todos los campos 'regex' en un diccionario."""
    encontrados = []
    
    if isinstance(d, dict):
        for key, value in d.items():
            nueva_ruta = f"{path}.{key}" if path else key
            
            if key == 'regex' and isinstance(value, str):
                encontrados.append((nueva_ruta, value))
            elif key == 'pattern' and isinstance(value, str):
                encontrados.append((nueva_ruta, value))
            else:
                encontrados.extend(buscar_regex_en_dict(value, nueva_ruta))
    
    elif isinstance(d, list):
        for i, item in enumerate(d):
            encontrados.extend(buscar_regex_en_dict(item, f"{path}[{i}]"))
    
    return encontrados


def validar_patron(archivo: str) -> ResultadoValidacion:
    """
    Valida un archivo YAML de patrón.
    
    Args:
        archivo: Ruta al archivo .yml o .yaml
    
    Returns:
        ResultadoValidacion con errores y avisos
    """
    resultado = ResultadoValidacion(archivo)
    
    # 1. Verificar que el archivo existe
    if not Path(archivo).exists():
        resultado.errores.append(f"Archivo no encontrado: {archivo}")
        return resultado
    
    # 2. Intentar cargar el YAML
    try:
        with open(archivo, encoding='utf-8') as f:
            contenido = yaml.safe_load(f)
    except yaml.YAMLError as e:
        resultado.errores.append(f"Error de sintaxis YAML: {e}")
        return resultado
    except Exception as e:
        resultado.errores.append(f"Error leyendo archivo: {e}")
        return resultado
    
    if not contenido:
        resultado.errores.append("Archivo vacío o no es un diccionario")
        return resultado
    
    # 3. Verificar campos básicos
    campos_identificacion = ['name', 'provider', 'pattern']
    tiene_identificacion = any(campo in contenido for campo in campos_identificacion)
    
    if not tiene_identificacion:
        resultado.errores.append(
            "Falta identificación del proveedor. Añade 'name', 'provider' o 'pattern'"
        )
    
    # 4. Validar todas las regex del archivo
    regex_encontradas = buscar_regex_en_dict(contenido)
    
    for ruta, regex_str in regex_encontradas:
        valida, error = validar_regex(regex_str, ruta)
        if not valida:
            resultado.errores.append(error)
    
    # 5. Avisos
    if 'output_map' not in contenido and 'output' not in contenido:
        resultado.avisos.append("No tiene 'output_map' ni 'output' definido")
    
    if contenido.get('source') == 'OCR' and 'anchors' not in contenido:
        resultado.avisos.append("Es OCR pero no tiene 'anchors' definidos")
    
    if 'category_map' not in contenido:
        resultado.avisos.append("No tiene 'category_map'")
    
    return resultado


def validar_carpeta(carpeta: str) -> List[ResultadoValidacion]:
    """Valida todos los archivos YAML de una carpeta."""
    carpeta_path = Path(carpeta)
    
    if not carpeta_path.exists():
        print(f"❌ Carpeta no encontrada: {carpeta}")
        return []
    
    archivos = list(carpeta_path.glob('*.yml')) + list(carpeta_path.glob('*.yaml'))
    
    if not archivos:
        print(f"⚠️  No se encontraron archivos YAML en {carpeta}")
        return []
    
    resultados = []
    for archivo in sorted(archivos):
        resultados.append(validar_patron(str(archivo)))
    
    return resultados


def imprimir_resumen(resultados: List[ResultadoValidacion]):
    """Imprime un resumen de la validación"""
    
    total = len(resultados)
    validos = sum(1 for r in resultados if r.valido)
    con_avisos = sum(1 for r in resultados if r.valido and r.avisos)
    con_errores = sum(1 for r in resultados if not r.valido)
    
    print("=" * 50)
    print("VALIDACIÓN DE PATRONES")
    print("=" * 50)
    print(f"Total patrones: {total}")
    print(f"✅ Válidos:     {validos}")
    print(f"⚠️  Con avisos:  {con_avisos}")
    print(f"❌ Con errores: {con_errores}")
    print("=" * 50)
    print()
    
    for resultado in resultados:
        print(resultado)
    
    print()
    if con_errores == 0:
        print("✅ Todos los patrones son válidos")
    else:
        print(f"❌ Hay {con_errores} patrón(es) con errores que debes corregir")


# Ejecución desde línea de comandos
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python validador.py <carpeta_patrones>")
        print("Ejemplo: python validador.py patterns/")
        sys.exit(1)
    
    carpeta = sys.argv[1]
    resultados = validar_carpeta(carpeta)
    
    if resultados:
        imprimir_resumen(resultados)
