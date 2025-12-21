# 📖 LEEME PRIMERO - ParsearFacturas

**Versión:** v4.4  
**Fecha:** 21/12/2025  
**Autor:** Tasca Barea + Claude  
**Repositorio:** https://github.com/TascaBarea/ParsearFacturas (privado)

---

## ⚠️ IMPORTANTE - LEER ANTES DE CONTINUAR

### Estado de los extractores (21/12/2025)
Los 12 extractores nuevos de la sesión 21/12/2025 **están copiados** en `extractores/` pero:
- ❓ **No confirmado** si están registrados en `__init__.py`
- ❓ **No confirmado** si MAESTROS tiene los CIF nuevos
- ❓ **Archivos vacíos** en raíz (`ExtractorSaboresPaterna`, etc. con 0 bytes) - IGNORAR

### Para verificar que todo funciona
```cmd
cd C:\_ARCHIVOS\TRABAJO\Facturas\ParsearFacturas-main
python -c "from extractores import listar_extractores; print(listar_extractores())"
```

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

## 📊 ESTADO ACTUAL (21/12/2025)

### Métricas de procesamiento

| Trimestre | Facturas | Cuadre OK | % | Con Líneas | Importe |
|-----------|----------|-----------|---|------------|---------|
| 1T25 | 252 | 167 | **66.3%** | 194 (77%) | 48,173€ |
| 2T25 | 307 | 165 | **53.7%** | 231 (75%) | 46,720€ |
| 3T25 | 161 | 86 | **53.4%** | 119 (74%) | 35,539€ |
| 4T25 | 183 | ~95 | **~52%** | ~120 | pendiente |
| **TOTAL** | **903** | **~513** | **~57%** | ~664 | ~130,000€ |

### Evolución del proyecto

| Versión | Fecha | Cuadre 1T25 | Cambio |
|---------|-------|-------------|--------|
| v3.5 | 09/12/2025 | 42% | Baseline |
| v3.6 | 10/12/2025 | 47% | +6 extractores servicios |
| v4.0 | 18/12/2025 | 54% | Arquitectura modular |
| v4.2 | 19/12/2025 | 56% | +12 extractores, bug IVA 0 |
| v4.3 | 20/12/2025 | 60% | +6 extractores (OCR) |
| **v4.4** | **21/12/2025** | **66%** | **+12 extractores sesión intensiva** |

---

## 📂 ESTRUCTURA DEL PROYECTO (Real - 21/12/2025)

```
ParsearFacturas-main/
│
├── 📄 main.py                 # Punto de entrada principal (12 KB)
├── 📄 verificar_extractores.py # Script para verificar extractores
├── 📄 requirements.txt        # Dependencias Python
│
├── 📦 extractores/            # ⭐ EXTRACTORES POR PROVEEDOR (modificado 21/12)
│   ├── __init__.py            # Sistema de registro @registrar
│   ├── base.py                # Clase base ExtractorBase
│   ├── bm.py, ceres.py...     # ~90+ extractores
│   └── [12 nuevos 21/12]      # zucca, panruje, fishgourmet, etc.
│
├── 📁 nucleo/                 # Funciones core
├── 📁 salidas/                # Generación Excel/logs
├── 📁 datos/                  # DiccionarioProveedoresCategoria.xlsx (47 KB)
├── 📁 config/                 # Configuración
├── 📁 docs/                   # Documentación (este archivo)
├── 📁 tests/                  # Testing
├── 📁 outputs/                # Salidas generadas (Excel, logs)
│
├── 🗂️ legacy/                 # Código antiguo - NO USAR
├── 🗂️ src/                    # Código antiguo - NO USAR
├── 🗂️ patterns/               # YAML antiguos - NO USAR
├── 🗂️ stage_focus/            # Temporal - IGNORAR
├── 🗂️ stage_fix_1/            # Temporal - IGNORAR
└── 🗂️ samples/                # Facturas ejemplo - OPCIONAL
```

