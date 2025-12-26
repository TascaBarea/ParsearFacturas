# 📖 ParsearFacturas - Manual del Proyecto

**Versión:** 5.1  
**Última actualización:** 26/12/2025  
**Negocio:** TASCA BAREA S.L.L. (restaurante + distribución gourmet COMESTIBLES BAREA)

---

## 🎯 OBJETIVO DEL PROYECTO

Automatizar el flujo completo de facturas de proveedores:

```
📧 Gmail → 📄 PDF → 🔍 Extracción → 📊 Categorización → 💳 Pago SEPA
```

**Meta final:** Cada viernes a las 07:00, el sistema descarga facturas, las procesa y genera ficheros SEPA para pagar automáticamente.

---

## 📊 ESTADO ACTUAL (26/12/2025)

| Componente | Estado | Progreso |
|------------|--------|----------|
| **ParsearFacturas** | ✅ Funcional | v5.1 - 120+ extractores |
| **Categorización** | ✅ Funcional | Fuzzy matching 80% |
| **Generador SEPA** | ✅ Prototipo | Falta validación IBAN |
| **Extractor Gmail** | 🟡 OAuth2 OK | Falta integrar |
| **Orquestador** | ❌ Pendiente | - |

**Métricas ParsearFacturas v5.1:**
- Cuadre OK: **57.8%** (4T25)
- Con líneas: **83.2%**
- Objetivo: **80%**

---

## 🗂️ TABLAS DEL SISTEMA

El negocio maneja estas tablas de datos:

### 1. ARTICULOS LOYVERSE (CRM)
- **Origen:** Exportación desde Loyverse POS
- **Contenido:** 578 artículos de venta con código, nombre, precio, categoría
- **Uso:** Referencia para análisis de márgenes

### 2. VENTAS POR ARTICULOS (CRM)
- **Origen:** Exportación desde Loyverse
- **Contenido:** Ventas detalladas por artículo
- **Uso:** Análisis de ventas

### 3. COMPRAS POR ARTICULOS (ParsearFacturas)
- **Origen:** Este proyecto - extracción de facturas PDF
- **Contenido:** 698 artículos de compra, 116 categorías
- **Uso:** Análisis de costes, categorización

### 4. FACTURAS
- **Origen:** Facturas procesadas
- **Contenido:** Código (del nombre archivo), Cuenta contable, Proveedor, Fecha, Ref, Total
- **Uso:** Contabilidad, cruce con gestoría

### 5. MOVIMIENTOS BANCO (N43)
- **Origen:** Descarga semanal de Banco Sabadell
- **Contenido:** Movimientos TASCA + COMESTIBLES
- **Uso:** Conciliación de pagos

### 6. PROVEEDORES (MAESTROS)
- **Origen:** Manual + extraído de facturas
- **Contenido:** Nombre, CIF, IBAN, forma de pago, cuenta contable
- **Uso:** Generación SEPA, cruce facturas

---

## 🔄 FLUJO DEL SISTEMA

```
┌─────────────────────────────────────────────────────────────────────┐
│                     FLUJO SEMANAL (VIERNES)                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  07:00  ┌──────────┐    ┌────────────────┐    ┌──────────────────┐  │
│   AM    │  Gmail   │───▶│ ParsearFacturas│───▶│ Categorización   │  │
│         │ Extractor│    │  (120+ extrac) │    │ (Diccionario)    │  │
│         └──────────┘    └────────────────┘    └──────────────────┘  │
│              │                                        │             │
│              ▼                                        ▼             │
│         ┌──────────┐                          ┌──────────────────┐  │
│         │ Dropbox  │                          │ Excel Facturas   │  │
│         │ Backup   │                          │ (revisar)        │  │
│         └──────────┘                          └──────────────────┘  │
│                                                       │             │
│  09:00                                               ▼             │
│   AM    ┌─────────────────────────────────────────────────────────┐ │
│         │         REVISIÓN MANUAL + CONFIRMACIÓN                  │ │
│         │         (Corregir PENDIENTES, verificar)                │ │
│         └─────────────────────────────────────────────────────────┘ │
│                                                       │             │
│  12:00                                               ▼             │
│   PM    ┌──────────────────┐    ┌──────────────────────────────┐   │
│         │ Generador SEPA   │───▶│ pain.001.xml → BS Online     │   │
│         │ (pain.001.001.03)│    │ Autorizar → Ejecutar         │   │
│         └──────────────────┘    └──────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 USO BÁSICO

### Procesar facturas de un trimestre

```cmd
cd C:\_ARCHIVOS\TRABAJO\Facturas\ParsearFacturas-main

