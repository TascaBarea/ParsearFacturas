"""
Módulo de validación de facturas.

Contiene funciones para:
- Validar cuadre de facturas
- Detectar facturas duplicadas
- Generar claves únicas de factura

Uso:
    from nucleo.validacion import validar_cuadre, detectar_duplicado
    
    cuadre = validar_cuadre(lineas, total_factura)
    es_duplicada = detectar_duplicado(factura, registro)
"""
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import pandas as pd
from datetime import datetime

# Configuración
TOLERANCIA_CUADRE = 0.05  # Tolerancia de 5 céntimos


# =============================================================================
# VALIDACIÓN DE CUADRE
# =============================================================================

def validar_cuadre(
    lineas: List[Dict],
    total_factura: Optional[float],
    tolerancia: float = TOLERANCIA_CUADRE
) -> str:
    """
    Valida que la suma de líneas cuadre con el total de la factura.
    
    Args:
        lineas: Lista de diccionarios con las líneas (debe tener 'base' e 'iva')
        total_factura: Total declarado en la factura
        tolerancia: Tolerancia permitida (por defecto 0.05€)
        
    Returns:
        Estado del cuadre:
        - 'OK': Cuadra correctamente
        - 'SIN_TOTAL': No se encontró total en la factura
        - 'SIN_LINEAS': No se encontraron líneas
        - 'DESCUADRE_X.XX': Diferencia de X.XX euros
    """
    # Sin líneas
    if not lineas:
        return 'SIN_LINEAS'
    
    # Sin total
    if total_factura is None:
        return 'SIN_TOTAL'
    
    # Calcular suma de líneas
    total_calculado = 0.0
    for linea in lineas:
        base = float(linea.get('base', 0))
        iva = int(linea.get('iva', 21))
        total_linea = base * (1 + iva / 100)
        total_calculado += total_linea
    
    total_calculado = round(total_calculado, 2)
    
    # Comparar
    diferencia = abs(total_factura - total_calculado)
    
    if diferencia <= tolerancia:
        return 'OK'
    else:
        return f'DESCUADRE_{diferencia:.2f}'


def calcular_total_lineas(lineas: List[Dict]) -> float:
    """
    Calcula el total sumando todas las líneas.
    
    Args:
        lineas: Lista de diccionarios con 'base' e 'iva'
        
    Returns:
        Total calculado
    """
    total = 0.0
    for linea in lineas:
        base = float(linea.get('base', 0))
        iva = int(linea.get('iva', 21))
        total += base * (1 + iva / 100)
    return round(total, 2)


def calcular_base_total(lineas: List[Dict]) -> float:
    """
    Calcula la base imponible total.
    
    Args:
        lineas: Lista de diccionarios con 'base'
        
    Returns:
        Base total
    """
    return round(sum(float(l.get('base', 0)) for l in lineas), 2)


# =============================================================================
# DETECCIÓN DE DUPLICADOS
# =============================================================================

def generar_clave_factura(
    proveedor: str,
    fecha: str,
    total: Optional[float]
) -> str:
    """
    Genera una clave única para identificar una factura.
    
    La clave se basa en: PROVEEDOR + FECHA + TOTAL (redondeado)
    
    Args:
        proveedor: Nombre del proveedor
        fecha: Fecha de la factura (DD/MM/YYYY)
        total: Total de la factura
        
    Returns:
        Clave única de la factura
    """
    proveedor_norm = proveedor.upper().strip()
    fecha_norm = fecha.strip() if fecha else ''
    total_norm = f"{total:.2f}" if total else '0.00'
    
    return f"{proveedor_norm}|{fecha_norm}|{total_norm}"


def detectar_duplicado(
    proveedor: str,
    fecha: str,
    total: Optional[float],
    registro: pd.DataFrame
) -> Tuple[bool, Optional[str]]:
    """
    Detecta si una factura ya existe en el registro.
    
    Args:
        proveedor: Nombre del proveedor
        fecha: Fecha de la factura
        total: Total de la factura
        registro: DataFrame con el registro de facturas procesadas
        
    Returns:
        Tupla (es_duplicada, archivo_original)
        - es_duplicada: True si la factura ya existe
        - archivo_original: Nombre del archivo original si es duplicada
    """
    if registro is None or registro.empty:
        return False, None
    
    clave = generar_clave_factura(proveedor, fecha, total)
    
    # Buscar en el registro
    if 'CLAVE' in registro.columns:
        duplicados = registro[registro['CLAVE'] == clave]
        if not duplicados.empty:
            archivo = duplicados.iloc[0].get('ARCHIVO', 'desconocido')
            return True, archivo
    
    # Búsqueda alternativa por campos
    proveedor_upper = proveedor.upper().strip()
    
    mascara = (
        (registro['PROVEEDOR'].str.upper().str.strip() == proveedor_upper) &
        (registro['FECHA'] == fecha)
    )
    
    if total is not None:
        # Tolerancia de 1 céntimo para el total
        mascara = mascara & (
            (registro['TOTAL FAC'] >= total - 0.01) &
            (registro['TOTAL FAC'] <= total + 0.01)
        )
    
    duplicados = registro[mascara]
    if not duplicados.empty:
        archivo = duplicados.iloc[0].get('ARCHIVO', 'desconocido')
        return True, archivo
    
    return False, None


