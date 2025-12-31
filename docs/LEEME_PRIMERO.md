# 📖 LEEME PRIMERO - ParsearFacturas

**Versión:** v5.4  
**Fecha:** 31/12/2025  
**Autor:** Tasca Barea + Claude  
**Repositorio:** https://github.com/TascaBarea/ParsearFacturas (privado)

---

## ⚠️ IMPORTANTE - LEER ANTES DE CONTINUAR

### Estado actual (31/12/2025)

**Última sesión - 1 extractor nuevo + 2 mejorados:**
```
lavapies.py             # NUEVO - IVA deducido de factura (13/13 ✅)
bodegas_munoz.py        # MEJORADO - Soporte OCR (4/4 ✅)
gredales.py             # MEJORADO - Líneas individuales (5/5 ✅)
```

### Para verificar que todo funciona
```cmd
cd C:\_ARCHIVOS\TRABAJO\Facturas\ParsearFacturas-main
python -c "from extractores import listar_extractores; print(len(listar_extractores()), 'extractores')"
```

Debe mostrar: **~140 extractores**

---

## 🎯 ¿QUÉ ES ESTE PROYECTO?

Sistema automatizado para **parsear facturas PDF** de proveedores y extraer líneas de producto con desglose IVA. El objetivo final es generar ficheros SEPA para pago automático por transferencia.

**Flujo del sistema:**
```
PDF factura → Detectar proveedor → Extractor específico → Líneas producto → Excel
                                                                              ↓
                                                           Cruce con MAESTROS (CIF→IBAN)
                                                                              ↓
                                                           Generador SEPA (pain.001)
```

---

## 📊 ESTADO ACTUAL (31/12/2025)

### Métricas de procesamiento

| Trimestre | Facturas | Cuadre OK | % |
|-----------|----------|-----------|---|
| 1T25 | ~250 | ~150 | ~60% |
| 2T25 | ~300 | ~180 | ~60% |
| 3T25 | ~160 | ~96 | ~60% |
| 4T25 | ~200 | ~120 | ~60% |
| **TOTAL** | **~910** | **~546** | **~60%** |

**Objetivo:** 80% cuadre OK

### Evolución del proyecto

| Versión | Fecha | Cuadre | Cambio principal |
|---------|-------|--------|------------------|
| v3.5 | 09/12/2025 | 42% | Baseline - 70 extractores |
| v4.0 | 18/12/2025 | 54% | Arquitectura modular @registrar |
| v4.5 | 21/12/2025 | ~70% | +20 extractores |
| v5.0 | 26/12/2025 | 54% | Normalización + prorrateo portes |
| v5.1 | 26/12/2025 | 57.8% | +16 extractores nuevos |
| v5.2 | 28/12/2025 | ~57% | +6 extractores (ECOMS, VIRGEN...) |
| v5.3 | 29-30/12/2025 | ~58% | Bugs corregidos + 4 extractores |
| **v5.4** | **31/12/2025** | **~60%** | **+LAVAPIES, mejoras OCR** |

---

## 📁 ESTRUCTURA DEL PROYECTO

```
ParsearFacturas-main/
│
├── 📄 main.py                 # Punto de entrada principal
├── 📄 requirements.txt        # Dependencias Python
│
├── 📦 extractores/            # ⭐ ~140 EXTRACTORES
│   ├── __init__.py            # Sistema de registro @registrar
│   ├── base.py                # Clase base ExtractorBase
│   └── [140+ extractores]     # Un archivo por proveedor
│
├── 📁 nucleo/                 # Funciones core
├── 📁 salidas/                # Generación Excel/logs
├── 📁 datos/                  # DiccionarioProveedoresCategoria.xlsx
├── 📁 config/                 # Configuración
├── 📁 docs/                   # Documentación
├── 📁 tests/                  # Testing
└── 📁 outputs/                # Salidas generadas
```

---

## ✅ SESIONES RECIENTES

### 31/12/2025 - Sesión actual (v5.4)

| Proveedor | CIF | Facturas | Método | Peculiaridad |
|-----------|-----|----------|--------|--------------|
| **DISTRIBUCIONES LAVAPIES** | F88424072 | 13/13 ✅ | pdfplumber | **IVA deducido de factura** |
| BODEGAS MUÑOZ MARTIN | E83182683 | 4/4 ✅ | **híbrido** | OCR para escaneadas |
| LOS GREDALES | B83594150 | 5/5 ✅ | pdfplumber | Líneas individuales |

**Técnicas nuevas:**
- **IVA deducido por subset-sum:** Para proveedores con IVA variable/errores
- **Sistema de avisos:** Alerta cuando IVA factura ≠ IVA esperado

### 30/12/2025 - Sesión anterior

| Proveedor | CIF | Estado |
|-----------|-----|--------|
| DE LUIS | B78380685 | ✅ Corregido (deduplicación) |
| ALFARERIA TALAVERANA | B45007374 | ✅ Corregido (descuento/portes) |
| PORVAZ | E36131709 | ✅ Corregido (bug Ñ ZAMBURIÑA) |
| INMAREPRO | B86310109 | ✅ Nuevo (mantenimiento extintores) |

### 29/12/2025 - Bugs corregidos

