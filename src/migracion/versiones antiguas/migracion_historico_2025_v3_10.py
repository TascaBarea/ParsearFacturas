#!/usr/bin/env python3
"""
MIGRACIÓN HISTÓRICO 2025 - v3.10
================================
Extrae líneas detalladas de facturas, categoriza artículos,
prorratrea gastos y descuentos, y actualiza maestros.

v3.10 - Añadido extractor JULIO GARCIA VIVAS (verdulería, IVA 4%)
      - Artículo siempre: "Verduras variadas"
      - Factura mensual con lista de albaranes
      - Calcula tipo IVA de la cuota/base (normalmente 4%)
      - NIF: 02869898G
      - NOTA: Algunos PDFs son imágenes escaneadas (requieren OCR)

v3.9 - Añadido extractor MIGUEZ CAL / ForPlan (productos limpieza, IVA 21%)
     - Soporta facturas multipágina con múltiples albaranes
     - Maneja líneas SCRAP (tasas ambientales) correctamente
     - CIF: B79868006
     - Añadido extractor MARITA COSTA (distribuidor gourmet, IVA 4%/10%)
     - Soporta descripciones multilinea
     - NIF: 48207369J
     - Añadido extractor PILAR RODRIGUEZ / HUEVOS EL MAJADAL (huevos, IVA 4%)
     - Maneja fechas partidas en OCR (formato peculiar PyPDF2)
     - NIF: 06582655D, IBAN: ES30 5853 0199 2810 0235 62
     - Añadido extractor PANIFIESTO (pan, IVA 4%)
     - Una línea por factura con total mensual
     - CIF: B87874327
     - MEJORA CRÍTICA: extraer_ref() y extraer_fecha() con patrones específicos
     - Corregida incompatibilidad pypdf vs PyPDF2 (diferentes outputs de OCR)
     - Patrones REF añadidos para: CERES (7 dígitos), LICORES MADRUEÑO (4 dígitos),
       BM (alfanumérico), PANIFIESTO (XX-XXXXXX-XXX), FABEIRO (YY-X.XXX),
       MARITA COSTA (MADRID 1 + 6 dígitos), MIGUEZ CAL (AXXXX),
       PILAR RODRIGUEZ (YYFNNNNN), SERRIN (FV/XXX/YYYY)
     - Patrones FECHA añadidos para: CERES, LICORES MADRUEÑO, BM, PANIFIESTO, SERRIN
     - Resultado: 100% FECHA, 100% REF en PDFs de prueba (59/59)
     - Añadido extractor PILAR RODRIGUEZ / Huevos El Majadal (huevos, IVA 4%)
     - Maneja fechas truncadas por OCR (2-3 dígitos de año)
     - NIF: 06582655D, IBAN: ES30 5853 0199 2810 0235 62

v3.7 - Añadido extractor DISTRIBUCIONES LAVAPIES (bebidas, IVA mixto 10%/21%)
     - Añadido extractor FABEIRO (charcutería/quesos, IVA explícito 4%/10%)
     - Añadido extractor SERRÍN NO CHAN (galletas/vermú, IVA explícito en factura)
     - Añadido extractor BENJAMIN ORTEGA (alquiler local, 500€ + 21% + 19% ret.)
     - Añadido extractor JAIME FERNANDEZ (alquiler local, 500€ + 21% + 19% ret.)
     - ACTIVADO prorrateo de portes/transporte (se distribuye entre líneas)
     - Los portes ya no aparecen como línea separada

v3.6 - Añadido extractor YOIGO/XFERA (telefonía, 1 línea por factura)
     - Añadido extractor SOM ENERGIA (electricidad, IVA 10% o 21% según fecha)
     - Añadido extractor LUCERA/ENERGÍA COLECTIVA (electricidad, IVA 21%)
     - Añadido extractor SEGURMA (alarmas, IVA 21%)
     - Añadido extractor KINEMA (gestoría/cooperativa, múltiples líneas)
     - Añadido extractor OPENAI (ChatGPT, USD sin IVA - reverse charge)
     - Todos son proveedores de adeudo/tarjeta (no necesitan IBAN/CIF)

v3.5 - Corregido extractor JAMONES BERNAL (nuevo formato 1T25)
     - El formato cambió: ahora %IVA está dentro de la línea, no separado
     - Corregido extractor LA PURÍSIMA (código pegado a descripción sin espacio)
     - Corregido extractor EMJAMESA (importe con € después del código, no al final)

v3.4 - Añadido extractor VINOS DE ARGANZA (formato invertido: precio-dto-importe+cant+codigo)
     - Añadido extractor LA PURÍSIMA (Cooperativa del Vino de Yecla, código 9 dígitos)
     - Añadido extractor MOLLETES ARTESANOS (pan artesano, IVA 4%)

v3.3 - Añadido extractor JAMONES BERNAL (formato con código al final)
     - Añadido extractor FELISA GOURMET (formato código pegado a importe)
     - Añadido extractor BODEGAS BORBOTÓN (vinos con promociones)
     - Mejorado extractor BM SUPERMERCADOS (múltiples patrones)
     - Añadido patrón fecha BM (DD/MM/YY HH:MM Caja)
     - Mejorado parsear_nombre_archivo para detectar trimestre en cualquier posición
       (soporta formatos 1001_1T25_... y 4T25_1127_...)

v3.2 - Añadido extractor CVNE (Compañía Vinícola del Norte de España)
     - Mejorado regex de fecha para más formatos (DD/MM/YYYY, DD-MM-YY)
     - Mejorado regex de CIF para formatos con espacios (B 86705126)
     - Corregido extractor LICORES MADRUEÑO
     - Corregido extractor SABORES DE PATERNA
     
v3.1 - Corregidos patrones LICORES MADRUEÑO y SABORES DE PATERNA
     - LICORES: columnas separadas por espacios (no pegadas)
     - SABORES: IVA pegado al precio sin espacio (17,3010,0)
     - Soporte Unicode para ñ y acentos españoles
"""

import os
import re
import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from difflib import SequenceMatcher
import pandas as pd

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader


# =============================================================================
# CONFIGURACIÓN
# =============================================================================

CIF_PROPIO = "B87760575"

# Bancos a evitar en IBAN (cuando hay varios)
BANCOS_EVITAR = ["0049"]

# Diccionario de proveedores conocidos con CIF e IBAN
# Datos recopilados de conversaciones anteriores
PROVEEDORES_CONOCIDOS = {
    # SERRÍN NO CHAN
    'SERRIN': {'cif': 'B87214755', 'iban': 'ES88 0049 6650 1329 1001 8834'},
    'SERRÍN': {'cif': 'B87214755', 'iban': 'ES88 0049 6650 1329 1001 8834'},
    # FABEIRO - CIF del PDF: "CIF.: B-79/992079"
    'FABEIRO': {'cif': 'B79992079', 'iban': 'ES70 0182 1292 2202 0150 5065'},
    # DISTRIBUCIONES LAVAPIES
    'LAVAPIES': {'cif': 'F88424072', 'iban': 'ES39 3035 0376 1437 6001 1213'},
    'DISTRIBUCIONES LAVAPIES': {'cif': 'F88424072', 'iban': 'ES39 3035 0376 1437 6001 1213'},
    # Alquileres (personas físicas)
    'BENJAMIN ORTEGA': {'cif': '09342596L', 'iban': 'ES31 0049 5977 5521 1606 6585'},
    'ORTEGA ALONSO': {'cif': '09342596L', 'iban': 'ES31 0049 5977 5521 1606 6585'},
    'JAIME FERNANDEZ': {'cif': '07219971H', 'iban': 'ES31 0049 5977 5521 1606 6585'},
    'FERNANDEZ MORENO': {'cif': '07219971H', 'iban': 'ES31 0049 5977 5521 1606 6585'},
    # Otros proveedores frecuentes
    'MARTIN ARBENZA': {'cif': '74305431K', 'iban': ''},
    'EL MODESTO': {'cif': '74305431K', 'iban': ''},
    'FRANCISCO GUERRA': {'cif': '50449614B', 'iban': ''},
    'TRUCCO': {'cif': '05247386M', 'iban': ''},
    'ISAAC RODRIGUEZ': {'cif': '05247386M', 'iban': ''},
    'ISTA': {'cif': 'A50090133', 'iban': ''},
    'AMAZON': {'cif': 'W0184081H', 'iban': ''},
    'VINOS DE ARGANZA': {'cif': 'B24416869', 'iban': 'ES92 0081 5385 6500 0121 7327'},
    'LA PURISIMA': {'cif': 'F30005193', 'iban': 'ES78 0081 0259 1000 0184 4495'},
    'PURISIMA': {'cif': 'F30005193', 'iban': 'ES78 0081 0259 1000 0184 4495'},
    'MOLLETES': {'cif': 'B93662708', 'iban': ''},
    'BODEGAS BORBOTON': {'cif': 'B45851755', 'iban': 'ES37 2100 1913 1902 0013 5677'},
    'BORBOTON': {'cif': 'B45851755', 'iban': 'ES37 2100 1913 1902 0013 5677'},
    'FELISA GOURMET': {'cif': 'B72113897', 'iban': 'ES68 0182 1076 9502 0169 3908'},
    'FELISA': {'cif': 'B72113897', 'iban': 'ES68 0182 1076 9502 0169 3908'},
    'JAMONES BERNAL': {'cif': 'B67784231', 'iban': 'ES49 2100 7191 2902 0003 7620'},
    'BERNAL': {'cif': 'B67784231', 'iban': 'ES49 2100 7191 2902 0003 7620'},
    'EMJAMESA': {'cif': 'B37352077', 'iban': ''},
    'MAKRO': {'cif': 'A28647451', 'iban': ''},  # Pago tarjeta
    # Adeudos (no necesitan IBAN)
    'YOIGO': {'cif': 'A82528548', 'iban': ''},
    'XFERA': {'cif': 'A82528548', 'iban': ''},
    'SOM ENERGIA': {'cif': 'F55091367', 'iban': ''},
    'LUCERA': {'cif': 'B98670003', 'iban': ''},
    'SEGURMA': {'cif': 'A48198626', 'iban': ''},
    'KINEMA': {'cif': 'F84600022', 'iban': ''},
    # v3.9 - MIGUEZ CAL (ForPlan)
    'MIGUEZ CAL': {'cif': 'B79868006', 'iban': ''},
    'FORPLAN': {'cif': 'B79868006', 'iban': ''},
    # v3.9 - MARITA COSTA (distribuidor gourmet)
    'MARITA COSTA': {'cif': '48207369J', 'iban': ''},
    # v3.9 - PILAR RODRIGUEZ / Huevos El Majadal
    'PILAR RODRIGUEZ': {'cif': '06582655D', 'iban': 'ES30 5853 0199 2810 0235 62'},
    'EL MAJADAL': {'cif': '06582655D', 'iban': 'ES30 5853 0199 2810 0235 62'},
    'HUEVOS EL MAJADAL': {'cif': '06582655D', 'iban': 'ES30 5853 0199 2810 0235 62'},
    # v3.9 - PANIFIESTO (pan)
    'PANIFIESTO': {'cif': 'B87874327', 'iban': ''},
    'PANIFIESTO LAVAPIES': {'cif': 'B87874327', 'iban': ''},
    # v3.10 - JULIO GARCIA VIVAS (verdulería)
    'JULIO GARCIA VIVAS': {'cif': '02869898G', 'iban': ''},
    'GARCIA VIVAS': {'cif': '02869898G', 'iban': ''},
}


# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass
class LineaFactura:
    """Representa una línea de artículo de la factura."""
    articulo: str
    base: float
    iva: int
    categoria: str = "PENDIENTE"
    codigo: str = ""


@dataclass
class Factura:
    """Representa una factura completa."""
    archivo: str
    numero: str  # Del nombre del archivo
    trimestre: str
    metodo_pago: str
    proveedor_archivo: str  # Del nombre del archivo
    proveedor_normalizado: str = ""  # Del diccionario
    fecha: str = ""
    ref: str = ""
    cif: str = ""
    iban: str = ""
    total: float = 0.0
    lineas: List[LineaFactura] = field(default_factory=list)
    alertas: List[str] = field(default_factory=list)
    texto_raw: str = ""


# =============================================================================
# CARGA DE DATOS
# =============================================================================

def cargar_diccionario(ruta: Path) -> Tuple[pd.DataFrame, pd.DataFrame, Dict]:
    """Carga el diccionario de artículos y patrones."""
    xlsx = pd.ExcelFile(ruta)
    
    # Artículos (obligatorio)
    articulos = pd.read_excel(xlsx, sheet_name='Articulos')
    articulos['PROVEEDOR'] = articulos['PROVEEDOR'].str.upper().str.strip()
    articulos['ARTICULO'] = articulos['ARTICULO'].str.strip()
    
    # Patrones específicos (opcional - puede no existir)
    patrones = pd.DataFrame()
    if 'Patrones especificos' in xlsx.sheet_names:
        patrones = pd.read_excel(xlsx, sheet_name='Patrones especificos')
    elif 'Patrones' in xlsx.sheet_names:
        patrones = pd.read_excel(xlsx, sheet_name='Patrones')
    # Si no existe ninguna, patrones queda vacío (no es crítico)
    
    # Crear índice de artículos por proveedor para búsqueda rápida
    indice = {}
    for _, row in articulos.iterrows():
        prov = row['PROVEEDOR']
        if prov not in indice:
            indice[prov] = []
        indice[prov].append({
            'articulo': row['ARTICULO'],
            'categoria': row['CATEGORIA'],
            'iva': row.get('TIPO_IVA', row.get('IVA', 21))  # Soportar ambos nombres de columna
        })
    
    return articulos, patrones, indice


def cargar_yaml(ruta: Path) -> Optional[Dict]:
    """Carga un archivo YAML de patrón."""
    if not ruta.exists():
        return None
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"    ⚠️ Error cargando YAML {ruta}: {e}")
        return None


def buscar_yaml(proveedor: str, carpeta_yaml: Path) -> Optional[Dict]:
    """Busca el YAML correspondiente a un proveedor."""
    # Normalizar nombre para buscar archivo
    nombre_archivo = proveedor.upper().replace(' ', '_').replace(',', '').replace('.', '')
    
    # Intentar varias variantes
    variantes = [
        f"{nombre_archivo}.yml",
        f"{nombre_archivo}.yaml",
        f"{nombre_archivo.replace('_SA', '')}.yml",
        f"{nombre_archivo.replace('_SL', '')}.yml",
        f"{nombre_archivo.replace('_SLL', '')}.yml",
    ]
    
    for variante in variantes:
        ruta = carpeta_yaml / variante
        if ruta.exists():
            return cargar_yaml(ruta)
    
    return None


# =============================================================================
# EXTRACCIÓN DE TEXTO
# =============================================================================

def extraer_texto_pdf(ruta: Path) -> str:
    """Extrae texto de un PDF."""
    try:
        reader = PdfReader(str(ruta))
        texto = ""
        for page in reader.pages:
            texto += page.extract_text() or ""
        return texto
    except Exception as e:
        print(f"    ⚠️ Error leyendo PDF: {e}")
        return ""


# =============================================================================
# PARSING DEL NOMBRE DE ARCHIVO
# =============================================================================

