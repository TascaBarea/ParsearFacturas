# 🚀 LÉEME PRIMERO - ParsearFacturas

> **Este documento es tu punto de entrada.** Léelo antes de cada sesión.

---

## 📍 ESTADO ACTUAL

| Dato | Valor |
|------|-------|
| **Versión** | v3.57 → **REFACTORIZANDO A v4.0** |
| **Fecha** | 18/12/2025 |
| **Script actual** | `migracion_historico_2025_v3_57.py` (7,618 líneas) |
| **Estado** | 🔄 EN REFACTORIZACIÓN |

### Métricas v3.57 (18/12/2025)

| Trimestre | Facturas | Con líneas | % |
|-----------|----------|------------|---|
| 1T25 | 252 | ~210 | **~83%** |
| 2T25 | 307 | ~225 | ~73% |
| **Total** | **559** | **~435** | **~78%** |

---

## 🔄 REFACTORIZACIÓN EN CURSO

### Objetivo
Dividir el monolito de 7,618 líneas en módulos manejables.

### Beneficios
- ✅ Fácil encontrar y arreglar errores
- ✅ 1 archivo por extractor (70 archivos)
- ✅ Probar extractores individualmente
- ✅ Anti-duplicados automático
- ✅ Preparado para futura app web

### Progreso

| Fase | Estado | Descripción |
|------|--------|-------------|
| 1. Estructura | ⏳ | Crear carpetas y configuración |
| 2. Núcleo | ⏳ | PDF, parser, validación |
| 3. Extractores | ⏳ | Sistema registro automático |
| 4. Migración | ⏳ | 70 extractores a archivos |
| 5. Salidas | ⏳ | Excel, logs, main.py |
| 6. Robustez | ⏳ | Anti-duplicados, testing |

**Documento detallado:** `docs/PLAN_REFACTORIZACION.md`

---

## ✅ SESIÓN 18/12/2025 - RESUMEN

### Trabajado hoy

| Tarea | Estado |
|-------|--------|
| Análisis completo del código | ✅ |
| Plan de refactorización | ✅ |
| Documentación inicial | ✅ |
| Fix LICORES MADRUEÑO total | ✅ |
| Inicio Fase 1 | 🔄 |

### Cambios v3.57

- Fix JIMELUZ: nuevo extractor OCR con tabla IVA
- Fix MADRUEÑO: patrón "TOTAL €:" + fallback robusto
- Función duplicada detectada: `extraer_lineas_mrm` (líneas 3774 y 5539)

---

## 🎯 PRÓXIMOS PASOS

### Inmediato (esta sesión)
1. ⏳ Crear estructura de carpetas
2. ⏳ Extraer configuración
3. ⏳ Crear clase base extractores

### Siguiente sesión
- Migrar 5 extractores piloto
- Test con facturas reales

---

## 🖥️ COMANDOS

### Versión actual (monolito)
```cmd
cd C:\_ARCHIVOS\TRABAJO\Facturas\ParsearFacturas-main\src\migracion

python migracion_historico_2025_v3_57.py -i "RUTA_FACTURAS" -d "RUTA_DICCIONARIO"
```

### Nueva versión (cuando esté lista)
```cmd
cd C:\_ARCHIVOS\TRABAJO\Facturas\ParsearFacturas-main

python main.py -i "RUTA_FACTURAS" -d "datos/diccionario.xlsx"
```

### Probar extractor individual (cuando esté listo)
```cmd
python tests/probar_extractor.py "CERES" "factura_ejemplo.pdf"
```

### Git
```cmd
git add .
git commit -m "Descripción del cambio"
git push
```

---

## 📁 ESTRUCTURA PROYECTO

### Actual (monolito)
```
ParsearFacturas-main/
├── src/migracion/
│   └── migracion_historico_2025_v3_57.py  ← 7,618 líneas
├── docs/
└── DiccionarioProveedoresCategoria.xlsx
```

### Destino (modular v4.0)
```
ParsearFacturas-main/
├── main.py
├── config/
├── extractores/     ← 70 archivos (1 por proveedor)
├── nucleo/
├── salidas/
├── datos/
├── tests/
├── docs/
└── legacy/          ← Backup v3.57
```

---

## 📚 DOCUMENTACIÓN

| Documento | Propósito |
|-----------|-----------|
| `LEEME_PRIMERO.md` | **Este archivo** - Punto de entrada |
| `ESTADO_PROYECTO.md` | Métricas y changelog |
| `PROVEEDORES.md` | Lista de extractores |
| `PLAN_REFACTORIZACION.md` | **NUEVO** - Plan detallado v4.0 |
| `COMO_AÑADIR_EXTRACTOR.md` | **NUEVO** - Guía para nuevos extractores |

---

## ▶️ AL EMPEZAR SESIÓN

```
1. Sube los 3 docs: LEEME_PRIMERO.md, ESTADO_PROYECTO.md, PLAN_REFACTORIZACION.md
2. Sube el script actual si hay cambios
3. Escribe: "Continúo refactorización ParsearFacturas - Fase X"
```

---

## 🔑 DECISIONES TÉCNICAS

1. **Registro automático**: Decorador `@registrar('PROVEEDOR')`
2. **Anti-duplicados**: PROVEEDOR + FECHA + TOTAL en Excel
3. **Backup**: Versión anterior en `legacy/`
4. **Testing**: Script `probar_extractor.py` individual

---

*Última actualización: 18/12/2025 - Inicio refactorización v4.0*
