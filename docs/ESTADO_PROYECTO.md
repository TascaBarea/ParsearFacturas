# 📊 ESTADO DEL PROYECTO - ParsearFacturas

**Última actualización:** 28/12/2025  
**Versión actual:** v5.3  
**Repositorio:** https://github.com/TascaBarea/ParsearFacturas

---

## 🎯 MÉTRICAS ACTUALES

### Resultados v5.3 (28/12/2025)

| Métrica | Antes sesión | Después sesión | Cambio |
|---------|--------------|----------------|--------|
| **Tasa de éxito** | 52.2% | **~57%** | **+5 pts** |
| **Facturas OK** | 473/906 | **~516/906** | **+43** |
| **Extractores nuevos** | - | **+6** | - |

### Desglose por tipo de error (última ejecución 28/12)

| Error | Facturas | % | Estado |
|-------|----------|---|--------|
| ✅ OK | 473 | 52.2% | Procesadas correctamente |
| ❌ SIN_TOTAL | 171 | 18.9% | Falta extraer_total() |
| ❌ DESCUADRE | 202 | 22.3% | IVA/bases mal calculados |
| ❌ SIN_LINEAS | 59 | 6.5% | Extractor no existe |

**Objetivo:** 80% cuadre OK

### Evolución histórica

| Versión | Fecha | Cuadre | Cambio principal |
|---------|-------|--------|------------------|
| v3.5 | 09/12/2025 | 42% | Baseline - 70 extractores |
| v4.0 | 18/12/2025 | 54% | Arquitectura modular @registrar |
| v5.0 | 26/12/2025 | 54% | Normalización + prorrateo portes |
| v5.2 | 26/12/2025 | ~66% | +10 extractores corregidos |
| **v5.3** | **28/12/2025** | **~57%** | **+6 extractores nuevos** |

**Nota:** La tasa 52.2% es pre-integración. Tras integrar extractores v5.2 y v5.3 se estima ~57-60%.

---

## ✅ SESIÓN 28/12/2025 - EXTRACTORES CREADOS

### 6 extractores nuevos (PENDIENTES INTEGRAR)

| # | Proveedor | CIF | Facturas | Tasa | Método |
|---|-----------|-----|----------|------|--------|
| 1 | **ECOMS SUPERMARKET** | B72738602 | 14 | 64% | Híbrido (pdfplumber + OCR) |
| 2 | **VIRGEN DE LA SIERRA** | F50019868 | 7 | 100% | Híbrido |
| 3 | **MARITA COSTA** | 48207369J | 7 | 100% | pdfplumber |
| 4 | **CASA DEL DUQUE** | B23613697 | 10 | 80% | OCR |
| 5 | **CELONIS/MAKE** | DE315052800 | 10 | 100% | pdfplumber |
| 6 | **PIFEMA** | B79048914 | 5 | 100% | pdfplumber |

**LIDL:** Verificado OK (5/5) - ya funcionaba correctamente

### Archivos generados

| Archivo | Descripción |
|---------|-------------|
| `ecoms.py` | Supermercado - tickets OCR híbrido, letras IVA (A=4%, B=10%, C=21%) |
| `virgen_de_la_sierra.py` | Bodega cooperativa Zaragoza - vinos, portes |
| `marita_costa.py` | Distribuidora gourmet - IVA mixto (4%/10%) |
| `casa_del_duque.py` | Tienda alimentación Jaén - OCR puro |
| `celonis.py` | SaaS Make/Integromat - facturas extranjeras |
| `pifema.py` | Distribuidor vinos Madrid - multi-albaranes |

### Características técnicas implementadas

| Proveedor | Características especiales |
|-----------|---------------------------|
| ECOMS | Letras IVA (A=4%, B=10%, C=21%), método híbrido |
| VIRGEN DE LA SIERRA | Portes incluidos, método híbrido OCR fallback |
| MARITA COSTA | IVA mixto (4% AOVE/picos, 10% resto), códigos con espacios |
| CASA DEL DUQUE | OCR puro para tickets escaneados |
| CELONIS | SaaS extranjero, IVA 0%, conversión USD→EUR |
| PIFEMA | Multi-albaranes por factura, bonificaciones |

---

## ⚠️ PROVEEDORES PRIORITARIOS (PRÓXIMA SESIÓN)

### 🔴 TOP 10 por impacto (errores pendientes)