def parsear_nombre_archivo(nombre: str) -> Dict:
    """
    Extrae información del nombre del archivo.
    Formatos soportados:
    - 1001_1T25_0101_PROVEEDOR_TF.pdf (número_trimestre_fecha_proveedor_método)
    - 4T25_1127_PROVEEDOR_TF.pdf (trimestre_número_proveedor_método)
    - PROVEEDOR_TF.pdf (solo proveedor)
    """
    resultado = {
        'numero': '',
        'trimestre': '',
        'fecha_nombre': '',
        'proveedor': '',
        'metodo_pago': ''
    }
    
    base = Path(nombre).stem
    
    # Normalizar: reemplazar espacios múltiples por uno solo, luego por _
    base_normalizado = re.sub(r'\s+', '_', base.strip())
    partes = base_normalizado.split('_')
    
    # Detectar método de pago (última parte si es conocido)
    metodos = ['TF', 'TR', 'RC', 'TJ', 'EF']
    if partes and partes[-1].upper() in metodos:
        resultado['metodo_pago'] = partes[-1].upper()
        partes = partes[:-1]
    
    # Detectar trimestre (formato: 1T25, 2T25, 3T25, 4T25, 1Q25, etc.)
    trimestre_idx = None
    for i, p in enumerate(partes):
        if re.match(r'^\d[TQ]\d{2}$', p, re.IGNORECASE):
            resultado['trimestre'] = p.upper()
            trimestre_idx = i
            break
    
    # Detectar número (secuencia de 3-4 dígitos que no es fecha)
    numero_idx = None
    for i, p in enumerate(partes):
        if p.isdigit() and len(p) >= 3:
            # Si es formato MMDD (4 dígitos empezando por 0 o 1), es fecha
            if len(p) == 4 and p[0] in '01':
                resultado['fecha_nombre'] = p
            else:
                resultado['numero'] = p
                numero_idx = i
    
    # Si no encontramos número, buscar cualquier secuencia de dígitos
    if not resultado['numero']:
        for i, p in enumerate(partes):
            if p.isdigit() and i != trimestre_idx:
                resultado['numero'] = p
                numero_idx = i
                break
    
    # Construir proveedor con las partes restantes
    proveedor_partes = []
    for i, p in enumerate(partes):
        # Saltar trimestre, número, fecha, y palabras especiales
        if i == trimestre_idx or i == numero_idx:
            continue
        if p.isdigit():  # Fecha u otro número
            continue
        if p.upper() in ['ATRASADA', 'DUPLICADA', 'DUPLICADO', 'OJO', 'CON', 'SIN', 'APUNTE', 'NO', 'ES', 'FACTURA']:
            continue
        proveedor_partes.append(p)
    
    resultado['proveedor'] = ' '.join(proveedor_partes)
    
    return resultado


# =============================================================================
# EXTRACCIÓN DE DATOS BÁSICOS
# =============================================================================

def extraer_cif(texto: str) -> Optional[str]:
    """Extrae el CIF del proveedor (excluyendo el propio)."""
    # Buscar CIF con etiqueta (varios formatos)
    patrones = [
        r'(?:CIF|NIF|C\.I\.F|N\.I\.F)[.:\s/-]*([ABCDEFGHJKLMNPQRSUVW][-\s]?\d{7,8})\b',
        r'(?:CIF|NIF)[.:\s/-]*([ABCDEFGHJKLMNPQRSUVW])\s+(\d{8})\b',  # CIF con espacio: B 86705126
        r'C\.IF\./N\.I\.F\s+([ABCDEFGHJKLMNPQRSUVW])-?(\d{8})',  # Formato SABORES: C.IF./N.I.F F-11794542
        r'CIF\.?:?\s*([ABCDEFGHJKLMNPQRSUVW])[-/]?(\d{2})[-/]?(\d{6})\b',  # Formato FABEIRO: CIF.: B-79/992079
    ]
    
    for patron_str in patrones:
        patron = re.compile(patron_str, re.IGNORECASE)
        matches = patron.findall(texto.upper())
        for match in matches:
            if isinstance(match, tuple):
                cif_limpio = ''.join(match).replace("-", "").replace(" ", "")
            else:
                cif_limpio = match.replace("-", "").replace(" ", "")
            if cif_limpio != CIF_PROPIO and len(cif_limpio) == 9:
                return cif_limpio
    
    # Buscar CIF sin etiqueta: letra seguida de 8 dígitos (con posible espacio)
    patron2 = re.compile(r'\b([ABCDEFGHJKLMNPQRSUVW])\s?[-]?\s?(\d{8})\b')
    matches2 = patron2.findall(texto.upper())
    for letra, numeros in matches2:
        cif = f"{letra}{numeros}"
        if cif != CIF_PROPIO:
            return cif
    
    return None


def extraer_ibans(texto: str) -> List[str]:
    """Extrae todos los IBANs del texto."""
    patron = re.compile(r'ES\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}', re.IGNORECASE)
    matches = patron.findall(texto)
    
    ibans = []
    for m in matches:
        iban = m.replace(" ", "").upper()
        if len(iban) == 24:
            # Formatear
            iban_fmt = f"{iban[:4]} {iban[4:8]} {iban[8:12]} {iban[12:16]} {iban[16:20]} {iban[20:24]}"
            ibans.append(iban_fmt)
    
    return ibans


def elegir_iban(ibans: List[str]) -> Optional[str]:
    """Elige el IBAN correcto (evitando bancos específicos si hay varios)."""
    if not ibans:
        return None
    if len(ibans) == 1:
        return ibans[0]
    
    # Si hay varios, evitar los bancos en BANCOS_EVITAR
    for iban in ibans:
        codigo_banco = iban.replace(" ", "")[4:8]
        if codigo_banco not in BANCOS_EVITAR:
            return iban
    
    # Si todos son de bancos a evitar, devolver el primero
    return ibans[0]