### ⚠️ Archivos a IGNORAR en raíz
Hay archivos vacíos (0 bytes) que parecen copias fallidas:
- `ExtractorSaboresPaterna`, `ExtractorBarraDulce`, `ExtractorEcoficus`, `ExtractorMolletesArtesanos`
- `python`, `cd` (archivos sin extensión)

**Estos NO afectan al funcionamiento** - los extractores reales están en `extractores/`

---

## 🔧 CÓMO FUNCIONA

### 1. Sistema de registro automático

Los extractores se registran automáticamente usando el decorador `@registrar`:

```python
# extractores/zucca.py
from extractores import registrar
from extractores.base import ExtractorBase

@registrar('QUESERIA ZUCCA', 'ZUCCA', 'FORMAGGIARTE')
class ExtractorZucca(ExtractorBase):
    nombre = 'QUESERIA ZUCCA'
    cif = 'B42861948'
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto):
        # Lógica específica del proveedor
        ...
```

**Ventaja:** Añadir proveedor = crear archivo .py, nada más que tocar.

### 2. Flujo de procesamiento

```python
# main.py (simplificado)
for pdf in carpeta.glob('*.pdf'):
    texto = extraer_texto(pdf)
    proveedor = detectar_proveedor(texto)
    extractor = obtener_extractor(proveedor)
    
    if extractor:
        lineas = extractor.extraer_lineas(texto)
        total = extractor.extraer_total(texto)
        cuadra = validar_cuadre(lineas, total)
```

### 3. Métodos de extracción

| Método | Uso | Proveedores ejemplo |
|--------|-----|---------------------|
| **pdfplumber** | PDF con texto seleccionable | CERES, BM, ZUCCA, PANRUJE |
| **OCR** | PDF escaneado/imagen | LA ROSQUILLERIA, FISHGOURMET, JIMELUZ |
| **híbrido** | Intenta pdfplumber, fallback OCR | DIA/ECOMS, DE LUIS |

---

## 📋 SESIÓN 21/12/2025 - 12 EXTRACTORES NUEVOS

### Extractores creados

| # | Proveedor | CIF | Facturas | Método | Estado |
|---|-----------|-----|----------|--------|--------|
| 1 | QUESERIA ZUCCA | B42861948 | 7/7 | pdfplumber | ✅ |
| 2 | PANRUJE | B13858014 | 6/6 | pdfplumber | ✅ |
| 3 | GRUPO DISBER | B43489039 | 4/4 | pdfplumber | ✅ |
| 4 | LIDL | A60195278 | 5/5 | pdfplumber | ✅ |
| 5 | LA ROSQUILLERIA | B86556081 | 7/7 | OCR | ✅ |
| 6 | GADITAUN | 34007216Z | 5/5 | OCR | ✅ |
| 7 | DE LUIS | B87893681 | 5/5 | híbrido | ✅ |
| 8 | MANIPULADOS ABELLAN | B30243737 | 6/6 | OCR | ✅ |
| 9 | ECOMS (DIA) | B72738602 | 6/8 | híbrido | ✅ |
| 10 | MARITA COSTA | 48207369J | 9/9 | pdfplumber | ✅ |
| 11 | SERRÍN NO CHAN | B87214755 | 7/7 | pdfplumber | ✅ |
| 12 | FISHGOURMET | B85975126 | 5/5 | OCR | ✅ |
| **TOTAL** | | | **72/74** | | **97%** |

### Archivos generados (copiar a `extractores/`)

```
zucca.py              # Quesería artesanal
panruje.py            # Panadería rosquillas
grupo_disber.py       # Distribuidor alimentación
lidl.py               # Supermercado
la_rosquilleria.py    # Rosquillas (OCR)
gaditaun.py           # Conservas Cádiz (OCR)
de_luis.py            # Gourmet Madrid (híbrido)
manipulados_abellan.py # Conservas vegetales (OCR)
ecoms.py              # DIA tickets (híbrido)
marita_costa.py       # AOVE y gourmet
serrin_no_chan.py     # Ultramarinos gallegos
fishgourmet.py        # Ahumados pescado (OCR)
__init__.py           # Actualizado con imports
```

