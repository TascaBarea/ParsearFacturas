# ESTADO DEL PROYECTO - ParsearFacturas

**Última actualización:** 2025-12-18
**Versión actual:** v3.57 → **REFACTORIZANDO A v4.0**

---

## 🔄 REFACTORIZACIÓN EN CURSO

> **IMPORTANTE:** El proyecto está siendo refactorizado de un monolito de 7,618 líneas a una estructura modular.
> 
> Ver detalles en: `docs/PLAN_REFACTORIZACION.md`

### Resumen del cambio

| Aspecto | Antes (v3.57) | Después (v4.0) |
|---------|---------------|----------------|
| Archivos | 1 (7,618 líneas) | ~80 archivos |
| Extractores | 70 funciones mezcladas | 70 archivos independientes |
| Añadir extractor | Editar archivo 7000+ líneas | Crear 1 archivo nuevo |
| Debugging | Buscar en 7000 líneas | Abrir archivo específico |
| Duplicados | Sin control | Detección automática |

---

## 📊 MÉTRICAS ACTUALES

### v3.57 - Resultados (18/12/2025)

| Trimestre | Facturas | Con líneas | % | Líneas | IBANs |
|-----------|----------|------------|---|--------|-------|
| 1T25 | 252 | ~210 | ~83% | ~800 | ~130 |
| 2T25 | 307 | ~225 | ~73% | ~830 | ~120 |
| **Total** | **559** | **~435** | **~78%** | **~1630** | **~250** |

### Evolución

| Versión | Fecha | 1T25 % | Cambio |
|---------|-------|--------|--------|
| v3.53 | 14/12 | 64.3% | - |
| v3.54 | 15/12 | 78.6% | +14.3% |
| v3.55 | 16/12 | 82.5% | +3.9% |
| v3.56 | 17/12 | ~85% | +2.5% |
| **v3.57** | **18/12** | **~83%** | Fix JIMELUZ/MADRUEÑO |

**Mejora total v3.53→v3.57: +18.7%**

---

## ✅ SESIÓN 2025-12-18: ANÁLISIS + REFACTORIZACIÓN

### Análisis del código realizado

| Métrica | Valor |
|---------|-------|
| Total líneas | 7,618 |
| Total funciones | 97 |
| Extractores | 70 |
| Líneas en extractores | ~4,600 (60%) |
| Función duplicada | `extraer_lineas_mrm` (líneas 3774 y 5539) |

### Problemas detectados

| Problema | Impacto | Solución v4.0 |
|----------|---------|---------------|
| Monolito 7,618 líneas | Difícil mantener | Dividir en módulos |
| 70+ elif cascada | Propenso errores | Registro automático |
| Función MRM duplicada | Bug silencioso | Eliminar duplicado |
| Sin anti-duplicados | Riesgo contable | Registro facturas |
| Sin tests individuales | Difícil validar | Script test |

### Cambios v3.57

1. **JIMELUZ**: Nuevo extractor OCR con doble estrategia (líneas + tabla IVA)
2. **LICORES MADRUEÑO**: Añadido patrón "TOTAL €:" + fallback robusto
3. **Documentación**: Creados PLAN_REFACTORIZACION.md y COMO_AÑADIR_EXTRACTOR.md

---

## ⚠️ PROBLEMAS PENDIENTES

### Por proveedor (prioritarios)

| Proveedor | Facturas | Error | Notas |
|-----------|----------|-------|-------|
| **JIMELUZ** | ~18 | CUADRE_PENDIENTE | v3.57 mejora OCR, algunos tickets muy malos |
| **SOM ENERGIA** | 5 | CUADRE_PENDIENTE | Investigar |
| **MADRUEÑO** | 3 | SIN_TOTAL | Problema Windows vs Linux |

### Por tipo de error (estimado 2T25)