def extraer_fecha(texto: str, yaml_config: Optional[Dict] = None, proveedor: str = '') -> Optional[str]:
    """Extrae la fecha de factura.
    
    Patrones específicos por proveedor (v3.9):
    - CERES: DD/MM/YYYY tras número de factura
    - LICORES MADRUEÑO: DD/MM/YYYY con espacios OCR antes de NÚMERO
    - BM: DD/MM/YY antes de "Caja:"
    - PANIFIESTO: DD-mes.-YYYY (ej: 30-nov.-2025)
    - SERRIN: Formato con espacios OCR
    """
    proveedor_upper = proveedor.upper() if proveedor else ''
    
    # Si hay YAML con regex específico
    if yaml_config and 'date' in yaml_config:
        regex = yaml_config['date'].get('regex', '')
        if regex:
            match = re.search(regex, texto)
            if match:
                fecha_str = match.group()
                # Convertir a DD-MM-YY
                partes = re.split(r'[/.-]', fecha_str)
                if len(partes) == 3:
                    d, m, y = partes
                    y = y[-2:] if len(y) == 4 else y
                    return f"{int(d):02d}-{int(m):02d}-{y}"
    
    # ===== PATRONES ESPECÍFICOS POR PROVEEDOR =====
    
    # CERES: "2538618 30/09/2025" - fecha tras número de 7 dígitos
    if 'CERES' in proveedor_upper or 'B83478669' in texto:
        patron = re.compile(r'\d{7}\s+(\d{2})/(\d{2})/(\d{4})')
        match = patron.search(texto)
        if match:
            d, m, y = match.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # LICORES MADRUEÑO: Fecha con espacios del OCR "3 0 /0 9 /2 0 2 5"
    if 'MADRUEÑO' in proveedor_upper or 'B-86705126' in texto or 'B86705126' in texto:
        # Patrón con espacios
        patron = re.compile(r'(\d)\s*(\d)\s*/\s*(\d)\s*(\d)\s*/\s*(\d)\s*(\d)\s*(\d)\s*(\d)')
        match = patron.search(texto)
        if match:
            g = match.groups()
            d = g[0] + g[1]
            m = g[2] + g[3]
            y = g[4] + g[5] + g[6] + g[7]
            return f"{d}-{m}-{y[-2:]}"
        # Patrón normal como fallback
        patron2 = re.compile(r'(\d{2})/(\d{2})/(\d{4})')
        match2 = patron2.search(texto[:500])
        if match2:
            d, m, y = match2.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # BM: "06/09/25 15:08 Caja:" 
    if 'BM' in proveedor_upper or 'B20099586' in texto:
        patron = re.compile(r'(\d{2})/(\d{2})/(\d{2})\s+\d{2}:\d{2}\s+Caja', re.IGNORECASE)
        match = patron.search(texto)
        if match:
            d, m, y = match.groups()
            return f"{d}-{m}-{y}"
    
    # PANIFIESTO: "30-nov.-2025" 
    if 'PANIFIESTO' in proveedor_upper or 'B87874327' in texto:
        meses = {'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04', 'may': '05', 'jun': '06',
                 'jul': '07', 'ago': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'}
        patron = re.compile(r'(\d{2})-([a-z]{3})\.-(\d{4})', re.IGNORECASE)
        match = patron.search(texto)
        if match:
            d, mes_txt, y = match.groups()
            m = meses.get(mes_txt.lower(), '01')
            return f"{d}-{m}-{y[-2:]}"
    
    # SERRIN NO CHAN: Formato D/M/YYYY o DD/M/YYYY después del CIF
    if 'SERRIN' in proveedor_upper or 'SERRÍN' in proveedor_upper or 'B-87.214.755' in texto or 'B87214755' in texto:
        # Buscar fecha después del CIF B87760575
        patron = re.compile(r'B87760575\s+(\d{1,2})/(\d{1,2})/(\d{4})')
        match = patron.search(texto)
        if match:
            d, m, y = match.groups()
            return f"{int(d):02d}-{int(m):02d}-{y[-2:]}"
    
    # v3.10 - JULIO GARCIA VIVAS: DD/MM/YYYY después de los 8 dígitos de factura
    if 'GARCIA VIVAS' in proveedor_upper or 'JULIO GARCIA' in proveedor_upper or '02869898G' in texto:
        # Patrón: 8 dígitos + newline + fecha
        patron = re.compile(r'\n\d{8}\s*\n\s*(\d{2})/(\d{2})/(\d{4})\s*\n')
        match = patron.search(texto)
        if match:
            d, m, y = match.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # ===== PATRONES GENÉRICOS =====
    
    # Buscar con etiqueta FECHA (varios formatos)
    patrones_fecha = [
        r'FECHA[:\s]*(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})',  # FECHA: DD/MM/YYYY
        r'Fecha[:\s]*(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})',  # Fecha: DD/MM/YY
        r'FEC\s*H\s*A[:\s]*(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})',  # FEC H A (espacios raros)
        r'(\d{2})/(\d{2})/(\d{2})\s+\d{2}:\d{2}\s+Caja',  # BM: DD/MM/YY HH:MM Caja
    ]
    
    for patron_str in patrones_fecha:
        patron = re.compile(patron_str, re.IGNORECASE)
        match = patron.search(texto)
        if match:
            d, m, y = match.groups()
            y = y[-2:] if len(y) == 4 else y
            return f"{int(d):02d}-{int(m):02d}-{y}"
    
    # Buscar formato DD/MM/YYYY o DD/MM/YY en la cabecera (primeros 800 chars)
    patron2 = re.compile(r'(\d{2})[/](\d{2})[/](\d{2,4})')
    match2 = patron2.search(texto[:800])
    if match2:
        d, m, y = match2.groups()
        y = y[-2:] if len(y) == 4 else y
        return f"{d}-{m}-{y}"
    
    # Buscar formato DD-MM-YY
    patron3 = re.compile(r'(\d{2})-(\d{2})-(\d{2})')
    match3 = patron3.search(texto[:800])
    if match3:
        d, m, y = match3.groups()
        return f"{d}-{m}-{y}"
    
    return None


def extraer_ref(texto: str, yaml_config: Optional[Dict] = None, proveedor: str = '') -> Optional[str]:
    """Extrae el número de factura/referencia.
    
    Patrones específicos por proveedor (v3.9):
    - CERES: 7 dígitos tras "B2B DIARIO" o al inicio
    - LICORES MADRUEÑO: 4 dígitos antes de "NÚMERO" 
    - BM: Alfanumérico tras "Datos FACTURA:"
    - PANIFIESTO: Formato XX-XXXXXX-XXX
    - ZUCCA/FORMAGGIARTE: Número tras "Nº Factura" o "N. Fatt"
    - FABEIRO: Número tras "Factura Nº" o "FACTURA"
    - CVNE: Formato FXXXXXX
    - FELISA: Número tras "Factura:"
    """
    proveedor_upper = proveedor.upper() if proveedor else ''
    
    # Si hay YAML con regex específico
    if yaml_config and 'ref' in yaml_config:
        regex = yaml_config['ref'].get('regex', '')
        if regex:
            match = re.search(regex, texto, re.MULTILINE)
            if match:
                return match.group(1) if match.groups() else match.group()
    
    # ===== PATRONES ESPECÍFICOS POR PROVEEDOR =====
    
    # CERES: "B2B DIARIO 2538618 30/09/2025" o "2538618 30/09/2025"
    if 'CERES' in proveedor_upper or 'B83478669' in texto:
        # Buscar 7 dígitos seguidos de fecha
        patron = re.compile(r'(\d{7})\s+\d{2}/\d{2}/\d{4}')
        match = patron.search(texto)
        if match:
            return match.group(1)
    
    # LICORES MADRUEÑO: "3 0 /0 9 /2 0 2 5 3 9 1 7NÚM ERO" o "3 9 1 7\nN Ú M ER O"
    if 'MADRUEÑO' in proveedor_upper or 'B-86705126' in texto or 'B86705126' in texto:
        # Patrón 1: pypdf - número con espacios en línea separada antes de "N Ú M"
        # Buscar 4 dígitos con espacios seguidos de newline y N Ú M
        patron_pypdf = re.compile(r'(\d)\s+(\d)\s+(\d)\s+(\d)\s*\n\s*N\s*Ú\s*M', re.IGNORECASE)
        match = patron_pypdf.search(texto)
        if match:
            g = match.groups()
            return g[0] + g[1] + g[2] + g[3]
        
        # Patrón 2: PyPDF2 - todo en una línea
        patron_pypdf2 = re.compile(r'(\d)\s*(\d)\s*(\d)\s*(\d)\s*NÚM\s*ERO', re.IGNORECASE)
        match2 = patron_pypdf2.search(texto)
        if match2:
            g = match2.groups()
            return g[0] + g[1] + g[2] + g[3]
        
        # Patrón 3: sin espacios como fallback
        patron3 = re.compile(r'(\d{4})\s*NÚM\s*ERO', re.IGNORECASE)
        match3 = patron3.search(texto)
        if match3:
            return match3.group(1)
    
    # BM: "Datos FACTURA: 142312505C0000090"
    if 'BM' in proveedor_upper or 'B20099586' in texto:
        patron = re.compile(r'Datos\s+FACTURA:\s*(\w+)', re.IGNORECASE)
        match = patron.search(texto)
        if match:
            return match.group(1)
    
    # PANIFIESTO: "25-100101-387" (formato XX-XXXXXX-XXX)
    if 'PANIFIESTO' in proveedor_upper or 'B87874327' in texto:
        patron = re.compile(r'(\d{2}-\d{6}-\d{3})')
        match = patron.search(texto)
        if match:
            return match.group(1)
    
    # ZUCCA/FORMAGGIARTE: "Nº Factura: 123" o "N. Fatt. 123"
    if 'ZUCCA' in proveedor_upper or 'FORMAGGIARTE' in proveedor_upper:
        patron = re.compile(r'(?:Nº\s*Factura|N\.\s*Fatt)[:\s.]*(\d+)', re.IGNORECASE)
        match = patron.search(texto)
        if match:
            return match.group(1)
    
    # FABEIRO: "25 - 3.960" después de "Nº Factura"
    if 'FABEIRO' in proveedor_upper or 'B-79/992079' in texto or 'B79992079' in texto:
        # Patrón: "Nº Factura" seguido de "25 - 3.960" en siguiente línea
        patron = re.compile(r'(\d{2}\s*-\s*\d{1,2}\.\d{3})')
        match = patron.search(texto)
        if match:
            return match.group(1).replace(' ', '')
    
    # MARITA COSTA: "MADRID 1 250111 1" - número de factura después de "MADRID 1"
    if 'MARITA' in proveedor_upper or '48207369J' in texto:
        patron = re.compile(r'MADRID\s+1\s+(2[45]\d{4})\s+1')
        match = patron.search(texto)
        if match:
            return match.group(1)
    
    # MIGUEZ CAL: "A 400" después de fecha DD/MM/YY
    if 'MIGUEZ' in proveedor_upper or 'B79868006' in texto:
        # Patrón: fecha + espacio + "A" + espacio + número
        patron = re.compile(r'\d{2}/\d{2}/\d{2}\s+(A\s*\d+)')
        match = patron.search(texto)
        if match:
            return match.group(1).replace(' ', '')
    
    # PILAR RODRIGUEZ: Formato "25F00003" (YYXNNNNN)
    if 'PILAR' in proveedor_upper or 'MAJADAL' in proveedor_upper or '06582655' in texto:
        patron = re.compile(r'\b(\d{2}F\d{5})\b')
        match = patron.search(texto)
        if match:
            return match.group(1)
    
    # CVNE: Formato FXXXXXX
    if 'CVNE' in proveedor_upper:
        patron = re.compile(r'(F\d{6,7})')
        match = patron.search(texto)
        if match:
            return match.group(1)
    
    # FELISA: "Factura: XXX"
    if 'FELISA' in proveedor_upper:
        patron = re.compile(r'Factura[:\s]*(\d+)', re.IGNORECASE)
        match = patron.search(texto)
        if match:
            return match.group(1)
    
    # LA MOLIENDA VERDE: Buscar número de factura
    if 'MOLIENDA' in proveedor_upper:
        patron = re.compile(r'(?:Factura|Nº)[:\s]*(\d+)', re.IGNORECASE)
        match = patron.search(texto)
        if match:
            return match.group(1)
    
    # DISTRIBUCIONES LAVAPIES: Número tras FACTURA
    if 'LAVAPIES' in proveedor_upper and 'PANIFIESTO' not in proveedor_upper:
        patron = re.compile(r'FACTURA[:\s]*(\d+)', re.IGNORECASE)
        match = patron.search(texto)
        if match:
            return match.group(1)
    
    # SERRIN NO CHAN: Formato "FV/021/2025" después de "Número fac."
    if 'SERRIN' in proveedor_upper or 'SERRÍN' in proveedor_upper or 'B-87.214.755' in texto or 'B87214755' in texto:
        patron = re.compile(r'(FV/\d{3}/\d{4})')
        match = patron.search(texto)
        if match:
            return match.group(1)
            return match.group(1)
    
    # SABORES DE PATERNA: Número tras Factura
    if 'PATERNA' in proveedor_upper or 'SABORES' in proveedor_upper:
        patron = re.compile(r'Factura[:\s]*(\d+)', re.IGNORECASE)
        match = patron.search(texto)
        if match:
            return match.group(1)
    
    # EMJAMESA: Número tras Factura
    if 'EMJAMESA' in proveedor_upper:
        patron = re.compile(r'Factura[:\s]*([A-Z]?\d+)', re.IGNORECASE)
        match = patron.search(texto)
        if match:
            return match.group(1)
    
    # KINEMA: Número de factura
    if 'KINEMA' in proveedor_upper:
        patron = re.compile(r'Factura[:\s]*(\d+)', re.IGNORECASE)
        match = patron.search(texto)
        if match:
            return match.group(1)
    
    # v3.10 - JULIO GARCIA VIVAS: 8 dígitos después del email o aislados
    if 'GARCIA VIVAS' in proveedor_upper or 'JULIO GARCIA' in proveedor_upper or '02869898G' in texto:
        # Patrón 1: 8 dígitos después de @gmail.com
        patron = re.compile(r'@gmail\.com\s*\n\s*(\d{8})\s*\n')
        match = patron.search(texto)
        if match:
            return match.group(1)
        # Patrón 2: 8 dígitos aislados en línea
        patron2 = re.compile(r'\n(\d{8})\n')
        match2 = patron2.search(texto)
        if match2:
            return match2.group(1)
    
    # ===== PATRONES GENÉRICOS (fallback) =====
    
    # Para BERZAL: el número está en línea sola después del CIF, antes de FACTURA
    patron_berzal = re.compile(r'B87760575\s*\n\s*(\d{1,5})\s*\n', re.IGNORECASE)
    match_berzal = patron_berzal.search(texto)
    if match_berzal:
        return match_berzal.group(1).strip()
    
    # Buscar "FACTURA" seguido de número en siguiente línea
    patron = re.compile(r'FACTURA\s*[\r\n]+\s*(\d{1,6})', re.IGNORECASE | re.MULTILINE)
    match = patron.search(texto)
    if match:
        return match.group(1)
    
    # Buscar Nº Factura: XXX
    patron2 = re.compile(r'(?:Nº\s*Factura|Factura\s*N[ºo°]?|NUM\.?\s*:?|Número\s*:?)\s*[:\s]*([A-Z]?\d{1,10}[-/]?\d*)', re.IGNORECASE)
    match2 = patron2.search(texto)
    if match2:
        return match2.group(1)
    
    return None


def extraer_total(texto: str) -> Optional[float]:
    """Extrae el total de la factura."""
    patron = re.compile(
        r'(?:TOTAL\s*FACTURA|TOTAL\s*IMPORTE|Total\s*Factura)[:\s]*(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})',
        re.IGNORECASE
    )
    match = patron.search(texto)
    if match:
        total_str = match.group(1)
        # Convertir formato europeo
        total_str = total_str.replace(".", "").replace(",", ".")
        try:
            return float(total_str)
        except:
            pass
    return None


# =============================================================================
# EXTRACCIÓN DE LÍNEAS
# =============================================================================

def extraer_lineas_berzal(texto: str) -> List[Dict]:
    """Extrae líneas de facturas tipo BERZAL."""
    lineas = []
    
    # Patrón para líneas de BERZAL
    # Formato real: 206017 Mantequilla "Cañada Real" dulce 120 grs 10       5,48   0,13 ...
    # El IVA (10) está después del concepto, seguido de espacios y el importe
    patron = re.compile(
        r'^(\d{6})\s+'  # Código 6 dígitos al inicio de línea
        r'(.+?)\s+'     # Concepto (captura lazy)
        r'(\d{1,2})\s+'  # IVA (10, 21, 4)
        r'(\d{1,5}[.,]\d{2})',  # Importe (primer número con decimales después del IVA)
        re.MULTILINE
    )
    
    for match in patron.finditer(texto):
        codigo, concepto, iva, importe = match.groups()
        
        # Limpiar concepto: quitar todo después del último carácter alfabético o comillas
        # El concepto termina donde empiezan los números de la tabla
        concepto_limpio = concepto.strip()
        
        # Buscar dónde termina el texto real del artículo
        # Normalmente es antes de secuencias como "0,13" o "1,000"
        match_fin = re.search(r'\s+\d+[.,]\d+\s+\d+[.,]\d+', concepto_limpio)
        if match_fin:
            concepto_limpio = concepto_limpio[:match_fin.start()].strip()
        
        lineas.append({
            'codigo': codigo,
            'articulo': concepto_limpio,
            'iva': int(iva),
            'base': float(importe.replace(',', '.'))
        })
    
    return lineas


def extraer_lineas_licores_madrueño(texto: str) -> List[Dict]:
    """Extrae líneas de facturas LICORES MADRUEÑO.
    
    Formato extraído: CÓDIGO + UNIDADES+DESC + IMPORTE,PRECIO
    Ejemplo: 1764 12XIC DA L FONS 43,203,60
    
    Las unidades están PEGADAS a la descripción y el importe+precio
    también están pegados sin espacio.
    Añadido soporte Unicode para ñ y acentos españoles.
    """
    lineas = []
    
    # Patrón: unidades pegadas a descripción, importe pegado a precio
    patron = re.compile(
        r'^(\d{1,4})\s+'              # Código (1-4 dígitos)
        r'(\d{1,3})'                  # Unidades (pegado a descripción)
        r'([A-ZÁÉÍÓÚÜÑa-záéíóúüñ][A-Za-z0-9\s\'\´\-\.\,ñÑáéíóúÁÉÍÓÚüÜ]+?)\s+'  # Descripción con acentos
        r'(\d{1,4}[,\.]\d{2})'        # Importe (pegado)
        r'(\d{1,3}[,\.]\d{2})',       # Precio (pegado al importe)
        re.MULTILINE
    )
    
    for match in patron.finditer(texto):
        codigo, uds, descripcion, importe, precio = match.groups()
        descripcion_limpia = ' '.join(descripcion.split()).strip()
        
        # Ignorar líneas de headers/totales
        desc_upper = descripcion_limpia.upper()
        if any(x in desc_upper for x in ['ALBAR', 'TOTAL', 'BRUTO', 'SUMA', 'SIGUE', 'BASE', 'IVA']):
            continue
            
        lineas.append({
            'codigo': codigo,
            'articulo': descripcion_limpia,
            'iva': 21,  # LICORES siempre 21%
            'base': float(importe.replace(',', '.'))
        })
    
    return lineas


def extraer_lineas_sabores_paterna(texto: str) -> List[Dict]:
    """Extrae líneas de facturas SABORES DE PATERNA.
    
    Formato: FECHA+DESCRIPCION + UNIDADES + PESO + PRECIO+IVA + IMPORTE
    Ejemplo: 18-03-25CHICHARRON ESPECIAL 0,014 16,040 17,3010,0 277,49
    
    El IVA está pegado al precio (17,3010,0 = precio 17,30 + IVA 10,0)
    """
    lineas = []
    
    # Patrón actualizado: el IVA está pegado al precio sin espacio
    # Busca: PRECIO(2 decimales) + IVA(1 o 2 dígitos) + ",0" o ".0"
    patron = re.compile(
        r'(\d{2}-\d{2}-\d{2})'         # Fecha (dd-mm-yy)
        r'([A-Z][A-Z\s\.\d]+?)\s+'     # Descripción
        r'[\d,]+\s+'                   # Unidades (ignorar)
        r'[\d,]+\s+'                   # Peso (ignorar)
        r'(\d{1,3}[,\.]\d{2})'         # Precio
        r'(\d{1,2})[,\.]0\s+'          # IVA (10 o 21, seguido de ,0 o .0)
        r'(\d+[,\.]\d{2})',            # Importe
        re.MULTILINE
    )
    
    for match in patron.finditer(texto):
        fecha, descripcion, precio, iva, importe = match.groups()
        descripcion_limpia = descripcion.strip()
        
        if len(descripcion_limpia) > 3:
            lineas.append({
                'codigo': '',
                'articulo': descripcion_limpia,
                'iva': int(iva),  # Capturamos el IVA real (10 o 21)
                'base': float(importe.replace(',', '.'))
            })
    
    # Caso especial: línea PORTE (sin fecha)
    patron_porte = re.compile(
        r'^PORTE\s+'
        r'[\d,]+\s+'      # cantidad
        r'[\d,]+\s+'      # peso
        r'(\d+[,\.]\d{2})' # precio
        r'(\d{1,2})[,\.]0\s+'  # IVA
        r'(\d+[,\.]\d{2})',    # importe
        re.MULTILINE
    )
    
    porte_match = patron_porte.search(texto)
    if porte_match:
        precio, iva, importe = porte_match.groups()
        lineas.append({
            'codigo': '',
            'articulo': 'PORTE',
            'iva': int(iva),
            'base': float(importe.replace(',', '.'))
        })
    
    return lineas


def extraer_lineas_francisco_guerra(texto: str) -> List[Dict]:
    """Extrae líneas de facturas FRANCISCO GUERRA."""
    lineas = []
    
    # Formato: 01071 MZ LATAS 5 KG " La Abuela" 3 59,70 19,900
    patron = re.compile(
        r'^(\d{4,5})\s+'  # Código
        r'([A-Z][A-Z0-9\s\"\'\-\.]+?)\s+'  # Descripción
        r'(\d+)\s+'  # Cantidad
        r'(\d+[.,]\d+)\s+'  # Importe total
        r'(\d+[.,]\d+)',  # Precio unitario
        re.MULTILINE
    )
    
    for match in patron.finditer(texto):
        codigo, articulo, cantidad, importe, precio = match.groups()
        articulo_limpio = articulo.strip()
        
        # Ignorar líneas de albarán
        if 'Albarán' in articulo_limpio or 'ALBARAN' in articulo_limpio:
            continue
            
        lineas.append({
            'codigo': codigo,
            'articulo': articulo_limpio,
            'iva': 10,  # Francisco Guerra normalmente 10%
            'base': float(importe.replace(',', '.'))
        })
    
    return lineas


def extraer_lineas_emjamesa(texto: str) -> List[Dict]:
    """Extrae líneas de facturas EMJAMESA.
    
    Formato: CODIGO IMPORTE € DESCRIPCION LOTE UDS KILOS PRECIO
    NOTA: El IMPORTE viene justo después del código, con símbolo €.
    La descripción puede tener espacios extra del OCR (SART A → SARTA).
    
    Ejemplo: 500 37,18 € SALCHICHON IBERICO EXTRA SARTA SISB-4724 1 3,325 11,181
    """
    lineas = []
    
    # Buscar líneas: CODIGO IMPORTE € RESTO
    patron = re.compile(
        r'^(\d{2,4})\s+'           # Código (2-4 dígitos)
        r'([\d,]+)\s*€\s+'         # Importe con €
        r'(.+)',                   # Todo el resto de la línea
        re.MULTILINE
    )
    
    for match in patron.finditer(texto):
        codigo, importe, resto = match.groups()
        
        # Ignorar cabeceras
        if 'DESCRIPCIÓN' in resto or 'CÓDIGO' in resto:
            continue
        
        # Buscar dónde empieza el lote (patrón tipo XXXX-1234)
        lote_match = re.search(r'\s+[A-Z]{2,5}\s*-?\s*\d+\s+\d+\s+', resto)
        if lote_match:
            desc = resto[:lote_match.start()]
        else:
            desc = resto
        
        # Limpiar espacios extra del OCR
        desc = desc.replace('SART A', 'SARTA').replace('BELLOT A', 'BELLOTA')
        desc = desc.replace('T ACOS', 'TACOS').replace('T A', 'TA')
        desc = ' '.join(desc.split()).strip()
        
        # Ignorar si descripción muy corta
        if len(desc) < 3:
            continue
            
        lineas.append({
            'codigo': codigo,
            'articulo': desc,
            'iva': 10,  # Chacinas 10%
            'base': float(importe.replace(',', '.'))
        })
    
    return lineas


def extraer_lineas_zucca(texto: str) -> List[Dict]:
    """Extrae líneas de facturas ZUCCA/FORMAGGIARTE."""
    lineas = []
    
    # Formato: 00042 Burrata Individual SN 10,00 3,40 34,00 34,00
    patron = re.compile(
        r'^(\d{2,5})\s+'  # Código
        r'([A-Za-z][A-Za-z\s\d]+?)\s+'  # Descripción
        r'(\d+[.,]\d+)\s+'  # Cantidad
        r'(\d+[.,]\d+)\s+'  # Precio
        r'(\d+[.,]\d+)\s+'  # Subtotal
        r'(\d+[.,]\d+)',  # Total
        re.MULTILINE
    )
    
    for match in patron.finditer(texto):
        codigo, articulo, cantidad, precio, subtotal, total = match.groups()
        articulo_limpio = articulo.strip()
        
        # Ignorar líneas de albarán
        if 'Albarán' in articulo_limpio:
            continue
            
        lineas.append({
            'codigo': codigo,
            'articulo': articulo_limpio,
            'iva': 4,  # Quesos normalmente 4%
            'base': float(total.replace(',', '.'))
        })
    
    return lineas


def extraer_lineas_quesos_navas(texto: str) -> List[Dict]:
    """Extrae líneas de facturas QUESOS NAVAS."""
    lineas = []
    
    # Formato: 27 QUESO DE SELECCION ORO 15 MESES MINI 0123 6,000 19,230 4,00 115,38
    patron = re.compile(
        r'^(\d{1,3})\s+'  # Código
        r'([A-Z][A-Z\s\d]+?)\s+'  # Artículo
        r'(\d{4})\s+'  # Lote
        r'(\d+[.,]\d+)\s+'  # Cantidad
        r'(\d+[.,]\d+)\s+'  # Precio
        r'(\d+[.,]\d+)\s+'  # IVA
        r'(\d+[.,]\d+)',  # Subtotal
        re.MULTILINE
    )
    
    for match in patron.finditer(texto):
        codigo, articulo, lote, cantidad, precio, iva, subtotal = match.groups()
        articulo_limpio = articulo.strip()
            
        lineas.append({
            'codigo': codigo,
            'articulo': articulo_limpio,
            'iva': 4,  # Quesos 4%
            'base': float(subtotal.replace(',', '.'))
        })
    
    return lineas


def extraer_lineas_ceres(texto: str) -> List[Dict]:
    """Extrae líneas de facturas CERES."""
    lineas = []
    
    # Formato CERES:
    # 001124 MH CLASICA BARRIL 30L 1 21108,8 50 54,40
    # CODIGO DESCRIPCION UDS IVA+PRECIO DTO IMPORTE
    # El IVA (21) está pegado al precio (108,8)
    
    patron = re.compile(
        r'^([A-Z0-9]{5,6})\s+'  # Código (001124 o CE1384)
        r'([A-Z][A-Z0-9\s\'/\-\.]+?)\s+'  # Descripción
        r'(-?\d+)\s+'  # Unidades (puede ser negativo)
        r'(\d{1,2})'  # IVA (21, 10, 4)
        r'(\d+[,\.]\d+)\s+'  # Precio (pegado al IVA)
        r'(\d+[,\.]?\d*)\s+'  # Descuento
        r'(-?\d+[,\.]\d+)',  # Importe
        re.MULTILINE
    )
    
    for match in patron.finditer(texto):
        codigo, descripcion, uds, iva, precio, dto, importe = match.groups()
        descripcion_limpia = descripcion.strip()
        
        # Ignorar líneas de envase o ajuste
        if 'ENVASE' in descripcion_limpia.upper() or 'REAJUSTE' in descripcion_limpia.upper():
            continue
            
        lineas.append({
            'codigo': codigo,
            'articulo': descripcion_limpia,
            'iva': int(iva),
            'base': float(importe.replace(',', '.'))
        })
    
    return lineas


def extraer_lineas_bm(texto: str) -> List[Dict]:
    """Extrae líneas de facturas BM SUPERMERCADOS (tickets)."""
    lineas = []
    
    # Formato ticket BM:
    # 1    ALUBIAS BLANCAS ECO P.LUIS F          3.19
    # CANTIDAD + DESCRIPCION + IMPORTE
    # También puede ser con precio/kg:
    # 0.23 CORTE JAMON MOSTOLES SV(LACO 14.48 3.33
    
    # Patrón para líneas con peso (cantidad precio_kg importe)
    patron_peso = re.compile(
        r'^\s*([\d,\.]+)\s+'  # Cantidad/Peso
        r'([A-Z][A-Z0-9\s\.\,\(\)/\*\-]+?)\s+'  # Descripción
        r'(\d+[,\.]\d{2})\s+'  # Precio por kg/ud
        r'(\d+[,\.]\d{2})\s*$',  # Importe
        re.MULTILINE
    )
    
    # Patrón para líneas simples (cantidad descripcion importe)
    patron_simple = re.compile(
        r'^\s*(\d+)\s+'  # Cantidad entera
        r'([A-Z][A-Z0-9\s\.\,\(\)/\*\-]+?)\s+'  # Descripción
        r'(\d+[,\.]\d{2})\s*$',  # Importe
        re.MULTILINE
    )
    
    # Extraer líneas con peso primero
    for match in patron_peso.finditer(texto):
        cantidad, descripcion, precio_ud, importe = match.groups()
        descripcion_limpia = descripcion.strip()
        
        # Ignorar líneas que no son productos
        if any(x in descripcion_limpia.upper() for x in 
               ['TOTAL', 'TARJETA', 'CUENTA', 'ACUMUL', 'TICKET', 'FACTURA', 
                'ENTREGADO', 'CAMBIO', 'AHORRO', 'PROMOCION', 'PUNTO']):
            continue
        
        # Determinar IVA según sección
        iva = 10  # Por defecto alimentación
        if any(x in descripcion_limpia.upper() for x in ['BOLSA', 'VAJILLA', 'LIMP', 'ESTROP', 'PAÑO']):
            iva = 21
            
        lineas.append({
            'codigo': '',
            'articulo': descripcion_limpia,
            'iva': iva,
            'base': float(importe.replace(',', '.'))
        })
    
    # Extraer líneas simples
    for match in patron_simple.finditer(texto):
        cantidad, descripcion, importe = match.groups()
        descripcion_limpia = descripcion.strip()
        
        # Ignorar líneas que no son productos
        if any(x in descripcion_limpia.upper() for x in 
               ['TOTAL', 'TARJETA', 'CUENTA', 'ACUMUL', 'TICKET', 'FACTURA',
                'ENTREGADO', 'CAMBIO', 'AHORRO', 'PROMOCION', 'PUNTO']):
            continue
        
        # Verificar que no sea una línea ya capturada por patron_peso
        ya_existe = any(l['articulo'] == descripcion_limpia for l in lineas)
        if ya_existe:
            continue
        
        iva = 10
        if any(x in descripcion_limpia.upper() for x in ['BOLSA', 'VAJILLA', 'LIMP', 'ESTROP', 'PAÑO']):
            iva = 21
            
        lineas.append({
            'codigo': '',
            'articulo': descripcion_limpia,
            'iva': iva,
            'base': float(importe.replace(',', '.'))
        })
    
    return lineas


def extraer_lineas_bernal(texto: str) -> List[Dict]:
    """Extrae líneas de facturas JAMONES Y EMBUTIDOS BERNAL.
    
    Formato: Lotes: XXX; DESCRIPCION CSEC UDS PRECIO %DES %IVA IMPORTE+CODIGO
    El código está PEGADO al importe al final (EM-MINERO, LO-JABELL, P-PORTES).
    La descripción puede estar en múltiples líneas.
    
    Ejemplo:
    Lotes: 20242; 
    MORCÓN ACHORIZADO DE 
    BELLOTA 100% IBÉRICO 0,00 2,090 12,7300 0,00 10,00 26,606EM-MINERO
    """
    lineas = []
    
    # Patrón para encontrar líneas con código al final
    patron_linea = re.compile(
        r'([\d,]+)\s+'  # C.Sec
        r'([\d,]+)\s+'  # Unidades  
        r'([\d,]+)\s+'  # Precio
        r'([\d,]+)\s+'  # %Des
        r'([\d,]+)\s+'  # %Iva
        r'([\d,]+)'     # Importe
        r'([A-Z]{1,3}-[A-Z]+)',  # Código (pegado al importe)
    )
    
    # Dividir por "Lotes:" para procesar cada bloque
    bloques = texto.split('Lotes:')
    
    for bloque in bloques[1:]:  # Saltar primera parte (cabecera)
        match = patron_linea.search(bloque)
        if match:
            csec, uds, precio, dto, iva_str, importe, codigo = match.groups()
            
            # Extraer descripción (texto entre lote y números)
            parte_antes = bloque[:match.start()]
            # Limpiar: quitar número de lote (ej: "20242; " o "22212-M; ")
            desc = re.sub(r'^\s*[\d\-A-Z;]+\s*', '', parte_antes)
            desc_limpia = ' '.join(desc.split())  # Normalizar espacios
            
            # Ignorar si descripción muy corta o es cabecera
            if len(desc_limpia) < 3:
                continue
            if 'Producto' in desc_limpia or 'C.Sec' in desc_limpia:
                continue
            
            # Extraer IVA (viene como 10,00 o 21,00)
            try:
                iva = int(float(iva_str.replace(',', '.')))
            except:
                iva = 10
            
            # Extraer importe
            try:
                base = float(importe.replace(',', '.'))
            except:
                continue
                
            lineas.append({
                'codigo': codigo,
                'articulo': desc_limpia,
                'iva': iva,
                'base': base
            })
    
    return lineas


def extraer_lineas_felisa(texto: str) -> List[Dict]:
    """Extrae líneas de facturas FELISA GOURMET (PESCADOS DON FELIX).
    
    Formato: DESCRIPCION PRECIO(4dec) IMPORTE(2dec)+CODIGO CANTIDAD Unidades/Kilos
    El código está PEGADO al importe, sin espacio.
    
    Ejemplo: MELVA 115GR ED.LIMITADA 3,3500 40,20M125 12 Unidades
             SARDINA AHUMADA 500GR FELISA 11,6000 81,20FSAH500 7 Unidades
    """
    lineas = []
    
    # Patrón para productos - código pegado al importe
    patron = re.compile(
        r'^(.+?)\s+'  # Descripción
        r'(\d+,\d{4})\s+'  # Precio (4 decimales)
        r'(\d+,\d{2})'  # Importe (2 decimales)
        r'([A-Z][A-Z0-9]*)\s+'  # Código (pegado al importe)
        r'([\d,]+)\s+'  # Cantidad
        r'(?:Unidades|Kilos)',
        re.MULTILINE
    )
    
    for match in patron.finditer(texto):
        desc, precio, importe, codigo, cantidad = match.groups()
        desc_limpia = desc.strip()
        
        # Ignorar líneas de albarán o lote
        if 'Albarán' in desc_limpia or 'Lote:' in desc_limpia or 'TOTAL' in desc_limpia:
            continue
        
        # Ignorar líneas con descripción muy corta
        if len(desc_limpia) < 3:
            continue
            
        lineas.append({
            'codigo': codigo,
            'articulo': desc_limpia,
            'iva': 10,  # Pescados/conservas 10%
            'base': float(importe.replace(',', '.'))
        })
    
    # Buscar TRANSPORTE (línea separada)
    if 'TRANSPORTE' in texto:
        match_transp = re.search(r'TRANSPORTE\s+([\d,]+)', texto)
        if match_transp:
            lineas.append({
                'codigo': 'TRANSP',
                'articulo': 'TRANSPORTE',
                'iva': 21,
                'base': float(match_transp.group(1).replace(',', '.'))
            })
    
    return lineas


def extraer_lineas_borboton(texto: str) -> List[Dict]:
    """Extrae líneas de facturas BODEGAS BORBOTÓN.
    
    Formato: CODIGO VINO UDS PRECIO € DTO% UD.PRECIO € TOTAL €
    Ejemplo: ARS0283 A RAS DE SUELO "EL TORREJÓN" 75 cl 54 9,92 € 0,00 % 9,92 € 535,68 €
    
    También incluye líneas de promoción/descuento.
    """
    lineas = []
    
    # Patrón para productos normales
    patron = re.compile(
        r'^([A-Z]{3}\d{4})\s+'  # Código (ARS0283)
        r'(.+?)\s+'  # Descripción del vino
        r'(\d+)\s+'  # Unidades
        r'([\d,]+)\s*€\s+'  # Precio
        r'[\d,]+\s*%\s+'  # Dto%
        r'[\d,]+\s*€\s+'  # Ud. Precio
        r'([\d,]+)\s*€',  # Total
        re.MULTILINE
    )
    
    for match in patron.finditer(texto):
        codigo, desc, uds, precio, total = match.groups()
        desc_limpia = desc.strip()
        
        # Limpiar descripción (quitar info de lote, vintage, etc.)
        desc_limpia = re.sub(r'\s+L\.\d+.*$', '', desc_limpia)
        desc_limpia = re.sub(r'\s+Vintage.*$', '', desc_limpia, flags=re.IGNORECASE)
        desc_limpia = re.sub(r'\s+Alc\..*$', '', desc_limpia, flags=re.IGNORECASE)
        
        lineas.append({
            'codigo': codigo,
            'articulo': desc_limpia.strip(),
            'iva': 21,  # Vinos 21%
            'base': float(total.replace(',', '.'))
        })
    
    # Patrón para promociones/descuentos
    patron_promo = re.compile(
        r'^Promoci[oó]n\s+especial.*?\s+'  # "Promoción especial"
        r'(\d+)\s+'  # Unidades
        r'(-?[\d,]+)\s*€\s+'  # Precio (puede ser negativo)
        r'[\d,]+\s*%\s+'  # Dto%
        r'(-?[\d,]+)\s*€\s+'  # Ud. Precio
        r'(-?[\d,]+)\s*€',  # Total
        re.MULTILINE
    )
    
    for match in patron_promo.finditer(texto):
        uds, precio, ud_precio, total = match.groups()
        
        lineas.append({
            'codigo': 'PROMO',
            'articulo': 'Promoción especial',
            'iva': 21,
            'base': float(total.replace(',', '.'))
        })
    
    return lineas


def extraer_lineas_arganza(texto: str) -> List[Dict]:
    """Extrae líneas de facturas VINOS DE ARGANZA.
    
    Formato peculiar: PRECIO DTO IMPORTE+CANTIDAD+CODIGO DESCRIPCION
    Los números están ANTES del código, con importe y cantidad pegados.
    
    Ejemplo: 2,500 0,00 120,0048,00P063 LEGADO DE FARRO SELECCIÓN 2024
    """
    lineas = []
    
    # Patrón: precio dto importe(XX,XX)cantidad(XX,XX)codigo descripcion
    patron = re.compile(
        r'([\d,]+)\s+'  # Precio
        r'[\d,]+\s+'  # Dto (ignorar)
        r'(\d+,\d{2})'  # Importe (XX,XX)
        r'(\d+,\d{2})'  # Cantidad (XX,XX)
        r'([A-Z0-9]+)\s+'  # Código
        r'(.+)',  # Descripción
        re.MULTILINE
    )
    
    for match in patron.finditer(texto):
        precio, importe, cantidad, codigo, desc = match.groups()
        desc_limpia = desc.strip()
        
        # Limpiar descripción (quitar lote)
        desc_limpia = re.sub(r'\s+L\d+[A-Z]*$', '', desc_limpia)
        
        # Ignorar líneas de cabecera
        if 'CANTIDAD' in desc_limpia or 'DESCRIPCION' in desc_limpia:
            continue
            
        # Determinar IVA: transporte 21%, vinos 21%
        iva = 21
        
        lineas.append({
            'codigo': codigo,
            'articulo': desc_limpia.strip(),
            'iva': iva,
            'base': float(importe.replace(',', '.'))
        })
    
    return lineas


def extraer_lineas_purisima(texto: str) -> List[Dict]:
    """Extrae líneas de facturas LA PURÍSIMA (Cooperativa del Vino de Yecla).
    
    Formato: CODIGO(9dig)DESCRIPCION UNIDADES PRECIO IMPORTE
    NOTA: El código está PEGADO a la descripción (sin espacio intermedio).
    
    Ejemplo: 135490106FILARMONIA MSM  PROD.ECOLOGICA CAJA 6 72 4,15 298,80
    """
    lineas = []
    
    # Patrón: código 9 dígitos PEGADO a descripción, luego unidades, precio, importe
    patron = re.compile(
        r'^(\d{9})'  # Código (9 dígitos, sin espacio después)
        r'([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ\s\d.]+?)\s+'  # Descripción (empieza con mayúscula)
        r'(\d+)\s+'  # Unidades
        r'([\d,]+)\s+'  # Precio
        r'([\d,]+)$',  # Importe
        re.MULTILINE
    )
    
    for match in patron.finditer(texto):
        codigo, desc, uds, precio, importe = match.groups()
        desc_limpia = desc.strip()
        
        # Ignorar líneas de cabecera o lote
        if 'DESCRIPCIÓN' in desc_limpia or 'Lote:' in desc_limpia:
            continue
        if 'Albarán' in desc_limpia or 'Pedido:' in desc_limpia:
            continue
            
        lineas.append({
            'codigo': codigo,
            'articulo': desc_limpia,
            'iva': 21,  # Vinos 21%
            'base': float(importe.replace(',', '.'))
        })
    
    return lineas


def extraer_lineas_molletes(texto: str) -> List[Dict]:
    """Extrae líneas de facturas MOLLETES ARTESANOS DE ANTEQUERA.
    
    Formato: CODIGO(5dig) DESC - CAD: FECHA CAJAS UDS PRECIO DTO IMPORTE
    
    Ejemplo: 10108 MOLLETE AT.80GR C-26 U*2M - CAD.: 22/07/2025 8 208,000 1,11 30,00 161,54
    """
    lineas = []
    
    # Patrón: código 5 dígitos, descripción hasta CAD o fin, números al final
    patron = re.compile(
        r'^(\d{5})\s+'  # Código (5 dígitos)
        r'(.+?)'  # Descripción
        r'(?:\s+-\s+CAD\.?:\s*\d{2}/\d{2}/\d{4})?\s+'  # CAD opcional
        r'(\d+)\s+'  # Cajas
        r'([\d,]+)\s+'  # Unidades
        r'([\d,]+)\s+'  # Precio
        r'[\d,]+\s+'  # Dto1
        r'([\d,]+)$',  # Importe
        re.MULTILINE
    )
    
    for match in patron.finditer(texto):
        codigo, desc, cajas, uds, precio, importe = match.groups()
        desc_limpia = desc.strip()
        
        # Ignorar líneas de cabecera
        if 'DESCRIPCIÓN' in desc_limpia or 'CÓDIGO' in desc_limpia:
            continue
            
        lineas.append({
            'codigo': codigo,
            'articulo': desc_limpia,
            'iva': 4,  # Pan superreducido 4%
            'base': float(importe.replace(',', '.'))
        })
    
    return lineas


def extraer_lineas_yoigo(texto: str) -> List[Dict]:
    """Extrae líneas de facturas YOIGO/XFERA (telefonía).
    
    Siempre genera UNA línea con:
    - Artículo: "Teléfono e Internet"
    - IVA: 21%
    - Base: extraída de "Base imponible"
    
    Pago por adeudo en cuenta, no necesita IBAN/CIF.
    """
    lineas = []
    
    # Patrón flexible para base imponible:
    # "(21%) 26,45€Base imponible" o "Base imponible (21%) 26,45€"
    patrones = [
        r'\(21%\)\s*([\d,]+)\s*€?\s*Base\s*imponible',  # (21%) 26,45€Base imponible
        r'Base\s*imponible\s*\(?21%?\)?\s*([\d,]+)\s*€?',  # Base imponible (21%) 26,45€
    ]
    
    for patron in patrones:
        match = re.search(patron, texto, re.IGNORECASE)
        if match:
            base_str = match.group(1).replace(',', '.')
            try:
                base = float(base_str)
                lineas.append({
                    'codigo': 'YOIGO',
                    'articulo': 'Teléfono e Internet',
                    'iva': 21,
                    'base': base
                })
                break
            except:
                pass
    
    return lineas


def extraer_lineas_som_energia(texto: str) -> List[Dict]:
    """Extrae líneas de facturas SOM ENERGIA (electricidad).
    
    Siempre genera UNA línea con:
    - Artículo: "ELECTRICIDAD"
    - IVA: extraído de la factura (10% o 21% según legislación)
    - Base: extraída directamente O calculada como TOTAL - IVA
    
    Pago por adeudo en cuenta, no necesita IBAN/CIF.
    """
    lineas = []
    
    # Extraer IVA (puede ser 10% o 21%)
    patron_iva = re.search(r'IVA\s*(\d+)%\s*([\d,]+)\s*€?', texto)
    
    iva = 21  # default
    importe_iva = 0
    if patron_iva:
        iva = int(patron_iva.group(1))
        importe_iva = float(patron_iva.group(2).replace(',', '.'))
    
    # Método 1: Buscar base imponible directamente
    # "127,97 € (BASE IMPONIBLE)" o similar
    patron_base = re.search(r'([\d,]+)\s*€?\s*\(?BASE\s*IMPONIBLE\)?', texto, re.IGNORECASE)
    
    base = None
    if patron_base:
        try:
            base = float(patron_base.group(1).replace(',', '.'))
        except:
            pass
    
    # Método 2: Si no encontramos base, calcular TOTAL - IVA
    if base is None:
        patron_total = re.search(r'TOTAL\s*(?:IMPORTE\s*)?FACTURA[:\s]*([\d,]+)\s*€?', texto, re.IGNORECASE)
        if patron_total and importe_iva > 0:
            try:
                total = float(patron_total.group(1).replace(',', '.'))
                base = total - importe_iva
            except:
                pass
    
    if base and base > 0:
        lineas.append({
            'codigo': 'SOM',
            'articulo': 'ELECTRICIDAD',
            'iva': iva,
            'base': round(base, 2)
        })
    
    return lineas


def extraer_lineas_lucera(texto: str) -> List[Dict]:
    """Extrae líneas de facturas LUCERA (Energía Colectiva).
    
    Siempre genera UNA línea con:
    - Artículo: "ELECTRICIDAD"
    - IVA: 21% (siempre en LUCERA)
    - Base: extraída de "IVA 21% (sobre XX,XX €)"
    
    Pago por adeudo en cuenta, no necesita IBAN/CIF.
    """
    lineas = []
    
    # Patrón: "IVA 21% (sobre 73,47 €)" 
    patron_base = re.search(r'IVA\s*21%\s*\(sobre\s*([\d,]+)\s*€?\)', texto)
    
    if patron_base:
        base_str = patron_base.group(1).replace(',', '.')
        try:
            base = float(base_str)
            lineas.append({
                'codigo': 'LUCERA',
                'articulo': 'ELECTRICIDAD',
                'iva': 21,
                'base': base
            })
        except:
            pass
    
    return lineas


def extraer_lineas_segurma(texto: str) -> List[Dict]:
    """Extrae líneas de facturas SEGURMA (alarmas).
    
    Siempre genera UNA línea con:
    - Artículo: "Alarma"
    - IVA: 21%
    - Base: después de "Subtotal"
    
    Pago por adeudo en cuenta, no necesita IBAN/CIF.
    """
    lineas = []
    
    patron = re.search(r'Subtotal\s*([\d,]+)\s*€', texto)
    if patron:
        base = float(patron.group(1).replace(',', '.'))
        lineas.append({
            'codigo': 'SEGURMA',
            'articulo': 'Alarma',
            'iva': 21,
            'base': base
        })
    return lineas


def extraer_lineas_kinema(texto: str) -> List[Dict]:
    """Extrae líneas de facturas KINEMA (gestoría/cooperativa).
    
    Formato tabla: CODIGO DESC CANTIDAD PRECIO SUBTOTAL TOTAL
    Puede tener múltiples líneas (contable + laboral).
    """
    lineas = []
    
    # Patrón: "00001 ASESORIA CONTABLE Y FISCAL 1,00 70,00 70,00 70,00"
    patron_linea = re.compile(
        r'(\d{5})\s+'   # Código 5 dígitos
        r'(.+?)\s+'     # Descripción
        r'[\d,]+\s+'    # Cantidad
        r'[\d,]+\s+'    # Precio unit
        r'[\d,]+\s+'    # Subtotal
        r'([\d,]+)$',   # Total (último número)
        re.MULTILINE
    )
    
    for match in patron_linea.finditer(texto):
        codigo, desc, importe = match.groups()
        lineas.append({
            'codigo': codigo,
            'articulo': desc.strip(),
            'iva': 21,
            'base': float(importe.replace(',', '.'))
        })
    
    return lineas


def extraer_lineas_openai(texto: str) -> List[Dict]:
    """Extrae líneas de facturas OpenAI (ChatGPT).
    
    Importe en USD, IVA 0% (reverse charge).
    Pago por tarjeta, no necesita IBAN/CIF.
    """
    lineas = []
    
    # Buscar "ChatGPT Plus Subscription" y precio $XX.XX
    patron = re.search(r'(ChatGPT\s+\w+\s+Subscription)[^\$]*\$?([\d.]+)', texto)
    
    if patron:
        desc = patron.group(1)
        base = float(patron.group(2))
        lineas.append({
            'codigo': 'OPENAI',
            'articulo': desc,
            'iva': 0,
            'base': base
        })
    
    return lineas


def extraer_lineas_cvne(texto: str) -> List[Dict]:
    """Extrae líneas de facturas CVNE (Compañía Vinícola del Norte de España).
    
    Formato: cada campo en línea separada
    CODIGO (9 dígitos + ES + 2 dígitos, ej: 926673510ES00)
    DESCRIPCION (puede ser multilínea, empieza con VALSANGIACOMO)
    00 (añada)
    CANTIDAD
    PRECIO
    DTO
    IMPORTE
    """
    lineas = []
    
    lineas_texto = texto.split('\n')
    i = 0
    
    while i < len(lineas_texto):
        linea = lineas_texto[i].strip()
        
        # Buscar código CVNE: 9 dígitos + ES + 2 dígitos
        if re.match(r'^\d{9}ES\d{2}$', linea):
            codigo = linea
            descripcion_partes = []
            
            # Recoger descripción hasta encontrar "00" (añada)
            j = i + 1
            while j < len(lineas_texto):
                l = lineas_texto[j].strip()
                if l == '00':
                    break
                descripcion_partes.append(l)
                j += 1
            
            descripcion = ' '.join(descripcion_partes)
            
            # Después de "00" vienen: cantidad, precio, dto, importe
            if j + 4 < len(lineas_texto):
                try:
                    cantidad = int(lineas_texto[j + 1].strip())
                    precio = float(lineas_texto[j + 2].strip().replace(',', '.'))
                    # j+3 es dto, lo ignoramos
                    importe = float(lineas_texto[j + 4].strip().replace(',', '.'))
                    
                    lineas.append({
                        'codigo': codigo,
                        'articulo': descripcion,
                        'iva': 21,  # CVNE siempre 21%
                        'base': importe
                    })
                except (ValueError, IndexError):
                    pass
            
            i = j + 5  # Saltar al siguiente artículo
        else:
            i += 1
    
    return lineas


def extraer_lineas_lavapies(texto: str) -> List[Dict]:
    """Extrae líneas de facturas DISTRIBUCIONES LAVAPIES.
    
    CIF: F88424072
    IBAN: ES39 3035 0376 14 3760011213
    
    Formato tabla:
    Nº ALBARÁN | REF    | DESCRIPCIÓN                    | CANT | DTO  | IMPORTE
    631/2025   | AGUVIC | AGUA VICHY CATALAN 300 ML      | 48   | 0,84 | 40,32 €
    
    IVA: Mixto 10% (bebidas alimentarias) y 21% (refrescos, etc.)
    Particularidad: El número de albarán puede repetirse en varias líneas
    """
    lineas = []
    
    # Patrón para líneas de productos
    # REF | DESCRIPCION | CANT | DTO | IMPORTE
    patron = re.compile(
        r'^(?:\d+/\d+\s+)?'  # Albarán opcional (631/2025)
        r'([A-Z0-9]{4,10})\s+'  # Código/REF (AGUVIC, etc.)
        r'(.+?)\s+'  # Descripción
        r'(\d+)\s+'  # Cantidad
        r'[\d,]+\s+'  # DTO (ignorar)
        r'(\d+[.,]\d{2})\s*€?',  # Importe
        re.MULTILINE
    )
    
    for match in patron.finditer(texto):
        codigo, desc, cant, importe = match.groups()
        desc_limpia = desc.strip()
        
        # Ignorar cabeceras y totales
        if any(x in desc_limpia.upper() for x in ['DESCRIPCIÓN', 'TOTAL', 'BASE', 'SUBTOTAL']):
            continue
        
        # Determinar IVA según tipo de producto
        # Bebidas alcohólicas y refrescos: 21%
        # Agua, zumos, lácteos: 10%
        iva = 10  # Por defecto alimentación
        desc_upper = desc_limpia.upper()
        if any(x in desc_upper for x in ['CERVEZA', 'VINO', 'LICOR', 'SIDRA', 'CAVA', 
                                          'COCA', 'FANTA', 'PEPSI', 'SPRITE', 'TONICA',
                                          'RED BULL', 'MONSTER', 'AQUARIUS']):
            iva = 21
        
        lineas.append({
            'codigo': codigo,
            'articulo': desc_limpia,
            'iva': iva,
            'base': float(importe.replace(',', '.'))
        })
    
    return lineas


def extraer_lineas_fabeiro(texto: str) -> List[Dict]:
    """Extrae líneas de facturas FABEIRO - v3.8 MEJORADA.
    
    CIF: B79992079
    IBAN: ES70 0182 1292 2202 0150 5065
    
    Formato peculiar del OCR de PyPDF - todo pegado en una línea:
    PRECIO_UNITCÓDIGO CANTIDADIVA% IMPORTECONCEPTO
    Ejemplo: "24,0000CA0005 12,000010,00% 288,00ANCHOA OLIVA GRAN SELECCION 60"
    
    IVA: Explícito en factura (4% quesos, 10% charcutería/anchoas)
    """
    lineas = []
    
    # Patrón principal para formato pegado de FABEIRO
    patron = re.compile(
        r'(\d+[.,]\d{4})'  # Precio unitario (24,0000)
        r'([A-Z]{2}\d{4})\s+'  # Código (CA0005)
        r'(\d+[.,]\d{4})'  # Cantidad (12,0000)
        r'(\d{1,2})[,.]00%\s+'  # IVA (10,00%)
        r'(\d+[.,]\d{2})'  # Importe (288,00)
        r'(.+?)(?=\n|$)',  # Concepto (hasta fin de línea)
        re.MULTILINE
    )
    
    for m in patron.finditer(texto):
        precio, codigo, cantidad, iva, importe, concepto = m.groups()
        concepto_limpio = re.sub(r'\s+', ' ', concepto.strip())
        
        # Ignorar si concepto es muy corto o parece cabecera
        if len(concepto_limpio) < 3:
            continue
        if any(x in concepto_limpio.upper() for x in ['CONCEPTO', 'ARTÍCULO', 'DESCRIPCIÓN']):
            continue
        
        lineas.append({
            'codigo': codigo,
            'articulo': concepto_limpio,
            'cantidad': float(cantidad.replace(',', '.')),
            'iva': int(iva),
            'base': float(importe.replace(',', '.'))
        })
    
    # Patrón alternativo si el primero no funciona (formato más separado)
    if not lineas:
        patron_alt = re.compile(
            r'^([A-Z]{2}\d{4})\s+'  # Código
            r'(.+?)\s+'  # Concepto
            r'(\d{1,2})[,.]00\s*%?\s+'  # IVA
            r'[\d,]+\s+'  # Cantidad
            r'[\d,]+\s+'  # Precio
            r'(\d+[.,]\d{2})',  # Importe
            re.MULTILINE
        )
        
        for match in patron_alt.finditer(texto):
            codigo, concepto, iva, importe = match.groups()
            concepto_limpio = concepto.strip()
            
            if any(x in concepto_limpio.upper() for x in ['CONCEPTO', 'ARTÍCULO', 'DESCRIPCIÓN']):
                continue
            
            lineas.append({
                'codigo': codigo,
                'articulo': concepto_limpio,
                'iva': int(iva),
                'base': float(importe.replace(',', '.'))
            })
    
    return lineas


def extraer_lineas_serrin(texto: str) -> List[Dict]:
    """Extrae líneas de facturas SERRÍN NO CHAN - v3.8 MEJORADA.
    
    CIF: B87214755
    IBAN: ES88 0049 6650 1329 1001 8834
    
    El PDF se extrae en 3 bloques separados que debemos correlacionar por posición:
    1. Artículos con IVA: "Vermú rojo botella 75cl 21,00%"
    2. Datos numéricos: "7,93 19,98 € 95,16 € 115,14 €" (precio|iva€|base|total)
    3. Códigos con cantidad: "LOD 12"
    
    Maneja dos formatos de extracción de PyPDF:
    - Con saltos de línea entre artículos
    - Todo pegado en una línea
    
    IVA: Explícito y variable (4% galletas ECO, 10% normales, 21% vermú)
    """
    lineas = []
    
    # ESTRATEGIA 1: Texto con saltos de línea
    patron_articulo_iva = re.compile(
        r'^([A-Za-záéíóúñÁÉÍÓÚÑ][A-Za-z0-9áéíóúñÁÉÍÓÚÑ\s]+?)\s+(\d{1,2}),00\s*%$',
        re.MULTILINE
    )
    
    articulos_iva = []
    for m in patron_articulo_iva.finditer(texto):
        articulo = m.group(1).strip()
        iva = int(m.group(2))
        if not articulo.lower().startswith('albarán') and 'i.v.a' not in articulo.lower():
            articulos_iva.append({'articulo': articulo, 'iva': iva})
    
    # ESTRATEGIA 2: Si no encontró nada, texto pegado
    if not articulos_iva:
        patron_pegado = re.compile(
            r'([A-Za-záéíóúñÁÉÍÓÚÑ][A-Za-z0-9áéíóúñÁÉÍÓÚÑ\s]+?)\s+(\d{1,2}),00\s*%'
        )
        for m in patron_pegado.finditer(texto):
            articulo = m.group(1).strip()
            iva = int(m.group(2))
            if (not articulo.lower().startswith('albarán') and 
                'i.v.a' not in articulo.lower() and
                'sobre' not in articulo.lower() and
                len(articulo) > 3):
                articulos_iva.append({'articulo': articulo, 'iva': iva})
    
    # Extraer datos numéricos (precio|iva€|base|total)
    patron_numeros = re.compile(
        r'(\d+[.,]\d{2})\s+(\d+[.,]\d{2})\s*€\s+(\d+[.,]\d{2})\s*€\s+(\d+[.,]\d{2})\s*€'
    )
    
    datos_numericos = []
    for m in patron_numeros.finditer(texto):
        base = float(m.group(3).replace(',', '.'))
        datos_numericos.append({'base': base})
    
    # Extraer códigos con cantidad
    patron_codigo_cant = re.compile(r'([A-Z]{3,5})\s+(\d{1,3})(?=[A-Z\n]|$)')
    
    codigos_cant = []
    for m in patron_codigo_cant.finditer(texto):
        codigo = m.group(1)
        cantidad = int(m.group(2))
        if codigo not in ['TOTAL', 'IVA', 'IBAN', 'SOBRE']:
            codigos_cant.append({'codigo': codigo, 'cantidad': cantidad})
    
    # Correlacionar por posición (usar el mínimo de los 3 para evitar desajustes)
    n = min(len(articulos_iva), len(datos_numericos), len(codigos_cant))
    
    for i in range(n):
        lineas.append({
            'codigo': codigos_cant[i]['codigo'],
            'articulo': articulos_iva[i]['articulo'],
            'cantidad': codigos_cant[i]['cantidad'],
            'iva': articulos_iva[i]['iva'],
            'base': datos_numericos[i]['base']
        })
    
    return lineas


def extraer_lineas_alquiler_ortega(texto: str) -> List[Dict]:
    """Extrae línea de facturas de BENJAMIN ORTEGA (alquiler local).
    
    NIF: 09342596L
    
    Formato extremadamente simple:
    DESCRIPCIÓN                              IMPORTE
    Alquiler mensual local Calle Rodas 2     500,00 €
    SUBTOTAL                                 500,00 €
    IVA AL 21%                               105,00 €
    
    Siempre: 500€ base, 21% IVA, 19% retención
    Categoría fija: ALQUILER
    """
    lineas = []
    
    # Buscar base imponible de alquiler
    patron_base = re.compile(
        r'(?:Alquiler|ALQUILER|Arrendamiento|ARRENDAMIENTO)[^\d]*'
        r'(\d+[.,]\d{2})\s*€?',
        re.IGNORECASE
    )
    
    match = patron_base.search(texto)
    if match:
        base = float(match.group(1).replace(',', '.'))
    else:
        # Si no encuentra el patrón, buscar SUBTOTAL
        patron_subtotal = re.compile(r'SUBTOTAL\s+(\d+[.,]\d{2})', re.IGNORECASE)
        match_sub = patron_subtotal.search(texto)
        if match_sub:
            base = float(match_sub.group(1).replace(',', '.'))
        else:
            # Valor por defecto conocido
            base = 500.00
    
    lineas.append({
        'codigo': 'ALQ',
        'articulo': 'Alquiler local Calle Rodas 2',
        'iva': 21,
        'base': base,
        'categoria': 'ALQUILER'  # Forzar categoría
    })
    
    return lineas


def extraer_lineas_alquiler_fernandez(texto: str) -> List[Dict]:
    """Extrae línea de facturas de JAIME FERNANDEZ (alquiler local).
    
    NIF: 07219971H
    
    Formato idéntico a ORTEGA:
    Siempre: 500€ base, 21% IVA, 19% retención
    Categoría fija: ALQUILER
    """
    lineas = []
    
    # Buscar base imponible de alquiler
    patron_base = re.compile(
        r'(?:Alquiler|ALQUILER|Arrendamiento|ARRENDAMIENTO)[^\d]*'
        r'(\d+[.,]\d{2})\s*€?',
        re.IGNORECASE
    )
    
    match = patron_base.search(texto)
    if match:
        base = float(match.group(1).replace(',', '.'))
    else:
        # Si no encuentra el patrón, buscar SUBTOTAL
        patron_subtotal = re.compile(r'SUBTOTAL\s+(\d+[.,]\d{2})', re.IGNORECASE)
        match_sub = patron_subtotal.search(texto)
        if match_sub:
            base = float(match_sub.group(1).replace(',', '.'))
        else:
            # Valor por defecto conocido
            base = 500.00
    
    lineas.append({
        'codigo': 'ALQ',
        'articulo': 'Alquiler local Calle Rodas 2',
        'iva': 21,
        'base': base,
        'categoria': 'ALQUILER'  # Forzar categoría
    })
    
    return lineas


def extraer_lineas_miguez_cal(texto: str) -> List[Dict]:
    """Extrae líneas de facturas MIGUEZ CAL (ForPlan) - v3.9.
    
    CIF: B79868006
    Proveedor de productos de limpieza y papel.
    
    Formato tabular:
    CÓDIGO          DESCRIPCIÓN                                      UNID.  PRECIO  DTO1  DTO2  IMPORTE
    FP2-06          FP-2 DETERGENTE MAQ. LAVAVAJILLAS GARRAFA 6 KG   2,00   13,01               26,02
    SCRAP5PG        APORTACION SCRAP PUNTO GRETA 5 L                        0,05
    
    Notas:
    - Las líneas con IMPORTE son productos (columna IMPORTE al final)
    - Las líneas SCRAP5PG son tasas ambientales (sin importe final) - ignorar
    - Líneas "ALBARÁN A-XXXX FECHA..." son separadores - ignorar
    - Líneas tipo "a partir de las 13 horas" son comentarios - ignorar
    - Algunas líneas tienen ENV/2023/... como referencia - puede estar pegado
    - IVA: Todo al 21% (productos de limpieza)
    """
    lineas = []
    
    # Códigos a ignorar (tasas ambientales, referencias)
    CODIGOS_IGNORAR = ['SCRAP5PG', 'SCRAP', 'ENV/']
    
    # Primero, normalizar texto: separar ENV/... de los números
    # Patrón: ENV/2023/0000245881,00 -> ENV/2023/000024588\n1,00
    texto_normalizado = re.sub(
        r'(ENV/\d+/\d+)(\d+[.,]\d{2})',
        r'\1\n\2',
        texto
    )
    
    # Patrón para líneas de producto con formato tabular
    # CÓDIGO  DESCRIPCIÓN  UNID.  PRECIO  [DTO1]  [DTO2]  IMPORTE
    # El código empieza con letras, luego puede tener números y guiones
    # El importe está al final de la línea
    patron_producto = re.compile(
        r'^([A-Z][A-Z0-9.\-]{2,15})\s+'  # Código (FP2-06, BOB.ECO1000, TOALLASZT, etc.)
        r'(.+?)\s+'  # Descripción
        r'(\d+[.,]\d{2})\s+'  # Cantidad (UNID.) - ej: 2,00, 1,00
        r'(\d+[.,]\d{2})\s+'  # Precio unitario
        r'(\d+[.,]\d{2})\s*$',  # Importe final (al final de línea)
        re.MULTILINE
    )
    
    for match in patron_producto.finditer(texto_normalizado):
        codigo, descripcion, cantidad, precio, importe = match.groups()
        
        # Ignorar códigos de tasas ambientales
        if any(cod in codigo.upper() for cod in CODIGOS_IGNORAR):
            continue
        
        # Ignorar líneas que son cabeceras o referencias
        desc_upper = descripcion.upper()
        if any(x in desc_upper for x in ['DESCRIPCIÓN', 'CONCEPTO', 'CÓDIGO', 'UNID.', 'PRECIO']):
            continue
        
        # Limpiar descripción: quitar referencias ENV/2023/...
        descripcion_limpia = re.sub(r'ENV/\d+/\d+', '', descripcion).strip()
        descripcion_limpia = re.sub(r'\s+', ' ', descripcion_limpia)
        
        lineas.append({
            'codigo': codigo,
            'articulo': descripcion_limpia,
            'cantidad': float(cantidad.replace(',', '.')),
            'precio_unitario': float(precio.replace(',', '.')),
            'iva': 21,  # Productos de limpieza al 21%
            'base': float(importe.replace(',', '.'))
        })
    
    # Patrón alternativo para líneas con formato más complejo
    # A veces la descripción puede estar en dos líneas o con ENV pegado
    # También buscar líneas de números sueltas y asociarlas al código anterior
    
    # Guardar posiciones ya procesadas
    posiciones_procesadas = set()
    
    # Buscar patrón: números al final de línea con 3 columnas numéricas
    patron_numeros = re.compile(
        r'^(\d+[.,]\d{2})\s+(\d+[.,]\d{2})\s+(\d+[.,]\d{2})\s*$',
        re.MULTILINE
    )
    
    for match in patron_numeros.finditer(texto_normalizado):
        cantidad, precio, importe = match.groups()
        match_pos = match.start()
        
        # Verificar si esta posición ya fue procesada (evitar duplicados reales)
        if match_pos in posiciones_procesadas:
            continue
        
        importe_num = float(importe.replace(',', '.'))
        
        # Buscar el código y descripción en las líneas anteriores
        texto_previo = texto_normalizado[:match_pos]
        lineas_previas = texto_previo.split('\n')
        
        # Buscar línea con código de producto (puede estar 1-5 líneas antes)
        for i in range(len(lineas_previas) - 1, max(0, len(lineas_previas) - 6), -1):
            linea_prev = lineas_previas[i].strip()
            if not linea_prev:
                continue
            
            # Ignorar líneas ENV/...
            if linea_prev.startswith('ENV/'):
                continue
                continue
            
            # Buscar patrón de código al inicio
            match_cod = re.match(r'^([A-Z][A-Z0-9.\-]{2,15})\s+(.+)', linea_prev)
            if match_cod:
                codigo = match_cod.group(1)
                descripcion = match_cod.group(2)
                
                # Ignorar si es SCRAP o ENV
                if any(cod in codigo.upper() for cod in CODIGOS_IGNORAR):
                    break
                
                # Limpiar descripción
                descripcion_limpia = re.sub(r'ENV/\d+/\d+', '', descripcion).strip()
                descripcion_limpia = re.sub(r'\s+', ' ', descripcion_limpia)
                
                if len(descripcion_limpia) > 3:
                    posiciones_procesadas.add(match_pos)
                    lineas.append({
                        'codigo': codigo,
                        'articulo': descripcion_limpia,
                        'cantidad': float(cantidad.replace(',', '.')),
                        'precio_unitario': float(precio.replace(',', '.')),
                        'iva': 21,
                        'base': importe_num
                    })
                break
    
    return lineas


def extraer_lineas_marita_costa(texto: str) -> List[Dict]:
    """Extrae líneas de facturas MARITA COSTA - v3.9.
    
    NIF: 48207369J (persona física)
    Distribuidor gourmet: aceites, patés, patatas, vinagres, conservas.
    
    Formato tabular:
    ARTÍCULO      DESCRIPCIÓN                              CANTIDAD  PRECIO UNIDAD  SUBTOTAL  DTO.  TOTAL
    AOVENOV500    AOVE NOBLEZA DEL SUR NOVO 500ML         12,00     13,2000€       158,40€         158,40€
    
    IVA:
    - 4% para AOVE (aceite de oliva)
    - 10% para el resto (alimentación general)
    """
    lineas = []
    lineas_texto = texto.split('\n')
    
    # Patrón para líneas con formato completo (6 grupos)
    patron_completo = re.compile(
        r'^([A-Z][A-Z0-9\s]{1,15}?)\s+'  # Código
        r'(.+?)\s+'  # Descripción
        r'(\d+[.,]\d{2})\s+'  # Cantidad
        r'(\d+[.,]\d{4})€\s+'  # Precio
        r'(\d+[.,]\d{2})€\s+'  # Subtotal
        r'(\d+[.,]\d{2})€'  # Total
    )
    
    # Patrón para líneas con continuación de descripción (números al final)
    patron_numeros = re.compile(
        r'(.+?)\s+'  # Descripción (cualquier cosa)
        r'(\d+[.,]\d{2})\s+'  # Cantidad
        r'(\d+[.,]\d{4})€\s+'  # Precio
        r'(\d+[.,]\d{2})€\s+'  # Subtotal
        r'(\d+[.,]\d{2})€$'  # Total
    )
    
    posiciones_procesadas = set()
    
    for i, linea in enumerate(lineas_texto):
        linea = linea.strip()
        if not linea or '€' not in linea:
            continue
        
        # Intentar patrón completo primero
        match = patron_completo.match(linea)
        if match:
            codigo, descripcion, cantidad, precio, subtotal, total = match.groups()
            codigo = codigo.strip()
            
            # Ignorar cabeceras
            if any(x in descripcion.upper() for x in ['DESCRIPCIÓN', 'CANTIDAD', 'PRECIO UNIDAD']):
                continue
            
            # Limpiar descripción
            descripcion_limpia = re.sub(r'\s*-\s*\d{6,}$', '', descripcion).strip()
            descripcion_limpia = re.sub(r'\s*-\s*[A-Z0-9]{6,}$', '', descripcion_limpia).strip()
            descripcion_limpia = re.sub(r'\s+', ' ', descripcion_limpia)
            
            # IVA
            codigo_upper = codigo.upper()
            desc_upper = descripcion_limpia.upper()
            iva = 4 if ('AOVE' in codigo_upper or 'AOVE' in desc_upper) else 10
            
            posiciones_procesadas.add(i)
            lineas.append({
                'codigo': codigo,
                'articulo': descripcion_limpia,
                'cantidad': float(cantidad.replace(',', '.')),
                'precio_unitario': float(precio.replace(',', '.')),
                'iva': iva,
                'base': float(total.replace(',', '.'))
            })
            continue
        
        # Intentar patrón de continuación (línea partida)
        match = patron_numeros.match(linea)
        if match and i not in posiciones_procesadas:
            cont_desc, cantidad, precio, subtotal, total = match.groups()
            total_num = float(total.replace(',', '.'))
            
            # Buscar código en líneas anteriores (que no empiezan con número)
            codigo = None
            desc_inicio = ''
            for j in range(i - 1, max(0, i - 3), -1):
                if j in posiciones_procesadas:
                    continue  # Saltar líneas ya procesadas
                linea_prev = lineas_texto[j].strip()
                if not linea_prev:
                    continue
                # Línea con código (empieza con mayúsculas)
                match_cod = re.match(r'^([A-Z][A-Z0-9\s]{1,15}?)\s+(.+)', linea_prev)
                if match_cod and '€' not in linea_prev:
                    codigo = match_cod.group(1).strip()
                    desc_inicio = match_cod.group(2).strip()
                    break
            
            if codigo:
                descripcion_completa = desc_inicio + ' ' + cont_desc.strip()
                descripcion_limpia = re.sub(r'\s*-\s*\d{6,}$', '', descripcion_completa).strip()
                descripcion_limpia = re.sub(r'\s*-\s*[A-Z0-9]{6,}$', '', descripcion_limpia).strip()
                descripcion_limpia = re.sub(r'\s+', ' ', descripcion_limpia)
                
                codigo_upper = codigo.upper()
                desc_upper = descripcion_limpia.upper()
                iva = 4 if ('AOVE' in codigo_upper or 'AOVE' in desc_upper) else 10
                
                posiciones_procesadas.add(i)
                lineas.append({
                    'codigo': codigo,
                    'articulo': descripcion_limpia,
                    'cantidad': float(cantidad.replace(',', '.')),
                    'precio_unitario': float(precio.replace(',', '.')),
                    'iva': iva,
                    'base': total_num
                })
    
    return lineas



def extraer_lineas_pilar_rodriguez(texto: str) -> List[Dict]:
    """Extrae líneas de facturas PILAR RODRIGUEZ / HUEVOS EL MAJADAL - v3.9.
    
    NIF: 06582655D (persona física)
    IBAN: ES30 5853 0199 2810 0235 62
    Producto: Huevos (docenas)
    IVA: 4%
    
    Maneja dos formatos de OCR diferentes:
    
    PyPDF2: '7-1-2025 3,50 21,00 € 6 Docenas de huevos' (espacios)
    pypdf:  '7-1-2025 3,50 21,00 €6Docenas de huevos' (sin espacios)
    
    Fechas truncadas:
    PyPDF2: '20-1-202' + '53,50 28,00 € 8 Docenas...' (5 pegado al precio)
    pypdf:  '20-1-202' + '5' + '3,50 28,00 €8Docenas...' (5 en línea separada)
    """
    lineas = []
    lineas_texto = texto.split('\n')
    
    # Patrón principal - funciona con ambos formatos (espacios opcionales)
    patron_completo = re.compile(
        r'^(\d{1,2}-\d{1,2}-\d{4})\s+'  # Fecha completa (7-1-2025)
        r'(\d+[.,]\d{2})\s+'  # Precio unitario
        r'(\d+[.,]\d{2})\s*€?\s*'  # Importe (espacio opcional después de €)
        r'(\d+)\s*'  # Cantidad (espacio opcional)
        r'[Dd]ocenas?',
        re.IGNORECASE
    )
    
    # Patrones para fechas truncadas
    patron_fecha_202 = re.compile(r'^(\d{1,2}-\d{1,2}-202)$')  # Ej: 20-1-202
    patron_fecha_20 = re.compile(r'^(\d{1,2}-\d{1,2}-20)$')    # Ej: 13-10-20
    
    # Patrón para línea que es solo "5" o "25" (pypdf separa los dígitos finales del año)
    patron_digito_solo = re.compile(r'^(5|25)$')
    
    # Patrón continuación PyPDF2: "5" o "25" pegado al precio
    patron_cont_pyPDF2 = re.compile(
        r'^(5|25)(\d+[.,]\d{2})\s+'  # "5" o "25" + precio
        r'(\d+[.,]\d{2})\s*€?\s*'
        r'(\d+)\s*'
        r'[Dd]ocenas?',
        re.IGNORECASE
    )
    
    # Patrón continuación pypdf: precio sin prefijo (después de línea con solo "5" o "25")
    patron_cont_pypdf = re.compile(
        r'^(\d+[.,]\d{2})\s+'  # Precio
        r'(\d+[.,]\d{2})\s*€?\s*'  # Importe
        r'(\d+)\s*'  # Cantidad
        r'[Dd]ocenas?',
        re.IGNORECASE
    )
    
    fecha_pendiente = None
    digitos_año_pendiente = None  # Para pypdf: cuando el "5" o "25" está en línea separada
    
    for i, linea in enumerate(lineas_texto):
        linea = linea.strip()
        if not linea:
            continue
        
        # Verificar si es fecha truncada tipo -202
        match = patron_fecha_202.match(linea)
        if match:
            fecha_pendiente = match.group(1)
            digitos_año_pendiente = None
            continue
        
        # Verificar si es fecha truncada tipo -20
        match = patron_fecha_20.match(linea)
        if match:
            fecha_pendiente = match.group(1)
            digitos_año_pendiente = None
            continue
        
        # Si tenemos fecha pendiente, verificar si esta línea es solo los dígitos del año (pypdf)
        if fecha_pendiente:
            match = patron_digito_solo.match(linea)
            if match:
                digitos_año_pendiente = match.group(1)
                continue
        
        # Verificar patrón completo (ambos formatos)
        match = patron_completo.match(linea)
        if match:
            fecha, precio, importe, cantidad = match.groups()
            lineas.append({
                'codigo': fecha,
                'articulo': 'Docenas de huevos',
                'cantidad': int(cantidad),
                'precio_unitario': float(precio.replace(',', '.')),
                'iva': 4,
                'base': float(importe.replace(',', '.'))
            })
            fecha_pendiente = None
            digitos_año_pendiente = None
            continue
        
        # Si tenemos fecha pendiente + dígitos del año (pypdf)
        if fecha_pendiente and digitos_año_pendiente:
            match = patron_cont_pypdf.match(linea)
            if match:
                precio, importe, cantidad = match.groups()
                fecha_completa = fecha_pendiente + digitos_año_pendiente
                lineas.append({
                    'codigo': fecha_completa,
                    'articulo': 'Docenas de huevos',
                    'cantidad': int(cantidad),
                    'precio_unitario': float(precio.replace(',', '.')),
                    'iva': 4,
                    'base': float(importe.replace(',', '.'))
                })
                fecha_pendiente = None
                digitos_año_pendiente = None
                continue
        
        # Si tenemos fecha pendiente pero dígitos están pegados al precio (PyPDF2)
        if fecha_pendiente and not digitos_año_pendiente:
            match = patron_cont_pyPDF2.match(linea)
            if match:
                digitos, precio, importe, cantidad = match.groups()
                fecha_completa = fecha_pendiente + digitos
                lineas.append({
                    'codigo': fecha_completa,
                    'articulo': 'Docenas de huevos',
                    'cantidad': int(cantidad),
                    'precio_unitario': float(precio.replace(',', '.')),
                    'iva': 4,
                    'base': float(importe.replace(',', '.'))
                })
                fecha_pendiente = None
                digitos_año_pendiente = None
                continue
    
    return lineas


def extraer_lineas_panifiesto(texto: str) -> List[Dict]:
    """Extrae línea única de facturas PANIFIESTO - v3.9.
    
    CIF: B87874327
    Producto: Solo pan
    IVA: 4%
    
    PANIFIESTO es especial: genera una factura mensual con muchos albaranes,
    pero para nuestro sistema solo necesitamos UNA línea con el total.
    
    El OCR puede generar diferentes ordenaciones:
    - Formato A: "168,41 4 6,74 175,15" → Base, %, IVA, Total
    - Formato B: "156,10 6,00 4 150,10" → Total, IVA, %, Base (invertido)
    """
    lineas = []
    
    # Patrón 1: Buscar en tabla de resumen IVA - Formato nuevo
    # Base % IVA Total: "168,41 4 6,74 175,15"
    patron_nuevo = re.compile(
        r'(\d+[.,]\d{2})\s+4\s+(\d+[.,]\d{2})\s+(\d+[.,]\d{2})',
        re.MULTILINE
    )
    
    # Patrón 2: Formato antiguo (invertido)
    # Total IVA % Base: "156,10 6,00 4 150,10"
    patron_antiguo = re.compile(
        r'(\d+[.,]\d{2})\s+(\d+[.,]\d{2})\s+4\s+(\d+[.,]\d{2})',
        re.MULTILINE
    )
    
    # Buscar TODOS los matches del patrón nuevo y elegir el que tenga base > 50€
    for match in patron_nuevo.finditer(texto):
        base = float(match.group(1).replace(',', '.'))
        iva = float(match.group(2).replace(',', '.'))
        total = float(match.group(3).replace(',', '.'))
        
        # Verificar que tiene sentido (base + iva ≈ total) y que es un total grande
        if abs((base + iva) - total) < 0.20 and base > 50:
            lineas.append({
                'codigo': 'PAN',
                'articulo': 'Pan',
                'cantidad': 1,
                'precio_unitario': base,
                'iva': 4,
                'base': base
            })
            return lineas
    
    # Buscar TODOS los matches del patrón antiguo
    for match in patron_antiguo.finditer(texto):
        total = float(match.group(1).replace(',', '.'))
        iva = float(match.group(2).replace(',', '.'))
        base = float(match.group(3).replace(',', '.'))
        
        # Verificar que tiene sentido y que es un total grande
        if abs((base + iva) - total) < 0.20 and base > 50:
            lineas.append({
                'codigo': 'PAN',
                'articulo': 'Pan',
                'cantidad': 1,
                'precio_unitario': base,
                'iva': 4,
                'base': base
            })
            return lineas
    
    # Patrón 3: Buscar "Total delegación" como fallback
    patron_total = re.compile(
        r'Total\s+delegaci[oó]n\s*[\n\s]*(\d+[.,]\d{2})\s+(\d+[.,]\d{2})\s+(\d+[.,]\d{2})',
        re.IGNORECASE | re.MULTILINE
    )
    
    match = patron_total.search(texto)
    if match:
        # Formato: base, iva, total
        base = float(match.group(1).replace(',', '.'))
        lineas.append({
            'codigo': 'PAN',
            'articulo': 'Pan',
            'cantidad': 1,
            'precio_unitario': base,
            'iva': 4,
            'base': base
        })
        return lineas
    
    return lineas


def extraer_lineas_julio_garcia_vivas(texto: str) -> List[Dict]:
    """Extrae líneas de facturas JULIO GARCIA VIVAS (verdulería) - v3.10.
    
    NIF: 02869898G
    Producto: Siempre "Verduras variadas"
    IVA: 4% (verduras frescas), puede haber 10% ocasionalmente
    
    Formato de factura:
    - Cabecera con datos del proveedor
    - Lista de albaranes con importes individuales
    - Resumen final: BASE\\nIVA\\nBASE IVA RE RE\\nTOTAL
    
    NOTA: Algunos PDFs son imágenes escaneadas (sin texto), 
    estos se marcarán como PDF_SIN_TEXTO y necesitarán OCR.
    
    Genera UNA línea con el total. El tipo de IVA se calcula
    a partir de cuota/base.
    """
    lineas = []
    
    # El texto termina con:
    # 65,87         <- BASE
    # 2,65          <- IVA  
    # 65,87 2,65 0,00 0,00   <- resumen (base, iva, re, re)
    # 68,52         <- TOTAL
    
    # Patrón principal: BASE\nIVA\nBASE IVA RE RE\nTOTAL
    patron = re.compile(
        r'(\d{1,3}(?:\.\d{3})*,\d{2})\s*\n\s*'  # BASE
        r'(\d{1,3}(?:\.\d{3})*,\d{2})\s*\n\s*'  # IVA
        r'\d{1,3}(?:\.\d{3})*,\d{2}\s+\d{1,3}(?:\.\d{3})*,\d{2}\s+\d{1,3}(?:\.\d{3})*,\d{2}\s+\d{1,3}(?:\.\d{3})*,\d{2}\s*\n\s*'  # RESUMEN
        r'(\d{1,3}(?:\.\d{3})*,\d{2})',  # TOTAL
        re.MULTILINE
    )
    
    match = patron.search(texto)
    if match:
        base_str = match.group(1)
        iva_str = match.group(2)
        total_str = match.group(3)
        
        base = float(base_str.replace('.', '').replace(',', '.'))
        iva_cuota = float(iva_str.replace('.', '').replace(',', '.'))
        total = float(total_str.replace('.', '').replace(',', '.'))
        
        # Calcular tipo IVA: cuota/base * 100
        if base > 0:
            iva_pct = round((iva_cuota / base) * 100)
            # Normalizar a tipos válidos
            if iva_pct <= 5:
                iva_pct = 4
            elif iva_pct <= 12:
                iva_pct = 10
            else:
                iva_pct = 21
        else:
            iva_pct = 4
        
        lineas.append({
            'codigo': 'VERDURAS',
            'articulo': 'Verduras variadas',
            'cantidad': 1,
            'precio_unitario': base,
            'iva': iva_pct,
            'base': round(base, 2)
        })
    
    return lineas


def extraer_lineas_generico(texto: str) -> List[Dict]:
    """Extrae líneas con patrón genérico."""
    lineas = []
    
    # Buscar patrones comunes de líneas con artículo, IVA e importe
    # Patrón: ARTICULO ... IVA% ... IMPORTE
    patron = re.compile(
        r'^(.{10,60}?)\s+'  # Artículo (10-60 chars)
        r'(\d{1,2})[%,]?\s+'  # IVA
        r'(\d{1,5}[.,]\d{2})\s*$',  # Importe
        re.MULTILINE
    )
    
    for match in patron.finditer(texto):
        articulo, iva, importe = match.groups()
        # Filtrar líneas que no son artículos
        if any(x in articulo.upper() for x in ['TOTAL', 'BASE', 'IVA', 'IMPORTE', 'FACTURA']):
            continue
        
        lineas.append({
            'codigo': '',
            'articulo': articulo.strip(),
            'iva': int(iva),
            'base': float(importe.replace(',', '.'))
        })
    
    return lineas


# =============================================================================
# MATCHING DE CATEGORÍAS
# =============================================================================

def similitud(a: str, b: str) -> float:
    """Calcula similitud entre dos strings (0-1)."""
    return SequenceMatcher(None, a.upper(), b.upper()).ratio()


def buscar_categoria(proveedor: str, articulo: str, indice: Dict, umbral: float = 0.8) -> Tuple[str, int]:
    """
    Busca la categoría de un artículo en el diccionario.
    Retorna (categoria, iva) o ('PENDIENTE', None).
    """
    # Normalizar proveedor para búsqueda
    proveedor_upper = proveedor.upper()
    
    # Buscar proveedor en el índice (matching flexible)
    proveedor_encontrado = None
    for prov in indice.keys():
        if not isinstance(prov, str):
            continue
        if prov in proveedor_upper or proveedor_upper in prov:
            proveedor_encontrado = prov
            break
        if similitud(prov, proveedor_upper) > 0.8:
            proveedor_encontrado = prov
            break
    
    if not proveedor_encontrado:
        return 'PENDIENTE', None
    
    # Buscar artículo
    articulos_prov = indice[proveedor_encontrado]
    mejor_match = None
    mejor_similitud = 0
    
    for item in articulos_prov:
        sim = similitud(articulo, item['articulo'])
        if sim > mejor_similitud:
            mejor_similitud = sim
            mejor_match = item
    
    if mejor_match and mejor_similitud >= umbral:
        return mejor_match['categoria'], mejor_match['iva']
    
    return 'PENDIENTE', None


# =============================================================================
# PRORRATEO
# =============================================================================

def prorratear_gastos(lineas: List[Dict], gasto: float, total_factura: float) -> List[Dict]:
    """
    Prorratear gastos de envío entre líneas manteniendo el total exacto.
    El gasto viene CON IVA incluido.
    """
    if not lineas or gasto == 0:
        return lineas
    
    # Calcular total de bases
    total_bases = sum(l['base'] for l in lineas)
    if total_bases == 0:
        return lineas
    
    # Calcular total actual con IVA
    total_actual = sum(l['base'] * (1 + l['iva']/100) for l in lineas)
    
    # Objetivo: total_actual + gasto = total_factura
    # Distribuir gasto proporcionalmente y ajustar bases
    
    nuevas_lineas = []
    for linea in lineas:
        proporcion = linea['base'] / total_bases
        gasto_linea = gasto * proporcion
        
        # Nueva base que al aplicar IVA da el importe correcto
        importe_original = linea['base'] * (1 + linea['iva']/100)
        nuevo_importe = importe_original + gasto_linea
        nueva_base = nuevo_importe / (1 + linea['iva']/100)
        
        nueva_linea = linea.copy()
        nueva_linea['base'] = round(nueva_base, 2)
        nuevas_lineas.append(nueva_linea)
    
    return nuevas_lineas


def aplicar_descuento(lineas: List[Dict], descuento: float) -> List[Dict]:
    """
    Aplicar descuento genérico prorrateado entre líneas.
    """
    if not lineas or descuento == 0:
        return lineas
    
    total_bases = sum(l['base'] for l in lineas)
    if total_bases == 0:
        return lineas
    
    nuevas_lineas = []
    for linea in lineas:
        proporcion = linea['base'] / total_bases
        descuento_linea = abs(descuento) * proporcion
        
        nueva_linea = linea.copy()
        nueva_linea['base'] = round(linea['base'] - descuento_linea, 2)
        nuevas_lineas.append(nueva_linea)
    
    return nuevas_lineas


# =============================================================================
# PROCESAMIENTO PRINCIPAL
# =============================================================================

def procesar_factura(ruta: Path, indice: Dict, carpeta_yaml: Path = None) -> Factura:
    """Procesa una factura completa."""
    nombre = ruta.name
    info = parsear_nombre_archivo(nombre)
    
    factura = Factura(
        archivo=nombre,
        numero=info['numero'],
        trimestre=info['trimestre'],
        metodo_pago=info['metodo_pago'],
        proveedor_archivo=info['proveedor']
    )
    
    # Extraer texto
    texto = extraer_texto_pdf(ruta)
    factura.texto_raw = texto[:1000]
    
    if not texto:
        factura.alertas.append('PDF_SIN_TEXTO')
        return factura
    
    # Buscar YAML del proveedor
    yaml_config = None
    if carpeta_yaml:
        yaml_config = buscar_yaml(info['proveedor'], carpeta_yaml)
    
    # Extraer datos básicos
    factura.cif = extraer_cif(texto)
    ibans = extraer_ibans(texto)
    factura.iban = elegir_iban(ibans)
    factura.fecha = extraer_fecha(texto, yaml_config, info['proveedor'])
    factura.ref = extraer_ref(texto, yaml_config, info['proveedor'])
    factura.total = extraer_total(texto)
    
    # Si falta CIF o IBAN, buscar en PROVEEDORES_CONOCIDOS
    proveedor_upper = info['proveedor'].upper()
    for nombre_prov, datos in PROVEEDORES_CONOCIDOS.items():
        if nombre_prov in proveedor_upper:
            if not factura.cif and datos.get('cif'):
                factura.cif = datos['cif']
            if not factura.iban and datos.get('iban'):
                factura.iban = datos['iban']
            break
    
    # Alertas
    if not factura.cif:
        factura.alertas.append('CIF_PENDIENTE')
    if factura.metodo_pago in ['TF', 'TR'] and not factura.iban:
        factura.alertas.append('IBAN_PENDIENTE')
    if not factura.fecha:
        factura.alertas.append('FECHA_PENDIENTE')
    
    # Extraer líneas según proveedor
    lineas_raw = []
    proveedor_upper = info['proveedor'].upper()
    
    if 'BERZAL' in proveedor_upper:
        lineas_raw = extraer_lineas_berzal(texto)
    elif 'LICORES' in proveedor_upper or 'MADRUEÑO' in proveedor_upper:
        lineas_raw = extraer_lineas_licores_madrueño(texto)
    elif 'SABORES' in proveedor_upper or 'PATERNA' in proveedor_upper:
        lineas_raw = extraer_lineas_sabores_paterna(texto)
    elif 'FRANCISCO' in proveedor_upper or 'GUERRA' in proveedor_upper:
        lineas_raw = extraer_lineas_francisco_guerra(texto)
    elif 'EMJAMESA' in proveedor_upper:
        lineas_raw = extraer_lineas_emjamesa(texto)
    elif 'ZUCCA' in proveedor_upper or 'FORMAGGIARTE' in proveedor_upper:
        lineas_raw = extraer_lineas_zucca(texto)
    elif 'NAVAS' in proveedor_upper or 'QUESOS_NAVAS' in proveedor_upper:
        lineas_raw = extraer_lineas_quesos_navas(texto)
    elif 'CERES' in proveedor_upper:
        lineas_raw = extraer_lineas_ceres(texto)
    elif 'BM' in proveedor_upper or 'SUPERMERCADO' in proveedor_upper:
        lineas_raw = extraer_lineas_bm(texto)
    elif 'CVNE' in proveedor_upper or 'VALSANGIACOMO' in texto.upper():
        lineas_raw = extraer_lineas_cvne(texto)
    elif 'BERNAL' in proveedor_upper or 'JAMONES' in proveedor_upper:
        lineas_raw = extraer_lineas_bernal(texto)
    elif 'FELISA' in proveedor_upper or 'DON FELIX' in proveedor_upper:
        lineas_raw = extraer_lineas_felisa(texto)
    elif 'BORBOTON' in proveedor_upper or 'BORBOTÓN' in proveedor_upper:
        lineas_raw = extraer_lineas_borboton(texto)
    elif 'ARGANZA' in proveedor_upper or 'VINOS DE ARGANZA' in texto.upper():
        lineas_raw = extraer_lineas_arganza(texto)
    elif 'PURISIMA' in proveedor_upper or 'PURÍSIMA' in proveedor_upper or 'LA PURISIMA' in texto.upper():
        lineas_raw = extraer_lineas_purisima(texto)
    elif 'MOLLETES' in proveedor_upper or 'ANTEQUERA' in proveedor_upper:
        lineas_raw = extraer_lineas_molletes(texto)
    elif 'YOIGO' in proveedor_upper or 'XFERA' in proveedor_upper:
        lineas_raw = extraer_lineas_yoigo(texto)
    elif 'SOM ENERGIA' in proveedor_upper or 'SOM ENERGI' in texto.upper():
        lineas_raw = extraer_lineas_som_energia(texto)
    elif 'LUCERA' in proveedor_upper or 'ENERGIA COLECTIVA' in proveedor_upper or 'ENERGÍA COLECTIVA' in texto.upper():
        lineas_raw = extraer_lineas_lucera(texto)
    elif 'SEGURMA' in proveedor_upper:
        lineas_raw = extraer_lineas_segurma(texto)
    elif 'KINEMA' in proveedor_upper or 'COOPERATIVA KINEMA' in proveedor_upper:
        lineas_raw = extraer_lineas_kinema(texto)
    elif 'OPENAI' in proveedor_upper or 'OPEN AI' in proveedor_upper or 'OPEN_AI' in proveedor_upper:
        lineas_raw = extraer_lineas_openai(texto)
    # v3.7 - Nuevos extractores
    elif 'LAVAPIES' in proveedor_upper or 'DISTRIBUCIONES LAVAPIES' in texto.upper():
        lineas_raw = extraer_lineas_lavapies(texto)
    elif 'FABEIRO' in proveedor_upper:
        lineas_raw = extraer_lineas_fabeiro(texto)
    elif 'SERRIN' in proveedor_upper or 'SERRÍN' in proveedor_upper or 'SERRIN NO CHAN' in texto.upper():
        lineas_raw = extraer_lineas_serrin(texto)
    elif 'ORTEGA' in proveedor_upper or 'BENJAMIN ORTEGA' in texto.upper() or '09342596L' in texto:
        lineas_raw = extraer_lineas_alquiler_ortega(texto)
    elif 'FERNANDEZ' in proveedor_upper or 'JAIME FERNANDEZ' in texto.upper() or '07219971H' in texto:
        lineas_raw = extraer_lineas_alquiler_fernandez(texto)
    # v3.9 - MIGUEZ CAL (ForPlan)
    elif 'MIGUEZ CAL' in proveedor_upper or 'MIGUEZ CAL' in texto.upper() or 'FORPLAN' in texto.upper() or 'FOR-PLAN' in texto.upper():
        lineas_raw = extraer_lineas_miguez_cal(texto)
    # v3.9 - MARITA COSTA
    elif 'MARITA COSTA' in proveedor_upper or 'MARITA COSTA' in texto.upper() or '48207369J' in texto:
        lineas_raw = extraer_lineas_marita_costa(texto)
    # v3.9 - PILAR RODRIGUEZ / Huevos El Majadal
    elif 'PILAR RODRIGUEZ' in proveedor_upper or 'MAJADAL' in proveedor_upper or 'MAJADAL' in texto.upper() or '06582655' in texto:
        lineas_raw = extraer_lineas_pilar_rodriguez(texto)
    # v3.9 - PANIFIESTO (pan, una sola línea con total)
    elif 'PANIFIESTO' in proveedor_upper or 'PANIFIESTO' in texto.upper() or 'B87874327' in texto:
        lineas_raw = extraer_lineas_panifiesto(texto)
    # v3.10 - JULIO GARCIA VIVAS (verdulería, una sola línea con total)
    elif 'GARCIA VIVAS' in proveedor_upper or 'JULIO GARCIA' in proveedor_upper or '02869898G' in texto:
        lineas_raw = extraer_lineas_julio_garcia_vivas(texto)
    
    # Si no hay líneas específicas, intentar genérico
    if not lineas_raw:
        lineas_raw = extraer_lineas_generico(texto)
    
    # v3.7 - PRORRATEO DE PORTES/TRANSPORTE
    # Identificar líneas de porte y prorratear entre el resto
    lineas_producto = []
    importe_portes = 0.0
    iva_portes = 21  # Por defecto portes al 21%
    
    for linea in lineas_raw:
        articulo_upper = linea['articulo'].upper()
        if any(x in articulo_upper for x in ['PORTE', 'PORTES', 'TRANSPORTE', 'ENVIO', 'ENVÍO', 'FLETE', 'GASTOS ENVIO']):
            importe_portes += linea['base']
            iva_portes = linea.get('iva', 21)
        else:
            lineas_producto.append(linea)
    
    # Si hay portes, prorratear entre productos
    if importe_portes > 0 and lineas_producto:
        total_bases = sum(l['base'] for l in lineas_producto)
        if total_bases > 0:
            for linea in lineas_producto:
                proporcion = linea['base'] / total_bases
                incremento_porte = importe_portes * proporcion
                
                # Ajustar la base: el porte se suma convertido al mismo tipo de IVA
                # Si el producto tiene IVA diferente al porte, convertimos
                if linea['iva'] != iva_portes:
                    # Convertir: base_porte * (1 + iva_porte/100) / (1 + iva_producto/100)
                    incremento_ajustado = incremento_porte * (1 + iva_portes/100) / (1 + linea['iva']/100)
                    linea['base'] = round(linea['base'] + incremento_ajustado, 2)
                else:
                    linea['base'] = round(linea['base'] + incremento_porte, 2)
        
        lineas_raw = lineas_producto  # Usar solo líneas de producto (sin portes)
    
    # Buscar categorías
    for linea in lineas_raw:
        # Si el extractor ya forzó una categoría (ej: alquileres), respetarla
        if 'categoria' in linea and linea['categoria'] != 'PENDIENTE':
            categoria = linea['categoria']
        else:
            categoria, iva_dicc = buscar_categoria(
                info['proveedor'], 
                linea['articulo'], 
                indice
            )
        factura.lineas.append(LineaFactura(
            codigo=linea.get('codigo', ''),
            articulo=linea['articulo'],
            base=linea['base'],
            iva=linea['iva'],
            categoria=categoria
        ))
    
    # Normalizar nombre proveedor
    proveedor_upper = info['proveedor'].upper().replace('_', ' ')
    for prov in indice.keys():
        if not isinstance(prov, str):
            continue
        if prov in proveedor_upper or proveedor_upper in prov:
            factura.proveedor_normalizado = prov
            break
    if not factura.proveedor_normalizado:
        factura.proveedor_normalizado = proveedor_upper
    
    if not factura.lineas:
        factura.alertas.append('SIN_LINEAS')
    
    return factura


# =============================================================================
# GENERACIÓN DE SALIDAS
# =============================================================================

def generar_excel_historico(facturas: List[Factura], ruta: Path):
    """Genera el Excel del histórico."""
    filas = []
    
    for f in facturas:
        if f.lineas:
            for linea in f.lineas:
                filas.append({
                    '#': f.numero,
                    'FECHA': f.fecha or '',
                    'REF': f.ref or '',
                    'PROVEEDOR': f.proveedor_normalizado,
                    'ARTICULO': linea.articulo,
                    'CATEGORIA': linea.categoria,
                    'TIPO IVA': linea.iva,
                    'BASE (€)': linea.base
                })
        else:
            # Factura sin líneas extraídas
            filas.append({
                '#': f.numero,
                'FECHA': f.fecha or '',
                'REF': f.ref or '',
                'PROVEEDOR': f.proveedor_normalizado,
                'ARTICULO': 'VER FACTURA',
                'CATEGORIA': 'PENDIENTE',
                'TIPO IVA': '',
                'BASE (€)': f.total or ''
            })
    
    df = pd.DataFrame(filas)
    df.to_excel(ruta, index=False, sheet_name='año 25')
    return len(filas)


def generar_log(facturas: List[Factura], ruta: Path):
    """Genera log detallado."""
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(f"MIGRACIÓN HISTÓRICO 2025 - v2.0\n")
        f.write(f"{'='*60}\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        total = len(facturas)
        con_cif = sum(1 for fa in facturas if fa.cif)
        con_iban = sum(1 for fa in facturas if fa.iban)
        con_lineas = sum(1 for fa in facturas if fa.lineas)
        total_lineas = sum(len(fa.lineas) for fa in facturas)
        
        f.write(f"RESUMEN:\n")
        f.write(f"  Facturas procesadas: {total}\n")
        if total > 0:
            f.write(f"  Con CIF extraído:    {con_cif} ({100*con_cif/total:.1f}%)\n")
            f.write(f"  Con IBAN extraído:   {con_iban}\n")
            f.write(f"  Con líneas extraídas: {con_lineas} ({100*con_lineas/total:.1f}%)\n")
        else:
            f.write(f"  Con CIF extraído:    {con_cif}\n")
            f.write(f"  Con IBAN extraído:   {con_iban}\n")
            f.write(f"  Con líneas extraídas: {con_lineas}\n")
        f.write(f"  Total líneas:        {total_lineas}\n")
        
        # IBANs encontrados
        f.write(f"\n{'='*60}\n")
        f.write(f"IBANs ENCONTRADOS:\n")
        for fa in facturas:
            if fa.iban:
                f.write(f"  {fa.proveedor_normalizado}: {fa.iban}\n")
        
        # CIFs encontrados
        f.write(f"\n{'='*60}\n")
        f.write(f"CIFs ENCONTRADOS:\n")
        for fa in facturas:
            if fa.cif:
                f.write(f"  {fa.proveedor_normalizado}: {fa.cif}\n")
        
        # Facturas con alertas
        f.write(f"\n{'='*60}\n")
        f.write(f"FACTURAS CON ALERTAS:\n")
        for fa in facturas:
            if fa.alertas:
                f.write(f"  {fa.archivo}: {', '.join(fa.alertas)}\n")
        
        # Artículos pendientes (sin categoría)
        f.write(f"\n{'='*60}\n")
        f.write(f"ARTÍCULOS PENDIENTES DE CATEGORIZAR:\n")
        pendientes = set()
        for fa in facturas:
            for linea in fa.lineas:
                if linea.categoria == 'PENDIENTE':
                    pendientes.add((fa.proveedor_normalizado, linea.articulo))
        for prov, art in sorted(pendientes):
            f.write(f"  [{prov}] {art}\n")


# =============================================================================
# MAIN
# =============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Migración histórico 2025 v2')
    parser.add_argument('--input', '-i', required=True, help='Carpeta de facturas')
    parser.add_argument('--output', '-o', default='Facturas_Recibidas_25.xlsx')
    parser.add_argument('--diccionario', '-d', required=True, help='DiccionarioProveedoresCategoria.xlsx')
    parser.add_argument('--yaml', '-y', default=None, help='Carpeta de YAMLs')
    
    args = parser.parse_args()
    
    print("="*60)
    print("MIGRACIÓN HISTÓRICO 2025 - v2.0")
    print("="*60)
    
    # Cargar diccionario
    print(f"\n📚 Cargando diccionario...")
    articulos, patrones, indice = cargar_diccionario(Path(args.diccionario))
    print(f"   {len(articulos)} artículos, {len(indice)} proveedores")
    
    # Buscar archivos
    carpeta = Path(args.input)
    archivos = list(carpeta.glob('*.pdf'))
    print(f"\n📂 Carpeta: {carpeta}")
    print(f"   Archivos: {len(archivos)}")
    
    # Procesar
    facturas = []
    for i, archivo in enumerate(sorted(archivos), 1):
        print(f"   [{i:3d}/{len(archivos)}] {archivo.name[:50]}...", end=" ")
        
        yaml_path = Path(args.yaml) if args.yaml else None
        factura = procesar_factura(archivo, indice, yaml_path)
        facturas.append(factura)
        
        if factura.alertas:
            print(f"⚠️  {', '.join(factura.alertas[:2])}")
        elif factura.lineas:
            print(f"✅ {len(factura.lineas)} líneas")
        else:
            print("⚠️  SIN_LINEAS")
    
    # Generar salidas
    print(f"\n📊 Generando Excel...")
    ruta_excel = Path(args.output)
    total_filas = generar_excel_historico(facturas, ruta_excel)
    print(f"   {ruta_excel}: {total_filas} filas")
    
    ruta_log = Path(f"log_migracion_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
    generar_log(facturas, ruta_log)
    print(f"   {ruta_log}")
    
    # Resumen
    print(f"\n{'='*60}")
    print("MIGRACIÓN COMPLETADA")
    print(f"{'='*60}")
    con_lineas = sum(1 for f in facturas if f.lineas)
    total_lineas = sum(len(f.lineas) for f in facturas)
    print(f"  Facturas: {len(facturas)}")
    print(f"  Con líneas: {con_lineas} ({100*con_lineas/len(facturas):.1f}%)")
    print(f"  Total líneas: {total_lineas}")
    print(f"  IBANs: {sum(1 for f in facturas if f.iban)}")


if __name__ == '__main__':
    main()
