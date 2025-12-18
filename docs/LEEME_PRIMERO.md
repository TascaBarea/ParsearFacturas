# 🚀 LÉEME PRIMERO - ParsearFacturas

> **Este documento es tu punto de entrada.** Léelo antes de cada sesión.

---

## 📍 ESTADO ACTUAL

| Dato | Valor |
|------|-------|
| **Versión** | v3.56 |
| **Fecha** | 17/12/2025 |
| **Script** | `migracion_historico_2025_v3_56.py` |
| **Extractor PDF** | pypdf → pdfplumber → OCR (Tesseract) |
| **OCR** | ✅ Funcionando (IBARRAKO, ROSQUILLERIA, ABELLAN, ECOMS) |

### Métricas actuales (v3.56)

| Trimestre | Facturas | Con líneas | % |
|-----------|----------|------------|---|
| 1T25 | 252 | ~215 | **~85%** |
| 2T25 | 307 | ~220 | ~72% |
| **Total** | **559** | **~435** | **~78%** |

---

## ✅ SESIÓN 17/12/2025 - RESUMEN

### Proveedores arreglados hoy

| Proveedor | Facturas | Problema resuelto |
|-----------|----------|-------------------|
| **ECOMS/DIA** | 5/7 ✅ | Nuevo extractor dual (OCR + digital) |
| **BODEGAS BORBOTON** | 10/10 ✅ | Fix orden patrones extraer_total() |
| **MARITA COSTA** | 4/4 ✅ | Añadido patrón TOTAL: antes de IBARRAKO |
| **LA ROSQUILLERIA** | 2/2 ✅ | Confirmado funcionando con OCR |

### Cambios técnicos v3.56

1. **Nuevo extractor ECOMS/DIA:**
   - `extraer_lineas_ecoms()` - Soporte dual OCR + PDF digital
   - Formato OCR: tabla "4,00% BASE CUOTA"
   - Formato DIA digital: "A 4% BASE €"
   - CIF: B72738602 (pago tarjeta, sin IBAN)

2. **Fix extraer_total() - Reorden patrones:**
   - BORBOTON movido ANTES de IBARRAKO
   - MARITA COSTA (TOTAL:) añadido ANTES de IBARRAKO
   - Problema: IBARRAKO capturaba importes de línea en vez de total

3. **Proveedores añadidos a DATOS_PROVEEDORES:**
   - ECOMS, ECOMS SUPERMARKET, DIA → B72738602

---

## 🎯 PRÓXIMOS PASOS (18/12/2025)

### Prioridad ALTA

| Proveedor | Facturas | Problema |
|-----------|----------|----------|
| **JIMELUZ** | ~18 | OCR tickets escaneados - PENDIENTE |
| SOM ENERGIA | 5 | CUADRE_PENDIENTE |

### Prioridad MEDIA

| Proveedor | Problema |
|-----------|----------|
| ECOMS (2 facturas) | OCR muy malo → manual |

### Resueltos ✅
- ~~BODEGAS BORBOTON~~ → 10/10 OK
- ~~MARITA COSTA~~ → 4/4 OK
- ~~LA ROSQUILLERIA~~ → Funciona con OCR

---

## ▶️ AL EMPEZAR PRÓXIMA SESIÓN

```
1. Sube: LEEME_PRIMERO.md + ESTADO_PROYECTO.md + PROVEEDORES.md
2. Sube: migracion_historico_2025_v3_56.py
3. Escribe: "Continúo proyecto ParsearFacturas"
4. Para JIMELUZ: Sube 2-3 facturas de muestra
```

---

## 🖥️ COMANDOS PARA EJECUTAR

**1T25:**
```cmd
cd C:\_ARCHIVOS\TRABAJO\Facturas\ParsearFacturas-main\src\migracion

python migracion_historico_2025_v3_56.py -i "C:\Users\jaime\Dropbox\File inviati\TASCA BAREA S.L.L\CONTABILIDAD\FACTURAS 2025\FACTURAS RECIBIDAS\1 TRI 2025" -d "C:\_ARCHIVOS\TRABAJO\Facturas\ParsearFacturas-main\DiccionarioProveedoresCategoria.xlsx"
```

**2T25:**
```cmd
python migracion_historico_2025_v3_56.py -i "C:\Users\jaime\Dropbox\File inviati\TASCA BAREA S.L.L\CONTABILIDAD\FACTURAS 2025\FACTURAS RECIBIDAS\2 TRI 2025" -d "C:\_ARCHIVOS\TRABAJO\Facturas\ParsearFacturas-main\DiccionarioProveedoresCategoria.xlsx"
```

---

## 📁 ARCHIVOS IMPORTANTES

| Qué | Dónde |
|-----|-------|
| Script actual | `migracion_historico_2025_v3_56.py` |
| Estado proyecto | `docs/ESTADO_PROYECTO.md` |
| Este archivo | `docs/LEEME_PRIMERO.md` |
| Lista proveedores | `docs/PROVEEDORES.md` |

---

## 🔑 DECISIONES TÉCNICAS CLAVE

1. **PDF**: pypdf principal → pdfplumber fallback → OCR (Tesseract)
2. **OCR**: Resolución 300dpi, escala grises, contraste x2
3. **Parche Windows**: Importes sin coma (7740 → 77.40)
4. **Portes**: Siempre repartidos proporcionalmente
5. **Tolerancia cuadre**: 0.05€
6. **Orden patrones total**: Específicos (BORBOTON, MARITA) ANTES de genéricos (IBARRAKO)

---

*Última actualización: 17/12/2025 - Sesión ECOMS + BORBOTON + MARITA*