---

## ⚠️ PROBLEMAS CONOCIDOS Y PENDIENTES

### Errores por tipo (basado en logs 21/12/2025)

| Error | Cantidad | Causa | Solución |
|-------|----------|-------|----------|
| **FECHA_PENDIENTE** | ~40 | BM, OPENAI, CELONIS tickets | Mejorar extractor BM |
| **SIN_TOTAL** | ~25 | Formato no reconocido | Crear/ajustar extractor |
| **DESCUADRE** | ~20 | Cálculo incorrecto | Revisar extractor |
| **CIF_PENDIENTE** | ~15 | Proveedor sin MAESTROS | Añadir a MAESTROS |
| **SIN_LINEAS** | ~15 | Sin extractor o OCR falla | Crear extractor |

### Proveedores prioritarios pendientes

| Proveedor | Facturas | Error | Impacto |
|-----------|----------|-------|---------|
| **JIMELUZ** | 14 | SIN_TOTAL, DESCUADRE | ALTO |
| **BM tickets** | 12 | FECHA_PENDIENTE | MEDIO |
| **CASA DEL DUQUE** | 4 | SIN_TOTAL | MEDIO |
| **PIFEMA** | 4 | DESCUADRE | BAJO |
| **SILVA CORDERO** | 4 | DESCUADRE | BAJO |

---

## 🚀 CÓMO USAR

### Procesar carpeta de facturas

```cmd
cd C:\_ARCHIVOS\TRABAJO\Facturas\ParsearFacturas-main
python main.py "C:\path\to\facturas\1 TRI 2025"
```

### Probar un extractor específico

```cmd
python tests/probar_extractor.py "ZUCCA" "factura.pdf"
python tests/probar_extractor.py "ZUCCA" "factura.pdf" --debug
```

### Añadir nuevo extractor

1. Copiar plantilla: `extractores/_plantilla.py` → `extractores/nuevo.py`
2. Cambiar nombre, CIF, variantes en `@registrar()`
3. Implementar `extraer_lineas()` con líneas individuales
4. Probar con facturas reales
5. ¡Listo! Se registra automáticamente

Ver `docs/COMO_AÑADIR_EXTRACTOR.md` para guía detallada.

---

## 📚 REGLAS CRÍTICAS

### 1. SIEMPRE líneas individuales

```python
# ❌ MAL - agrupado por IVA
lineas.append({'articulo': 'PRODUCTOS IVA 10%', 'base': 500.00, 'iva': 10})

# ✅ BIEN - cada producto
lineas.append({'articulo': 'QUESO MANCHEGO', 'cantidad': 2, 'base': 15.50, 'iva': 10})
lineas.append({'articulo': 'JAMON IBERICO', 'cantidad': 1, 'base': 45.00, 'iva': 10})
```

### 2. Portes: distribuir proporcionalmente

