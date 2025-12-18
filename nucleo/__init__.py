"""
Módulo núcleo del sistema.
Contiene las funciones principales de procesamiento.
"""
from .factura import Factura
from .pdf import extraer_texto_pdf
from .parser import extraer_fecha, extraer_cif, extraer_iban, extraer_total, extraer_ref
from .validacion import validar_cuadre, detectar_duplicado
