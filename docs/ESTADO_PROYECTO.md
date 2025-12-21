# ESTADO DEL PROYECTO - ParsearFacturas

**Última actualización:** 2025-12-21
**Versión actual:** v4.4

---

## 📊 MÉTRICAS ACTUALES

### v4.4 - Resultados (21/12/2025)

| Trimestre | Facturas | Cuadre OK | % | Con Líneas | Importe |
|-----------|----------|-----------|---|------------|---------|
| 1T25 | 252 | 167 | **66.3%** | 194 (77%) | 48,173€ |
| 2T25 | 307 | 165 | **53.7%** | 231 (75%) | 46,720€ |
| 3T25 | 161 | 86 | **53.4%** | 119 (74%) | 35,539€ |
| 4T25 | 183 | ~95 | **~52%** | ~120 | pendiente |
| **TOTAL** | **903** | **~513** | **~57%** | ~664 | ~130,000€ |

### Evolución histórica

| Versión | Fecha | Cuadre 1T25 | Cambio principal |
|---------|-------|-------------|------------------|
| v3.5 | 09/12/2025 | 42% | Baseline - 70 extractores monolíticos |
| v3.6 | 10/12/2025 | 47% | +6 extractores servicios |
| v4.0 | 18/12/2025 | 54% | Arquitectura modular @registrar |
| v4.2 | 19/12/2025 | 56% | +12 extractores, bug IVA 0 |
| v4.3 | 20/12/2025 | 60% | +6 extractores OCR |
| **v4.4** | **21/12/2025** | **66%** | **+12 extractores sesión intensiva** |

**Mejora total:** 42% → 66% = **+24 puntos** (+57% relativo)

---

## ✅ SESIÓN 2025-12-21: 12 EXTRACTORES NUEVOS

### Extractores creados

| # | Proveedor | CIF | Facturas | Método | Estado |
|---|-----------|-----|----------|--------|--------|
| 1 | QUESERIA ZUCCA | B42861948 | 7/7 | pdfplumber | ✅ |
| 2 | PANRUJE | B13858014 | 6/6 | pdfplumber | ✅ |
| 3 | GRUPO DISBER | B43489039 | 4/4 | pdfplumber | ✅ |
| 4 | LIDL | A60195278 | 5/5 | pdfplumber | ✅ |
| 5 | LA ROSQUILLERIA | B86556081 | 7/7 | OCR | ✅ |
| 6 | GADITAUN | 34007216Z | 5/5 | OCR | ✅ |
| 7 | DE LUIS SABORES UNICOS | B87893681 | 5/5 | híbrido | ✅ |
| 8 | MANIPULADOS ABELLAN | B30243737 | 6/6 | OCR | ✅ |
| 9 | ECOMS/DIA | B72738602 | 6/8 | híbrido | ✅ |
| 10 | MARITA COSTA | 48207369J | 9/9 | pdfplumber | ✅ |
| 11 | SERRÍN NO CHAN | B87214755 | 7/7 | pdfplumber | ✅ |
| 12 | FISHGOURMET | B85975126 | 5/5 | OCR | ✅ |
| **TOTAL** | | | **72/74** | | **97%** |

### Archivos generados

```
extractores/
├── zucca.py              # Quesería artesanal
├── panruje.py            # Panadería rosquillas
├── grupo_disber.py       # Distribuidor alimentación
├── lidl.py               # Supermercado
├── la_rosquilleria.py    # Rosquillas El Torro (OCR)
├── gaditaun.py           # Conservas Cádiz (OCR)
├── de_luis.py            # Gourmet Madrid (híbrido)
├── manipulados_abellan.py # Conservas vegetales (OCR)
├── ecoms.py              # DIA tickets (híbrido)
├── marita_costa.py       # AOVE y gourmet
├── serrin_no_chan.py     # Ultramarinos gallegos
├── fishgourmet.py        # Ahumados pescado (OCR)
└── __init__.py           # Actualizado con imports
```

