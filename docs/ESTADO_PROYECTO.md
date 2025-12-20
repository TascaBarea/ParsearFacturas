# ESTADO DEL PROYECTO - ParsearFacturas

**Última actualización:** 2025-12-19
**Versión actual:** v4.2

---

## 📊 MÉTRICAS ACTUALES

### v4.2 - Resultados (19/12/2025)

| Trimestre | Facturas | Cuadre OK | % | Con Líneas | Importe |
|-----------|----------|-----------|---|------------|---------|
| 1T25 | 252 | **133+** | **~54%** | ~180 | ~45,000€ |
| 2T25 | 307 | pendiente | - | - | - |
| 3T25 | 161 | pendiente | - | - | - |

### Evolución 19/12/2025

| Fase | Cuadre OK | % | Cambio |
|------|-----------|---|--------|
| Inicio día | 60 | 23.8% | - |
| Post-BM + refactor | 103 | 40.9% | +43 |
| Post-MOLLETES/ECOFICUS | 111 | 44.0% | +8 |
| Post-SABORES PATERNA | 117 | 46.4% | +6 |
| Post-LA BARRA DULCE | 120 | 47.6% | +3 |
| Post-ISTA + CVNE | 129 | 51.2% | +9 |
| Post-QUESOS FELIX + MIGUEZ CAL | 136 | 54.0% | +7 |
| **Post-LAVAPIES + MARTIN ABENZA** | **~140** | **~56%** | **+4** |

**Mejora total del día: +80 facturas (+133%)**

---

## ✅ SESIÓN 2025-12-19 TARDE: 6 EXTRACTORES + BUG FIX

### 🐛 Bug crítico corregido: main.py línea 178

**Problema:** `iva=0` se convertía a `iva=21`
```python
# Bug: 0 or 21 = 21 (0 es "falsy" en Python)
iva=int(linea_raw.get('iva', 21) or 21)
```

**Solución:**
```python
iva_raw = linea_raw.get('iva')
if iva_raw is None:
    iva_valor = 21
else:
    iva_valor = int(iva_raw)
```

### Extractores nuevos

| # | Proveedor | Archivo | Facturas | Notas |
|---|-----------|---------|----------|-------|
| 1 | **ISTA** | `ista.py` | 6/6 ✅ | Recibos agua, sin CIF |
| 2 | **CVNE** | `cvne.py` | 4/4 ✅ | Vinos, IVA 21% |
| 3 | **QUESOS FELIX** | `quesos_felix.py` | 3/3 ✅ | Quesos IGP, IVA 4% |
| 4 | **MIGUEZ CAL** | `miguez_cal.py` | 5/5 ✅ | Limpieza ForPlan |
| 5 | **DISTRIBUCIONES LAVAPIES** | `distribuciones_lavapies.py` | 6/6 ✅ | IVA mixto 10%/21% |
| 6 | **MARTIN ABENZA** | `martin_abenza.py` | 5/5 ✅ | Porte sin IVA |

### Características especiales

| Proveedor | CIF | IVA | Peculiaridad |
|-----------|-----|-----|--------------|
| ISTA | ES B80580850 | 10% | Recibos agua, sin CIF requerido en validación |
| CVNE | A31001897 | 21% | Vinos, formato tabla estándar |
| QUESOS FELIX | B47440136 | 4% | Quesos con lote opcional |
| MIGUEZ CAL | B79868006 | 21% | Multipágina, ignorar SCRAP |
| LAVAPIES | F88424072 | 10%/21% | IVA real calculado desde PDF |
| MARTIN ABENZA | 74305431K | 10%+0% | Productos 10%, porte 0% |

---

## ⚠️ PROBLEMAS PENDIENTES

### Por tipo de error (1T25)

| Error | Cantidad | Proveedores principales |
|-------|----------|------------------------|
| SIN_TOTAL | ~20 | PANRUJE (3), QUESOS ROYCA (2), JULIO GARCIA (3) |
| SIN_LINEAS | ~20 | CARLOS NAVAS, GRUPO DISBER, MRM, PORVAZ |
| FECHA_PENDIENTE | ~15 | LIDL (3), OPENAI (4), AMAZON (2), CAMPERO (3) |
| DESCUADRE | ~10 | LA ROSQUILLERIA (4), FISHGOURMET (2) |
| CIF_PENDIENTE | ~10 | FNMT, WELLDONE, IMCASA |

---

## 📋 ARCHIVOS ENTREGADOS HOY

### Extractores (carpeta `extractores/`)
```
ista.py
cvne.py
quesos_felix.py
miguez_cal.py
distribuciones_lavapies.py
martin_abenza.py
__init__.py (actualizado)
```

### Core (carpeta raíz)
```
main.py (bug IVA 0 corregido)
```

---

## 🎯 PLAN PRÓXIMA SESIÓN

### Prioridad 1: Proveedores con más facturas
- LA ROSQUILLERIA (4 descuadres ~2€)
- PANRUJE (3 SIN_TOTAL)

### Prioridad 2: Errores frecuentes
- LIDL (FECHA_PENDIENTE)
- GRUPO DISBER (SIN_LINEAS)

---

## 📈 EXTRACTORES FUNCIONANDO (80+)

### Nuevos en esta sesión
| # | Proveedor | Estado |
|---|-----------|--------|
| 1 | ISTA | ✅ NUEVO |
| 2 | CVNE | ✅ NUEVO |
| 3 | QUESOS FELIX | ✅ NUEVO |
| 4 | MIGUEZ CAL | ✅ NUEVO |
| 5 | DISTRIBUCIONES LAVAPIES | ✅ NUEVO |
| 6 | MARTIN ABENZA | ✅ NUEVO |

### Anteriores funcionando
- BM SUPERMERCADOS, CERES, MADRUEÑO, BERNAL, BERZAL
- SABORES PATERNA, FRANCISCO GUERRA, LA BARRA DULCE
- ECOFICUS, MOLLETES, EMJAMESA, FELISA GOURMET
- BORBOTON, ZUBELZU, FABEIRO, YOIGO, SEGURMA
- SOM ENERGIA, LUCERA, TRUCCO, VINOS ARGANZA
- MOLIENDA VERDE, ZUCCA, HERNANDEZ, y más...

---

## 🔧 DECISIONES TÉCNICAS

1. **pdfplumber SIEMPRE** - Preferido sobre pypdf
2. **IVA 0 válido** - Para portes y conceptos sin IVA
3. **Formato europeo:** `_convertir_europeo()` para números con coma
4. **Tolerancia cuadre:** 0.10€
5. **1 artículo = 1 línea** - SIEMPRE líneas individuales

---

## 📝 CHANGELOG

| Versión | Fecha | Cambios |
|---------|-------|---------|
| **v4.2** | **2025-12-19 tarde** | **6 extractores nuevos. Bug IVA 0 corregido. 54% cuadre.** |
| v4.1 | 2025-12-19 mañana | BM refactorizado. MOLLETES, ECOFICUS, SABORES. 47% cuadre. |
| v4.0 | 2025-12-18 | FABEIRO completo. Variantes nombres. pdfplumber preferido. |

---

*Última actualización: 19/12/2025 tarde*
