"""
Sistema de extractores con registro automático.

Uso:
    from extractores import EXTRACTORES, registrar
    
    @registrar('NOMBRE_PROVEEDOR')
    class MiExtractor(ExtractorBase):
        ...

El decorador @registrar añade automáticamente el extractor al diccionario EXTRACTORES.
"""
import os
import importlib
from pathlib import Path

# Diccionario global de extractores registrados
# Clave: nombre proveedor (mayúsculas)
# Valor: clase del extractor
EXTRACTORES = {}


def registrar(*nombres_proveedor):
    """
    Decorador para registrar extractores automáticamente.
    
    Uso:
        @registrar('CERES')
        class ExtractorCeres(ExtractorBase):
            ...
        
        # También permite múltiples nombres (alias):
        @registrar('ECOMS', 'ECOMS SUPERMARKET', 'DIA')
        class ExtractorEcoms(ExtractorBase):
            ...
    
    Args:
        *nombres_proveedor: Nombres del proveedor (se convierten a mayúsculas)
    """
    def decorator(cls):
        for nombre in nombres_proveedor:
            EXTRACTORES[nombre.upper()] = cls
        return cls
    return decorator


def obtener_extractor(nombre_proveedor: str):
    """
    Obtiene el extractor para un proveedor dado.
    
    Args:
        nombre_proveedor: Nombre del proveedor
        
    Returns:
        Instancia del extractor o None si no existe
    """
    nombre_upper = nombre_proveedor.upper()
    
    # Buscar coincidencia exacta
    if nombre_upper in EXTRACTORES:
        return EXTRACTORES[nombre_upper]()
    
    # Buscar coincidencia parcial
    for clave, extractor_cls in EXTRACTORES.items():
        if clave in nombre_upper or nombre_upper in clave:
            return extractor_cls()
    
    return None


def listar_extractores():
    """Lista todos los extractores registrados."""
    return sorted(EXTRACTORES.keys())


def _cargar_extractores():
    """
    Carga automáticamente todos los extractores del directorio.
    Se ejecuta al importar el módulo.
    """
    directorio = Path(__file__).parent
    
    for archivo in directorio.glob('*.py'):
        if archivo.name.startswith('_') or archivo.name == 'base.py':
            continue
        
        modulo_nombre = archivo.stem
        try:
            importlib.import_module(f'.{modulo_nombre}', package='extractores')
        except Exception as e:
            print(f"⚠️ Error cargando extractor {modulo_nombre}: {e}")


# Cargar extractores al importar el módulo
_cargar_extractores()