# =============================================================================
# REGISTRO DE FACTURAS
# =============================================================================

def cargar_registro(ruta: Path) -> pd.DataFrame:
    """
    Carga el registro de facturas procesadas.
    
    Args:
        ruta: Ruta al archivo Excel de registro
        
    Returns:
        DataFrame con el registro o DataFrame vacío si no existe
    """
    ruta = Path(ruta)
    
    if not ruta.exists():
        # Crear registro vacío con las columnas necesarias
        return pd.DataFrame(columns=[
            'CLAVE', 'PROVEEDOR', 'FECHA', 'TOTAL FAC', 
            'ARCHIVO', 'PROCESADO_AT'
        ])
    
    try:
        return pd.read_excel(ruta)
    except Exception as e:
        print(f"⚠️ Error cargando registro: {e}")
        return pd.DataFrame()


def guardar_registro(registro: pd.DataFrame, ruta: Path):
    """
    Guarda el registro de facturas procesadas.
    
    Args:
        registro: DataFrame con el registro
        ruta: Ruta donde guardar el archivo Excel
    """
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        registro.to_excel(ruta, index=False)
    except Exception as e:
        print(f"⚠️ Error guardando registro: {e}")


def agregar_al_registro(
    registro: pd.DataFrame,
    proveedor: str,
    fecha: str,
    total: Optional[float],
    archivo: str
) -> pd.DataFrame:
    """
    Agrega una factura al registro.
    
    Args:
        registro: DataFrame del registro actual
        proveedor: Nombre del proveedor
        fecha: Fecha de la factura
        total: Total de la factura
        archivo: Nombre del archivo
        
    Returns:
        DataFrame actualizado
    """
    clave = generar_clave_factura(proveedor, fecha, total)
    
    nueva_fila = pd.DataFrame([{
        'CLAVE': clave,
        'PROVEEDOR': proveedor,
        'FECHA': fecha,
        'TOTAL FAC': total,
        'ARCHIVO': archivo,
        'PROCESADO_AT': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }])
    
    return pd.concat([registro, nueva_fila], ignore_index=True)


# =============================================================================
# VALIDACIONES ADICIONALES
# =============================================================================

def validar_factura(
    proveedor: str,
    fecha: str,
    cif: str,
    total: Optional[float],
    lineas: List[Dict]
) -> List[str]:
    """
    Valida una factura y devuelve lista de errores/warnings.
    
    Args:
        proveedor: Nombre del proveedor
        fecha: Fecha de la factura
        cif: CIF del proveedor
        total: Total de la factura
        lineas: Lista de líneas
        
    Returns:
        Lista de errores encontrados
    """
    errores = []
    
    # Validar proveedor
    if not proveedor or proveedor.strip() == '':
        errores.append('PROVEEDOR_PENDIENTE')
    
    # Validar fecha
    if not fecha or fecha.strip() == '':
        errores.append('FECHA_PENDIENTE')
    
    # Validar CIF
    if not cif or cif.strip() == '':
        errores.append('CIF_PENDIENTE')
    
    # Validar total
    if total is None:
        errores.append('SIN_TOTAL')
    
    # Validar líneas
    if not lineas:
        errores.append('SIN_LINEAS')
    
    # Validar cuadre
    if lineas and total is not None:
        cuadre = validar_cuadre(lineas, total)
        if cuadre != 'OK':
            errores.append(cuadre)
    
    return errores


def es_factura_valida(errores: List[str]) -> bool:
    """
    Determina si una factura es válida basándose en sus errores.
    
    Una factura es válida si solo tiene errores menores (CIF, IBAN pendiente)
    pero tiene líneas y cuadra.
    
    Args:
        errores: Lista de errores de la factura
        
    Returns:
        True si la factura es válida
    """
    errores_criticos = ['SIN_LINEAS', 'SIN_TOTAL']
    
    for error in errores:
        if error in errores_criticos or error.startswith('DESCUADRE'):
            return False
    
    return True