| Extractor | Problema | Solución |
|-----------|----------|----------|
| DEBORA GARCIA | IRPF mal calculado | Corregido |
| FELISA | No detectaba alias | Alias añadido |
| HERNÁNDEZ BODEGA | Encoding Ñ | UTF-8 |
| SILVA CORDERO | IVA mixto | Corregido |
| **base.py** | extraer_referencia no llamaba a extraer_numero_factura | **SOLUCIONADO** |

---

## ⚠️ PROBLEMAS CONOCIDOS Y PENDIENTES

### Proveedores prioritarios

| # | Proveedor | Errores | Tipo | Dificultad |
|---|-----------|---------|------|------------|
| 1 | **BM SUPERMERCADOS** | 37 | DESCUADRE | 🟡 Media |
| 2 | **JIMELUZ** | 19 | OCR | 🔴 Alta |
| 3 | **FELISA GOURMET** | 12 | DESCUADRE | 🟢 Fácil |
| 4 | **LA ROSQUILLERIA** | 10 | OCR | 🔴 Alta |
| 5 | JAMONES BERNAL | 6 | DESCUADRE | 🟡 Media |
| 6 | SILVA CORDERO | 5 | DESCUADRE | 🟡 Media |

### Por tipo de error

| Error | Cantidad | Acción |
|-------|----------|--------|
| DESCUADRE | ~80 | Revisar extractor |
| SIN_TOTAL | ~30 | Crear/arreglar extractor |
| SIN_LINEAS | ~15 | Crear extractor |
| FECHA_PENDIENTE | ~10 | Mejorar extractor |

---

## 🚀 CÓMO USAR

### Procesar carpeta de facturas

```cmd
cd C:\_ARCHIVOS\TRABAJO\Facturas\ParsearFacturas-main
python main.py -i "C:\path\to\facturas\4 TRI 2025"
```

### Probar un extractor específico

```cmd
python tests/probar_extractor.py "LAVAPIES" "factura.pdf"
python tests/probar_extractor.py "LAVAPIES" "factura.pdf" --debug
```

### Añadir nuevo extractor

1. Copiar plantilla: `extractores/_plantilla.py` → `extractores/nuevo.py`
2. Cambiar nombre, CIF, variantes en `@registrar()`
3. Implementar `extraer_lineas()` con líneas individuales
4. Probar con facturas reales
5. ¡Listo! Se registra automáticamente

---

## 📚 REGLAS CRÍTICAS

### 1. SIEMPRE líneas individuales

```python
# ❌ MAL - agrupado por IVA
lineas.append({'articulo': 'PRODUCTOS IVA 10%', 'base': 500.00, 'iva': 10})

# ✅ BIEN - cada producto
lineas.append({'articulo': 'QUESO MANCHEGO', 'cantidad': 2, 'base': 15.50, 'iva': 10})
```

### 2. Portes: distribuir proporcionalmente

```python
# Los portes NUNCA van como línea separada
if portes > 0:
    for linea in lineas:
        proporcion = linea['base'] / base_total
        linea['base'] += portes * proporcion
```

### 3. Formato números europeo

```python
def _convertir_europeo(self, texto):
    # "1.234,56" → 1234.56
    texto = texto.replace('.', '').replace(',', '.')
    return float(texto)
```

### 4. Tolerancia de cuadre: 0.10€

### 5. IVA variable: deducir de factura
Para proveedores con errores frecuentes de IVA (ej: LAVAPIES), deducir el IVA de las bases imponibles de la factura usando algoritmo subset-sum.

---

## 📋 CHECKLIST PARA RETOMAR PROYECTO

Antes de cada sesión de trabajo:

- [ ] ¿Está el Excel de salida cerrado?
- [ ] ¿Hay facturas nuevas por procesar?
- [ ] ¿El último commit de GitHub está actualizado?
- [ ] ¿Subiste ESTADO_PROYECTO.md y PROVEEDORES.md a Claude?

Después de añadir extractores:

- [ ] ¿Están copiados a `extractores/`?
- [ ] ¿Se limpió el caché? (`rmdir /s /q __pycache__`)
- [ ] ¿Se ejecutó test con facturas reales?
- [ ] ¿Se actualizó la documentación?

---

## 📝 HISTORIAL DE CAMBIOS

| Fecha | Versión | Cambios |
|-------|---------|---------|
| **31/12/2025** | **v5.4** | **+LAVAPIES (IVA deducido), MUÑOZ OCR, GREDALES líneas** |
| 30/12/2025 | v5.3+ | DE LUIS, ALFARERIA, PORVAZ, INMAREPRO |
| 29/12/2025 | v5.3 | Bugs: DEBORA, FELISA, HERNÁNDEZ, SILVA, base.py |
| 28/12/2025 | v5.2 | +6: ECOMS, VIRGEN, MARITA, CASA DUQUE, CELONIS, PIFEMA |
| 26/12/2025 | v5.1 | +16: YOIGO, SOM, OPENAI, ANTHROPIC... |
| 21/12/2025 | v4.5 | +20 extractores (OCR: ROSQUILLERIA, FISHGOURMET) |
| 18/12/2025 | v4.0 | Arquitectura modular @registrar |

---

*Última actualización: 31/12/2025 - ¡Feliz Año Nuevo! 🎉*
