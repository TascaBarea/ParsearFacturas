#!/usr/bin/env python3
"""
LOGGER PARA PARSEARFACTURAS
============================
Sistema de registro (logging) que guarda todo lo que pasa en un archivo.

¿PARA QUÉ SIRVE?
- Saber qué facturas se procesaron bien
- Ver qué facturas fallaron y POR QUÉ
- Tener un historial de cada ejecución

USO BÁSICO:
    from src.facturas.utils.logger import crear_logger, log_factura
    
    logger = crear_logger()
    logger.info("Empezando a procesar facturas...")
    
    # Cuando procesas una factura:
    log_factura(logger, "ZUBELZU", "A-51993", 1175.20, ok=True)
    
    # Si falla:
    log_factura(logger, "BERNAL", "???", 0, ok=False, error="No encontré el número")
"""

import logging
import os
from datetime import datetime
from pathlib import Path


def crear_logger(nombre='parsear_facturas', carpeta_logs='logs'):
    """
    Crea un logger que escribe en archivo y en pantalla.
    
    Args:
        nombre: Nombre del logger (aparece en los mensajes)
        carpeta_logs: Dónde guardar los archivos de log
    
    Returns:
        Logger configurado y listo para usar
    
    Ejemplo:
        logger = crear_logger()
        logger.info("Hola, esto es un mensaje informativo")
        logger.error("Esto es un error")
        logger.warning("Esto es una advertencia")
    """
    
    # Crear carpeta de logs si no existe
    Path(carpeta_logs).mkdir(parents=True, exist_ok=True)
    
    # Crear el logger
    logger = logging.getLogger(nombre)
    logger.setLevel(logging.DEBUG)
    
    # Si ya tiene handlers, no añadir más (evita duplicados)
    if logger.handlers:
        return logger
    
    # Formato de los mensajes
    # Ejemplo: 2025-12-04 09:30:15 | INFO | Procesando factura ZUBELZU
    formato = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # === ARCHIVO: Guarda TODO (incluido DEBUG) ===
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')
    archivo_log = Path(carpeta_logs) / f'{nombre}_{fecha_hoy}.log'
    
    handler_archivo = logging.FileHandler(archivo_log, encoding='utf-8')
    handler_archivo.setLevel(logging.DEBUG)
    handler_archivo.setFormatter(formato)
    logger.addHandler(handler_archivo)
    
    # === ARCHIVO DE ERRORES: Solo errores ===
    archivo_errores = Path(carpeta_logs) / f'{nombre}_ERRORES.log'
    
    handler_errores = logging.FileHandler(archivo_errores, encoding='utf-8')
    handler_errores.setLevel(logging.ERROR)
    handler_errores.setFormatter(formato)
    logger.addHandler(handler_errores)
    
    # === PANTALLA: INFO y superiores ===
    handler_pantalla = logging.StreamHandler()
    handler_pantalla.setLevel(logging.INFO)
    
    # Formato con colores para pantalla
    formato_pantalla = logging.Formatter('%(levelname)-8s | %(message)s')
    handler_pantalla.setFormatter(formato_pantalla)
    logger.addHandler(handler_pantalla)
    
    return logger


def log_factura(logger, proveedor, num_factura, importe, ok=True, error=None):
    """
    Registra el resultado de procesar una factura.
    
    Args:
        logger: El logger creado con crear_logger()
        proveedor: Nombre del proveedor (ej: "ZUBELZU")
        num_factura: Número de factura (ej: "A-51993")
        importe: Importe total en euros (ej: 1175.20)
        ok: True si se procesó bien, False si falló
        error: Mensaje de error (solo si ok=False)
    
    Ejemplos:
        # Factura procesada correctamente:
        log_factura(logger, "BERNAL", "F-2025-001", 543.21, ok=True)
        
        # Factura con error:
        log_factura(logger, "KINEMA", "???", 0, ok=False, error="Patrón no encontrado")
    """
    if ok:
        logger.info(f"✅ {proveedor} | {num_factura} | €{importe:.2f}")
    else:
        logger.error(f"❌ {proveedor} | {num_factura} | Error: {error}")


def log_resumen(logger, procesadas_ok, procesadas_error, total_euros, segundos):
    """
    Registra el resumen al final de una ejecución.
    
    Args:
        logger: El logger
        procesadas_ok: Número de facturas procesadas correctamente
        procesadas_error: Número de facturas con error
        total_euros: Suma total de importes
        segundos: Tiempo que tardó en ejecutar
    
    Ejemplo:
        log_resumen(logger, procesadas_ok=25, procesadas_error=3, 
                    total_euros=15420.50, segundos=45.3)
    """
    total = procesadas_ok + procesadas_error
    logger.info("=" * 50)
    logger.info(f"RESUMEN: {procesadas_ok}/{total} OK ({procesadas_error} errores)")
    logger.info(f"TOTAL: €{total_euros:,.2f}")
    logger.info(f"TIEMPO: {segundos:.1f} segundos")
    logger.info("=" * 50)


# ============================================================
# EJEMPLO DE USO
# ============================================================
if __name__ == '__main__':
    # Crear logger
    logger = crear_logger()
    
    logger.info("=== INICIO PROCESAMIENTO ===")
    
    # Simular procesamiento de facturas
    log_factura(logger, "ZUBELZU", "A-51993", 1175.20, ok=True)
    log_factura(logger, "BERNAL", "F-001", 543.21, ok=True)
    log_factura(logger, "KINEMA", "???", 0, ok=False, error="Patrón no encontrado")
    log_factura(logger, "CROQUELLANAS", "A/1234", 89.50, ok=True)
    
    # Resumen final
    log_resumen(logger, procesadas_ok=3, procesadas_error=1, 
                total_euros=1807.91, segundos=12.5)
    
    print("\n✅ Logs guardados en la carpeta 'logs/'")