python main.py -i "C:\...\FACTURAS 2025\FACTURAS RECIBIDAS\4 TRI 2025"
```

**Salida:**
- `outputs/Facturas_4T25.xlsx` - Excel con líneas extraídas
- `outputs/log_YYYYMMDD_HHMM.txt` - Log de procesamiento

### Probar un extractor específico

```cmd
python tests/probar_extractor.py "CERES" "factura.pdf"
python tests/probar_extractor.py "CERES" "factura.pdf" --debug
```

### Listar extractores disponibles

```cmd
python main.py --listar-extractores
```

### Actualizar diccionario de categorías

```cmd
python actualizar_diccionario.py
```
(Se abre ventana para seleccionar Excel corregido)

---

## 📁 ESTRUCTURA DEL PROYECTO

```
ParsearFacturas-main/
├── main.py                          # Script principal v5.1
├── actualizar_diccionario.py        # Actualiza categorías
├── generar_proveedores.py           # Genera PROVEEDORES.md
│
├── extractores/                     # 120+ extractores
│   ├── __init__.py                  # Registro automático
│   ├── base.py                      # Clase ExtractorBase
│   ├── ceres.py                     # 1 archivo por proveedor
│   ├── bm.py
│   └── ...
│
├── nucleo/                          # Funciones core
│   ├── factura.py                   # Dataclass LineaFactura
│   └── ...
│
├── salidas/                         # Generación Excel/logs
│   └── ...
│
├── datos/                           # Datos del sistema
│   └── DiccionarioProveedoresCategoria.xlsx
│
├── config/                          # Configuración
│   └── settings.py
│
├── docs/                            # Documentación
│   ├── README.md                    # Este archivo
│   ├── ESTADO_PROYECTO.md           # Estado actual
│   ├── PROVEEDORES.md               # Lista extractores
│   └── COMO_AÑADIR_EXTRACTOR.md     # Guía técnica
│
├── tests/                           # Testing
│   └── probar_extractor.py
│
└── outputs/                         # Salidas generadas
    ├── Facturas_1T25.xlsx
    └── log_*.txt
```

---

## 🔧 REGLAS TÉCNICAS CRÍTICAS

### 1. Siempre pdfplumber (OCR solo si es escaneado)
```python
metodo_pdf = 'pdfplumber'  # SIEMPRE por defecto
metodo_pdf = 'ocr'         # SOLO si es imagen/escaneado
metodo_pdf = 'hibrido'     # Si algunas facturas son escaneadas y otras no
```

### 2. Siempre líneas individuales
**1 artículo = 1 línea en el Excel**

```python
# ❌ MAL (agrupado)
lineas.append({'articulo': 'PRODUCTOS IVA 10%', 'base': 500.00})

# ✅ BIEN (individual)
lineas.append({'articulo': 'QUESO MANCHEGO', 'cantidad': 2, 'base': 15.50})
```

### 3. Portes: distribuir proporcionalmente
```python
# Los portes NUNCA van como línea separada
if portes > 0:
    for linea in lineas:
        proporcion = linea['base'] / base_total
        linea['base'] += portes * proporcion
```

### 4. Tolerancia de cuadre: 0.10€

### 5. Formato números europeo
```python
def _convertir_europeo(self, texto):
    # "1.234,56" → 1234.56
    texto = texto.replace('.', '').replace(',', '.')
    return float(texto)
```

---

## 📋 RUTINA DE TRABAJO CON CLAUDE

### Al INICIAR sesión:
1. Subir estos archivos a Claude:
   - `docs/ESTADO_PROYECTO.md`
   - `docs/PROVEEDORES.md` (si hay cambios en extractores)
   - Facturas PDF del proveedor a trabajar
2. Decir: "Continúo proyecto ParsearFacturas v5.1. Tarea: [describir]"

### Al CERRAR sesión:
1. Pedir: "Actualiza ESTADO_PROYECTO.md con lo de hoy"
2. Descargar el archivo actualizado
3. Copiar a `docs/` y hacer commit:
```cmd
git add docs/ESTADO_PROYECTO.md
git commit -m "Actualizar estado sesión DD/MM/YYYY"
git push
```

### Si añades extractores:
1. Copiar archivos `.py` a `extractores/`
2. Ejecutar: `python generar_proveedores.py`
3. Hacer commit de todo

---

## 🔗 ENLACES ÚTILES

- **Repositorio:** https://github.com/TascaBarea/ParsearFacturas
- **Dropbox facturas:** `Dropbox/File inviati/TASCA BAREA S.L.L/CONTABILIDAD/FACTURAS 2025`
- **Banco Sabadell:** BS Online para SEPA

---

## 📞 SOPORTE

Este proyecto se desarrolla con asistencia de Claude (Anthropic).
Para continuar el trabajo, usa el patrón descrito en "Rutina de trabajo con Claude".

---

*Documento generado el 26/12/2025*