| Error | Cantidad aprox. |
|-------|-----------------|
| SIN_LINEAS | ~50 |
| CUADRE_PENDIENTE | ~25 |
| CIF_PENDIENTE | ~25 |
| IBAN_PENDIENTE | ~20 |
| FECHA_PENDIENTE | ~15 |

---

## 📈 PROVEEDORES CON EXTRACTOR (70)

Ver lista completa en: `docs/PROVEEDORES.md`

### Añadidos/Arreglados v3.57

| # | Proveedor | Cambio |
|---|-----------|--------|
| 1 | JIMELUZ | Nuevo extractor OCR con tabla IVA |
| 2 | LICORES MADRUEÑO | Fix extracción total |

---

## 🎯 PLAN REFACTORIZACIÓN

### Fases

| Fase | Sesiones | Estado |
|------|----------|--------|
| 1. Estructura | 1 | ⏳ EN CURSO |
| 2. Núcleo | 1 | ⏳ |
| 3. Sistema extractores | 1 | ⏳ |
| 4. Migración 70 extractores | 2 | ⏳ |
| 5. Salidas + main | 1 | ⏳ |
| 6. Robustez | 1 | ⏳ |
| **TOTAL** | **7-9** | |

Ver detalle en: `docs/PLAN_REFACTORIZACION.md`

---

## 📁 ARCHIVOS DEL PROYECTO

### Estructura actual
```
ParsearFacturas-main/
├── src/migracion/
│   ├── migracion_historico_2025_v3_57.py  ← VERSIÓN ACTUAL
│   └── outputs/
│       ├── Facturas_1T25.xlsx
│       ├── Facturas_2T25.xlsx
│       └── log_migracion_*.txt
├── docs/
│   ├── ESTADO_PROYECTO.md      ← ESTE ARCHIVO
│   ├── LEEME_PRIMERO.md
│   ├── PROVEEDORES.md
│   ├── PLAN_REFACTORIZACION.md ← NUEVO
│   └── COMO_AÑADIR_EXTRACTOR.md ← NUEVO
└── DiccionarioProveedoresCategoria.xlsx
```

### Estructura destino (v4.0)
```
ParsearFacturas-main/
├── main.py
├── config/
├── extractores/     ← 70 archivos
├── nucleo/
├── salidas/
├── datos/
├── tests/
├── docs/
└── legacy/          ← Backup v3.57
```

---

## 📝 CHANGELOG

| Versión | Fecha | Cambios |
|---------|-------|---------|
| **v3.57** | **2025-12-18** | **JIMELUZ OCR tabla IVA. MADRUEÑO fix total. Inicio refactorización v4.0** |
| v3.56 | 2025-12-17 | ECOMS nuevo, BORBOTON/MARITA fix total. ~78% global |
| v3.55 | 2025-12-16 | OCR: IBARRAKO, ROSQUILLERIA, ABELLAN. Auditoría código. 82.5% 1T25 |
| v3.54 | 2025-12-15 | LIDL nuevo, BORBOTON/FELISA/LAVAPIES/ZUBELZU/MUÑOZ MARTIN. 78.6% |
| v3.53 | 2025-12-14 | pdfplumber + Tesseract OCR base. 64.3% |

---

## 🔑 DECISIONES TÉCNICAS

1. **PDF extractor:** pypdf principal → pdfplumber fallback → OCR (Tesseract)
2. **OCR preprocesado:** Resolución 300dpi, escala grises, contraste x2
3. **Parche Windows:** Búsqueda importes sin coma decimal (7740 → 77.40)
4. **Portes:** NUNCA línea aparte, siempre repartidos proporcionalmente
5. **Tolerancia cuadre:** 0.05€
6. **Orden patrones total:** Específicos ANTES de genéricos
7. **v4.0 - Registro extractores:** Decorador `@registrar('PROVEEDOR')`
8. **v4.0 - Anti-duplicados:** PROVEEDOR + FECHA + TOTAL en Excel

---

*Última actualización: 18/12/2025 - Sesión análisis + inicio refactorización*
