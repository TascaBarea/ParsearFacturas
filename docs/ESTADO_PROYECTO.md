# ESTADO DEL PROYECTO - Migración Histórico 2025

**Última actualización:** 2025-12-17
**Versión actual:** 3.56

---

## 📊 MÉTRICAS ACTUALES

### v3.56 - Resultados estimados (17/12/2025)

| Trimestre | Facturas | Con líneas | % | Líneas | IBANs |
|-----------|----------|------------|---|--------|-------|
| 1T25 | 252 | ~215 | ~85% | ~800 | ~130 |
| 2T25 | 307 | ~220 | ~72% | ~830 | ~120 |
| **Total** | **559** | **~435** | **~78%** | **~1630** | **~250** |

### Evolución

| Versión | Fecha | 1T25 % | Cambio |
|---------|-------|--------|--------|
| v3.53 | 14/12 | 64.3% | - |
| v3.54 | 15/12 | 78.6% | +14.3% |
| v3.55 | 16/12 | 82.5% | +3.9% |
| **v3.56** | **17/12** | **~85%** | **+2.5%** |

**Mejora total v3.53→v3.56: +20.7%**

---

## ✅ SESIÓN 2025-12-17: ECOMS + BORBOTON + MARITA

### Proveedores arreglados

| Proveedor | Facturas | Problema resuelto |
|-----------|----------|-------------------|
| **ECOMS/DIA** | 5/7 ✅ | Nuevo extractor dual (OCR + PDF digital) |
| **BODEGAS BORBOTON** | 10/10 ✅ | Fix orden patrones en extraer_total() |
| **MARITA COSTA** | 4/4 ✅ | Añadido patrón TOTAL: antes de IBARRAKO |
| **LA ROSQUILLERIA** | 2/2 ✅ | Confirmado funcionando con OCR existente |

### Cambios técnicos implementados

1. **Nuevo extractor ECOMS/DIA:**
   - `extraer_lineas_ecoms()` con soporte dual:
     - **Método 1 (OCR)**: Busca tabla IVA después de "TIPO IVA"
     - **Método 2 (PDF digital)**: Patrón "A 4% BASE €"
     - **Método 3 (Fallback)**: Línea TOTALES para OCR muy malo
   - Limpieza OCR: maneja `:` por `,` en importes
   - CIF: B72738602, IBAN: vacío (pago tarjeta)

2. **Fix extraer_total() - Reordenamiento de patrones:**
   - **Problema**: Patrón IBARRAKO (`[\d,]+€[ \t]+(\d+[,\.]\d{2})€$`) capturaba importes de línea
   - **Solución**: Mover patrones específicos ANTES de IBARRAKO:
     - BORBOTON: `BASE € IVA% CUOTA € TOTAL €`
     - MARITA COSTA: `TOTAL: XXX,XX€`
   - Orden actual: GREDALES → SERRIN → BORBOTON → MARITA → IBARRAKO → ...

3. **Proveedores añadidos a diccionarios:**
   ```python
   DATOS_PROVEEDORES:
     'ECOMS': {'cif': 'B72738602', 'iban': ''}
     'ECOMS SUPERMARKET': {'cif': 'B72738602', 'iban': ''}
     'DIA': {'cif': 'B72738602', 'iban': ''}
   
   CIF_TO_PROVEEDOR:
     'B72738602': 'ECOMS'
   ```

---

## ⚠️ PROBLEMAS PENDIENTES

### Por proveedor (prioritarios)

| Proveedor | Facturas | Error | Notas |
|-----------|----------|-------|-------|
| **JIMELUZ** | ~18 | SIN_LINEAS/OCR | Tickets escaneados, necesita extractor OCR |
| **SOM ENERGIA** | 5 | CUADRE_PENDIENTE | Extractor existe pero falla |
| **ECOMS** | 2 | OCR muy malo | Tickets arrugados → manual |

### Resueltos en v3.56 ✅

| Proveedor | Era | Ahora |
|-----------|-----|-------|
| BODEGAS BORBOTON | CUADRE_PENDIENTE | ✅ 10/10 OK |
| MARITA COSTA | CUADRE_PENDIENTE | ✅ 4/4 OK |
| LA ROSQUILLERIA | CUADRE_PENDIENTE | ✅ 2/2 OK |
| ECOMS/DIA | SIN_LINEAS | ✅ 5/7 OK |

### Por tipo de error (estimado)

| Error | Cantidad aprox. |
|-------|-----------------|
| SIN_LINEAS | ~35 |
| CUADRE_PENDIENTE | ~20 |
| CIF_PENDIENTE | ~25 |
| IBAN_PENDIENTE | ~20 |
| FECHA_PENDIENTE | ~15 |

---

## 📈 PROVEEDORES CON EXTRACTOR OK (68+)

### Añadidos/Arreglados v3.56

| # | Proveedor | Notas |
|---|-----------|-------|
| 66 | **ECOMS/DIA** | **v3.56 ✅ Nuevo extractor dual** |
| 67 | **BODEGAS BORBOTON** | **v3.56 ✅ Fix total** |
| 68 | **MARITA COSTA** | **v3.56 ✅ Fix total** |

### Confirmados funcionando v3.55+

| # | Proveedor | Notas |
|---|-----------|-------|
| 1 | BM SUPERMERCADOS | 147 fact/año |
| 2 | CERES | 102 fact/año |
| 3 | LICORES MADRUÑO | 93+ líneas/mes |
| 4 | IBARRAKO PIPARRAK | v3.55 ✅ OCR |
| 5 | MANIPULADOS ABELLAN | v3.55 ✅ OCR |
| 6 | EMJAMESA | v3.55 ✅ |
| 7 | LA ROSQUILLERIA | v3.55 ✅ OCR |
| ... | (ver PROVEEDORES.md) | |

---

## 🎯 PLAN PRÓXIMAS SESIONES

### Prioridad ALTA
1. **JIMELUZ** (~18 facturas) - Crear extractor OCR para tickets

### Prioridad MEDIA
2. **SOM ENERGIA** (5 facturas) - Investigar cuadre
3. Añadir IBANs/CIFs faltantes

### Completado ✅
- ~~BODEGAS BORBOTON~~ - Fix total
- ~~MARITA COSTA~~ - Fix total
- ~~ECOMS/DIA~~ - Nuevo extractor
- ~~LA ROSQUILLERIA~~ - Confirmado OK

---

## 📁 ARCHIVOS DEL PROYECTO

```
ParsearFacturas-main/
├── src/migracion/
│   ├── migracion_historico_2025_v3_56.py  ← VERSIÓN ACTUAL
│   └── outputs/
│       ├── Facturas_1T25.xlsx
│       ├── Facturas_2T25.xlsx
│       └── log_migracion_*.txt
├── docs/
│   ├── ESTADO_PROYECTO.md      ← ESTE ARCHIVO
│   ├── LEEME_PRIMERO.md
│   └── PROVEEDORES.md
└── DiccionarioProveedoresCategoria.xlsx
```

---

## 📝 CHANGELOG

| Versión | Fecha | Cambios |
|---------|-------|---------|
| **v3.56** | **2025-12-17** | **ECOMS nuevo, BORBOTON/MARITA fix total. ~78% global** |
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
6. **Orden patrones total:** Específicos ANTES de genéricos (evita falsos positivos)

---

*Última actualización: 17/12/2025 - Sesión ECOMS + BORBOTON + MARITA*
