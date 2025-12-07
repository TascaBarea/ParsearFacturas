"""
Módulo de migración para histórico de facturas 2025.

Uso único para procesar facturas existentes en Dropbox y generar
el archivo Facturas_Recibidas_25.xlsx

Después de la migración inicial, las nuevas facturas se procesan
automáticamente con el módulo gmail.
"""

from .migracion_historico_2025 import main, procesar_carpeta, procesar_factura

__all__ = ['main', 'procesar_carpeta', 'procesar_factura']