| # | Proveedor | Errores | Tipo | Dificultad |
|---|-----------|---------|------|------------|
| 1 | **BM + BM SUPERMERCADOS** | 37 | DESCUADRE | 🟡 Media |
| 2 | **JIMELUZ** | 19 | OCR (SIN_TOTAL/SIN_LINEAS) | 🔴 Alta |
| 3 | **FELISA GOURMET** | 12 | DESCUADRE | 🟢 Fácil |
| 4 | **DISTRIBUCIONES LAVAPIES** | 11 | DESCUADRE | 🟢 Fácil |
| 5 | **LA ROSQUILLERIA** | 10 | OCR (SIN_LINEAS) | 🔴 Alta |
| 6 | JAMONES BERNAL | 6 | DESCUADRE | 🟡 Media |
| 7 | SILVA CORDERO | 5 | DESCUADRE | 🟡 Media |
| 8 | EMJAMESA | 4 | DESCUADRE | 🟡 Media |
| 9 | ECOFICUS | 4 | DESCUADRE | 🟡 Media |
| 10 | ALCAMPO | 4 | DESCUADRE | 🟡 Media |

### Recomendación próxima sesión

**Opción A - Quick wins (DESCUADRES):**
- BM SUPERMERCADOS (37)
- FELISA GOURMET (12)
- DISTRIBUCIONES LAVAPIES (11)
- Potencial: **+60 facturas** (+6.6%)

**Opción B - OCR (más complejo):**
- JIMELUZ (19) - Tickets escaneados
- LA ROSQUILLERIA (10) - Tickets escaneados
- Potencial: **+29 facturas** (+3.2%)

---

## 📋 CHECKLIST DESPLIEGUE

```cmd
# 1. Copiar extractores nuevos de sesión 28/12
copy ecoms.py C:\...\ParsearFacturas-main\extractores\
copy virgen_de_la_sierra.py C:\...\ParsearFacturas-main\extractores\
copy marita_costa.py C:\...\ParsearFacturas-main\extractores\
copy casa_del_duque.py C:\...\ParsearFacturas-main\extractores\
copy celonis.py C:\...\ParsearFacturas-main\extractores\
copy pifema.py C:\...\ParsearFacturas-main\extractores\

# 2. Regenerar documentación
python generar_proveedores.py

# 3. Commit
git add .
git commit -m "Sesión 28/12: +6 extractores (ECOMS, VIRGEN, MARITA, CASA DUQUE, CELONIS, PIFEMA)"
git push

# 4. Reprocesar facturas
python main.py -i "ruta\1 TRI 2025"
python main.py -i "ruta\2 TRI 2025"
python main.py -i "ruta\3 TRI 2025"
python main.py -i "ruta\4 TRI 2025"
```

---

## 📈 PROYECCIÓN

| Escenario | Tasa | Facturas OK |
|-----------|------|-------------|
| Antes de hoy | 52.2% | 473 |
| **+ Extractores 28/12** | **~57%** | **~516** |
| + BM + FELISA + LAVAPIES | ~63% | ~571 |
| + JIMELUZ + ROSQUILLERIA | ~66% | ~600 |
| **OBJETIVO** | **80%** | **725** |

---

## 📊 ESTADÍSTICAS GENERALES

| Métrica | Valor |
|---------|-------|
| Extractores totales | ~136 |
| Facturas analizadas | 906 (4 trimestres) |
| Proveedores únicos | ~100 |
| Artículos en diccionario | ~925 |
| % con errores | 47.8% |

---

## 🔍 HISTORIAL DE SESIONES

| Fecha | Versión | Extractores | Mejora | Destacado |
|-------|---------|-------------|--------|-----------|
| **28/12/2025** | **v5.3** | **+6 nuevos** | **52%→57%** | **ECOMS, VIRGEN, MARITA, CASA DUQUE, CELONIS, PIFEMA** |
| 26/12/2025 PM | v5.2 | +10 corregidos | 54%→66% | BM, JIMELUZ, ECOMS, LAVAPIES |
| 26/12/2025 AM | v5.1 | +16 nuevos | - | YOIGO, SOM, OPENAI, ANTHROPIC |
| 21/12/2025 | v4.5 | +20 | - | JAIME FERNANDEZ, ROSQUILLERIA OCR |
| 18/12/2025 | v4.0 | - | 42%→54% | Arquitectura modular |

---

## 🔧 TAREAS PENDIENTES

### Inmediato (próxima sesión)
- [ ] **DESPLEGAR** los 6 extractores de sesión 28/12
- [ ] Quick wins: BM, FELISA GOURMET, DISTRIBUCIONES LAVAPIES
- [ ] Revisar SERRIN NO CHAN (reportado como problemático)
- [ ] Revisar SILVA CORDERO (reportado como problemático)

### Corto plazo
- [ ] **CONSOLIDAR nombres de proveedores duplicados:**
  - "BM" + "BM SUPERMERCADOS" → Unificar
  - "ECOMS" + "ECOMS SUPERMARKET SL" → Unificar
- [ ] Crear extractores para proveedores con SIN_TOTAL
- [ ] Llegar a **70%** cuadre OK

### Medio plazo
- [ ] Llegar a **80%** cuadre OK (objetivo)
- [ ] Integrar extractor Gmail
- [ ] Completar IBANs (actualmente ~25%)
- [ ] Generador SEPA con validación

---

*Actualizado: 28/12/2025 - Sesión extractores v5.3*
