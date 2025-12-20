"""
Sistema de extractores de facturas.

Cada extractor es una clase que hereda de ExtractorBase y se registra
automaticamente con el decorador @registrar.

Actualizado: 19/12/2025
"""

# Registro global de extractores
_EXTRACTORES = {}


def registrar(*nombres):
    """
    Decorador para registrar un extractor con uno o mas nombres.
    
    Uso:
        @registrar('BERZAL', 'BERZAL HERMANOS')
        class ExtractorBerzal(ExtractorBase):
            ...
    """
    def decorator(cls):
        for nombre in nombres:
            _EXTRACTORES[nombre.upper()] = cls
        return cls
    return decorator


def obtener_extractor(proveedor: str):
    """
    Obtiene el extractor adecuado para un proveedor.
    
    Args:
        proveedor: Nombre del proveedor
        
    Returns:
        Instancia del extractor o None si no hay uno especifico
    """
    if not proveedor:
        return None
    
    proveedor_upper = proveedor.upper().strip()
    
    # Busqueda exacta
    if proveedor_upper in _EXTRACTORES:
        return _EXTRACTORES[proveedor_upper]()
    
    # Busqueda parcial
    for nombre, clase in _EXTRACTORES.items():
        if nombre in proveedor_upper or proveedor_upper in nombre:
            return clase()
    
    return None


def listar_extractores() -> dict:
    """
    Lista todos los extractores registrados.
    
    Returns:
        Dict {nombre: clase}
    """
    return _EXTRACTORES.copy()


def tiene_extractor(proveedor: str) -> bool:
    """
    Comprueba si existe un extractor para el proveedor.
    """
    return obtener_extractor(proveedor) is not None


# Constante para acceso externo
EXTRACTORES = _EXTRACTORES


# Importar la clase base
from extractores.base import ExtractorBase

# Importar todos los extractores para que se registren
# Los archivos deben existir en la carpeta extractores/

# Extractores individuales (piloto)
try:
    from extractores import berzal
    from extractores import ceres
    from extractores import bm
    from extractores import jimeluz
except ImportError:
    pass

# Extractores de madrueno (con ñ)
try:
    from extractores import madrueño
except ImportError:
    try:
        # Fallback por si hay problemas de encoding
        import importlib
        import sys
        from pathlib import Path
        extractores_dir = Path(__file__).parent
        for archivo in extractores_dir.glob('madru*.py'):
            if archivo.stem != '__init__':
                spec = importlib.util.spec_from_file_location(archivo.stem, archivo)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
    except:
        pass

# Extractores por archivo (multiples clases por archivo)
try:
    from extractores import emjamesa
    from extractores import zucca
    from extractores import quesos_navas
    from extractores import molienda_verde
    from extractores import bernal
    from extractores import felisa
    from extractores import borboton
    from extractores import gredales
    from extractores import gaditaun
    from extractores import ecoms
    from extractores import fabeiro
except ImportError:
    pass

# Extractores agrupados
try:
    from extractores import suministros  # YOIGO, SOM ENERGIA, LUCERA, SEGURMA, KINEMA, ISTA
    from extractores import vinos        # ARGANZA, PURISIMA, CVNE, MUNOZ MARTIN
    from extractores import quesos       # QUESOS FELIX, ROYCA, CATI, SILVA CORDERO
    from extractores import servicios    # ALQUILERES, CONTROLPLAGA, TRUCCO, PANRUJE, ANGEL Y LOLI
    from extractores import productos    # MOLLETES, ZUBELZU, IBARRAKO, ADELL, ECOFICUS, ANA CABALLO, CAMPERO
    from extractores import distribuidores  # LAVAPIES, FABEIRO, SERRIN, MRM, DISBER, LIDL, MAKRO
    from extractores import varios       # MARITA, PILAR, PANIFIESTO, etc.
except ImportError:
    pass

# Extractor generico (siempre disponible)
try:
    from extractores import generico
except ImportError:
    pass

# ============================================================
# EXTRACTORES CORREGIDOS - CARGAR AL FINAL PARA SOBRESCRIBIR
# Estos tienen prioridad sobre los extractores antiguos
# ============================================================

# Sesión 19/12/2025 mañana
try:
    from extractores import molletes_artesanos  # MOLLETES ARTESANOS
except ImportError:
    pass

try:
    from extractores import ista                # ISTA (liquidaciones agua)
except ImportError:
    pass

try:
    from extractores import cvne                # CVNE (vinos y vermuts)
except ImportError:
    pass

try:
    from extractores import quesos_felix        # QUESOS FELIX
except ImportError:
    pass

try:
    from extractores import miguez_cal          # MIGUEZ CAL (ForPlan limpieza)
except ImportError:
    pass

try:
    from extractores import distribuciones_lavapies  # DISTRIBUCIONES LAVAPIES
except ImportError:
    pass

try:
    from extractores import martin_abenza       # MARTIN ABENZA (Conservas El Modesto)
except ImportError:
    pass

try:
    from extractores import ecoficus            # ECOFICUS
except ImportError:
    pass

try:
    from extractores import la_barra_dulce      # LA BARRA DULCE
except ImportError:
    pass

try:
    from extractores import sabores_paterna     # SABORES PATERNA
except ImportError:
    pass

try:
    from extractores import francisco_guerra    # FRANCISCO GUERRA
except ImportError:
    pass

# ============================================================
# SESIÓN 19/12/2025 tarde - NUEVOS EXTRACTORES
# ============================================================

try:
    from extractores import panruje             # PANRUJE (Rosquillas La Ermita)
except ImportError:
    pass

try:
    from extractores import carlos_navas        # CARLOS NAVAS / QUESOS NAVAS / QUESERIA NAVAS
except ImportError:
    pass

try:
    from extractores import porvaz              # PORVAZ / PORVAZ TITO / CONSERVAS TITO
except ImportError:
    pass

try:
    from extractores import grupo_disber        # GRUPO DISBER / VEGAMAR / HERENCIA DEL MAR
except ImportError:
    pass

try:
    from extractores import mrm                 # MRM / INDUSTRIAS CARNICAS MRM
except ImportError:
    pass

try:
    from extractores import pilar_rodriguez     # PILAR RODRIGUEZ / EL MAJADAL / HUEVOS
except ImportError:
    pass

try:
    from extractores import manipulados_abellan # MANIPULADOS ABELLAN / EL LABRADOR / PEPEJO (OCR)
except ImportError:
    pass

try:
    from extractores import la_rosquilleria     # LA ROSQUILLERIA / EL TORRO (OCR)
except ImportError:
    pass

try:
    from extractores import fabeiro             # FABEIRO S.L. (Productos ibericos, anchoas, quesos)
except ImportError:
    pass

try:
    from extractores import kinema              # KINEMA S.COOP.MAD. (Gestoria - categoria fija GESTORIA)
except ImportError:
    pass

try:
    from extractores import silva_cordero       # SILVA CORDERO / QUESOS DE ACEHUCHE (quesos artesanales)
except ImportError:
    pass

try:
    from extractores import artesanos_mollete   # ARTESANOS DEL MOLLETE / MOLLETES ARTESANOS DE ANTEQUERA
except ImportError:
    pass


__all__ = [
    'ExtractorBase',
    'registrar',
    'obtener_extractor',
    'listar_extractores',
    'tiene_extractor',
    'EXTRACTORES'
]