---

## ⚠️ PROBLEMAS PENDIENTES

### Por tipo de error (basado en logs 21/12/2025)

| Error | Cantidad | Proveedores principales |
|-------|----------|------------------------|
| FECHA_PENDIENTE | ~40 | BM tickets, OPENAI, CELONIS, ANTHROPIC |
| SIN_TOTAL | ~25 | LA PURISIMA, VIRGEN SIERRA, QUESOS ROYCA |
| DESCUADRE | ~20 | PIFEMA, SILVA CORDERO, INMAREPRO |
| CIF_PENDIENTE | ~15 | Proveedores nuevos sin dar de alta |
| SIN_LINEAS | ~10 | GRUPO KUAI, LA LLEIDIRIA |

### Proveedores prioritarios para próxima sesión

| Proveedor | Facturas | Error | Impacto |
|-----------|----------|-------|---------|
| **JIMELUZ** | 14 | SIN_TOTAL/DESCUADRE | ALTO |
| **BM tickets** | 12 | FECHA_PENDIENTE | MEDIO |
| **PIFEMA** | 4 | DESCUADRE ~100€ | MEDIO |
| **SILVA CORDERO** | 4 | DESCUADRE | BAJO |

---

## 📋 SESIONES ANTERIORES

### v4.3 - Sesión 20/12/2025
- +6 extractores: MANIPULADOS ABELLAN, LA ROSQUILLERIA, FABEIRO, KINEMA, SILVA CORDERO, ARTESANOS MOLLETE
- 38 facturas validadas

### v4.2 - Sesión 19/12/2025 tarde
- +6 extractores: ISTA, CVNE, QUESOS FELIX, MIGUEZ CAL, LAVAPIES, MARTIN ABENZA
- Bug IVA 0 corregido

### v4.1 - Sesión 19/12/2025 mañana
- BM refactorizado completo
- +4: ECOFICUS, SABORES PATERNA, LA BARRA DULCE

### v4.0 - Sesión 18/12/2025
- Arquitectura modular implementada
- Sistema @registrar funcionando
- FABEIRO nuevo

---

## 🔧 DECISIONES TÉCNICAS VIGENTES

1. **pdfplumber SIEMPRE** - Preferido sobre pypdf/PyPDF2
2. **OCR solo para escaneados** - Tesseract con pdf2image
3. **IVA 0 válido** - Para portes y conceptos exentos
4. **Formato europeo:** `_convertir_europeo()` para números con coma
5. **Tolerancia cuadre:** 0.10€
6. **1 artículo = 1 línea** - SIEMPRE líneas individuales
7. **Portes:** Distribuir proporcionalmente, nunca línea separada
8. **Registro automático:** Decorador `@registrar()` en cada extractor

---

## 📝 CHANGELOG

| Versión | Fecha | Cambios |
|---------|-------|---------|
| **v4.4** | **2025-12-21** | **+12 extractores: ZUCCA, PANRUJE, DISBER, LIDL, ROSQUILLERIA, GADITAUN, DE LUIS, ABELLAN, ECOMS, MARITA COSTA, SERRIN, FISHGOURMET. 72 facturas validadas. 66% cuadre 1T25.** |
| v4.3 | 2025-12-20 | +6 extractores OCR. 38 facturas. 60% cuadre. |
| v4.2 | 2025-12-19 tarde | +6 extractores. Bug IVA 0. 56% cuadre. |
| v4.1 | 2025-12-19 mañana | BM refactorizado. +4 extractores. |
| v4.0 | 2025-12-18 | Arquitectura modular. Sistema @registrar. |
| v3.41 | 2025-12-12 | Fix FELISA, CERES, MARTIN ABENZA. |
| v3.5 | 2025-12-09 | Baseline: 42% cuadre. |

---

*Última actualización: 21/12/2025 - Sesión intensiva 12 extractores*
