"""
Configuración general del sistema ParsearFacturas.

Este archivo contiene todas las constantes y rutas configurables.
Modificar aquí para adaptar a otro entorno.
"""
from pathlib import Path

# =============================================================================
# VERSIÓN
# =============================================================================
VERSION = "4.0.0"
VERSION_FECHA = "2025-12-18"

# =============================================================================
# RUTAS (modificar según tu instalación)
# =============================================================================

# Ruta base del proyecto
RUTA_PROYECTO = Path(__file__).parent.parent

# Ruta al diccionario de proveedores/categorías
RUTA_DICCIONARIO = RUTA_PROYECTO / "datos" / "diccionario.xlsx"

# Ruta al registro de facturas (anti-duplicados)
RUTA_REGISTRO = RUTA_PROYECTO / "datos" / "registro_facturas.xlsx"

# Carpeta de salida por defecto
CARPETA_OUTPUTS = RUTA_PROYECTO / "outputs"

# Carpeta de PDFs de test
CARPETA_TEST_PDFS = RUTA_PROYECTO / "tests" / "pdfs"

# =============================================================================
# CONFIGURACIÓN OCR (Tesseract)
# =============================================================================

# Ruta a Tesseract en Windows
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configuración de preprocesamiento OCR
OCR_DPI = 300           # Resolución para conversión PDF→imagen
OCR_CONTRASTE = 2.0     # Factor de contraste
OCR_IDIOMA = 'spa'      # Idioma para OCR

# =============================================================================
# CONFIGURACIÓN DE PROCESAMIENTO
# =============================================================================

# Tolerancia para cuadre de facturas (en euros)
TOLERANCIA_CUADRE = 0.05

# Métodos de extracción PDF disponibles
METODOS_PDF = ['pypdf', 'pdfplumber', 'ocr']

# Método por defecto
METODO_PDF_DEFAULT = 'pypdf'

# =============================================================================
# TIPOS DE IVA
# =============================================================================

IVA_GENERAL = 21
IVA_REDUCIDO = 10
IVA_SUPERREDUCIDO = 4

TIPOS_IVA = [IVA_SUPERREDUCIDO, IVA_REDUCIDO, IVA_GENERAL]

# =============================================================================
# CATEGORÍAS POR DEFECTO
# =============================================================================

CATEGORIAS_DEFAULT = {
    'BEBIDAS': 'BEBIDAS',
    'VINOS': 'BEBIDAS',
    'LICORES': 'BEBIDAS',
    'CERVEZAS': 'BEBIDAS',
    'REFRESCOS': 'BEBIDAS',
    'CARNES': 'CARNES',
    'EMBUTIDOS': 'CARNES',
    'JAMONES': 'CARNES',
    'QUESOS': 'LACTEOS',
    'LACTEOS': 'LACTEOS',
    'CONSERVAS': 'CONSERVAS',
    'ACEITES': 'ACEITES',
    'PANADERIA': 'PANADERIA',
    'LIMPIEZA': 'LIMPIEZA',
    'SUMINISTROS': 'SUMINISTROS',
    'SERVICIOS': 'SERVICIOS',
    'ALQUILER': 'ALQUILER',
}

# =============================================================================
# CONFIGURACIÓN DE LOGS
# =============================================================================

# Formato de fecha para logs
FORMATO_FECHA_LOG = "%Y%m%d_%H%M%S"

# Nivel de log (DEBUG, INFO, WARNING, ERROR)
NIVEL_LOG = "INFO"

# =============================================================================
# CONFIGURACIÓN DE EXCEL
# =============================================================================

# Nombre de la hoja en el Excel de salida
EXCEL_NOMBRE_HOJA = "año 25"

# Columnas del Excel de salida
EXCEL_COLUMNAS = [
    '#',           # Número de factura (del nombre archivo)
    'FECHA',       # Fecha de la factura
    'PROVEEDOR',   # Nombre del proveedor
    'REF',         # Referencia/número factura
    'CIF',         # CIF del proveedor
    'ARTICULO',    # Descripción del artículo
    'CODIGO',      # Código del artículo
    'CATEGORIA',   # Categoría asignada
    'ID_CAT',      # ID de categoría
    'BASE',        # Base imponible
    'IVA',         # Tipo de IVA (4, 10, 21)
    'TOTAL',       # Total línea (base + IVA)
    'TOTAL FAC',   # Total factura
    'CUADRE',      # Estado del cuadre
    'IBAN',        # IBAN del proveedor
    'ARCHIVO',     # Nombre del archivo PDF
]