```python
# Los portes NUNCA van como línea separada
# Se distribuyen entre los productos
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

---

## 🔗 RELACIÓN CON OTROS COMPONENTES

### MAESTROS.xlsx
- Contiene CIF, IBAN, método de pago de cada proveedor
- Se usa para cruzar facturas parseadas con datos bancarios
- **Estado:** 79% de IBANs pendientes para proveedores con transferencia

### Generador SEPA
- Genera ficheros `pain.001.001.03` para Banco Sabadell
- Requiere IBAN válido del proveedor
- **Estado:** Prototipo funcional, pendiente integración

### Extractor Gmail
- Descarga automática de facturas PDF del email
- **Estado:** No implementado

---

## 📝 HISTORIAL DE CAMBIOS

| Fecha | Versión | Cambios |
|-------|---------|---------|
| **21/12/2025** | **v4.4** | **+12 extractores: ZUCCA, PANRUJE, DISBER, LIDL, ROSQUILLERIA, GADITAUN, DE LUIS, ABELLAN, ECOMS, MARITA COSTA, SERRIN, FISHGOURMET. 72 facturas validadas.** |
| 20/12/2025 | v4.3 | +6 extractores OCR. Mejoras en LA ROSQUILLERIA, MANIPULADOS ABELLAN. |
| 19/12/2025 | v4.2 | +12 extractores. Bug IVA 0 corregido. 56% cuadre. |
| 18/12/2025 | v4.0 | Arquitectura modular. Sistema @registrar. |
| 12/12/2025 | v3.41 | Fix FELISA, CERES, MARTIN ABENZA. |
| 09/12/2025 | v3.5 | Baseline: 42% cuadre, 70 extractores monolíticos. |

---

## ❓ PREGUNTAS FRECUENTES

### ¿Por qué una factura da DESCUADRE?
1. El extractor no captura todas las líneas
2. Hay portes no distribuidos
3. El IVA detectado es incorrecto
4. Hay descuentos no aplicados

### ¿Por qué SIN_LINEAS si existe el extractor?
1. El nombre del proveedor no coincide con `@registrar()`
2. El PDF es imagen y necesita OCR
3. El patrón regex no encuentra las líneas

### ¿Cómo sé qué extractor se usó?
Ejecuta con `--debug` para ver el texto extraído y el extractor seleccionado.

### ¿Puedo procesar facturas de años anteriores?
Sí, pero algunos formatos pueden haber cambiado. Prueba primero con `--debug`.

---

## 🔧 TROUBLESHOOTING

### "Extractor no encontrado" para proveedor que sí existe
```cmd
# 1. Verificar que el extractor está registrado
python -c "from extractores import listar_extractores; print([x for x in listar_extractores() if 'ZUCCA' in x])"

# 2. Si no aparece, verificar el import en extractores/__init__.py
```

### "SIN_LINEAS" para factura que antes funcionaba
1. El PDF puede estar dañado - abrir manualmente
2. El formato del proveedor cambió
3. Ejecutar con `--debug` para ver el texto extraído

### Error "PermissionError" al generar Excel
El archivo Excel está abierto en otro programa. Ciérralo y vuelve a ejecutar.

### OCR no funciona (SIN_LINEAS en facturas escaneadas)
```cmd
# Verificar Tesseract instalado
tesseract --version

# Si no está: descargar de https://github.com/UB-Mannheim/tesseract/wiki
# Añadir a PATH: C:\Program Files\Tesseract-OCR
```

### Los 12 extractores nuevos no se cargan
```cmd
# Verificar que están en la carpeta correcta
dir C:\_ARCHIVOS\TRABAJO\Facturas\ParsearFacturas-main\extractores\*.py

# Verificar imports en __init__.py
type C:\_ARCHIVOS\TRABAJO\Facturas\ParsearFacturas-main\extractores\__init__.py
```

---

## 📋 CHECKLIST PARA RETOMAR PROYECTO

Antes de cada sesión de trabajo:

- [ ] ¿Está el Excel de salida cerrado?
- [ ] ¿Hay facturas nuevas por procesar?
- [ ] ¿El último commit de GitHub está actualizado?

Después de añadir extractores:

- [ ] ¿Están copiados a `extractores/`?
- [ ] ¿El `__init__.py` tiene los imports?
- [ ] ¿Se ejecutó test con facturas reales?
- [ ] ¿Se actualizó PROVEEDORES.md?

---

## 🤝 SOPORTE

- **GitHub:** https://github.com/TascaBarea/ParsearFacturas (privado)
- **Documentación:** Este archivo + `docs/`
- **Conversaciones Claude:** Contexto completo del proyecto guardado

---

*Última actualización: 21/12/2025 - Sesión intensiva 12 extractores*
