#!/usr/bin/env python3
"""
MIGRACIÓN HISTÓRICO 2025 - v3.23
================================
Extrae líneas detalladas de facturas, categoriza artículos,
prorratrea gastos y descuentos, y actualiza maestros.

v3.27 - EXTRACTOR LA MOLIENDA VERDE
      - Nuevo extractor específico para LA MOLIENDA VERDE
      - Extrae bases del desglose fiscal (10% productos, 21% portes)
      - Cuadre perfecto garantizado
      v3.26b - EXTRACTOR BM PERFECCIONADO
      v3.26 - MEJORA CUADRE BM SUPERMERCADOS
      v3.25 - MEJORA EXTRACCIÓN TOTAL FACTURA
      v3.24 - ISTA + BIELLEBI + FERRIOL + ABBATI + MUÑOZ MARTÍN
      - Añadido extractor ISTA (liquidación consumo agua)
        CIF: A50090133, Categoría: CONSUMO DE AGUA, IVA 10%
      - Añadido extractor BIELLEBI (taralli italiano intracomunitario)
        CIF: 06089700725, IBAN: IT68B0306941603100000001003
        Categoría: TARALLI, IVA 0%, portes repartidos
      - Añadido extractor FERRIOL (chacinas Mallorca)
        CIF: B57955098, IBAN: ES22 2100 0088 0502 0014 6500
        Categoría: CHACINAS, IVA 10%
      - Añadido extractor ABBATI CAFFE
        CIF: B82567876, Categoría: CAFE, IVA 10%
      - Añadido extractor BODEGAS MUÑOZ MARTÍN
        CIF: E83182683, IBAN: ES62 0049 5184 11 2016002766
        Categoría: VINOS, IVA 21%, portes repartidos
      v3.23 - AMAZON + CONTROLPLAGA + PANRUJE + ANGEL Y LOLI + QUESOS DEL CATI + CORRECCIONES
      - Añadido extractor CONTROLPLAGA / Javier Alborés (desinsectación)
        NIF: 11812266H, Categoría: DESINSECTACION, IVA 21%
      - Añadido extractor PANRUJE / Rosquillas La Ermita
        CIF: B13858014, Categoría: ROSQUILLAS M, IVA 4% o 10%
        Portes repercutidos, BASE = TOTAL / (1 + IVA/100)
      - Añadido extractor ANGEL Y LOLI / Alfarería
        NIF: 75727068M, Categoría: CACHARRERIA, IVA 21%
        Portes repartidos proporcionalmente entre artículos
      - Añadido extractor QUESOS DEL CATI
        CIF: F12499455, Categoría: QUESOS, IVA 4%
        Separación automática código-nombre (CATIABRIGO -> CATI ABRIGO)
      - Corregido FABEIRO: añadido patrón v3.23 para formato alternativo
      - Eliminada función duplicada extraer_lineas_panruje
      - Añadido patrón REF para AMAZON: "Número de la factura DS-AEU-INV-ES-..."
      - Corregido dispatcher ORTEGA/FERNANDEZ para evitar falsos positivos

v3.22 - CORRECCIÓN LA PURÍSIMA + BUG RUTA OUTPUTS
      - Añadido patrón REF para LA PURÍSIMA: "Número factura: 24−00−483"
      - Añadido patrón FECHA para LA PURÍSIMA: "Fecha factura: DD/MM/YYYY"
      - Corregido bug: -o ahora guarda en outputs/ si es nombre simple
      - Soporta guiones Unicode (−) y normales (-)

v3.21 - VALIDACIÓN DE CUADRE
      - Nueva columna CUADRE: verifica que Σ bases + Σ IVAs ≈ Total factura
      - Valores: OK / DESCUADRE: ±X.XX€ / SIN_TOTAL / SIN_LINEAS
      - Detecta automáticamente facturas con líneas faltantes o mal extraídas
      - Tolerancia de ±0.05€ para redondeos

v3.20 - Corregido patrón FECHA/REF de QUESOS FELIX
      - PyPDF2 extrae "25 0014827/03/2025" (número PEGADO a fecha, sin espacio)
      - Antes fallaba porque el patrón esperaba espacio entre número y fecha

v3.16 - Añadido extractor PORVAZ VILAGARCÍA / Conservas Tito
      - CIF: B36281087, IVA: 10%, IBAN: ES63 0049 5368 0625 1628 3321
      - Categoría fija: CONSERVAS PESCADO
      - Formato limpio: DESCRIPCION CANTIDAD PRECIO IVA IMPORTE
      - Añadido alias "QUESERIA NAVAS" para extractor CARLOS NAVAS
      - Corregido patrón FECHA para DISTRIBUCIONES LAVAPIES
      - Formato: "DD/MM/YY NNNNNN" al inicio del documento
      
v3.15 - Añadidos 3 nuevos extractores:
      - QUESOS FELIX / Armando Sanz (quesos IGP)
        CIF: B47440136, IVA: 4%, categoría: QUESOS
        IBAN: ES40 2103 4346 3300 3306 5431
      - PANRUJE / Rosquillas La Ermita (pan/rosquillas)
        CIF: B13858014, IVA: 4%, categoría: PAN
        IBAN: ES19 0081 5344 2800 0261 4066
      - CARLOS NAVAS / Quesería Carlos Navas (quesos oveja)
        CIF: B37416419, IVA: 4%, categoría: QUESOS
        IBAN: ES62 2100 6153 0402 0001 6597

v3.14 - Configuración de carpeta outputs/ por defecto
      - Los resultados se guardan en src/migracion/outputs/
      - El log también se guarda en outputs/
      - Se crea la carpeta automáticamente si no existe
      - Corregido patrón FECHA de LA BARRA DULCE (formato CIF + DD.MM.YYYY)
      - Añadido IBAN MARTIN ABENZA: ES37 0049 6193 4128 9534 3887
      - Añadido IBAN GRUPO TERRITORIO CAMPERO: ES71 0049 3739 4027 1401 6466

v3.13 - Añadidos 6 nuevos extractores:
      - PRODUCTOS ADELL / Croquellanas (conservas gourmet)
        CIF: B12711636, IVA: 10%, IBAN: ES62 3058 7413 2127 2000 8367
      - ECOFICUS (higos ecológicos)
        CIF: B10214021, IVA: 10%, IBAN: ES23 2103 7136 4700 3002 4378
      - QUESOS ROYCA / Comercial Royca (quesos)
        CIF: E06388631, IVA: 4%, categoría: QUESOS
      - IBARRAKO PIPARRAK (guindillas)
        CIF: F20532297, IVA: 10%, categoría fija: PIPARRAS
        IBAN: ES69 2095 5081 9010 6181 7077
      - ANA CABALLO VERMOUTH (vermuts)
        CIF: B87925970, IVA: 21%, categoría fija: LICORES Y VERMUS
        IBAN: ES75 2100 1360 2202 0006 0355
      - MARTIN ABENZA / El Modesto (conservas artesanas)
        NIF: 74305431K, IVA: 10%, categoría fija: CONSERVAS VEGETALES

v3.12 - Añadido extractor TRUCCO COPIAS / Isaac Rodríguez Pacha (imprenta)
      - NIF: 05247386M, IVA: 21%, categoría fija: GASTOS VARIOS
      - Sin IBAN (pago por tarjeta)
      - Añadido IBAN EMJAMESA: ES08 3016 0206 5221 8503 2527
      - Añadido extractor LA BARRA DULCE (pastelería)
      - CIF: B19981141, IVA: 10%, categoría fija: DULCES
      - IBAN: ES76 2100 5606 4802 0017 4138
      - Añadido extractor GRUPO TERRITORIO CAMPERO (patatas fritas)
      - CIF: B16690141, IVA: 10%, categoría fija: PATATAS FRITAS APERITIVO
      - Sin IBAN (pendiente)
      - Añadido extractor ZUBELZU PIPARRAK (guindillas y mousse)
      - CIF: B75079608, IVA: 10%
      - Categorías: GUINDILLAS→PIPARRAS, MOUSSE PIPARRA→CONSERVAS VEGETALES
      - IBAN: ES?? 3035 0141 82 1410019635 (formato parcial en factura)

v3.11 - Añadido extractor MRM / Industrias Cárnicas MRM-2 (patés, mousses, salmón)
      - CIF: A80280845, IVA: 10%, IBAN: ES28 2100 8662 5702 0004 8824
      - Añadido extractor DISBER / Grupo Disber (vinos, conservas gourmet)
      - CIF: B46144424, IVA: 21% (vinos) / 10% (conservas)
      - IBAN: ES39 2100 8617 1502 0002 4610

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

# Alias de proveedores para búsqueda en diccionario de categorías
# Mapea nombre en factura → nombre en diccionario Excel
PROVEEDOR_ALIAS_DICCIONARIO = {
    'JAMONES BERNAL': 'EMBUTIDOS BERNAL',
    'BERNAL': 'EMBUTIDOS BERNAL',
}

# v3.23 - Alias para normalización de nombre de proveedor en salida
PROVEEDOR_NOMBRE_SALIDA = {
    'JAVIER ALBORES': 'CONTROLPLAGA',
    'JAVIER ARBORES': 'CONTROLPLAGA',
    'ALBORES': 'CONTROLPLAGA',
    'ARBORES': 'CONTROLPLAGA',
}

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
    'SABORES DE PATERNA': {'cif': 'B96771832', 'iban': 'ES65 2100 8505 1802 0003 1050'},
    'SABORES': {'cif': 'B96771832', 'iban': 'ES65 2100 8505 1802 0003 1050'},
    'PATERNA': {'cif': 'B96771832', 'iban': 'ES65 2100 8505 1802 0003 1050'},
    'MARTIN ARBENZA': {'cif': '74305431K', 'iban': ''},
    'EL MODESTO': {'cif': '74305431K', 'iban': ''},
    'FRANCISCO GUERRA': {'cif': '50449614B', 'iban': 'ES70 0049 4007 1428 1402 7169'},
    'TRUCCO': {'cif': '05247386M', 'iban': ''},
    'ISAAC RODRIGUEZ': {'cif': '05247386M', 'iban': ''},
    'ISTA': {'cif': 'A50090133', 'iban': ''},
    'AMAZON': {'cif': 'W0184081H', 'iban': ''},
    'VINOS DE ARGANZA': {'cif': 'B24416869', 'iban': 'ES92 0081 5385 6500 0121 7327'},
    'LA PURISIMA': {'cif': 'F30005193', 'iban': 'ES78 0081 0259 1000 0184 4495'},
    'PURISIMA': {'cif': 'F30005193', 'iban': 'ES78 0081 0259 1000 0184 4495'},
    'MOLLETES': {'cif': 'B93662708', 'iban': 'ES34 0049 4629 5323 1715 7896'},
    'BODEGAS BORBOTON': {'cif': 'B45851755', 'iban': 'ES37 2100 1913 1902 0013 5677'},
    'BORBOTON': {'cif': 'B45851755', 'iban': 'ES37 2100 1913 1902 0013 5677'},
    'FELISA GOURMET': {'cif': 'B72113897', 'iban': 'ES68 0182 1076 9502 0169 3908'},
    'FELISA': {'cif': 'B72113897', 'iban': 'ES68 0182 1076 9502 0169 3908'},
    'JAMONES BERNAL': {'cif': 'B67784231', 'iban': 'ES49 2100 7191 2902 0003 7620'},
    'BERNAL': {'cif': 'B67784231', 'iban': 'ES49 2100 7191 2902 0003 7620'},
    'EMJAMESA': {'cif': 'B37352077', 'iban': 'ES08 3016 0206 5221 8503 2527'},
    'MAKRO': {'cif': 'A28647451', 'iban': ''},  # Pago tarjeta
    # v3.19 - ZUCCA / FORMAGGIARTE (quesos italianos)
    'ZUCCA': {'cif': 'B42861948', 'iban': 'ES05 1550 0001 2000 1157 7624'},
    'FORMAGGIARTE': {'cif': 'B42861948', 'iban': 'ES05 1550 0001 2000 1157 7624'},
    'QUESERIA ZUCCA': {'cif': 'B42861948', 'iban': 'ES05 1550 0001 2000 1157 7624'},
    # v3.19 - CVNE (Compañía Vinícola del Norte de España)
    'CVNE': {'cif': 'A48002893', 'iban': 'ES09 2100 9144 3102 0002 5176'},
    'COMPAÑIA VINICOLA': {'cif': 'A48002893', 'iban': 'ES09 2100 9144 3102 0002 5176'},
    # Adeudos (no necesitan IBAN)
    'YOIGO': {'cif': 'A82528548', 'iban': ''},
    'XFERA': {'cif': 'A82528548', 'iban': ''},
    'SOM ENERGIA': {'cif': 'F55091367', 'iban': ''},
    'LUCERA': {'cif': 'B98670003', 'iban': ''},
    'SEGURMA': {'cif': 'A48198626', 'iban': ''},
    'KINEMA': {'cif': 'F84600022', 'iban': ''},
    # v3.9 - MIGUEZ CAL (ForPlan)
    'MIGUEZ CAL': {'cif': 'B79868006', 'iban': 'ES96 2085 9748 9203 0003 9285'},
    'FORPLAN': {'cif': 'B79868006', 'iban': 'ES96 2085 9748 9203 0003 9285'},
    # v3.9 - MARITA COSTA (distribuidor gourmet)
    'MARITA COSTA': {'cif': '48207369J', 'iban': 'ES08 0182 7036 0902 0151 9833'},
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
    # v3.11 - MRM / Industrias Cárnicas MRM-2
    'MRM': {'cif': 'A80280845', 'iban': 'ES28 2100 8662 5702 0004 8824'},
    'MRM-2': {'cif': 'A80280845', 'iban': 'ES28 2100 8662 5702 0004 8824'},
    'INDUSTRIAS CARNICAS MRM': {'cif': 'A80280845', 'iban': 'ES28 2100 8662 5702 0004 8824'},
    # v3.11 - DISBER / Grupo Disber
    'DISBER': {'cif': 'B46144424', 'iban': 'ES39 2100 8617 1502 0002 4610'},
    'GRUPO DISBER': {'cif': 'B46144424', 'iban': 'ES39 2100 8617 1502 0002 4610'},
    # v3.12 - TRUCCO COPIAS / Isaac Rodríguez Pacha (imprenta) - sin IBAN (pago tarjeta)
    'TRUCCO': {'cif': '05247386M', 'iban': ''},
    'TRUCCO COPIAS': {'cif': '05247386M', 'iban': ''},
    'ISAAC RODRIGUEZ': {'cif': '05247386M', 'iban': ''},
    'ISAAC RODRIGUEZ PACHA': {'cif': '05247386M', 'iban': ''},
    # v3.12 - LA BARRA DULCE (pastelería)
    'LA BARRA DULCE': {'cif': 'B19981141', 'iban': 'ES76 2100 5606 4802 0017 4138'},
    'BARRA DULCE': {'cif': 'B19981141', 'iban': 'ES76 2100 5606 4802 0017 4138'},
    # v3.12/v3.14 - GRUPO TERRITORIO CAMPERO (patatas fritas) - IBAN añadido v3.14
    'GRUPO TERRITORIO CAMPERO': {'cif': 'B16690141', 'iban': 'ES71 0049 3739 4027 1401 6466'},
    'TERRITORIO CAMPERO': {'cif': 'B16690141', 'iban': 'ES71 0049 3739 4027 1401 6466'},
    'GRUPO CAMPERO': {'cif': 'B16690141', 'iban': 'ES71 0049 3739 4027 1401 6466'},
    # v3.12 - ZUBELZU PIPARRAK (guindillas y mousse)
    'ZUBELZU': {'cif': 'B75079608', 'iban': ''},
    'ZUBELZU PIPARRAK': {'cif': 'B75079608', 'iban': ''},
    # v3.13 - PRODUCTOS ADELL / Croquellanas
    'PRODUCTOS ADELL': {'cif': 'B12711636', 'iban': 'ES62 3058 7413 2127 2000 8367'},
    'CROQUELLANAS': {'cif': 'B12711636', 'iban': 'ES62 3058 7413 2127 2000 8367'},
    # v3.13 - ECOFICUS
    'ECOFICUS': {'cif': 'B10214021', 'iban': 'ES23 2103 7136 4700 3002 4378'},
    # v3.13 - QUESOS ROYCA / Comercial Royca
    'QUESOS ROYCA': {'cif': 'E06388631', 'iban': ''},
    'COMERCIAL ROYCA': {'cif': 'E06388631', 'iban': ''},
    'ROYCA': {'cif': 'E06388631', 'iban': ''},
    # v3.13 - IBARRAKO PIPARRAK
    'IBARRAKO PIPARRAK': {'cif': 'F20532297', 'iban': 'ES69 2095 5081 9010 6181 7077'},
    'IBARRAKO': {'cif': 'F20532297', 'iban': 'ES69 2095 5081 9010 6181 7077'},
    # v3.13 - ANA CABALLO VERMOUTH
    'ANA CABALLO': {'cif': 'B87925970', 'iban': 'ES75 2100 1360 2202 0006 0355'},
    'ANA CABALLO VERMOUTH': {'cif': 'B87925970', 'iban': 'ES75 2100 1360 2202 0006 0355'},
    # v3.13/v3.14 - MARTIN ABENZA / El Modesto - IBAN añadido v3.14
    'MARTIN ABENZA': {'cif': '74305431K', 'iban': 'ES37 0049 6193 4128 9534 3887'},
    'MARTIN ARBENZA': {'cif': '74305431K', 'iban': ''},
    'EL MODESTO': {'cif': '74305431K', 'iban': ''},
    # v3.15 - QUESOS FELIX / Armando Sanz
    'QUESOS FELIX': {'cif': 'B47440136', 'iban': 'ES40 2103 4346 3300 3306 5431'},
    'ARMANDO SANZ': {'cif': 'B47440136', 'iban': 'ES40 2103 4346 3300 3306 5431'},
    'FELIX': {'cif': 'B47440136', 'iban': 'ES40 2103 4346 3300 3306 5431'},
    # v3.15 - PANRUJE / Rosquillas La Ermita
    'PANRUJE': {'cif': 'B13858014', 'iban': 'ES19 0081 5344 2800 0261 4066'},
    'ROSQUILLAS LA ERMITA': {'cif': 'B13858014', 'iban': 'ES19 0081 5344 2800 0261 4066'},
    # v3.15 - CARLOS NAVAS / Quesería Carlos Navas
    'CARLOS NAVAS': {'cif': 'B37416419', 'iban': 'ES62 2100 6153 0402 0001 6597'},
    'QUESERIA CARLOS NAVAS': {'cif': 'B37416419', 'iban': 'ES62 2100 6153 0402 0001 6597'},
    'QUESERIA NAVAS': {'cif': 'B37416419', 'iban': 'ES62 2100 6153 0402 0001 6597'},
    'QUESOS NAVAS': {'cif': 'B37416419', 'iban': 'ES62 2100 6153 0402 0001 6597'},
    # v3.16 - PORVAZ VILAGARCÍA / Conservas Tito
    'PORVAZ': {'cif': 'B36281087', 'iban': 'ES63 0049 5368 0625 1628 3321'},
    'PORVAZ VILAGARCIA': {'cif': 'B36281087', 'iban': 'ES63 0049 5368 0625 1628 3321'},
    'CONSERVAS TITO': {'cif': 'B36281087', 'iban': 'ES63 0049 5368 0625 1628 3321'},
    'TITO': {'cif': 'B36281087', 'iban': 'ES63 0049 5368 0625 1628 3321'},
    # v3.23 - CONTROLPLAGA / Javier Alborés Rey (desinsectación)
    'CONTROLPLAGA': {'cif': '11812266H', 'iban': 'ES86 0081 7122 58 0001218325'},
    'JAVIER ALBORES': {'cif': '11812266H', 'iban': 'ES86 0081 7122 58 0001218325'},
    'JAVIER ARBORES': {'cif': '11812266H', 'iban': 'ES86 0081 7122 58 0001218325'},
    'ALBORES': {'cif': '11812266H', 'iban': 'ES86 0081 7122 58 0001218325'},
    # v3.23 - PANRUJE / Rosquillas La Ermita
    'PANRUJE': {'cif': 'B13858014', 'iban': 'ES19 0081 5344 2800 0261 4066'},
    'LA ERMITA': {'cif': 'B13858014', 'iban': 'ES19 0081 5344 2800 0261 4066'},
    # v3.23 - ANGEL Y LOLI / Alfarería
    'ANGEL Y LOLI': {'cif': '75727068M', 'iban': ''},
    'ALFARERIA ANGEL': {'cif': '75727068M', 'iban': ''},
    # v3.23 - QUESOS DEL CATI
    'QUESOS DEL CATI': {'cif': 'F12499455', 'iban': 'ES89 2100 7363 72 1100030799'},
    'QUESOS CATI': {'cif': 'F12499455', 'iban': 'ES89 2100 7363 72 1100030799'},
    # v3.24 - ISTA (consumo agua)
    'ISTA': {'cif': 'A50090133', 'iban': ''},
    # v3.24 - BIELLEBI (taralli italiano intracomunitario)
    'BIELLEBI': {'cif': '06089700725', 'iban': 'IT68B0306941603100000001003'},
    'BIELLEBI SRL': {'cif': '06089700725', 'iban': 'IT68B0306941603100000001003'},
    # v3.24 - EMBUTIDOS FERRIOL (chacinas Mallorca)
    'EMBUTIDOS FERRIOL': {'cif': 'B57955098', 'iban': 'ES22 2100 0088 0502 0014 6500'},
    'EMBOTITS FERRIOL': {'cif': 'B57955098', 'iban': 'ES22 2100 0088 0502 0014 6500'},
    'FERRIOL': {'cif': 'B57955098', 'iban': 'ES22 2100 0088 0502 0014 6500'},
    # v3.24 - ABBATI CAFFE
    'ABBATI CAFFE': {'cif': 'B82567876', 'iban': ''},
    'ABBATI': {'cif': 'B82567876', 'iban': ''},
    # v3.24 - BODEGAS MUÑOZ MARTÍN
    'BODEGAS MUÑOZ MARTIN': {'cif': 'E83182683', 'iban': 'ES62 0049 5184 11 2016002766'},
    'MUÑOZ MARTIN': {'cif': 'E83182683', 'iban': 'ES62 0049 5184 11 2016002766'},
}


# =============================================================================
# v3.19 - CATEGORÍAS POR DEFECTO PARA PROVEEDORES CONOCIDOS
# =============================================================================
# Cuando no se encuentra en el diccionario, usar estas categorías fijas

CATEGORIA_PROVEEDOR_DEFAULT = {
    # Quesos
    'QUESOS FELIX': 'QUESOS',
    'CARLOS NAVAS': 'QUESOS',
    'QUESERIA CARLOS NAVAS': 'QUESOS',
    'ZUCCA': 'QUESOS',
    'FORMAGGIARTE': 'QUESOS',
    'QUESOS DEL CATI': 'QUESOS',
    'QUESOS MONTEALVA': 'QUESOS',
    'QUESOS ROYCA': 'QUESOS',
    
    # Vinos y licores
    'BORBOTON': 'VINOS',
    'BODEGAS BORBOTON': 'VINOS',
    'LICORES MADRUEÑO': 'LICORES',
    'CVNE': 'VINOS',
    'LA PURISIMA': 'VINOS',
    'BODEGAS MUÑOZ MARTIN': 'VINOS',
    'VINOS DE ARGANZA': 'VINOS',
    
    # Pan y bollería
    'MOLLETES ARTESANOS': 'PAN',
    'PANIFIESTO': 'PAN',
    'PANRUJE': 'PAN',
    'LA ROSQUILLERIA': 'BOLLERIA',
    'LA BARRA DULCE': 'BOLLERIA',
    
    # Embutidos y jamones
    'EMJAMESA': 'JAMONES',
    'JAMONES BERNAL': 'JAMONES',
    'FABEIRO': 'EMBUTIDOS',
    
    # Conservas
    'EUROANCHOAS': 'ANCHOAS',
    'FELISA': 'CONSERVAS',
    'PORVAZ': 'CONSERVAS',
    'CONSERVAS TITO': 'CONSERVAS',
    
    # Verduras y frutas
    'JULIO GARCIA VIVAS': 'VERDURAS',
    'LA MOLIENDA VERDE': 'CONSERVAS VEGETALES',
    'SABORES DE PATERNA': 'CONSERVAS VEGETALES',
    
    # Lácteos
    'WELLLDONE LACTICOS': 'LACTEOS',
    
    # Servicios
    'SOM ENERGIA': 'LUZ',
    'LUCERA': 'LUZ',
    'KINEMA': 'GESTORIA',
    'COOPERATIVA KINEMA': 'GESTORIA',
    'SEGURMA': 'ALARMA',
    'YOIGO': 'TELEFONO Y COMUNICACIONES',
    'XFERA': 'TELEFONO Y COMUNICACIONES',
    'OPEN AI': 'SOFTWARE',
    'OPENAI': 'SOFTWARE',
    'MAKE': 'SOFTWARE',
    'MAKE.COM': 'SOFTWARE',
    'WEBEMPRESA': 'SOFTWARE',
    'CONTROLPLAGA': 'DESINSECTACION',
    'JAVIER ALBORES': 'DESINSECTACION',
    'JAVIER ARBORES': 'DESINSECTACION',
    # v3.23 - PANRUJE
    'PANRUJE': 'ROSQUILLAS M',
    'LA ERMITA': 'ROSQUILLAS M',
    # v3.23 - ANGEL Y LOLI
    'ANGEL Y LOLI': 'CACHARRERIA',
    'ALFARERIA ANGEL': 'CACHARRERIA',
    # v3.23 - QUESOS DEL CATI
    'QUESOS DEL CATI': 'QUESOS',
    'QUESOS CATI': 'QUESOS',
    # v3.24 - ISTA
    'ISTA': 'CONSUMO DE AGUA',
    # v3.24 - BIELLEBI
    'BIELLEBI': 'TARALLI',
    'BIELLEBI SRL': 'TARALLI',
    # v3.24 - EMBUTIDOS FERRIOL
    'EMBUTIDOS FERRIOL': 'CHACINAS',
    'EMBOTITS FERRIOL': 'CHACINAS',
    'FERRIOL': 'CHACINAS',
    # v3.24 - ABBATI CAFFE
    'ABBATI CAFFE': 'CAFE',
    'ABBATI': 'CAFE',
    # v3.24 - BODEGAS MUÑOZ MARTÍN
    'BODEGAS MUÑOZ MARTIN': 'VINOS',
    'MUÑOZ MARTIN': 'VINOS',
    
    # Supermercados
    'BM': 'SUPERMERCADO',
    'BM SUPERMERCADOS': 'SUPERMERCADO',
    'LIDL': 'SUPERMERCADO',
    'MAKRO': 'SUPERMERCADO',
    
    # Otros
    'DISTRIBUCIONES LAVAPIES': 'BEBIDAS',
    'ISTA': 'CONTADORES',
    'PC COMPONENTES': 'MATERIAL OFICINA',
    'AMAZON': 'MATERIAL OFICINA',
    'FNMT': 'TASAS',
    'REGISTRO MERCANTIL': 'TASAS',
}

# Mapeo de palabras clave en artículo -> categoría (fallback)
CATEGORIA_PALABRAS_CLAVE = {
    # Quesos
    ('QUESO', 'BURRATA', 'MOZZARELLA', 'SCAMORZA', 'CILIEGINE'): 'QUESOS',
    # Vinos
    ('VINO', 'TINTO', 'BLANCO', 'ROSADO', 'COUPAGE', 'CRIANZA', 'RESERVA', 'TEMPRANILLO', 'VERDEJO', 'ALBARIÑO'): 'VINOS',
    # Licores
    ('VERMUT', 'GINEBRA', 'RON', 'WHISKY', 'LICOR', 'ORUJO', 'AGUARDIENTE'): 'LICORES',
    # Pan
    ('PAN', 'MOLLETE', 'HOGAZA', 'BAGUETTE'): 'PAN',
    # Bollería
    ('ROSQUILLA', 'BOLLO', 'CROISSANT', 'ENSAIMADA'): 'BOLLERIA',
    # Embutidos
    ('CHORIZO', 'SALCHICHON', 'LOMO', 'CECINA', 'FUET'): 'EMBUTIDOS',
    # Jamones
    ('JAMON', 'PALETA', 'IBERICO', 'BELLOTA'): 'JAMONES',
    # Conservas
    ('ANCHOA', 'SARDINA', 'ATUN', 'BONITO', 'MEJILLON', 'BERBERECHO'): 'CONSERVAS',
    # Verduras
    ('VERDURA', 'TOMATE', 'PIMIENTO', 'CEBOLLA', 'AJO', 'ENSALADA', 'LECHUGA'): 'VERDURAS',
    # Servicios
    ('ELECTRICIDAD', 'LUZ', 'ENERGIA'): 'LUZ',
    ('TELEFONO', 'INTERNET', 'MOVIL', 'FIBRA'): 'TELEFONO Y COMUNICACIONES',
    ('ASESORIA', 'GESTORIA', 'CONTABLE', 'FISCAL', 'LABORAL'): 'ASESORIA',
    ('ALARMA', 'SEGURIDAD'): 'ALARMA',
    ('SUBSCRIPTION', 'SUSCRIPCION', 'SOFTWARE', 'CHATGPT', 'HOSTING'): 'SOFTWARE',
}


def obtener_categoria_default(proveedor: str, articulo: str) -> str:
    """
    v3.19: Obtiene categoría por defecto basada en proveedor o palabras clave.
    Se usa como fallback cuando no se encuentra en el diccionario principal.
    """
    proveedor_upper = proveedor.upper().strip() if proveedor else ''
    articulo_upper = articulo.upper().strip() if articulo else ''
    
    # Primero: buscar por proveedor exacto
    if proveedor_upper in CATEGORIA_PROVEEDOR_DEFAULT:
        return CATEGORIA_PROVEEDOR_DEFAULT[proveedor_upper]
    
    # Segundo: buscar por proveedor parcial
    for prov, cat in CATEGORIA_PROVEEDOR_DEFAULT.items():
        if prov in proveedor_upper or proveedor_upper in prov:
            return cat
    
    # Tercero: buscar por palabras clave en artículo
    for palabras, cat in CATEGORIA_PALABRAS_CLAVE.items():
        for palabra in palabras:
            if palabra in articulo_upper:
                return cat
    
    return 'PENDIENTE'


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
    cuadre: str = ""  # v3.21: OK / DESCUADRE: ±X.XX€ / SIN_TOTAL / SIN_LINEAS
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
    
    # v3.16 - DISTRIBUCIONES LAVAPIES: "DD/MM/YY NNNNNN" al inicio
    # Formato: "04/12/25 251131" donde 04/12/25 es fecha y 251131 es nº documento
    if 'LAVAPIES' in proveedor_upper and 'PANIFIESTO' not in proveedor_upper or 'F88424072' in texto:
        # Buscar fecha DD/MM/YY seguida de número de documento (6 dígitos)
        patron = re.compile(r'(\d{2})/(\d{2})/(\d{2})\s+\d{6}')
        match = patron.search(texto)
        if match:
            d, m, y = match.groups()
            return f"{d}-{m}-{y}"
    
    # v3.10 - JULIO GARCIA VIVAS: DD/MM/YYYY después de los 8 dígitos de factura
    if 'GARCIA VIVAS' in proveedor_upper or 'JULIO GARCIA' in proveedor_upper or '02869898G' in texto:
        # Patrón: 8 dígitos + newline + fecha
        patron = re.compile(r'\n\d{8}\s*\n\s*(\d{2})/(\d{2})/(\d{4})\s*\n')
        match = patron.search(texto)
        if match:
            d, m, y = match.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.11 - MRM: DD/MM/YYYY seguido de EURO
    if 'MRM' in proveedor_upper or 'A80280845' in texto:
        patron = re.search(r'(\d{2})/(\d{2})/(\d{4})\s+EURO', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.11 - DISBER: Fecha de factura: DD/MM/YYYY
    if 'DISBER' in proveedor_upper or 'B46144424' in texto:
        patron = re.search(r'Fecha de factura:\s*\n?\s*(\d{2})/(\d{2})/(\d{4})', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.12 - TRUCCO: Fecha: DD/MM/YYYY
    if 'TRUCCO' in proveedor_upper or 'ISAAC RODRIGUEZ' in proveedor_upper or '05247386M' in texto:
        patron = re.search(r'Fecha:\s*(\d{2})/(\d{2})/(\d{4})', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.12/v3.14 - LA BARRA DULCE: Fecha DD.MM.YYYY (después del CIF)
    if 'BARRA DULCE' in proveedor_upper or 'B19981141' in texto:
        # v3.14: El texto extraído tiene formato "CIF: B19981141 30.11.2025"
        patron = re.search(r'B19981141\s+(\d{2})\.(\d{2})\.(\d{4})', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.12 - GRUPO TERRITORIO CAMPERO: "31 de Marzo del 2025"
    if 'CAMPERO' in proveedor_upper or 'TERRITORIO' in proveedor_upper or 'B16690141' in texto:
        meses = {'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
                 'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
                 'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'}
        patron = re.search(r'(\d{1,2})\s+de\s+(\w+)\s+del?\s+(\d{4})', texto, re.IGNORECASE)
        if patron:
            d, mes_texto, y = patron.groups()
            m = meses.get(mes_texto.lower(), '00')
            return f"{d.zfill(2)}-{m}-{y[-2:]}"
    
    # v3.12 - ZUBELZU: Fecha DD/MM/YY en cabecera
    if 'ZUBELZU' in proveedor_upper or 'B75079608' in texto:
        patron = re.search(r'B87760575\s+(\d{2})/(\d{2})/(\d{2})', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y}"
    
    # v3.13 - PRODUCTOS ADELL: "Fecha: 07/04/2025" o "07/04/2025" después de Nº Factura
    if 'ADELL' in proveedor_upper or 'CROQUELLANAS' in proveedor_upper or 'B12711636' in texto:
        patron = re.search(r'Fecha[:\s]*(\d{2})/(\d{2})/(\d{4})', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.13 - ECOFICUS: "Fecha: 04/06/2025"
    if 'ECOFICUS' in proveedor_upper or 'B10214021' in texto:
        patron = re.search(r'Fecha:\s*(\d{2})/(\d{2})/(\d{4})', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.13 - QUESOS ROYCA: "FECHA: 31/05/2025"
    if 'ROYCA' in proveedor_upper or 'E06388631' in texto:
        patron = re.search(r'FECHA:\s*(\d{2})/(\d{2})/(\d{4})', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.13 - IBARRAKO PIPARRAK: "EGUNA / FECHA" seguido de fecha, o "Fecha Factura: DD/MM/YYYY"
    if 'IBARRAKO' in proveedor_upper or 'F20532297' in texto:
        # Formato nuevo: "20/5/2025" en cabecera
        patron = re.search(r'EGUNA\s*/\s*FECHA\s*\n?\s*(\d{1,2})/(\d{1,2})/(\d{4})', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d.zfill(2)}-{m.zfill(2)}-{y[-2:]}"
        # Formato antiguo
        patron = re.search(r'Fecha Factura:\s*(\d{2})/(\d{2})/(\d{4})', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.13 - ANA CABALLO: "Fecha: 18-09-2025"
    if 'ANA CABALLO' in proveedor_upper or 'B87925970' in texto:
        patron = re.search(r'Fecha:\s*(\d{2})-(\d{2})-(\d{4})', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.13 - MARTIN ABENZA: "Fecha Factura: DD/MM/YYYY"
    if 'MARTIN' in proveedor_upper and ('ABENZA' in proveedor_upper or 'ARBENZA' in proveedor_upper) or 'MODESTO' in proveedor_upper or '74305431K' in texto:
        patron = re.search(r'Fecha Factura:\s*(\d{2})/(\d{2})/(\d{4})', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.16 - PORVAZ: "Fecha: DD-MM-YYYY" 
    if 'PORVAZ' in proveedor_upper or 'TITO' in proveedor_upper or 'B36281087' in texto:
        patron = re.search(r'Fecha:\s*(\d{2})-(\d{2})-(\d{4})', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.22 - LA PURISIMA: "Fecha factura: 31/03/2025"
    if 'PURISIMA' in proveedor_upper or 'PURÍSIMA' in proveedor_upper or 'F30005193' in texto:
        patron = re.search(r'Fecha\s+factura:\s*(\d{2})/(\d{2})/(\d{4})', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.20 - QUESOS FELIX / ARMANDO SANZ
    # PyPDF2 extrae: "25 0014827/03/2025" (año + número + fecha SIN ESPACIO)
    # El orden está INVERTIDO respecto al visual del PDF
    if 'FELIX' in proveedor_upper or 'ARMANDO SANZ' in proveedor_upper or 'B47440136' in texto or 'B 47.440.136' in texto or 'B47.440.136' in texto:
        # Patrón: NN NNNNN[N]DD/MM/YYYY (número pegado a fecha, sin espacio)
        patron = re.search(r'\d{2}\s+\d{5,6}(\d{2})/(\d{2})/(\d{4})', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.16 - CARLOS NAVAS / QUESOS NAVAS
    # Formato PDF: "A/5 ... 02/01/2025 Fecha Referencia"
    # La fecha está ANTES de la palabra "Fecha"
    if 'NAVAS' in proveedor_upper or 'B37416419' in texto:
        # Buscar DD/MM/YYYY seguido de "Fecha" (la fecha está antes de la etiqueta)
        patron = re.search(r'(\d{2})/(\d{2})/(\d{4})\s*\n?\s*Fecha', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
        # Alternativa: cualquier fecha DD/MM/YYYY después de A/N
        patron2 = re.search(r'A/\d+.*?(\d{2})/(\d{2})/(\d{4})', texto, re.DOTALL)
        if patron2:
            d, m, y = patron2.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.16 - SOM ENERGIA: "Fecha de la factura: DD/MM/YYYY"
    if 'SOM ENERGIA' in proveedor_upper or 'F55091367' in texto:
        patron = re.search(r'Fecha de la factura:\s*(\d{2})/(\d{2})/(\d{4})', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.19 - ZUCCA / FORMAGGIARTE: "MADRID 1 000034 1 31/01/2025"
    if 'ZUCCA' in proveedor_upper or 'FORMAGGIARTE' in proveedor_upper or 'B42861948' in texto:
        patron = re.search(r'MADRID\s+\d+\s+\d{6}\s+\d+\s+(\d{2})/(\d{2})/(\d{4})', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.19 - EMJAMESA: "FECHA 15/01/2025" (después de CLIENTE)
    if 'EMJAMESA' in proveedor_upper or 'B37352077' in texto:
        patron = re.search(r'FECHA\s*(\d{2})/(\d{2})/(\d{4})', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.19 - FABEIRO: "31-01-2025" después de Nº Factura
    if 'FABEIRO' in proveedor_upper or 'B79992079' in texto or 'B-79/992079' in texto:
        patron = re.search(r'Fecha Factura.*?(\d{2})-(\d{2})-(\d{4})', texto, re.DOTALL)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
        # Alternativa: buscar patrón DD-MM-YYYY después de número de factura
        patron2 = re.search(r'\d{2}\s*-\s*\d+\s+(\d{2})-(\d{2})-(\d{4})', texto)
        if patron2:
            d, m, y = patron2.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.19 - CVNE: "21/01/2025" después de Nº factura
    if 'CVNE' in proveedor_upper or 'VINICOLA DEL NORTE' in texto or 'A48002893' in texto:
        patron = re.search(r'Nº factura.*?(\d{2})/(\d{2})/(\d{4})', texto, re.DOTALL)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
        # Alternativa: buscar fecha después del número XX-XX-XXXXXX
        patron2 = re.search(r'\d{2}-\d{2}-\d{6}\s+(\d{2})/(\d{2})/(\d{4})', texto)
        if patron2:
            d, m, y = patron2.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.19 - SEGURMA: "Fecha de factura: 01/02/2025"
    if 'SEGURMA' in proveedor_upper or 'A48198626' in texto:
        patron = re.search(r'Fecha de factura:\s*(\d{2})/(\d{2})/(\d{4})', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.23 - AMAZON: "Fecha de la factura/Fecha de la entrega 28.03.2025" (formato DD.MM.YYYY)
    if 'AMAZON' in proveedor_upper or 'W0184081H' in texto or 'LU20260743' in texto:
        patron = re.search(r'Fecha de la factura.*?(\d{2})\.(\d{2})\.(\d{4})', texto, re.DOTALL)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.23 - CONTROLPLAGA: "Madrid, 20 DE noviembre DE 2025"
    if 'CONTROLPLAGA' in proveedor_upper or 'ALBORES' in proveedor_upper or 'ARBORES' in proveedor_upper or '11812266' in texto:
        meses = {'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
                 'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
                 'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'}
        patron = re.search(r'Madrid,\s*(\d{1,2})\s+DE\s+(\w+)\s+DE\s+(\d{4})', texto, re.IGNORECASE)
        if patron:
            d, mes_texto, y = patron.groups()
            m = meses.get(mes_texto.lower(), '00')
            return f"{int(d):02d}-{m}-{y[-2:]}"
    
    # v3.23 - PANRUJE: "24/11/2025" en campo FECHA (después de FT XXX)
    if 'PANRUJE' in proveedor_upper or 'ERMITA' in proveedor_upper or 'B13858014' in texto or 'B-13.858.014' in texto:
        # Buscar fecha después de FT XXX
        patron = re.search(r'FT\s+\d+\s+(\d{2})/(\d{2})/(\d{4})', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.23 - ANGEL Y LOLI: fecha al final de línea con NÚMERO (XXXXXX 1 DD/MM/YYYY)
    if 'ANGEL' in proveedor_upper or 'LOLI' in proveedor_upper or 'ALFARERIA' in proveedor_upper or '75727068' in texto:
        patron = re.search(r'\d{6}\s+\d+\s+(\d{2})/(\d{2})/(\d{4})', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.23 - QUESOS DEL CATI: "Fecha: 03/12/2025"
    if 'CATI' in proveedor_upper or 'F12499455' in texto or 'F-12499455' in texto:
        patron = re.search(r'Fecha[:\s]+(\d{2})/(\d{2})/(\d{4})', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.24 - ISTA: fecha después del Nº Recibo (XXXXXXXX/XX\nDD/MM/YYYY)
    if 'ISTA' in proveedor_upper or 'A50090133' in texto:
        patron = re.search(r'\d{8}/\d{2}\s*\n\s*(\d{2})/(\d{2})/(\d{4})\s*\n', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.24 - BIELLEBI: fecha después de "FATTURA XX / V / XXXX"
    if 'BIELLEBI' in proveedor_upper or '06089700725' in texto:
        patron = re.search(r'FATTURA\s+\d+\s*/\s*V\s*/\s*\d{4}\s+(\d{2})/(\d{2})/(\d{4})', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.24 - FERRIOL: "10/03/25" después de REF
    if 'FERRIOL' in proveedor_upper or 'B57955098' in texto:
        patron = re.search(r'\d{2}/\d{4}\s+(\d{2})/(\d{2})/(\d{2})', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y}"
    
    # v3.24 - ABBATI CAFFE: "30/11/2024"
    if 'ABBATI' in proveedor_upper or 'B82567876' in texto:
        patron = re.search(r'(\d{2})/(\d{2})/(\d{4})', texto)
        if patron:
            d, m, y = patron.groups()
            return f"{d}-{m}-{y[-2:]}"
    
    # v3.24 - BODEGAS MUÑOZ MARTÍN: "03/04/2024"
    if 'MUÑOZ' in proveedor_upper or 'MUNOZ' in proveedor_upper or 'E83182683' in texto or 'E-83182683' in texto:
        patron = re.search(r'(\d{2})/(\d{2})/(\d{4})', texto)
        if patron:
            d, m, y = patron.groups()
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
    
    # ZUCCA/FORMAGGIARTE: "Factura 1 000407" (DOCUMENTO + NUMERO)
    if 'ZUCCA' in proveedor_upper or 'FORMAGGIARTE' in proveedor_upper or 'B42861948' in texto:
        patron = re.compile(r'Factura\s+(\d+)\s+(\d{6})', re.IGNORECASE)
        match = patron.search(texto)
        if match:
            return f"{match.group(1)}-{match.group(2)}"
    
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
    
    # DISTRIBUCIONES LAVAPIES: "Nº DOCUMENTO" + "DD/MM/YY NNNNNN"
    if 'LAVAPIES' in proveedor_upper and 'PANIFIESTO' not in proveedor_upper or 'F88424072' in texto:
        # Formato: "04/12/25 251131" después de "Nº DOCUMENTO"
        patron = re.compile(r'\d{2}/\d{2}/\d{2}\s+(\d{5,6})\s')
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
    
    # v3.20 - SABORES DE PATERNA: "NºA 131363" (A + espacio + 6 dígitos)
    if 'PATERNA' in proveedor_upper or 'SABORES' in proveedor_upper:
        patron = re.search(r'NºA\s*(\d{6})', texto)
        if patron:
            return 'A' + patron.group(1)  # Formato: "A131363"
    
    # v3.20 - MOLLETES ARTESANOS: "G 2733" después de FECHA DD/MM/YYYY
    if 'MOLLETES' in proveedor_upper or 'ANTEQUERA' in proveedor_upper or 'B93662708' in texto:
        # Patrón: FECHA + newline + DD/MM/YYYY + newline + G NNNN
        patron = re.search(r'FECHA\s*\n\s*\d{2}/\d{2}/\d{4}\s*\n\s*(G\s*\d{4})', texto)
        if patron:
            return patron.group(1)  # Formato: "G 2733"
    
    # v3.20 - PRODUCTOS ADELL / CROQUELLANAS: "A/328" al inicio del texto
    if 'ADELL' in proveedor_upper or 'CROQUELLANAS' in proveedor_upper or 'B12711636' in texto or 'B-12711636' in texto:
        # Patrón: A/N o A/NN o A/NNN al inicio
        patron = re.search(r'^(A/\d+)', texto)
        if patron:
            return patron.group(1)  # Formato: "A/328"
    
    # EMJAMESA: Número tras Factura
    if 'EMJAMESA' in proveedor_upper:
        patron = re.compile(r'Factura[:\s]*([A-Z]?\d+)', re.IGNORECASE)
        match = patron.search(texto)
        if match:
            return match.group(1)
    
    # v3.20 - KINEMA: "1 002003 1 26/09/2025" (número + página + fecha)
    # REF formato: "1 NNNNNN"
    if 'KINEMA' in proveedor_upper or 'F84600022' in texto:
        # Patrón: 1 + espacio + 6 dígitos + espacio + 1 + espacio + fecha
        patron = re.search(r'(\d\s+\d{6})\s+\d+\s+\d{2}/\d{2}/\d{4}', texto)
        if patron:
            return patron.group(1)  # Formato: "1 002003"
    
    # v3.20 - XFERA/YOIGO: "YC250001983027" (YC + 12 dígitos)
    if 'XFERA' in proveedor_upper or 'YOIGO' in proveedor_upper or 'A82528548' in texto:
        patron = re.search(r'(YC\d{12})', texto)
        if patron:
            return patron.group(1)  # Formato: "YC250001983027"
    
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
    
    # v3.11 - MRM: ALBARÁN / FACTURA 1-2025 -9.495
    if 'MRM' in proveedor_upper or 'A80280845' in texto:
        patron = re.search(r'ALBARÁN\s*/\s*FACTURA\s+([\d-]+\s*-[\d.]+)', texto)
        if patron:
            return patron.group(1).replace(' ', '')
    
    # v3.11 - DISBER: Factura FCVD250100023
    if 'DISBER' in proveedor_upper or 'B46144424' in texto:
        patron = re.search(r'Factura\s*\n?\s*(FCVD\d+)', texto)
        if patron:
            return patron.group(1)
    
    # v3.12 - TRUCCO: Número de factura: 2025-3928
    if 'TRUCCO' in proveedor_upper or 'ISAAC RODRIGUEZ' in proveedor_upper or '05247386M' in texto:
        patron = re.search(r'N[úu]mero de factura:\s*(\d{4}-\d+)', texto)
        if patron:
            return patron.group(1)
    
    # v3.12 - LA BARRA DULCE: Nº factura después del teléfono
    if 'BARRA DULCE' in proveedor_upper or 'B19981141' in texto:
        # El nº factura está en: "Teléfono: 91 846 83 85 530"
        patron = re.search(r'91 846 83 85\s+(\d+)', texto)
        if patron:
            return patron.group(1)
    
    # v3.12 - GRUPO TERRITORIO CAMPERO: NÚMERO DE FACTURA: 99220
    if 'CAMPERO' in proveedor_upper or 'TERRITORIO' in proveedor_upper or 'B16690141' in texto:
        patron = re.search(r'N[ÚU]MERO DE FACTURA:\s*(\d+)', texto)
        if patron:
            return patron.group(1)
    
    # v3.12 - ZUBELZU: Nº FACTURA A 51.993
    if 'ZUBELZU' in proveedor_upper or 'B75079608' in texto:
        patron = re.search(r'[A-Z]\s+(\d{2}\.\d{3})', texto)
        if patron:
            return patron.group(1)
    
    # v3.13 - PRODUCTOS ADELL: "Nº Factura A/328"
    if 'ADELL' in proveedor_upper or 'CROQUELLANAS' in proveedor_upper or 'B12711636' in texto:
        patron = re.search(r'N[ºo°]\s*Factura\s*\n?\s*(A/\d+)', texto, re.IGNORECASE)
        if patron:
            return patron.group(1)
    
    # v3.13 - ECOFICUS: "Número: F25/0000109"
    if 'ECOFICUS' in proveedor_upper or 'B10214021' in texto:
        patron = re.search(r'N[úu]mero:\s*(F\d+/\d+)', texto)
        if patron:
            return patron.group(1)
    
    # v3.13 - QUESOS ROYCA: "Nº FACTURA: 1 /252164"
    if 'ROYCA' in proveedor_upper or 'E06388631' in texto:
        patron = re.search(r'N[ºo°]\s*FACTURA:\s*(\d+\s*/\s*\d+)', texto)
        if patron:
            return patron.group(1).replace(' ', '')
    
    # v3.13 - IBARRAKO PIPARRAK: "FRA. ZENB. / NUM. FRA. FV24-0240" o "Nº FACTURA 11.942.488"
    if 'IBARRAKO' in proveedor_upper or 'F20532297' in texto:
        patron = re.search(r'FRA\.\s*ZENB\.\s*/\s*NUM\.\s*FRA\.\s*\n?\s*(FV\d+-\d+)', texto)
        if patron:
            return patron.group(1)
        patron = re.search(r'N[ºo°]\s*FACTURA\s+(\d+[\.\d]*)', texto)
        if patron:
            return patron.group(1)
    
    # v3.13 - ANA CABALLO: "Factura FAC2025A234"
    if 'ANA CABALLO' in proveedor_upper or 'B87925970' in texto:
        patron = re.search(r'Factura\s+(FAC\d+[A-Z]*\d*)', texto)
        if patron:
            return patron.group(1)
    
    # v3.20 - MARTIN ABENZA: "Número de Factura: ... \n 543/25"
    # El número está en la línea siguiente después de los headers
    if 'MARTIN' in proveedor_upper and ('ABENZA' in proveedor_upper or 'ARBENZA' in proveedor_upper) or 'MODESTO' in proveedor_upper or '74305431K' in texto:
        patron = re.search(r'N[úu]mero de Factura:.*?(\d+/\d+)', texto, re.DOTALL)
        if patron:
            return patron.group(1)
    
    # v3.16 - PORVAZ: "Número: 0454/25"
    if 'PORVAZ' in proveedor_upper or 'TITO' in proveedor_upper or 'B36281087' in texto:
        patron = re.search(r'N[úu]mero:\s*(\d+/\d+)', texto)
        if patron:
            return patron.group(1)
    
    # v3.22 - LA PURISIMA: "Número factura: 24−00−483" (guiones Unicode EN DASH)
    # También "Número factura: 25-00-107" con guiones normales
    if 'PURISIMA' in proveedor_upper or 'PURÍSIMA' in proveedor_upper or 'F30005193' in texto:
        # Patrón con guiones Unicode (−) o normales (-)
        patron = re.search(r'N[úu]mero\s+factura:\s*(\d{2})[−-](\d{2})[−-](\d+)', texto)
        if patron:
            año, serie, num = patron.groups()
            return f"{año}-{serie}-{num}"  # Normalizar a guiones normales
    
    # v3.20 - QUESOS FELIX / ARMANDO SANZ
    # PyPDF2 extrae: "25 0014827/03/2025" (año + número + fecha SIN ESPACIO)
    # REF: "25-00148"
    if 'FELIX' in proveedor_upper or 'ARMANDO SANZ' in proveedor_upper or 'B47440136' in texto or 'B 47.440.136' in texto or 'B47.440.136' in texto:
        patron = re.search(r'(\d{2})\s+(\d{5,6})\d{2}/\d{2}/\d{4}', texto)
        if patron:
            año, num = patron.groups()
            return f"{año}-{num}"  # Formato: "25-00148"
    
    # v3.16 - CARLOS NAVAS / QUESOS NAVAS: "Nº Factura A/598"
    # Formato: A/NNN donde NNN es el número de factura
    if 'NAVAS' in proveedor_upper or 'B37416419' in texto:
        patron = re.search(r'(A/\d+)', texto)
        if patron:
            return patron.group(1)  # Formato: "A/598"
    
    # v3.16 - SOM ENERGIA: "N.º de factura:FE2501314182"
    if 'SOM ENERGIA' in proveedor_upper or 'F55091367' in texto:
        patron = re.search(r'N\.º de factura:\s*(FE\d+)', texto)
        if patron:
            return patron.group(1)
    
    # v3.19 - ZUCCA / FORMAGGIARTE: "MADRID 1 000034 1 31/01/2025"
    # Serie + Número (6 dígitos) -> REF: "1-000034"
    if 'ZUCCA' in proveedor_upper or 'FORMAGGIARTE' in proveedor_upper or 'B42861948' in texto:
        patron = re.search(r'MADRID\s+(\d+)\s+(\d{6})\s+\d+\s+\d{2}/\d{2}/\d{4}', texto)
        if patron:
            serie, num = patron.groups()
            return f"{serie}-{num}"
    
    # v3.19 - EMJAMESA: "002500014 V //" -> REF: "V/002500014"
    if 'EMJAMESA' in proveedor_upper or 'B37352077' in texto:
        patron = re.search(r'(\d{9,})\s+([A-Z])\s*//', texto)
        if patron:
            num, serie = patron.groups()
            return f"{serie}/{num}"
    
    # v3.19 - FABEIRO: "25 - 782" después de "Nº Factura"
    if 'FABEIRO' in proveedor_upper or 'B79992079' in texto or 'B-79/992079' in texto:
        patron = re.search(r'Nº Factura.*?(\d{2}\s*-\s*\d+)', texto, re.DOTALL)
        if patron:
            return patron.group(1).replace(' ', '')
    
    # v3.19 - CVNE: "25-40-011293"
    if 'CVNE' in proveedor_upper or 'VINICOLA DEL NORTE' in texto or 'A48002893' in texto:
        patron = re.search(r'(\d{2}-\d{2}-\d{6})', texto)
        if patron:
            return patron.group(1)
    
    # v3.19 - SEGURMA: "Factura C/2025/02/025378"
    if 'SEGURMA' in proveedor_upper or 'A48198626' in texto:
        patron = re.search(r'Factura\s+(C/\d{4}/\d{2}/\d+)', texto)
        if patron:
            return patron.group(1)
    
    # v3.23 - AMAZON: "Número de la factura DS-AEU-INV-ES-2025-30149915"
    if 'AMAZON' in proveedor_upper or 'W0184081H' in texto or 'LU20260743' in texto:
        patron = re.search(r'N[úu]mero de la factura\s+(DS-[A-Z]+-INV-[A-Z]+-\d{4}-\d+)', texto)
        if patron:
            return patron.group(1)
        # Alternativa: Nº de referencia de pago (alfanumérico)
        patron2 = re.search(r'N[ºo°] de referencia de pago\s+([A-Z0-9]+)', texto)
        if patron2:
            return patron2.group(1)
    
    # v3.23 - BENJAMIN ORTEGA / JAIME FERNANDEZ (alquileres): REF = mes de la factura
    # La REF se extrae de la fecha (mes), pero primero intentamos buscar un número de factura
    if 'BENJAMIN ORTEGA' in proveedor_upper or 'ORTEGA ALONSO' in proveedor_upper or '09342596L' in texto:
        # Buscar número de factura o mes
        patron = re.search(r'(?:Factura|FACTURA)[:\s]*[Nn]?[ºo°]?\s*(\d{1,4})', texto)
        if patron:
            return patron.group(1)
    
    if 'JAIME FERNANDEZ' in proveedor_upper or 'FERNANDEZ MORENO' in proveedor_upper or '07219971H' in texto:
        # Buscar número de factura o mes
        patron = re.search(r'(?:Factura|FACTURA)[:\s]*[Nn]?[ºo°]?\s*(\d{1,4})', texto)
        if patron:
            return patron.group(1)
    
    # v3.23 - CONTROLPLAGA / JAVIER ALBORES: "Nº factura 20250410"
    if 'CONTROLPLAGA' in proveedor_upper or 'ALBORES' in proveedor_upper or 'ARBORES' in proveedor_upper or '11812266' in texto:
        patron = re.search(r'N[ºo°]\s*factura\s+(\d+)', texto, re.IGNORECASE)
        if patron:
            return patron.group(1)
    
    # v3.23 - PANRUJE: "FT    183" en Nº DOCUMENTO
    if 'PANRUJE' in proveedor_upper or 'ERMITA' in proveedor_upper or 'B13858014' in texto or 'B-13.858.014' in texto:
        patron = re.search(r'(FT\s+\d+)', texto)
        if patron:
            return patron.group(1).replace('  ', ' ')  # Normalizar espacios
    
    # v3.23 - ANGEL Y LOLI: "000064" (6 dígitos) en campo NÚMERO
    if 'ANGEL' in proveedor_upper or 'LOLI' in proveedor_upper or 'ALFARERIA' in proveedor_upper or '75727068' in texto:
        patron = re.search(r'(\d{6})\s+\d+\s+\d{2}/\d{2}/\d{4}', texto)
        if patron:
            return patron.group(1).lstrip('0') or '0'  # Quitar ceros a la izquierda
    
    # v3.23 - QUESOS DEL CATI: "Número FRA: 4118"
    if 'CATI' in proveedor_upper or 'F12499455' in texto or 'F-12499455' in texto:
        patron = re.search(r'N[úu]mero\s+FRA[:\s]+(\d+)', texto, re.IGNORECASE)
        if patron:
            return patron.group(1)
    
    # v3.24 - ISTA: "Nº Recibo: 30512924/25"
    if 'ISTA' in proveedor_upper or 'A50090133' in texto:
        patron = re.search(r'(\d{8}/\d{2})', texto)
        if patron:
            return patron.group(1)
    
    # v3.24 - BIELLEBI: "FATTURA 48 / V / 2025"
    if 'BIELLEBI' in proveedor_upper or '06089700725' in texto:
        patron = re.search(r'FATTURA\s+(\d+\s*/\s*V\s*/\s*\d{4})', texto)
        if patron:
            return patron.group(1)
    
    # v3.24 - FERRIOL: "25/0186" después de "Nº Factura"
    if 'FERRIOL' in proveedor_upper or 'B57955098' in texto:
        patron = re.search(r'(\d{2}/\d{4})\s+\d{2}/\d{2}/\d{2}', texto)
        if patron:
            return patron.group(1)
    
    # v3.24 - ABBATI CAFFE: "1013421" o "1/ 013421"
    if 'ABBATI' in proveedor_upper or 'B82567876' in texto:
        patron = re.search(r'(\d)\s*(\d{6})', texto)
        if patron:
            return patron.group(1) + patron.group(2)
    
    # v3.24 - BODEGAS MUÑOZ MARTÍN: "24F00100"
    if 'MUÑOZ' in proveedor_upper or 'MUNOZ' in proveedor_upper or 'E83182683' in texto or 'E-83182683' in texto:
        patron = re.search(r'(\d{2}F\d{5})', texto)
        if patron:
            return patron.group(1)
    
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
    """Extrae el total de la factura - v3.29 con SEGURMA y MRM."""
    
    # Patrones ordenados de más específico a más genérico
    # IMPORTANTE: Evitar patrones que capturen precios unitarios o cantidades
    patrones = [
        # Patrón 1: TOTAL FACTURA / TOTAL IMPORTE / TOTAL FACT (muy específico)
        r'(?:TOTAL\s*FACTURA|TOTAL\s*IMPORTE|TOTAL\s*FACT|Total\s*Factura)[:\s]*(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*€?',
        # Patrón 2: TOTAL A PAGAR (común en tickets)
        r'TOTAL\s*A\s*PAGAR[:\s]*(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*€?',
        # Patrón 3: TOTAL COMPRA (BM, supermercados)
        r'TOTAL\s*COMPRA[^0-9]*(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})',
        # Patrón 4: TOTAL con € inmediatamente después (sin texto intermedio)
        r'TOTAL[:\s]+(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*€',
        # Patrón 5: Importe Total (con T mayúscula)
        r'Importe\s*Total[:\s]*(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*€?',
        # v3.29 - Patrón 5b: Importe Líquido (MRM)
        r'(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*€?\s*Importe\s*L[íi]quido',
        r'Importe\s*L[íi]quido\s*:?\s*(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*€?',
        # Patrón 6: XX,XX € en línea que termina con TOTAL
        r'(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*€\s*$.*TOTAL',
        # Patrón 7: SUMA TOTAL
        r'SUMA\s*TOTAL[:\s]*(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*€?',
        # Patrón 8: NETO A PAGAR / LIQUIDO A PAGAR
        r'(?:NETO|LIQUIDO|LÍQUIDO)\s*A\s*PAGAR[:\s]*(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*€?',
        # Patrón 9: T O T A L (espaciado)
        r'T\s*O\s*T\s*A\s*L[:\s]*(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*€?',
        # v3.29 - Patrón 10: Total XX,XX € (SEGURMA - "Total 48,23 €")
        r'\bTotal\s+(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*€',
    ]
    
    for patron_str in patrones:
        patron = re.compile(patron_str, re.IGNORECASE | re.MULTILINE)
        match = patron.search(texto)
        if match:
            total_str = match.group(1)
            # Convertir formato europeo (1.234,56 → 1234.56)
            if ',' in total_str and '.' in total_str:
                total_str = total_str.replace(".", "").replace(",", ".")
            elif ',' in total_str:
                total_str = total_str.replace(",", ".")
            try:
                valor = float(total_str)
                # Validación: el total debe ser razonable (> 1€)
                if valor > 1.0:
                    return valor
            except:
                continue
    
    return None


def validar_cuadre(lineas: List, total_factura: Optional[float], tolerancia: float = 0.05) -> str:
    """
    Valida que la suma de líneas + IVA cuadre con el total de la factura.
    
    v3.21 - Validación de cuadre para detectar líneas faltantes.
    
    Args:
        lineas: Lista de líneas extraídas (cada una con 'base' e 'iva')
        total_factura: Total extraído de la factura
        tolerancia: Diferencia máxima permitida (default 0.05€)
    
    Returns:
        str: 'OK' si cuadra, 'DESCUADRE: ±X.XX€', 'SIN_TOTAL', o 'SIN_LINEAS'
    """
    if not lineas:
        return 'SIN_LINEAS'
    
    if total_factura is None or total_factura == 0:
        return 'SIN_TOTAL'
    
    # Calcular suma de bases + IVAs
    suma_bases = 0.0
    suma_ivas = 0.0
    
    for linea in lineas:
        base = linea.get('base', 0) or 0
        iva_pct = linea.get('iva', 0) or 0
        
        suma_bases += base
        suma_ivas += base * (iva_pct / 100.0)
    
    total_calculado = suma_bases + suma_ivas
    diferencia = total_factura - total_calculado
    
    # Comprobar si cuadra dentro de la tolerancia
    if abs(diferencia) <= tolerancia:
        return 'OK'
    else:
        # Mostrar diferencia con signo
        signo = '+' if diferencia > 0 else ''
        return f'DESCUADRE: {signo}{diferencia:.2f}€'


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
    """Extrae líneas de facturas FRANCISCO GUERRA.
    
    Formato: CODIGO DESCRIPCION CANTIDAD TOTAL PRECIO_UD
    Ejemplo: 00192 CHUPADEO ZAMBUDIO      4         84,28     21,070
    
    NOTA: El TOTAL de cada línea YA ES LA BASE (sin IVA).
    El precio unitario tiene 3 decimales (21,070).
    """
    lineas = []
    
    # Patrón mejorado: permite minúsculas y más caracteres en descripción
    # Requiere al menos 2 espacios entre descripción y cantidad
    patron = re.compile(
        r'^(\d{3,5})\s+'                    # Código (3-5 dígitos)
        r'(.+?)\s{2,}'                       # Descripción (seguido de 2+ espacios)
        r'(\d+)\s+'                          # Cantidad
        r'(\d+[,\.]\d{2})\s+'               # Total línea = BASE (2 decimales)
        r'(\d+[,\.]\d{2,3})$',              # Precio unitario (2-3 decimales)
        re.MULTILINE
    )
    
    for match in patron.finditer(texto):
        codigo, articulo, cantidad, importe, precio = match.groups()
        articulo_limpio = articulo.strip()
        
        # Ignorar líneas de albarán o cabeceras
        if any(x in articulo_limpio for x in ['Albarán', 'ALBARAN', 'Descripción', 'DESCRIPCIÓN']):
            continue
            
        lineas.append({
            'codigo': codigo,
            'articulo': articulo_limpio,
            'iva': 10,  # Francisco Guerra siempre 10%
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
    """Extrae líneas de facturas QUESOS NAVAS - v3.20.
    
    Formato PyPDF extraído (todo pegado en orden diferente):
    6,0055 QUESO GRAN RESERVA 10 MESES 18,170 4,00 109,118524
    11,3906 QUESO OVEJA INVIERNO 2 AÑOS 26,370 4,00 300,3518823
    
    Es: CANTIDAD + CODIGO (pegados) + ARTICULO + PRECIO + IVA + SUBTOTAL + LOTE (pegados)
    - CANTIDAD: N,NNN o NN,NNN (con 3 decimales, kg)
    - CODIGO: 1-2 dígitos (5, 6, 17, etc.)
    - ARTICULO: texto (QUESO...)
    - PRECIO: NN,NNN (con 3 decimales)
    - IVA: N,NN (típico 4,00 o 2,00)
    - SUBTOTAL: NNN,NN
    - LOTE: 4-5 dígitos (pegado al subtotal)
    """
    lineas = []
    
    # Patrón v3.20: CANTIDAD(N,NNN) + CODIGO(N o NN) pegados, luego ARTICULO, PRECIO, IVA, SUBTOTAL+LOTE
    # Ej: "6,0055" = cantidad 6,005 + codigo 5
    # Ej: "11,3906" = cantidad 11,390 + codigo 6
    patron = re.compile(
        r'(\d{1,2}[,\.]\d{3})'       # Cantidad (kg con 3 decimales) - ej: 6,005 o 11,390
        r'(\d{1,2})\s+'              # Código (1-2 dígitos) - ej: 5 o 6 o 17
        r'(QUESO[A-ZÑÁÉÍÓÚ\s\d]+?)\s+'     # Artículo (empieza con QUESO, incluye acentos)
        r'(\d+[,\.]\d{3})\s+'        # Precio (con 3 decimales) - ej: 18,170
        r'(\d+[,\.]\d{2})\s+'        # IVA (con 2 decimales) - ej: 4,00
        r'(\d+[,\.]\d{2})'           # Subtotal - ej: 109,11
        r'(\d{3,5})?',               # Lote opcional (pegado) - ej: 8524
        re.MULTILINE
    )
    
    for match in patron.finditer(texto):
        cantidad, codigo, articulo, precio, iva, subtotal, lote = match.groups()
        articulo_limpio = articulo.strip()
        
        # Detectar IVA real del texto (puede ser 4% o 2%)
        iva_valor = int(float(iva.replace(',', '.')))
            
        lineas.append({
            'codigo': codigo,
            'articulo': articulo_limpio,
            'cantidad': float(cantidad.replace(',', '.')),
            'precio_unitario': float(precio.replace(',', '.')),
            'iva': iva_valor,
            'base': float(subtotal.replace(',', '.')),
            'categoria': 'QUESOS'
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
    """Extrae líneas de facturas BM SUPERMERCADOS (tickets).
    
    ESTRATEGIA v3.26b: Los tickets BM incluyen un desglose fiscal al final:
        Tipo    Base    Iva    Req   Total
        10.00%  24.61   2.46   0.00  27.07
        4.00%   1.00    0.04   0.00  1.04
    
    Extraemos las BASES IMPONIBLES directamente del desglose, no de los productos.
    Esto garantiza cuadre perfecto.
    """
    lineas = []
    
    # Patrón para extraer el desglose fiscal:
    # 10.00%  24.61   2.46   0.00  27.07
    # 4.00%   1.00    0.04   0.00  1.04
    # 21.00%  0.55    0.11   0.00  0.66
    patron_desglose = re.compile(
        r'^\s*(\d+)[,\.](\d{2})%\s+'  # Tipo IVA (10.00%, 4.00%, 21.00%)
        r'(\d+[,\.]\d{2})\s+'          # Base
        r'(\d+[,\.]\d{2})\s+'          # IVA
        r'(\d+[,\.]\d{2})\s+'          # Req (recargo equivalencia)
        r'(\d+[,\.]\d{2})',            # Total
        re.MULTILINE
    )
    
    # Buscar todas las líneas de desglose
    for match in patron_desglose.finditer(texto):
        iva_entero = int(match.group(1))
        iva_decimal = int(match.group(2))
        base_str = match.group(3)
        
        # Calcular IVA real
        iva = iva_entero + iva_decimal / 100.0
        if iva_decimal == 0:
            iva = iva_entero  # 10.00% -> 10, 4.00% -> 4
        
        # Convertir base
        base = float(base_str.replace(',', '.'))
        
        # Solo añadir si la base es > 0
        if base > 0:
            # Descripción genérica según tipo IVA
            if iva == 4 or iva == 4.0:
                descripcion = "PRODUCTOS IVA SUPERREDUCIDO 4%"
                iva_int = 4
            elif iva == 10 or iva == 10.0:
                descripcion = "PRODUCTOS IVA REDUCIDO 10%"
                iva_int = 10
            elif iva == 21 or iva == 21.0:
                descripcion = "PRODUCTOS IVA GENERAL 21%"
                iva_int = 21
            else:
                descripcion = f"PRODUCTOS IVA {iva}%"
                iva_int = int(iva)
            
            lineas.append({
                'codigo': '',
                'articulo': descripcion,
                'iva': iva_int,
                'base': base
            })
    
    # Si no encontramos desglose, intentar método antiguo (fallback)
    if not lineas:
        lineas = extraer_lineas_bm_productos(texto)
    
    return lineas


def extraer_lineas_bm_productos(texto: str) -> List[Dict]:
    """Fallback: Extrae líneas de productos BM si no hay desglose fiscal."""
    lineas = []
    
    # Patrón para líneas con peso (cantidad precio_kg importe)
    patron_peso = re.compile(
        r'^\s*([\d,\.]+)\s+'  # Cantidad/Peso
        r'([A-Z][A-Z0-9\s\.\,\(\)/\*\-]+?)\s+'  # Descripción
        r'(\d+[,\.]\d{2})\s+'  # Precio por kg/ud
        r'(\d+[,\.]\d{2})\s*$',  # Importe PVP
        re.MULTILINE
    )
    
    # Patrón para líneas simples (cantidad descripcion importe)
    patron_simple = re.compile(
        r'^\s*(\d+)\s+'  # Cantidad entera
        r'([A-Z][A-Z0-9\s\.\,\(\)/\*\-]+?)\s+'  # Descripción
        r'(\d+[,\.]\d{2})\s*$',  # Importe PVP
        re.MULTILINE
    )
    
    def determinar_iva_bm(descripcion: str) -> int:
        """Determina el tipo de IVA según el producto en BM."""
        desc_upper = descripcion.upper()
        
        # IVA 4% - Productos básicos
        if any(x in desc_upper for x in [
            'PAN ', 'BARRA', 'HOGAZA', 'CHAPATA', 'MOLDE', 'ESPIGAS', 'CANDEAL',
            'LECHE ', 'LECHE',
            'HUEVO', 'DOCENA',
            'CALABACIN', 'ALCACHOFA', 'PLATANO', 'MANZANA', 'NARANJA', 'TOMATE',
            'PATATA', 'CEBOLLA', 'ZANAHORIA', 'LECHUGA', 'PIMIENTO',
            'QUESO', 'YOGUR',
            'HARINA', 'ARROZ', 'PASTA', 'LEGUMB', 'AZUCAR',
            'ACEITE OLIVA', 'FRUTER'
        ]):
            return 4
        
        # IVA 21% - No alimentación
        if any(x in desc_upper for x in [
            'BOLSA', 'REUTILIZABLE', 'VAJILLA', 'LIMP', 'ESTROP', 'PAÑO',
            'DETERGENTE', 'SUAVIZANTE', 'LEJIA', 'FREG',
            'PAPEL ', 'SERVILLETA', 'ROLLO',
            'PILAS', 'BOMBILLA', 'HOGAR', 'MENAJE'
        ]):
            return 21
        
        # Por defecto alimentación 10%
        return 10
    
    def calcular_base_desde_pvp(pvp: float, iva: int) -> float:
        """Calcula la base imponible desde el PVP."""
        return round(pvp / (1 + iva / 100), 2)
    
    # Extraer líneas con peso primero
    for match in patron_peso.finditer(texto):
        cantidad, descripcion, precio_ud, importe = match.groups()
        descripcion_limpia = descripcion.strip()
        
        if any(x in descripcion_limpia.upper() for x in 
               ['TOTAL', 'TARJETA', 'CUENTA', 'ACUMUL', 'TICKET', 'FACTURA', 
                'ENTREGADO', 'CAMBIO', 'AHORRO', 'PROMOCION', 'PUNTO']):
            continue
        
        pvp = float(importe.replace(',', '.'))
        iva = determinar_iva_bm(descripcion_limpia)
        base = calcular_base_desde_pvp(pvp, iva)
            
        lineas.append({
            'codigo': '',
            'articulo': descripcion_limpia,
            'iva': iva,
            'base': base
        })
    
    # Extraer líneas simples
    for match in patron_simple.finditer(texto):
        cantidad, descripcion, importe = match.groups()
        descripcion_limpia = descripcion.strip()
        
        if any(x in descripcion_limpia.upper() for x in 
               ['TOTAL', 'TARJETA', 'CUENTA', 'ACUMUL', 'TICKET', 'FACTURA',
                'ENTREGADO', 'CAMBIO', 'AHORRO', 'PROMOCION', 'PUNTO']):
            continue
        
        ya_existe = any(l['articulo'] == descripcion_limpia for l in lineas)
        if ya_existe:
            continue
        
        pvp = float(importe.replace(',', '.'))
        iva = determinar_iva_bm(descripcion_limpia)
        base = calcular_base_desde_pvp(pvp, iva)
            
        lineas.append({
            'codigo': '',
            'articulo': descripcion_limpia,
            'iva': iva,
            'base': base
        })
    
    return lineas


def extraer_lineas_molienda_verde(texto: str) -> List[Dict]:
    """Extrae líneas de facturas LA MOLIENDA VERDE S.L.U.
    
    ESTRATEGIA: Extraer las bases imponibles del desglose fiscal.
    
    El texto del PDF tiene formato pegado:
    "243,00 Euros207,27\n12,4010\n2120,73..."
    
    Donde:
    - 207,27 es la base al 10%
    - 12,40 es la base al 21% (PORTES)
    """
    lineas = []
    
    # Patrón 1: TOTAL seguido de Euros y la BASE principal (10%)
    # "243,00 Euros207,27" -> total=243,00, base10=207,27
    patron_total_base = re.compile(r'(\d+[,\.]\d{2})\s*Euros\s*(\d+[,\.]\d{2})')
    match = patron_total_base.search(texto)
    
    if match:
        base_10 = float(match.group(2).replace(',', '.'))
        if base_10 > 0:
            lineas.append({
                'codigo': '',
                'articulo': 'PRODUCTOS LA MOLIENDA VERDE (IVA 10%)',
                'iva': 10,
                'base': base_10
            })
    
    # Patrón 2: Buscar línea con PORTES que tiene IVA 21%
    # Formato: PORTES 1 PRECIO 0 21 IMPORTE (todo pegado)
    # Ej: "PORTES 112,4002112,40"
    patron_portes = re.compile(r'PORTES\s*1\s*(\d+[,\.]\d{2})\s*0?\s*21\s*(\d+[,\.]\d{2})')
    match_portes = patron_portes.search(texto)
    
    if match_portes:
        base_21 = float(match_portes.group(1).replace(',', '.'))
        if base_21 > 0:
            lineas.append({
                'codigo': '',
                'articulo': 'PORTES (IVA 21%)',
                'iva': 21,
                'base': base_21
            })
    else:
        # Alternativa: buscar base 21% en el desglose
        # El formato puede ser "12,40\n21" o similar
        patron_base21_alt = re.compile(r'(\d+[,\.]\d{2})\s*\n?\s*21\s*\n?\s*(\d+[,\.]\d{2})')
        match_21 = patron_base21_alt.search(texto)
        if match_21:
            base_21 = float(match_21.group(1).replace(',', '.'))
            if base_21 > 0 and base_21 < 100:  # Los portes suelen ser < 100€
                lineas.append({
                    'codigo': '',
                    'articulo': 'PORTES (IVA 21%)',
                    'iva': 21,
                    'base': base_21
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
    
    Formato actual: DESCRIPCION PRECIO(4dec) IMPORTE(2dec) CODIGO CANTIDAD Unidades/Kilos
    El código ahora está SEPARADO del importe (antes estaba pegado).
    
    Ejemplo: MELVA 115GR ED.LIMITADA 3,3500 40,20 M125 12 Unidades
             SARDINA AHUMADA 500GR FELISA 11,6000 81,20 FSAH500 7 Unidades
    """
    lineas = []
    
    # Patrón actualizado - código separado del importe
    patron = re.compile(
        r'^(.+?)\s+'                     # Descripción
        r'(\d+,\d{4})\s+'                # Precio (4 decimales)
        r'(\d+,\d{2})\s+'                # Importe (2 decimales) - ahora con espacio después
        r'([A-Z][A-Z0-9]*)\s+'           # Código (separado)
        r'([\d,]+)\s+'                   # Cantidad
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
    
    # Buscar TRANSPORTE (línea separada, IVA 21%)
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
    - Categoría: TELEFONO Y COMUNICACIONES
    
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
                    'base': base,
                    'categoria': 'TELEFONO Y COMUNICACIONES'
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
    - Categoría: ELECTRICIDAD
    
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
                'base': base,
                'categoria': 'ELECTRICIDAD'
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


def extraer_lineas_mrm(texto: str) -> List[Dict]:
    """Extrae líneas de facturas MRM (Industrias Cárnicas MRM-2).
    
    Formato complejo con líneas intercaladas de Lote/Cajas.
    Los productos tienen: CODIGO - DESCRIPCION con el importe al final.
    
    Estrategia: Extraer Base Imponible del desglose fiscal y crear
    una línea genérica por tipo de IVA, similar a BM Supermercados.
    
    Desglose fiscal:
    Base Imponible TOTAL : 119,05
    10,00 % IVA Reducido sobre 119,05    11,900
    """
    lineas = []
    
    # Intentar extraer productos individualmente
    # Patrón: buscar líneas con CODIGO - DESCRIPCION
    patron_prod = re.compile(
        r'(\d{3,4})\s+-\s+'              # Código (3-4 dígitos)
        r'([A-Z][A-Z0-9\s\.\,]+?)'       # Descripción
        r'\s+[UP]\s+'                     # Tipo U o P
        r'[\d,]+\s+'                      # Precio 1
        r'[\d,]+\s+'                      # Precio 2
        r'([\d,]+)',                      # Importe
        re.MULTILINE
    )
    
    for match in patron_prod.finditer(texto):
        codigo = match.group(1)
        desc = match.group(2).strip()
        importe = float(match.group(3).replace(',', '.'))
        
        if len(desc) > 3:
            lineas.append({
                'codigo': codigo,
                'articulo': desc,
                'iva': 10,  # MRM productos alimentarios 10%
                'base': importe
            })
    
    # Si no se encontraron productos, usar Base Imponible
    if not lineas:
        base_match = re.search(r'Base Imponible TOTAL\s*:\s*([\d,]+)', texto)
        if base_match:
            base = float(base_match.group(1).replace(',', '.'))
            lineas.append({
                'codigo': 'MRM',
                'articulo': 'PRODUCTOS MRM',
                'iva': 10,
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
    
    Formato alternativo (v3.23):
    CODIGO CANTIDAD CONCEPTO IVA% IMPORTE PRECIO
    Ejemplo: "AL0007 3,1600 QUESO OVEJA AHUMADO NAVARRA - 4,00% 56,41 17,8500"
    
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
    
    # v3.23 - Patrón para formato: CODIGO CANTIDAD CONCEPTO IVA% IMPORTE PRECIO
    # Ejemplo: AL0007 3,1600 QUESO OVEJA AHUMADO NAVARRA - 4,00% 56,41 17,8500
    if not lineas:
        patron_v323 = re.compile(
            r'([A-Z]{2}\d{4})\s+'           # Código (AL0007)
            r'(\d+[.,]\d+)\s+'              # Cantidad (3,1600)
            r'(.+?)\s+'                      # Concepto (QUESO OVEJA...)
            r'(\d{1,2})[,.]00%\s+'          # IVA (4,00%)
            r'(\d+[.,]\d{2})\s+'            # Importe (56,41)
            r'\d+[.,]\d+',                   # Precio unitario (ignorar)
            re.MULTILINE
        )
        
        for m in patron_v323.finditer(texto):
            codigo, cantidad, concepto, iva, importe = m.groups()
            concepto_limpio = re.sub(r'\s+', ' ', concepto.strip())
            # Quitar guiones y números de lote al final
            concepto_limpio = re.sub(r'\s*-\s*\d*\s*$', '', concepto_limpio).strip()
            concepto_limpio = re.sub(r'\s*-\s*$', '', concepto_limpio).strip()
            
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
    
    # v3.23b - Patrón para formato: PRECIO CODIGO CANTIDAD IVA% IMPORTE CONCEPTO
    # Ejemplo: 17,8500 AL0007 3,1600 4,00% 56,41 QUESO OVEJA AHUMADO NAVARRA -
    if not lineas:
        patron_v323b = re.compile(
            r'(\d+[.,]\d{4})\s+'           # Precio (17,8500)
            r'([A-Z]{2}\d{4})\s+'          # Código (AL0007)
            r'(\d+[.,]\d{4})\s+'           # Cantidad (3,1600)
            r'(\d{1,2})[,.]00%\s+'         # IVA (4,00%)
            r'(\d+[.,]\d{2})\s+'           # Importe (56,41)
            r'(.+?)(?=\n|$)',              # Concepto al final
            re.MULTILINE
        )
        
        for m in patron_v323b.finditer(texto):
            precio, codigo, cantidad, iva, importe, concepto = m.groups()
            concepto_limpio = re.sub(r'\s+', ' ', concepto.strip())
            # Quitar guiones y números de lote al final
            concepto_limpio = re.sub(r'\s*-\s*\d*\s*$', '', concepto_limpio).strip()
            concepto_limpio = re.sub(r'\s*-\s*$', '', concepto_limpio).strip()
            
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
    
    # Patrón alternativo si los anteriores no funcionan (formato más separado)
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


def extraer_lineas_controlplaga(texto: str) -> List[Dict]:
    """Extrae línea de facturas de CONTROLPLAGA / Javier Alborés Rey (desinsectación).
    
    NIF: 11812266H
    IBAN: ES86 0081 7122 58 0001218325
    
    Formato:
    Tratamiento desinsectación y desratización [COMESTIBLES BAREA]    90.00
    Base imponible                                                     90.00
    I.V.A. 21%                                                         18.90
    TOTAL FACTURA                                                     108.90
    
    Siempre: 90€ base (puede variar), 21% IVA
    Categoría fija: DESINSECTACION
    """
    lineas = []
    
    # Buscar Base imponible primero (más fiable)
    patron_base = re.compile(r'Base\s+imponible\s+(\d+[.,]\d{2})', re.IGNORECASE)
    match_base = patron_base.search(texto)
    
    if match_base:
        base = float(match_base.group(1).replace(',', '.'))
    else:
        base = 90.00  # Valor por defecto
    
    # Buscar la descripción - puede tener COMESTIBLES BAREA en línea siguiente
    articulo = 'Tratamiento desinsectación y desratización'
    if 'COMESTIBLES BAREA' in texto.upper():
        articulo = 'Tratamiento desinsectación y desratización COMESTIBLES BAREA'
    
    lineas.append({
        'codigo': 'DES',
        'articulo': articulo,
        'iva': 21,
        'base': base,
        'categoria': 'DESINSECTACION'  # Forzar categoría
    })
    
    return lineas


def extraer_lineas_panruje(texto: str) -> List[Dict]:
    """Extrae línea de facturas de PANRUJE / Rosquillas La Ermita.
    
    CIF: B13858014
    IBAN: ES19 0081 5344 2800 0261 4066
    
    Formato:
    CÓDIGO  CANTIDAD  DETALLE                        LOTE  PRECIO  DTO.  IMPORTE
    NOR 7   4,0       CAJAS DE ROSQUILLAS NORMALES   47    16,50   2,00  64,68
    POR     1,0       PORTES                               24,60         24,60
    
    Línea de totales:
    89,28 89,28 4,0 3,57 92,85
    (TOTAL_BRUTO  BASE_IMP  %IVA  IVA  TOTAL)
    
    Notas:
    - IVA puede ser 4% o 10% (extraer de la factura)
    - Portes se repercuten en una sola línea
    - BASE se calcula como TOTAL / (1 + IVA/100) para que cuadre
    - Categoría fija: ROSQUILLAS M
    """
    lineas = []
    
    # Buscar la línea de totales: BASE_IMP BASE_IMP %IVA IVA TOTAL
    # Formato: 43,78 43,78 10,0 4,38 48,16
    patron_totales = re.compile(
        r'(\d+[.,]\d{2})\s+(\d+[.,]\d{2})\s+(\d+)[.,]?(\d*)\s+(\d+[.,]\d{2})\s+(\d+[.,]\d{2})\s*$',
        re.MULTILINE
    )
    match = patron_totales.search(texto)
    
    if not match:
        return lineas  # No se puede procesar sin totales
    
    # Extraer valores
    total = float(match.group(6).replace(',', '.'))
    iva = int(match.group(3))  # Solo parte entera (4 o 10)
    
    # Calcular BASE a partir del TOTAL e IVA para que cuadre
    base = round(total / (1 + iva / 100), 2)
    
    # El artículo siempre es el mismo
    articulo = 'CAJAS DE ROSQUILLAS NORMALES'
    
    lineas.append({
        'codigo': 'NOR',
        'articulo': articulo,
        'iva': iva,
        'base': base,
        'categoria': 'ROSQUILLAS M'  # Forzar categoría
    })
    
    return lineas


def extraer_lineas_angel_y_loli(texto: str) -> List[Dict]:
    """Extrae líneas de facturas ANGEL Y LOLI / Alfarería - v3.23b.
    
    NIF: 75727068M
    Productos: Platos, cuencos, chupitos, etc.
    IVA: 21%
    Categoría fija: CACHARRERIA
    
    Formato:
    ARTICULO    CANTIDAD    PRECIO    TOTAL
    PLATO LLANO    20    5,70    114,00
    PLATO POSTRE   50    3,72    186,00
    
    Línea totales (formato variable):
    177,10 17,71 159,39 21,00 33,47  (SUBTOTAL DESCUENTO BASE IVA% IVA_IMPORTE)
    o
    21,00 549,50 45,00 594,50 124,85 (IVA% SUBTOTAL PORTES BASE IVA_IMPORTE)
    
    Notas:
    - Los PORTES se reparten proporcionalmente entre artículos
    """
    lineas = []
    
    # Buscar líneas de producto: ARTICULO CANTIDAD PRECIO TOTAL
    # Formato: "PLATO LLANO 20 5,70 114,00" o "CUENCO 10 CM 15 2,07 31,05"
    patron_linea = re.compile(
        r'^([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s\d/]+?)\s+'  # Artículo (con números como "10 CM")
        r'(\d+)\s+'                              # Cantidad
        r'(\d+[,]\d{2})\s+'                      # Precio unitario
        r'(\d+[,]\d{2})\s*$',                    # Importe
        re.MULTILINE
    )
    
    # Extraer líneas de producto
    productos = []
    total_productos = 0.0
    
    # Lista de artículos válidos de alfarería
    ARTICULOS_VALIDOS = ['PLATO', 'CUENCO', 'LEBRILLA', 'CHUPITO', 'VASO', 'BANDEJA', 
                         'TAZA', 'CAZUELA', 'FUENTE', 'BOL', 'JARRA', 'CUENCOS']
    
    for m in patron_linea.finditer(texto):
        articulo, cantidad, precio, importe = m.groups()
        articulo = articulo.strip()
        
        # Ignorar cabeceras y líneas de totales
        if articulo.upper() in ['ARTÍCULO', 'ARTICULO', 'TIPO', 'IMPORTE', 'TOTAL']:
            continue
        
        # Ignorar líneas que contienen fechas o códigos
        if re.search(r'\d{2}/\d{2}/\d{4}', articulo):
            continue
        if re.search(r'\d{6}', articulo):  # Números de documento
            continue
        if 'MADRID' in articulo.upper():
            continue
        
        # Verificar que empieza con un artículo válido de alfarería
        articulo_upper = articulo.upper()
        es_valido = any(articulo_upper.startswith(av) for av in ARTICULOS_VALIDOS)
        if not es_valido:
            continue
        
        importe_float = float(importe.replace(',', '.'))
        productos.append({
            'articulo': articulo,
            'cantidad': int(cantidad),
            'precio': float(precio.replace(',', '.')),
            'importe': importe_float
        })
        total_productos += importe_float
    
    # Buscar PORTES - puede estar en diferentes formatos
    portes = 0.0
    
    # Formato 1: "PORTES XX,XX"
    patron_portes = re.compile(r'PORTES\s+(\d+[,]\d{2})', re.IGNORECASE)
    m_portes = patron_portes.search(texto)
    if m_portes:
        portes = float(m_portes.group(1).replace(',', '.'))
    else:
        # Formato 2: En línea de totales después de 21,00
        # "21,00 549,50 45,00 594,50 124,85" -> portes = 45,00
        patron_totales = re.compile(
            r'21[,.]00\s+(\d+[,]\d{2})\s+(\d+[,]\d{2})\s+(\d+[,]\d{2})',
            re.MULTILINE
        )
        m_totales = patron_totales.search(texto)
        if m_totales:
            subtotal = float(m_totales.group(1).replace(',', '.'))
            portes_candidato = float(m_totales.group(2).replace(',', '.'))
            # Verificar si es un porte razonable (menor que subtotal * 0.5)
            if portes_candidato < subtotal * 0.5:
                portes = portes_candidato
        else:
            # Formato 3: "SUBTOTAL DESCUENTO BASE 21,00 IVA"
            # "177,10 17,71 159,39 21,00 33,47" -> descuento = 17,71 (no es porte)
            # En este caso no hay portes explícitos
            pass
    
    # Repartir portes proporcionalmente entre productos
    for prod in productos:
        proporcion = prod['importe'] / total_productos if total_productos > 0 else 0
        portes_producto = round(portes * proporcion, 2)
        base_con_portes = prod['importe'] + portes_producto
        
        lineas.append({
            'codigo': '',
            'articulo': prod['articulo'],
            'cantidad': prod['cantidad'],
            'iva': 21,
            'base': base_con_portes,
            'categoria': 'CACHARRERIA'
        })
    
    return lineas


def extraer_lineas_quesos_cati(texto: str) -> List[Dict]:
    """Extrae líneas de facturas QUESOS DEL CATI - v3.23.
    
    CIF: F12499455
    IBAN: ES89 2100 7363 72 1100030799
    Productos: Quesos de cabra
    IVA: 4%
    Categoría fija: QUESOS
    
    Formato:
    REF.    DESCRIPCIÓN           Kg/Un.    PRECIO    DTO.    IMPORTE
    13016   CATIABRIGO CABRA      4,700     17,00             79,90
    13018   CATIABRIGO CABRA 0.5  2,950     17,00             50,15
    
    Nota: El código está pegado a la descripción (CATIABRIGO = CATI ABRIGO)
    """
    lineas = []
    
    # Patrón para líneas de producto
    # REF DESCRIPCION KG PRECIO [DTO] IMPORTE
    patron = re.compile(
        r'^(\d{5})\s+'                    # REF (5 dígitos)
        r'([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s\d.]+?)\s+'  # Descripción
        r'(\d+[,]\d{3})\s+'               # Kg/Un (X,XXX)
        r'(\d+[,]\d{2})\s+'               # Precio
        r'(\d+[,]\d{2})\s*$',             # Importe
        re.MULTILINE
    )
    
    for m in patron.finditer(texto):
        ref, descripcion, kg, precio, importe = m.groups()
        
        # Separar código de descripción (CATIABRIGO -> CATI ABRIGO)
        descripcion = descripcion.strip()
        descripcion = re.sub(r'^CATI(\w)', r'CATI \1', descripcion)
        descripcion = re.sub(r'^PAÑOLETA(\w)', r'PAÑOLETA \1', descripcion)
        
        lineas.append({
            'codigo': ref,
            'articulo': descripcion,
            'cantidad': float(kg.replace(',', '.')),
            'iva': 4,
            'base': float(importe.replace(',', '.')),
            'categoria': 'QUESOS'
        })
    
    return lineas


def extraer_lineas_ista(texto: str) -> List[Dict]:
    """Extrae líneas de facturas ISTA (consumo agua) - v3.24.
    
    CIF: A50090133
    IBAN: No necesario (adeudo)
    Productos: Consumo de agua fría
    IVA: 10%
    Categoría fija: CONSUMO DE AGUA
    
    Formato:
    470239 Consumo (A.Fria) 58 49,35 10%
    470239 Cuotas de Servicio del Canal de Isabel II (A.Fria) 16,12 10%
    72,02 €
    65,47 10%
    Importe total
    BASE IMP. % IMP. IVA
    
    Nota: Se extrae UNA sola línea con la BASE IMP total (suma de consumo + cuotas)
    """
    lineas = []
    
    # Buscar BASE IMPONIBLE: número antes de "10%" en la línea previa a "Importe total"
    # Formato: "65,47 10%\nImporte total"
    patron_base = re.search(r'(\d+[,]\d{2})\s+10%\s*\n\s*Importe total', texto)
    
    if patron_base:
        base = float(patron_base.group(1).replace(',', '.'))
        
        lineas.append({
            'codigo': '',
            'articulo': 'Consumo Agua Fria',
            'iva': 10,
            'base': base,
            'categoria': 'CONSUMO DE AGUA'
        })
    
    return lineas


def extraer_lineas_biellebi(texto: str) -> List[Dict]:
    """Extrae líneas de facturas BIELLEBI (taralli italiano) - v3.24.
    
    CIF: 06089700725 (italiano)
    IBAN: IT68B0306941603100000001003
    Productos: Taralli, Trecce (intracomunitario)
    IVA: 0% (cessioni intracomunitarie)
    Categoría fija: TARALLI
    
    Formato:
    COD.           DESCRIZIONE ARTICOLO          LOTTO  UM  Q.TA'  CT  PREZZO  % SC.  IMPONIBILE  C.I.
    02FRICI/250/25 TARALLINI CIPOLLA g250X25     028/8  PZ  275,00 11  0,90           247,50      41
    Spese di spedizione                                 N   1,00       100,00         100,00      41
    
    Nota: Los portes (Spese di spedizione) se reparten proporcionalmente entre productos
    """
    lineas = []
    productos = []
    portes = 0.0
    
    for line in texto.split('\n'):
        # Detectar línea de portes
        if 'Spese di spedizione' in line or 'spedizione' in line.lower():
            m = re.search(r'(\d+[,]\d{2})\s+41\s*$', line)
            if m:
                portes = float(m.group(1).replace(',', '.'))
            continue
        
        # Patrón para líneas de producto
        # CODIGO DESCRIPCION LOTTO UM QTA CT PRECIO IMPONIBLE 41
        patron = re.match(
            r'^(\d{2}[A-Z]+/\d+/\d+)\s+'     # Código (02FRICI/250/25)
            r'(.+?)\s+'                       # Descripción 
            r'(\d{3}/\d)\s+'                  # Lote (028/8)
            r'PZ\s+'                          # UM
            r'(\d+[,]\d{2})\s+'              # Cantidad
            r'(\d+)\s+'                       # CT
            r'(\d+[,]\d{2})\s+'              # Precio
            r'(\d+[,]\d{2})\s+'              # Imponible
            r'41',                            # C.I.
            line
        )
        
        if patron:
            codigo, desc, lote, qty, ct, precio, imponible = patron.groups()
            # Simplificar descripción: quitar gXXXXXX y XXXXX
            desc_simple = re.sub(r'\s*g\d+X\d+', '', desc).strip()
            desc_simple = re.sub(r'\s*\d+X\d+', '', desc_simple).strip()
            
            productos.append({
                'codigo': codigo,
                'articulo': desc_simple,
                'base': float(imponible.replace(',', '.'))
            })
    
    # Calcular proporción de portes y construir líneas finales
    total_productos = sum(p['base'] for p in productos)
    
    for p in productos:
        if total_productos > 0 and portes > 0:
            proporcion = p['base'] / total_productos
            portes_repartidos = round(portes * proporcion, 2)
            base_final = round(p['base'] + portes_repartidos, 2)
        else:
            base_final = p['base']
        
        lineas.append({
            'codigo': p['codigo'],
            'articulo': p['articulo'],
            'iva': 0,
            'base': base_final,
            'categoria': 'TARALLI'
        })
    
    return lineas


def extraer_lineas_ferriol(texto: str) -> List[Dict]:
    """Extrae líneas de facturas EMBUTIDOS FERRIOL (chacinas Mallorca) - v3.24.
    
    CIF: B57955098
    IBAN: ES22 2100 0088 0502 0014 6500
    Productos: Sobrasada, Longaniza, Camayot, Sepultrus, etc.
    IVA: 10%
    Categoría fija: CHACINAS
    
    Formato:
    CANT COD DESCRIPCION           PRECIO_UD  TOTAL  LOTE
    3,6  07  KG CAMAYOT            12,40      44,64  06
    4,8  29  SEPULTRUS I.G.P.      13,30      63,84  48
    
    Nota: El código está pegado a la descripción (07KG, 29SEPULTRUS)
    """
    lineas = []
    
    # Patrón para líneas de producto
    # Formato: CANT CODDESCRIPCION PRECIO TOTAL LOTE
    patron_linea = re.compile(
        r'^\s*(\d+[,]\d)\s+'           # CANT (3,6)
        r'(\d{2})'                      # COD (07) - pegado a desc
        r'([A-Z].+?)\s+'               # DESC (KG CAMAYOT)
        r'(\d+[,]\d{2})\s+'            # PRECIO (12,40)
        r'(\d+[,]\d{2})\s+'            # TOTAL (44,64)
        r'(\d{2})\s*$',                # LOTE (06)
        re.MULTILINE
    )
    
    for m in patron_linea.finditer(texto):
        cant, cod, desc, precio, total, lote = m.groups()
        # Limpiar descripción (quitar KG al inicio si existe)
        desc_clean = re.sub(r'^KG\s*', '', desc.strip())
        
        lineas.append({
            'codigo': cod,
            'articulo': desc_clean,
            'cantidad': float(cant.replace(',', '.')),
            'iva': 10,
            'base': float(total.replace(',', '.')),
            'categoria': 'CHACINAS'
        })
    
    return lineas


def extraer_lineas_abbati(texto: str) -> List[Dict]:
    """Extrae líneas de facturas ABBATI CAFFE - v3.24.
    
    CIF: B82567876
    IBAN: Recibo Bancario (adeudo)
    Productos: Dosis de café
    IVA: 10%
    Categoría fija: CAFE
    
    Formato línea:
    00616 DOSIS CAFE  X 150 1,00 50,50 10,00 50,50
    COD   DESCRIPCION       CANT PRECIO IVA%  TOTAL
    """
    lineas = []
    
    # Patrón: COD DESC CANT PRECIO IVA% TOTAL
    patron = re.compile(
        r'(\d{5})\s+'                    # Código (00616)
        r'(.+?)\s+'                       # Descripción
        r'(\d+[,]\d{2})\s+'              # Cantidad
        r'(\d+[,]\d{2})\s+'              # Precio
        r'(\d+[,]\d{2})\s+'              # % IVA
        r'(\d+[,]\d{2})'                 # Total
    )
    
    for m in patron.finditer(texto):
        cod, desc, cant, precio, iva_pct, total = m.groups()
        # Limpiar descripción
        desc_clean = desc.strip()
        # Quitar "X 150" o similar del final
        desc_clean = re.sub(r'\s+X\s*\d+\s*$', '', desc_clean)
        
        lineas.append({
            'codigo': cod,
            'articulo': desc_clean,
            'cantidad': float(cant.replace(',', '.')),
            'iva': 10,
            'base': float(total.replace(',', '.')),
            'categoria': 'CAFE'
        })
    
    return lineas


def extraer_lineas_munoz_martin(texto: str) -> List[Dict]:
    """Extrae líneas de facturas BODEGAS MUÑOZ MARTÍN - v3.24.
    
    CIF: E83182683
    IBAN: ES62 0049 5184 11 2016002766
    Productos: Vinos (Viña Jesusa)
    IVA: 21%
    Categoría fija: VINOS
    
    Formato línea (columnas desordenadas en PDF):
    076 12,40 74,38 € 6 R CAJA 6 BOT. VIÑA JESUSA TINTO
    COD PRECIO IMPORTE € CANT DESCRIPCION
    
    Nota: Los portes se reparten proporcionalmente
    """
    lineas = []
    productos = []
    portes = 0.0
    
    # Patrón: COD PRECIO IMPORTE € CANT DESCRIPCION
    patron = re.compile(
        r'^(\d{3})\s+'                   # Código (076)
        r'(\d+[,]\d{2})\s+'              # Precio
        r'(\d+[,]\d{2})\s*€?\s+'         # Importe
        r'(\d+)\s+'                       # Cantidad
        r'(.+?)$',                        # Descripción
        re.MULTILINE
    )
    
    for m in patron.finditer(texto):
        cod, precio, importe, cant, desc = m.groups()
        desc_clean = desc.strip()
        
        if 'PORTE' in desc_clean.upper():
            portes = float(importe.replace(',', '.'))
        else:
            productos.append({
                'codigo': cod,
                'articulo': desc_clean,
                'cantidad': int(cant),
                'base': float(importe.replace(',', '.'))
            })
    
    # Repartir portes proporcionalmente
    total_productos = sum(p['base'] for p in productos)
    
    for p in productos:
        if total_productos > 0 and portes > 0:
            proporcion = p['base'] / total_productos
            portes_repartidos = round(portes * proporcion, 2)
            base_final = round(p['base'] + portes_repartidos, 2)
        else:
            base_final = p['base']
        
        lineas.append({
            'codigo': p['codigo'],
            'articulo': p['articulo'],
            'cantidad': p['cantidad'],
            'iva': 21,
            'base': base_final,
            'categoria': 'VINOS'
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
    Categoría: HUEVOS
    
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
                'base': float(importe.replace(',', '.')),
                'categoria': 'HUEVOS'
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
                    'base': float(importe.replace(',', '.')),
                    'categoria': 'HUEVOS'
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
                    'base': float(importe.replace(',', '.')),
                    'categoria': 'HUEVOS'
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


def extraer_lineas_mrm(texto: str) -> List[Dict]:
    """Extrae líneas de facturas MRM (Industrias Cárnicas MRM-2) - v3.11.
    
    CIF: A80280845
    Productos: Patés, mousses, salmón ahumado
    IVA: 10% (reducido)
    IBAN: ES28 2100 8662 5702 0004 8824
    
    Formato de línea en texto extraído:
    " 1,200  6,700  6,700  40,2001161 - PATE LECHAZO"
    Donde: peso, precio_ud, precio, IMPORTE + CODIGO - DESCRIPCION
    """
    lineas = []
    
    # Patrón para líneas de producto
    patron_linea = re.compile(
        r'\s*(\d+,\d{3})\s+'           # peso (1,200)
        r'(\d+,\d{2,3})\s+'            # precio_ud (6,700)
        r'(\d+,\d{2,3})\s+'            # precio (6,700)
        r'(\d+,\d{2,3})'               # importe (40,200) - pegado al código
        r'(\d+)\s*-\s*'                # código (1161)
        r'([A-ZÁÉÍÓÚÑ0-9][A-ZÁÉÍÓÚÑ0-9\s\+\.]+)',  # descripción
        re.MULTILINE
    )
    
    # Mapeo de códigos a descripciones limpias
    descripciones_mrm = {
        '377': 'SALMON AHUMADO PRECORTADO',
        '1159': 'PATE COCHINILLO 200g',
        '1161': 'PATE LECHAZO CHURRO 200g',
        '1157': 'MOUSSE DE FOIE 200g',
        '1440': 'MOUSSE PATO PIMIENTA VERDE',
        '2150': 'MOUSSE PATO AL ORUJO 200g',
    }
    
    for match in patron_linea.finditer(texto):
        peso, precio_ud, precio, importe, codigo, descripcion = match.groups()
        
        base = float(importe.replace(',', '.'))
        
        # Usar descripción conocida o limpiar la extraída
        articulo = descripciones_mrm.get(codigo, ' '.join(descripcion.split()))
        
        lineas.append({
            'codigo': codigo,
            'articulo': articulo,
            'cantidad': 1,
            'precio_unitario': base,
            'iva': 10,
            'base': round(base, 2)
        })
    
    return lineas


def extraer_lineas_disber(texto: str) -> List[Dict]:
    """Extrae líneas de facturas DISBER (Grupo Disber) - v3.11.
    
    CIF: B46144424
    Productos: Vinos (21%), conservas gourmet (10%)
    IBAN: ES39 2100 8617 1502 0002 4610
    
    Formato línea:
    [CODIGO] Descripción... CANTIDAD PRECIO_BASE PRECIO_UNIT IMPORTE €
    """
    lineas = []
    
    # Detectar tipo de IVA de la factura
    iva = 21  # default
    if 'IVA 10%' in texto:
        iva = 10
    elif 'IVA 21%' in texto:
        iva = 21
    
    # Patrón para líneas de producto
    patron = re.compile(
        r'\[([A-Z0-9]+)\]\s*'           # [CODIGO]
        r'([^\[]+?)'                     # Descripción
        r'(\d+,\d{2})\s*\n'             # Cantidad
        r'(\d+,\d{2})\s*\n'             # Precio base
        r'(\d+,\d{4})\s*\n'             # Precio unitario
        r'(\d+,\d{2})\s*\n?\s*€',       # Importe
        re.DOTALL
    )
    
    for match in patron.finditer(texto):
        codigo, descripcion, cantidad, precio_base, precio_unit, importe = match.groups()
        
        # Limpiar descripción
        descripcion = ' '.join(descripcion.split())
        
        base = float(importe.replace(',', '.'))
        
        lineas.append({
            'codigo': codigo,
            'articulo': descripcion[:60],
            'cantidad': int(float(cantidad.replace(',', '.'))),
            'precio_unitario': float(precio_unit.replace(',', '.')),
            'iva': iva,
            'base': round(base, 2)
        })
    
    return lineas


def extraer_lineas_trucco(texto: str) -> List[Dict]:
    """Extrae líneas de facturas TRUCCO COPIAS / Isaac Rodríguez Pacha - v3.12.
    
    NIF: 05247386M
    Servicios: Impresión, copias, papelería
    IVA: siempre 21%
    Categoría fija: GASTOS VARIOS
    Sin IBAN (pago por tarjeta)
    
    Formato típico:
    Concepto                              Cantidad      Base imp.     IVA
    IMPRESIONES                          1 x 6,45 €     6,45 €    21% (1,35 €)
    
    Total Base Imponible: 6,45 €
    """
    lineas = []
    
    # Patrón para línea de concepto - captura el texto y la base imponible
    # Formato: Concepto    1 x XX,XX €    XX,XX €    21% (X,XX €)
    patron = re.compile(
        r'^([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñÁÉÍÓÚÑ\s]+?)\s+'  # Concepto (empieza con mayúscula)
        r'(\d+)\s*x\s*'                                 # Cantidad (1 x)
        r'(\d+[.,]\d{2})\s*€\s+'                        # Precio unitario
        r'(\d+[.,]\d{2})\s*€\s+'                        # Base imponible
        r'21%',                                          # IVA 21%
        re.MULTILINE | re.IGNORECASE
    )
    
    for match in patron.finditer(texto):
        concepto, cantidad, precio_unit, base = match.groups()
        
        lineas.append({
            'codigo': '',
            'articulo': concepto.strip()[:50],
            'cantidad': int(cantidad),
            'precio_unitario': float(precio_unit.replace(',', '.')),
            'iva': 21,
            'base': float(base.replace(',', '.')),
            'categoria': 'GASTOS VARIOS'  # Forzar categoría
        })
    
    # Si no encontramos líneas con el patrón detallado, usar Total Base Imponible
    if not lineas:
        patron_total = re.search(r'Total Base Imponible:\s*(\d+[.,]\d{2})\s*€', texto)
        if patron_total:
            base = float(patron_total.group(1).replace(',', '.'))
            
            # Buscar concepto en la tabla
            concepto_match = re.search(
                r'Concepto\s+Cantidad\s+Base imp\.\s+IVA\s*\n'
                r'([A-Za-záéíóúñÁÉÍÓÚÑ\s]+?)\s+\d+\s*x',
                texto
            )
            concepto = concepto_match.group(1).strip() if concepto_match else 'Trabajos de impresión'
            
            lineas.append({
                'codigo': '',
                'articulo': concepto[:50],
                'cantidad': 1,
                'precio_unitario': base,
                'iva': 21,
                'base': round(base, 2),
                'categoria': 'GASTOS VARIOS'  # Forzar categoría
            })
    
    return lineas


def extraer_lineas_barra_dulce(texto: str) -> List[Dict]:
    """Extrae líneas de facturas LA BARRA DULCE (pastelería) - v3.12.
    
    CIF: B19981141
    Productos: Palmeritas, buñuelos, rosquillas, etc.
    IVA: siempre 10%
    Categoría fija: DULCES
    IBAN: ES76 2100 5606 4802 0017 4138
    
    Formato línea:
    Descripción Unidades Precio Unitario
    Palmeritas 1 43,78 43,78
    Desayuno 21/11 1 11,23 11,23
    """
    lineas = []
    
    # Primero extraer solo la zona de productos (entre cabecera y Observaciones/Base)
    zona_match = re.search(
        r'Descripción\s+Unidades\s+Precio Unitario\s*\n(.*?)(?=Observaciones:|Base Imponible)',
        texto, re.DOTALL
    )
    
    if not zona_match:
        return lineas
    
    zona = zona_match.group(1)
    
    # Patrón para líneas de producto dentro de la zona
    # Formato: Descripción UNIDADES PRECIO_UNIT TOTAL
    # Descripción puede incluir números y / (para fechas como "21/11" o "12 de septiembre")
    patron = re.compile(
        r'^([A-Za-záéíóúñÁÉÍÓÚÑ][A-Za-záéíóúñÁÉÍÓÚÑ\s\d/]+?)\s+'  # Descripción con números
        r'(\d+)\s+'                                                  # Unidades
        r'(\d+[.,]\d{2})\s+'                                        # Precio unitario
        r'(\d+[.,]\d{2})\s*$',                                      # Total
        re.MULTILINE
    )
    
    for match in patron.finditer(zona):
        descripcion, unidades, precio_unit, total = match.groups()
        
        base = float(total.replace(',', '.'))
        
        lineas.append({
            'codigo': '',
            'articulo': descripcion.strip()[:50],
            'cantidad': int(unidades),
            'precio_unitario': float(precio_unit.replace(',', '.')),
            'iva': 10,
            'base': round(base, 2),
            'categoria': 'DULCES'  # Forzar categoría
        })
    
    return lineas


def extraer_lineas_grupo_campero(texto: str) -> List[Dict]:
    """Extrae líneas de facturas GRUPO TERRITORIO CAMPERO (patatas fritas) - v3.12.
    
    CIF: B16690141
    Productos: Patatas fritas artesanas
    IVA: siempre 10%
    Categoría fija: PATATAS FRITAS APERITIVO
    
    Formato línea:
    Cantidad Producto Precio/Ud IVA Suma Base
    16 PATATAS FRITAS ARTESANAS 9.90 € 10% 158.40 €
    """
    lineas = []
    
    # Patrón para líneas de producto
    # Formato: CANTIDAD PRODUCTO PRECIO € IVA% TOTAL €
    patron = re.compile(
        r'^(\d+)\s+'                                              # Cantidad
        r'([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]+?)\s+'                        # Producto
        r'(\d+[.,]\d{2})\s*€\s+'                                  # Precio/Ud
        r'(\d+)%\s+'                                               # IVA
        r'(\d+[.,]\d{2})\s*€',                                    # Suma Base
        re.MULTILINE
    )
    
    for match in patron.finditer(texto):
        cantidad, producto, precio_unit, iva, total = match.groups()
        
        base = float(total.replace(',', '.'))
        
        lineas.append({
            'codigo': '',
            'articulo': producto.strip()[:50],
            'cantidad': int(cantidad),
            'precio_unitario': float(precio_unit.replace(',', '.')),
            'iva': int(iva),
            'base': round(base, 2),
            'categoria': 'PATATAS FRITAS APERITIVO'  # Forzar categoría
        })
    
    return lineas


def extraer_lineas_zubelzu(texto: str) -> List[Dict]:
    """Extrae líneas de facturas ZUBELZU PIPARRAK - v3.12.
    
    CIF: B75079608
    Productos: Guindillas de Ibarra, Mousse de piparra
    IVA: siempre 10%
    Categorías:
      - GUINDILLAS de IBARRA -> PIPARRAS
      - MOUSSE DE PIPARRA -> CONSERVAS VEGETALES
    
    Formato línea (con espacios entre caracteres):
    1901 MOUSSE DE PIPARRA 400 g 2 12 5,630 67,56
    150 GUINDILLAS de IBARRA 1/2 GALON 12 72 11,450 824,40
    """
    lineas = []
    
    # Buscar zona de productos (entre ALBARAN y BRUTO)
    zona_match = re.search(r'\*\*\* ALBARAN.*?(?=BRUTO)', texto, re.DOTALL)
    if not zona_match:
        return lineas
    
    zona = zona_match.group(0)
    
    for linea in zona.split('\n'):
        # Ignorar líneas de LOTE, CONSUMO, ALBARAN
        if 'LOTE:' in linea or 'CONSUMO' in linea or 'ALBARAN' in linea or not linea.strip():
            continue
        
        # Buscar números decimales (formato: X X X , X X con espacios)
        numeros = re.findall(r'(\d(?:\s*\d)*\s*,\s*\d(?:\s*\d)?)', linea)
        
        if len(numeros) >= 2:
            # Último = total, penúltimo = precio unitario
            total_raw = numeros[-1]
            precio_raw = numeros[-2]
            
            total = float(total_raw.replace(' ', '').replace(',', '.'))
            precio = float(precio_raw.replace(' ', '').replace(',', '.'))
            
            # Extraer código (al inicio, puede tener espacios entre dígitos)
            codigo_match = re.match(r'^\s*(\d(?:\s*\d){2,3})', linea)
            if codigo_match:
                codigo = codigo_match.group(1).replace(' ', '')
                
                # Extraer descripción
                resto = linea[codigo_match.end():]
                desc_match = re.match(r'\s*([A-Za-z].*?)(?=\s+\d)', resto)
                if desc_match:
                    descripcion = desc_match.group(1).strip()
                    
                    # Determinar categoría según artículo
                    desc_upper = descripcion.upper()
                    if 'GUINDILLA' in desc_upper:
                        categoria = 'PIPARRAS'
                    elif 'MOUSSE' in desc_upper and 'PIPARRA' in desc_upper:
                        categoria = 'CONSERVAS VEGETALES'
                    else:
                        categoria = 'PENDIENTE'
                    
                    # Extraer cantidad
                    numeros_enteros = re.findall(r'(\d(?:\s*\d)*)', resto)
                    enteros = [n.replace(' ', '') for n in numeros_enteros 
                              if ',' not in n and n.replace(' ','').isdigit()]
                    cantidad = int(enteros[1]) if len(enteros) >= 2 else 1
                    
                    lineas.append({
                        'codigo': codigo,
                        'articulo': descripcion[:50],
                        'cantidad': cantidad,
                        'precio_unitario': precio,
                        'iva': 10,
                        'base': round(total, 2),
                        'categoria': categoria
                    })
    
    return lineas


def extraer_lineas_productos_adell(texto: str) -> List[Dict]:
    """Extrae líneas de facturas PRODUCTOS ADELL / Croquellanas - v3.13.
    
    CIF: B12711636
    Productos: Conservas gourmet (alcachofas, patés, mousses)
    IVA: 10%
    
    Formato línea (OCR):
    24,000ALCACHOFAS EN ACEITE 330 GR 4,920 10,00 118,08250128 - 28/01/2027 2 cajas de
    8,000PATÉ CECINA 110 GR 3,700 10,00 29,60240613 - 13/12/2025 1 caja de 8u
    """
    lineas = []
    
    # Patrón: CANTIDAD + DESCRIPCION + PRECIO + IVA + SUBTOTAL + LOTE
    patron = re.compile(
        r'(\d+[,.]\d+)'                         # Cantidad (ej: 24,000 o 8,000)
        r'([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s\d]+?)\s+'   # Descripción (mayúsculas)
        r'(\d+[,.]\d+)\s+'                       # Precio
        r'(\d+[,.]\d+)\s+'                       # IVA
        r'(\d+[,.]\d+)'                          # Subtotal
        r'\d+\s*-\s*\d{2}/\d{2}/\d{4}',          # Lote - Caducidad
        re.MULTILINE
    )
    
    for match in patron.finditer(texto):
        cantidad, descripcion, precio, iva, subtotal = match.groups()
        
        lineas.append({
            'codigo': '',
            'articulo': descripcion.strip()[:50],
            'cantidad': int(float(cantidad.replace(',', '.'))),
            'precio_unitario': float(precio.replace(',', '.')),
            'iva': int(float(iva.replace(',', '.'))),
            'base': round(float(subtotal.replace(',', '.')), 2),
            'categoria': ''  # Se asignará del diccionario
        })
    
    return lineas


def extraer_lineas_ecoficus(texto: str) -> List[Dict]:
    """Extrae líneas de facturas ECOFICUS - v3.13.
    
    CIF: B10214021
    Productos: Higos ecológicos (pan de higo, bombones, biosnacks)
    IVA: 10%
    
    Formato línea (OCR - columnas desordenadas):
    PH200NFB
    2,550
    12,00
    30,60
    Pan de Higo ecológico Naranja 200g Ecoficus
    092/09125
    1,00
    €/uni
    30/11/25
    """
    lineas = []
    
    # Patrón: CODIGO + PRECIO + CANTIDAD + IMPORTE + DESCRIPCION + LOTE + CAJAS + €/uni + CADUCIDAD
    # El OCR mezcla las columnas, buscar patrón en texto lineal
    patron = re.compile(
        r'([A-Z]{2}\d+[A-Z]*)\s*\n'              # Código (ej: PH200NFB, LB18)
        r'(\d+[,.]\d+)\s*\n'                     # Precio
        r'(\d+[,.]\d+)\s*\n'                     # Cantidad
        r'(\d+[,.]\d+)\s*\n'                     # Importe
        r'([A-Za-záéíóúñÁÉÍÓÚÑ][^\n]+?)\s*\n'  # Descripción
        r'[\d/]+\s*\n'                           # Lote
        r'(\d+[,.]\d+)\s*\n'                     # Cajas
        r'€/uni',                                # Marcador
        re.MULTILINE
    )
    
    for match in patron.finditer(texto):
        codigo, precio, cantidad, importe, descripcion, cajas = match.groups()
        
        # Ignorar muestras gratuitas (precio 0)
        if float(precio.replace(',', '.')) == 0:
            continue
        
        lineas.append({
            'codigo': codigo,
            'articulo': descripcion.strip()[:50],
            'cantidad': int(float(cantidad.replace(',', '.'))),
            'precio_unitario': float(precio.replace(',', '.')),
            'iva': 10,
            'base': round(float(importe.replace(',', '.')), 2),
            'categoria': ''  # Se asignará del diccionario
        })
    
    return lineas


def extraer_lineas_quesos_royca(texto: str) -> List[Dict]:
    """Extrae líneas de facturas QUESOS ROYCA / Comercial Royca - v3.13.
    
    CIF: E06388631
    Productos: Quesos (La Barranquera)
    IVA: 4%
    
    Formato línea (ASCII art):
    QS0002 │QUESO LA BARRANQUERA │ │11,160 │15,60 │ │174,10 │
    """
    lineas = []
    
    # Patrón para líneas de producto (ignorar PORTES)
    patron = re.compile(
        r'(Q[SV]\d+)\s*│\s*'                    # Código (QS0002, QV0027)
        r'([^│]+?)\s*│'                          # Descripción
        r'[^│]*│\s*'                             # PZS (vacío)
        r'(\d+[,.]\d+)\s*│\s*'                   # Unidades/Cantidad
        r'(\d+[,.]\d+)\s*│'                      # Precio
        r'[^│]*│\s*'                             # Dto (vacío)
        r'(\d+[,.]\d+)\s*│',                     # Importe
        re.MULTILINE
    )
    
    for match in patron.finditer(texto):
        codigo, descripcion, cantidad, precio, importe = match.groups()
        
        # Ignorar líneas de PORTES
        if 'PORTE' in descripcion.upper():
            continue
        
        lineas.append({
            'codigo': codigo,
            'articulo': descripcion.strip()[:50],
            'cantidad': int(float(cantidad.replace(',', '.'))),
            'precio_unitario': float(precio.replace(',', '.')),
            'iva': 4,  # Quesos al 4%
            'base': round(float(importe.replace(',', '.')), 2),
            'categoria': 'QUESOS'  # Categoría fija
        })
    
    return lineas


def extraer_lineas_ibarrako_piparrak(texto: str) -> List[Dict]:
    """Extrae líneas de facturas IBARRAKO PIPARRAK - v3.13.
    
    CIF: F20532297
    Productos: Guindillas de Ibarra (piparras)
    IVA: 10%
    Categoría fija: PIPARRAS
    
    Formato nuevo:
    2008 GALON IBARLUR PET 8,00 21,00 0,00 168,00
    
    Formato antiguo (OCR):
    2004  12,00  0,00BOTES GALON 1ª  12,00  144,00
    """
    lineas = []
    
    # Patrón formato nuevo: CODIGO DESCRIPCION CANTIDAD PRECIO DTO IMPORTE
    patron_nuevo = re.compile(
        r'^(\d{4})\s+'                          # Código (4 dígitos)
        r'([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñº\s]+?)\s+'  # Descripción
        r'(\d+[,.]\d+)\s+'                       # Cantidad
        r'(\d+[,.]\d+)\s+'                       # Precio
        r'\d+[,.]\d+\s+'                         # Dto (ignorar)
        r'(\d+[,.]\d+)',                         # Importe
        re.MULTILINE
    )
    
    # Patrón formato antiguo: CODIGO PRECIO DTO DESCRIPCION CANTIDAD IMPORTE
    patron_antiguo = re.compile(
        r'^(\d{4})\s+'                          # Código (4 dígitos)
        r'(\d+[,.]\d+)\s+'                       # Precio
        r'\d+[,.]\d+\s*'                         # Dto (ignorar)
        r'([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñº\s]+?)\s+'  # Descripción
        r'(\d+[,.]\d+)\s+'                       # Cantidad
        r'(\d+[,.]\d+)',                         # Importe
        re.MULTILINE
    )
    
    # Intentar formato nuevo primero
    for match in patron_nuevo.finditer(texto):
        codigo, descripcion, cantidad, precio, importe = match.groups()
        
        lineas.append({
            'codigo': codigo,
            'articulo': descripcion.strip()[:50],
            'cantidad': int(float(cantidad.replace(',', '.'))),
            'precio_unitario': float(precio.replace(',', '.')),
            'iva': 10,
            'base': round(float(importe.replace(',', '.')), 2),
            'categoria': 'PIPARRAS'  # Categoría fija
        })
    
    # Si no hay líneas, intentar formato antiguo
    if not lineas:
        for match in patron_antiguo.finditer(texto):
            codigo, precio, descripcion, cantidad, importe = match.groups()
            
            lineas.append({
                'codigo': codigo,
                'articulo': descripcion.strip()[:50],
                'cantidad': int(float(cantidad.replace(',', '.'))),
                'precio_unitario': float(precio.replace(',', '.')),
                'iva': 10,
                'base': round(float(importe.replace(',', '.')), 2),
                'categoria': 'PIPARRAS'  # Categoría fija
            })
    
    return lineas


def extraer_lineas_ana_caballo(texto: str) -> List[Dict]:
    """Extrae líneas de facturas ANA CABALLO VERMOUTH - v3.13.
    
    CIF: B87925970
    Productos: Vermuts (rojo, blanco, amenities)
    IVA: 21%
    Categoría fija: LICORES Y VERMUS
    
    Formato línea:
    Botella 75 cl. Ana Caballo Vermouth Rojo. L011223 12 15,80 20,00% 151,68
    """
    lineas = []
    
    # Buscar zona de productos (entre DESCRIPCIÓN y Neto:)
    zona_match = re.search(r'DESCRIPCI[ÓO]N\s+CANT\.\s+PRECIO.*?(?=Neto:)', texto, re.DOTALL)
    if not zona_match:
        return lineas
    
    zona = zona_match.group(0)
    
    # Patrón para líneas de producto
    patron = re.compile(
        r'^(.+?)\s+'                            # Descripción
        r'(\d+)\s+'                              # Cantidad
        r'(\d+[,.]\d+)\s+'                       # Precio
        r'(\d+[,.]\d+)%\s+'                      # Dto %
        r'(\d+[,.]\d+)',                         # Neto
        re.MULTILINE
    )
    
    for match in patron.finditer(zona):
        descripcion, cantidad, precio, dto, neto = match.groups()
        
        # Ignorar promocionales (precio 0)
        if float(precio.replace(',', '.')) == 0:
            continue
        
        # Limpiar descripción (quitar lote)
        desc_limpia = re.sub(r'\s*L\d+$', '', descripcion.strip())
        desc_limpia = re.sub(r'\s*\d{6}$', '', desc_limpia)  # Quitar lote tipo 011222
        
        lineas.append({
            'codigo': '',
            'articulo': desc_limpia[:50],
            'cantidad': int(cantidad),
            'precio_unitario': float(precio.replace(',', '.')),
            'iva': 21,
            'base': round(float(neto.replace(',', '.')), 2),
            'categoria': 'LICORES Y VERMUS'  # Categoría fija
        })
    
    return lineas


def extraer_lineas_martin_abenza(texto: str) -> List[Dict]:
    """Extrae líneas de facturas MARTIN ABENZA / El Modesto - v3.13.
    
    NIF: 74305431K
    Productos: Conservas artesanas (alcachofas, piparras, escalivada)
    IVA: 10%
    Categoría fija: CONSERVAS VEGETALES
    
    Formato línea (columnas separadas en OCR):
    CANTIDAD CONCEPTO - REFERENCIA PRECIO IMPORTE
    3                              31,80 95,40 €
    [luego más abajo]
    CAJAS PIPARRAS
    """
    lineas = []
    
    # El formato de MARTIN ABENZA tiene cantidades/precios separados de descripciones
    # Buscar patrón: CANTIDAD + PRECIO + IMPORTE en una zona
    numeros = re.findall(r'^(\d+)\s+(\d+[,.]\d+)\s+(\d+[,.]\d+)\s*€?', texto, re.MULTILINE)
    
    # Buscar descripciones en otra zona (después de DESCUENTO o IVA)
    descripciones = re.findall(r'(CAJA[S]?\s+[A-ZÁÉÍÓÚÑ\s/\d]+|LOTES?\s+CONSERVAS\s+VARIADAS)', texto)
    
    # Filtrar descripciones que no sean "PORTE"
    descripciones = [d for d in descripciones if 'PORTE' not in d.upper()]
    
    # Emparejar números con descripciones
    for i, (cantidad, precio, importe) in enumerate(numeros):
        # Ignorar si es PORTE (generalmente el último)
        if i < len(descripciones):
            descripcion = descripciones[i]
        else:
            descripcion = f"CONSERVA {i+1}"
        
        lineas.append({
            'codigo': '',
            'articulo': descripcion.strip()[:50],
            'cantidad': int(cantidad),
            'precio_unitario': float(precio.replace(',', '.')),
            'iva': 10,
            'base': round(float(importe.replace(',', '.')), 2),
            'categoria': 'CONSERVAS VEGETALES'  # Categoría fija
        })
    
    return lineas


def extraer_lineas_porvaz(texto: str) -> List[Dict]:
    """Extrae líneas de facturas PORVAZ VILAGARCÍA / Conservas Tito - v3.16.
    
    CIF: B36281087
    IBAN: ES63 0049 5368 0625 1628 3321
    Productos: Conservas de marisco (berberechos, mejillones, navajas, zamburiñas)
    IVA: 10%
    Categoría fija: CONSERVAS PESCADO
    
    Formato línea (muy limpio):
    Descripción Cantidad Precio IVA Importe
    BERBERECHO ENLATADO 40/60 RR120 AL 10 4,500 10,0 45,00
    MEJILLON ESCABECHE 8/12 RR120 AL 30 3,800 10,0 114,00
    """
    lineas = []
    
    # Patrón: DESCRIPCION (texto) + CANTIDAD (entero) + PRECIO (decimal coma) + IVA (10,0) + IMPORTE (decimal coma)
    # Descripción puede incluir números como "40/60" o "8/12"
    patron = re.compile(
        r'^([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s\d/]+?)\s+'  # Descripción (empieza con mayúscula)
        r'(\d+)\s+'                               # Cantidad (entero)
        r'(\d+[,]\d{3})\s+'                       # Precio (formato X,XXX)
        r'10[,.]0\s+'                             # IVA siempre 10,0
        r'(\d+[,]\d{2})',                         # Importe (formato XX,XX)
        re.MULTILINE
    )
    
    for match in patron.finditer(texto):
        descripcion, cantidad, precio, importe = match.groups()
        
        lineas.append({
            'codigo': '',
            'articulo': descripcion.strip()[:50],
            'cantidad': int(cantidad),
            'precio_unitario': float(precio.replace(',', '.')),
            'iva': 10,
            'base': round(float(importe.replace(',', '.')), 2),
            'categoria': 'CONSERVAS PESCADO'  # Categoría fija
        })
    
    return lineas


def extraer_lineas_quesos_felix(texto: str) -> List[Dict]:
    """Extrae líneas de facturas QUESOS FELIX / Armando Sanz - v3.19.
    
    CIF: B47440136
    IBAN: ES40 2103 4346 3300 3306 5431
    Productos: Quesos IGP semicurado/curado, Patamulo
    IVA: 4% (quesos)
    Categoría fija: QUESOS
    
    Formato PyPDF2 (orden invertido respecto al visual):
    QUESO IGP FELIX. SEMICURADO GRANDE 1 3,000 14,00 42,00 € -
    QUESO FELIX. Especial PATAMULO GRANDE 4 6,000 15,00 90,00 € -
    
    Orden: DESCRIPCION + UDS + CANTIDAD + PRECIO + IMPORTE + LOTE
    El LOTE está AL FINAL (puede ser "-" o un número como "4170")
    """
    lineas = []
    
    # v3.19: Patrón corregido - LOTE al final
    # DESCRIPCION(QUESO...) + UDS + CANTIDAD + PRECIO + IMPORTE + LOTE
    # Permite guiones y números en la descripción (ej: "QUESO de Autor DORADO. CURADO - 8K")
    patron = re.compile(
        r'(QUESO\s+[\w\s\.\-]+?)\s+'             # Descripción (flexible)
        r'(\d+)\s+'                              # UDS (unidades enteras)
        r'(\d+[,\.]\d{3})\s+'                   # Cantidad (kg con 3 decimales)
        r'(\d+[,\.]\d{2})\s+'                   # Precio
        r'(\d+[,\.]\d{2})\s*€?',                # Importe
        re.IGNORECASE
    )
    
    for match in patron.finditer(texto):
        descripcion, uds, cantidad_kg, precio, importe = match.groups()
        
        lineas.append({
            'codigo': '',
            'articulo': descripcion.strip()[:50],
            'cantidad': float(cantidad_kg.replace(',', '.')),  # kg
            'precio_unitario': float(precio.replace(',', '.')),
            'iva': 4,
            'base': round(float(importe.replace(',', '.')), 2),
            'categoria': 'QUESOS'  # Categoría fija
        })
    
    return lineas


def extraer_lineas_carlos_navas(texto: str) -> List[Dict]:
    """Extrae líneas de facturas CARLOS NAVAS / QUESOS NAVAS - v3.16.
    
    CIF: B37416419
    IBAN: ES62 2100 6153 0402 0001 6597
    Productos: Queso de oveja curado/añejo
    IVA: 4% (quesos), algunos 2%
    Categoría fija: QUESOS
    
    Formato real (columnas separadas):
    Código  Artículo                                Lote    Cantidad  Precio   IVA    Subtotal
    6       QUESO OVEJA INVIERNO 2 AÑOS             0723    9,020     25,860   4,00   233,26
    27      QUESO DE SELECCION ORO 15 MESES CUÑA    2924    2,820     22,590   4,00   63,70
    
    Notas:
    - Código es número de 1-2 dígitos
    - Lote es número de 3-5 dígitos
    - Cantidad tiene 3 decimales (kg)
    - Precio tiene 3 decimales
    - IVA siempre "4,00" o "2,00"
    - Subtotal tiene 2 decimales
    """
    lineas = []
    
    # Patrón para líneas de producto
    # CODIGO + DESCRIPCION(QUESO...) + LOTE + CANTIDAD + PRECIO + IVA + SUBTOTAL
    patron = re.compile(
        r'^(\d{1,2})\s+'                            # Código (1-2 dígitos)
        r'(QUESO[A-ZÁÉÍÓÚÑ\s\d]+?)\s+'              # Descripción (empieza con QUESO)
        r'(\d{3,5})\s+'                             # Lote (3-5 dígitos)
        r'(\d{1,3},\d{3})\s+'                       # Cantidad (X,XXX kg)
        r'(\d{1,2},\d{3})\s+'                       # Precio (XX,XXX)
        r'(\d,\d{2})\s+'                            # IVA (X,XX)
        r'(\d{1,4},\d{2})',                         # Subtotal (XXX,XX)
        re.MULTILINE
    )
    
    for match in patron.finditer(texto):
        codigo, descripcion, lote, cantidad, precio, iva_pct, subtotal = match.groups()
        
        lineas.append({
            'codigo': codigo,
            'articulo': descripcion.strip()[:50],
            'cantidad': float(cantidad.replace(',', '.')),
            'precio_unitario': float(precio.replace(',', '.')),
            'iva': int(float(iva_pct.replace(',', '.'))),
            'base': round(float(subtotal.replace(',', '.')), 2),
            'categoria': 'QUESOS'  # Categoría fija
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


def limpiar_ocr(texto: str) -> str:
    """Limpia problemas comunes de OCR.
    
    - Quita sufijos de lote/fecha: "QUESO - 280624" → "QUESO"
    - Une letras sueltas antes de palabra: "A NTONIO" → "ANTONIO"
    - Normaliza espacios múltiples
    """
    if not texto:
        return texto
    
    resultado = texto
    
    # Quitar sufijos de lote/fecha: " - DDMMYY" o " - NNNNNN" al final
    resultado = re.sub(r'\s+-\s+\d{6}$', '', resultado)
    resultado = re.sub(r'\s+-\s+\d{4}$', '', resultado)
    
    # Unir letra suelta + espacio + palabra que empieza con mayúscula
    # "A NTONIO" → "ANTONIO", "V ERMUT" → "VERMUT"
    # Patrón: letra mayúscula sola (rodeada de espacios o inicio) + espacio + letras
    resultado = re.sub(r'(?<!\S)([A-ZÁÉÍÓÚÑ])\s+([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑa-záéíóúñ]+)', r'\1\2', resultado)
    
    # Repetir para casos múltiples en la misma palabra: "M ERM ELADA" 
    for _ in range(3):
        nuevo = re.sub(r'(?<!\S)([A-ZÁÉÍÓÚÑ])\s+([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑa-záéíóúñ]+)', r'\1\2', resultado)
        if nuevo == resultado:
            break
        resultado = nuevo
    
    # Normalizar espacios múltiples
    resultado = re.sub(r'\s+', ' ', resultado).strip()
    
    return resultado


def buscar_categoria(proveedor: str, articulo: str, indice: Dict, umbral: float = 0.8) -> Tuple[str, int]:
    """
    Busca la categoría de un artículo en el diccionario.
    Retorna (categoria, iva) o ('PENDIENTE', None).
    
    v3.16: Mejoras de búsqueda:
    - Limpieza de OCR (espacios rotos, letras sueltas)
    - Quita sufijos de lote/fecha
    - Búsqueda parcial como fallback
    """
    # Normalizar proveedor para búsqueda
    proveedor_upper = proveedor.upper()
    
    # v3.16: Verificar si hay alias para este proveedor
    proveedor_buscar = PROVEEDOR_ALIAS_DICCIONARIO.get(proveedor_upper, proveedor_upper)
    
    # Buscar proveedor en el índice (matching flexible)
    proveedor_encontrado = None
    for prov in indice.keys():
        if not isinstance(prov, str):
            continue
        if prov in proveedor_buscar or proveedor_buscar in prov:
            proveedor_encontrado = prov
            break
        if similitud(prov, proveedor_buscar) > 0.8:
            proveedor_encontrado = prov
            break
    
    if not proveedor_encontrado:
        # v3.19: Fallback - usar categoría por defecto
        categoria_default = obtener_categoria_default(proveedor, articulo)
        return categoria_default, None
    
    # v3.16: Limpiar artículo antes de buscar
    articulo_limpio = limpiar_ocr(articulo)
    articulo_upper = articulo_limpio.upper()
    
    # Buscar artículo
    articulos_prov = indice[proveedor_encontrado]
    mejor_match = None
    mejor_similitud = 0
    
    # Intento 1: Similitud con artículo limpio
    for item in articulos_prov:
        item_upper = item['articulo'].upper()
        sim = similitud(articulo_upper, item_upper)
        if sim > mejor_similitud:
            mejor_similitud = sim
            mejor_match = item
    
    if mejor_match and mejor_similitud >= umbral:
        return mejor_match['categoria'], mejor_match['iva']
    
    # Intento 2: Búsqueda parcial - si el artículo del diccionario contiene el extraído
    # Útil para "Chorizos 240g" vs "Chorizos lalinense 240g"
    if len(articulo_upper) >= 8:  # Solo si tiene longitud razonable
        for item in articulos_prov:
            item_upper = item['articulo'].upper()
            # Si el extraído está contenido en el del diccionario
            if articulo_upper in item_upper:
                return item['categoria'], item['iva']
            # Si el del diccionario está contenido en el extraído
            if item_upper in articulo_upper:
                return item['categoria'], item['iva']
    
    # Intento 3: Buscar por palabras clave principales (sin números ni tamaños)
    palabras_articulo = re.findall(r'[A-ZÁÉÍÓÚÑ]{4,}', articulo_upper)
    if palabras_articulo:
        for item in articulos_prov:
            item_upper = item['articulo'].upper()
            # Si todas las palabras principales del artículo están en el diccionario
            coincidencias = sum(1 for p in palabras_articulo if p in item_upper)
            if coincidencias >= len(palabras_articulo) * 0.7:  # 70% de palabras coinciden
                return item['categoria'], item['iva']
    
    # v3.19: Fallback - usar categoría por defecto basada en proveedor/artículo
    categoria_default = obtener_categoria_default(proveedor, articulo)
    if categoria_default != 'PENDIENTE':
        return categoria_default, None  # IVA se asignará después
    
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
    # v3.27 - LA MOLIENDA VERDE (antes del genérico)
    elif 'MOLIENDA' in proveedor_upper or 'B06936140' in texto:
        lineas_raw = extraer_lineas_molienda_verde(texto)
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
        # v3.31 - Extraer total específico para SEGURMA (formato multiline)
        # El patrón genérico no funciona porque "Total\n48,23\n€" tiene saltos de línea
        total_match = re.search(r'(?<!Sub)Total[\s\n]*(\d+[.,]\d{2})[\s\n]*€', texto, re.IGNORECASE)
        if total_match:
            factura.total = float(total_match.group(1).replace(',', '.'))
    # v3.29 - MRM (Industrias Cárnicas MRM-2)
    elif 'MRM' in proveedor_upper or 'A80280845' in texto:
        lineas_raw = extraer_lineas_mrm(texto)
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
    # v3.23 - Corregido: ser más específico para no capturar "HNOS ORTEGA"
    elif 'BENJAMIN ORTEGA' in proveedor_upper or 'ORTEGA ALONSO' in proveedor_upper or '09342596L' in texto:
        lineas_raw = extraer_lineas_alquiler_ortega(texto)
    # v3.23 - Corregido: ser más específico para no capturar otros FERNANDEZ
    elif 'JAIME FERNANDEZ' in proveedor_upper or 'FERNANDEZ MORENO' in proveedor_upper or '07219971H' in texto:
        lineas_raw = extraer_lineas_alquiler_fernandez(texto)
    # v3.23 - CONTROLPLAGA / Javier Alborés Rey (desinsectación)
    elif 'CONTROLPLAGA' in proveedor_upper or 'ALBORES' in proveedor_upper or 'ARBORES' in proveedor_upper or '11812266' in texto:
        lineas_raw = extraer_lineas_controlplaga(texto)
    # v3.23 - PANRUJE / Rosquillas La Ermita
    elif 'PANRUJE' in proveedor_upper or 'ERMITA' in proveedor_upper or 'B13858014' in texto or 'B-13.858.014' in texto:
        lineas_raw = extraer_lineas_panruje(texto)
    # v3.23 - ANGEL Y LOLI / Alfarería
    elif 'ANGEL' in proveedor_upper or 'LOLI' in proveedor_upper or 'ALFARERIA' in proveedor_upper or '75727068' in texto:
        lineas_raw = extraer_lineas_angel_y_loli(texto)
    # v3.23 - QUESOS DEL CATI
    elif 'CATI' in proveedor_upper or 'F12499455' in texto or 'F-12499455' in texto:
        lineas_raw = extraer_lineas_quesos_cati(texto)
    # v3.24 - ISTA (consumo agua)
    elif 'ISTA' in proveedor_upper or 'A50090133' in texto:
        lineas_raw = extraer_lineas_ista(texto)
    # v3.24 - BIELLEBI (taralli italiano)
    elif 'BIELLEBI' in proveedor_upper or '06089700725' in texto:
        lineas_raw = extraer_lineas_biellebi(texto)
    # v3.24 - EMBUTIDOS FERRIOL (chacinas Mallorca)
    elif 'FERRIOL' in proveedor_upper or 'FERRIOL' in texto.upper() or 'B57955098' in texto:
        lineas_raw = extraer_lineas_ferriol(texto)
    # v3.24 - ABBATI CAFFE
    elif 'ABBATI' in proveedor_upper or 'B82567876' in texto:
        lineas_raw = extraer_lineas_abbati(texto)
    # v3.24 - BODEGAS MUÑOZ MARTÍN
    elif 'MUÑOZ' in proveedor_upper or 'MUNOZ' in proveedor_upper or 'E83182683' in texto or 'E-83182683' in texto:
        lineas_raw = extraer_lineas_munoz_martin(texto)
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
    # v3.11 - MRM / Industrias Cárnicas MRM-2 (patés, mousses, salmón)
    elif 'MRM' in proveedor_upper or 'A80280845' in texto:
        lineas_raw = extraer_lineas_mrm(texto)
    # v3.11 - DISBER / Grupo Disber (vinos, conservas)
    elif 'DISBER' in proveedor_upper or 'B46144424' in texto:
        lineas_raw = extraer_lineas_disber(texto)
    # v3.12 - TRUCCO COPIAS / Isaac Rodríguez Pacha (imprenta)
    elif 'TRUCCO' in proveedor_upper or 'ISAAC RODRIGUEZ' in proveedor_upper or '05247386M' in texto:
        lineas_raw = extraer_lineas_trucco(texto)
    # v3.12 - LA BARRA DULCE (pastelería)
    elif 'BARRA DULCE' in proveedor_upper or 'B19981141' in texto:
        lineas_raw = extraer_lineas_barra_dulce(texto)
    # v3.12 - GRUPO TERRITORIO CAMPERO (patatas fritas)
    elif 'CAMPERO' in proveedor_upper or 'TERRITORIO' in proveedor_upper or 'B16690141' in texto:
        lineas_raw = extraer_lineas_grupo_campero(texto)
    # v3.12 - ZUBELZU PIPARRAK (guindillas y mousse)
    elif 'ZUBELZU' in proveedor_upper or 'B75079608' in texto:
        lineas_raw = extraer_lineas_zubelzu(texto)
    # v3.13 - PRODUCTOS ADELL / Croquellanas
    elif 'ADELL' in proveedor_upper or 'CROQUELLANAS' in proveedor_upper or 'B12711636' in texto:
        lineas_raw = extraer_lineas_productos_adell(texto)
    # v3.13 - ECOFICUS
    elif 'ECOFICUS' in proveedor_upper or 'B10214021' in texto:
        lineas_raw = extraer_lineas_ecoficus(texto)
    # v3.13 - QUESOS ROYCA
    elif 'ROYCA' in proveedor_upper or 'E06388631' in texto:
        lineas_raw = extraer_lineas_quesos_royca(texto)
    # v3.13 - IBARRAKO PIPARRAK
    elif 'IBARRAKO' in proveedor_upper or 'F20532297' in texto:
        lineas_raw = extraer_lineas_ibarrako_piparrak(texto)
    # v3.13 - ANA CABALLO VERMOUTH
    elif 'ANA CABALLO' in proveedor_upper or 'B87925970' in texto:
        lineas_raw = extraer_lineas_ana_caballo(texto)
    # v3.13 - MARTIN ABENZA / El Modesto
    elif 'MARTIN' in proveedor_upper and ('ABENZA' in proveedor_upper or 'ARBENZA' in proveedor_upper) or 'MODESTO' in proveedor_upper or '74305431K' in texto:
        lineas_raw = extraer_lineas_martin_abenza(texto)
    # v3.15 - QUESOS FELIX / Armando Sanz
    elif 'QUESOS' in proveedor_upper and 'FELIX' in proveedor_upper or 'ARMANDO SANZ' in proveedor_upper or 'B47440136' in texto:
        lineas_raw = extraer_lineas_quesos_felix(texto)
    # v3.15 - PANRUJE / Rosquillas La Ermita
    elif 'PANRUJE' in proveedor_upper or 'ROSQUILLAS LA ERMITA' in proveedor_upper or 'B13858014' in texto:
        lineas_raw = extraer_lineas_panruje(texto)
    # v3.15/v3.16 - CARLOS NAVAS / Quesería Carlos Navas (incluye alias QUESERIA NAVAS)
    elif 'CARLOS NAVAS' in proveedor_upper or 'QUESERIA NAVAS' in proveedor_upper or 'QUESOS NAVAS' in proveedor_upper or 'B37416419' in texto:
        lineas_raw = extraer_lineas_carlos_navas(texto)
    # v3.16 - PORVAZ / Conservas Tito
    elif 'PORVAZ' in proveedor_upper or 'TITO' in proveedor_upper or 'B36281087' in texto:
        lineas_raw = extraer_lineas_porvaz(texto)
    
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
    
    # v3.23 - Primero verificar si hay un alias de salida
    for alias, nombre_salida in PROVEEDOR_NOMBRE_SALIDA.items():
        if alias in proveedor_upper:
            factura.proveedor_normalizado = nombre_salida
            break
    
    # Si no hay alias, buscar en el índice del diccionario
    if not factura.proveedor_normalizado:
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
    
    # v3.21 - Validación de cuadre
    lineas_dict = [{'base': l.base, 'iva': l.iva} for l in factura.lineas]
    factura.cuadre = validar_cuadre(lineas_dict, factura.total)
    
    # Añadir alerta si hay descuadre significativo
    if factura.cuadre.startswith('DESCUADRE'):
        factura.alertas.append('CUADRE_PENDIENTE')
    
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
                    'BASE (€)': linea.base,
                    'TOTAL FAC': f.total or '',  # v3.21
                    'CUADRE': f.cuadre  # v3.21
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
                'BASE (€)': f.total or '',
                'TOTAL FAC': f.total or '',  # v3.21
                'CUADRE': f.cuadre  # v3.21
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
        
        # v3.21 - Estadísticas de cuadre
        cuadre_ok = sum(1 for fa in facturas if fa.cuadre == 'OK')
        cuadre_descuadre = sum(1 for fa in facturas if fa.cuadre.startswith('DESCUADRE'))
        cuadre_sin_total = sum(1 for fa in facturas if fa.cuadre == 'SIN_TOTAL')
        cuadre_sin_lineas = sum(1 for fa in facturas if fa.cuadre == 'SIN_LINEAS')
        
        f.write(f"\n  VALIDACIÓN CUADRE (v3.21):\n")
        f.write(f"    OK:          {cuadre_ok}\n")
        f.write(f"    DESCUADRE:   {cuadre_descuadre}\n")
        f.write(f"    SIN_TOTAL:   {cuadre_sin_total}\n")
        f.write(f"    SIN_LINEAS:  {cuadre_sin_lineas}\n")
        
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
    
    # Ruta por defecto del diccionario (ajustar según tu sistema)
    DICCIONARIO_DEFAULT = r"C:\_ARCHIVOS\TRABAJO\Facturas\ParsearFacturas-main\DiccionarioProveedoresCategoria.xlsx"
    
    parser = argparse.ArgumentParser(description='Migración histórico 2025 v3.24')
    parser.add_argument('--input', '-i', required=True, help='Carpeta de facturas')
    parser.add_argument('--output', '-o', default=None, help='Archivo Excel de salida (default: outputs/Facturas_[trimestre].xlsx)')
    parser.add_argument('--diccionario', '-d', default=DICCIONARIO_DEFAULT, 
                        help=f'DiccionarioProveedoresCategoria.xlsx (default: {DICCIONARIO_DEFAULT})')
    parser.add_argument('--yaml', '-y', default=None, help='Carpeta de YAMLs (legacy, no usar)')
    
    args = parser.parse_args()
    
    # Verificar que el diccionario existe
    if not Path(args.diccionario).exists():
        print(f"❌ ERROR: No se encuentra el diccionario: {args.diccionario}")
        print(f"   Usa -d para especificar la ruta correcta")
        sys.exit(1)
    
    print("="*60)
    print("MIGRACIÓN HISTÓRICO 2025 - v3.27")
    print("="*60)
    
    # Determinar carpeta outputs (relativa al script)
    script_dir = Path(__file__).parent
    outputs_dir = script_dir / 'outputs'
    outputs_dir.mkdir(exist_ok=True)
    
    # Determinar nombre de archivo de salida
    if args.output:
        # v3.22: Si se pasa un nombre sin ruta (ej: "resultado.xlsx"), guardarlo en outputs/
        output_path = Path(args.output)
        if not output_path.is_absolute() and output_path.parent == Path('.'):
            ruta_excel = outputs_dir / output_path.name
        else:
            ruta_excel = output_path
    else:
        # Extraer trimestre del nombre de la carpeta de entrada
        carpeta_input = Path(args.input).name.upper()
        if '1' in carpeta_input and 'TRI' in carpeta_input:
            trimestre = '1T25'
        elif '2' in carpeta_input and 'TRI' in carpeta_input:
            trimestre = '2T25'
        elif '3' in carpeta_input and 'TRI' in carpeta_input:
            trimestre = '3T25'
        elif '4' in carpeta_input and 'TRI' in carpeta_input:
            trimestre = '4T25'
        else:
            trimestre = datetime.now().strftime('%Y%m%d')
        ruta_excel = outputs_dir / f'Facturas_{trimestre}.xlsx'
    
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
    total_filas = generar_excel_historico(facturas, ruta_excel)
    print(f"   {ruta_excel}: {total_filas} filas")
    
    ruta_log = outputs_dir / f"log_migracion_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
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
