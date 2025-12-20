# PROVEEDORES - Estado de Extractores

**Actualizado:** 19/12/2025 | **Versión:** v4.2

---

## 📊 RESUMEN

| Estado | Cantidad | % |
|--------|----------|---|
| ✅ Con extractor funcionando | **80+** | ~80% |
| ⚠️ Parcial/OCR | 6 | 6% |
| ❌ Sin extractor | ~14 | 14% |
| **Total proveedores** | **~100** | 100% |

---

## ✅ NUEVOS EN SESIÓN 19/12/2025 TARDE

| Proveedor | Archivo | Facturas | IVA | Notas |
|-----------|---------|----------|-----|-------|
| **ISTA** | `ista.py` | 6/6 ✅ | 10% | Recibos agua |
| **CVNE** | `cvne.py` | 4/4 ✅ | 21% | Vinos |
| **QUESOS FELIX** | `quesos_felix.py` | 3/3 ✅ | 4% | Quesos IGP |
| **MIGUEZ CAL** | `miguez_cal.py` | 5/5 ✅ | 21% | Limpieza ForPlan |
| **DISTRIBUCIONES LAVAPIES** | `distribuciones_lavapies.py` | 6/6 ✅ | 10%/21% | Bebidas |
| **MARTIN ABENZA** | `martin_abenza.py` | 5/5 ✅ | 10%+0% | Conservas El Modesto |

---

## ✅ ARREGLADOS EN SESIÓN 19/12/2025 MAÑANA

| Proveedor | Archivo | Facturas | Cambio |
|-----------|---------|----------|--------|
| **BM SUPERMERCADOS** | `bm.py` | 34 ✅ | Refactorizado completo |
| **MOLLETES ARTESANOS** | `molletes.py` | 4 ✅ | Líneas individuales |
| **ECOFICUS** | `ecoficus.py` | 2 ✅ | Higos ecológicos |
| **SABORES DE PATERNA** | `sabores_paterna.py` | 6 ✅ | Embutidos Cádiz |
| **LA BARRA DULCE** | `la_barra_dulce.py` | 3 ✅ | Pastelería |

---

## 🔴 PENDIENTES PRIORITARIOS

### Por volumen de facturas

| # | Proveedor | Facturas | Error | Notas |
|---|-----------|----------|-------|-------|
| 1 | **LA ROSQUILLERIA** | 4 | DESCUADRE_~2€ | Investigar |
| 2 | **PANRUJE** | 3 | SIN_TOTAL | |
| 3 | **LIDL** | 3 | FECHA_PENDIENTE | |
| 4 | **OPENAI** | 4 | FECHA_PENDIENTE | |
| 5 | **GRUPO DISBER** | 2 | SIN_LINEAS | |
| 6 | **MRM** | 3 | SIN_LINEAS | |

---

## 📋 EXTRACTORES POR ARCHIVO

### Nuevos (19/12/2025 tarde)
| Archivo | Proveedor | CIF | Estado |
|---------|-----------|-----|--------|
| `ista.py` | ISTA | ES B80580850 | ✅ NUEVO |
| `cvne.py` | CVNE | A31001897 | ✅ NUEVO |
| `quesos_felix.py` | QUESOS FELIX | B47440136 | ✅ NUEVO |
| `miguez_cal.py` | MIGUEZ CAL | B79868006 | ✅ NUEVO |
| `distribuciones_lavapies.py` | DISTRIBUCIONES LAVAPIES | F88424072 | ✅ NUEVO |
| `martin_abenza.py` | MARTIN ABENZA | 74305431K | ✅ NUEVO |

### Refactorizados (19/12/2025 mañana)
| Archivo | Proveedor | Estado |
|---------|-----------|--------|
| `bm.py` | BM SUPERMERCADOS | ✅ REFACTORIZADO |
| `molletes.py` | MOLLETES ARTESANOS | ✅ REFACTORIZADO |
| `ecoficus.py` | ECOFICUS | ✅ REFACTORIZADO |
| `sabores_paterna.py` | SABORES DE PATERNA | ✅ REFACTORIZADO |
| `la_barra_dulce.py` | LA BARRA DULCE | ✅ REFACTORIZADO |

### Anteriores funcionando
| Archivo | Proveedores |
|---------|-------------|
| `madrueño.py` | LICORES MADRUEÑO |
| `bernal.py` | JAMONES BERNAL |
| `berzal.py` | BERZAL HERMANOS |
| `ceres.py` | CERES |
| `francisco_guerra.py` | FRANCISCO GUERRA |
| `felisa.py` | FELISA GOURMET |
| `borboton.py` | BODEGAS BORBOTON |
| `zubelzu.py` | ZUBELZU |
| `emjamesa.py` | EMJAMESA |
| `molienda_verde.py` | LA MOLIENDA VERDE |
| `zucca.py` | QUESERIA ZUCCA |
| `yoigo.py` | YOIGO/XFERA |
| `segurma.py` | SEGURMA |
| `som_energia.py` | SOM ENERGIA |
| `lucera.py` | LUCERA |
| `trucco.py` | TRUCCO/ISAAC RODRIGUEZ |
| `arganza.py` | VINOS DE ARGANZA |
| `hernandez.py` | HERNANDEZ |
| `fabeiro.py` | FABEIRO |
| `jimeluz.py` | JIMELUZ |
| `direccion360.py` | DIRECCION TRES SESENTA |

---

## 📈 LISTA COMPLETA EXTRACTORES (80+)

| # | Proveedor | Archivo | pdfplumber | Estado |
|---|-----------|---------|------------|--------|
| 1 | BM SUPERMERCADOS | bm.py | ✅ | ✅ OK |
| 2 | CERES | ceres.py | ✅ | ✅ OK |
| 3 | LICORES MADRUEÑO | madrueño.py | ✅ | ✅ OK |
| 4 | JAMONES BERNAL | bernal.py | ✅ | ✅ OK |
| 5 | BERZAL | berzal.py | ✅ | ✅ OK |
| 6 | FRANCISCO GUERRA | francisco_guerra.py | ✅ | ✅ OK |
| 7 | SABORES DE PATERNA | sabores_paterna.py | ✅ | ✅ OK |
| 8 | LA BARRA DULCE | la_barra_dulce.py | ✅ | ✅ OK |
| 9 | ECOFICUS | ecoficus.py | ✅ | ✅ OK |
| 10 | MOLLETES ARTESANOS | molletes.py | ✅ | ✅ OK |
| 11 | **ISTA** | ista.py | ✅ | ✅ NUEVO |
| 12 | **CVNE** | cvne.py | ✅ | ✅ NUEVO |
| 13 | **QUESOS FELIX** | quesos_felix.py | ✅ | ✅ NUEVO |
| 14 | **MIGUEZ CAL** | miguez_cal.py | ✅ | ✅ NUEVO |
| 15 | **DISTRIBUCIONES LAVAPIES** | distribuciones_lavapies.py | ✅ | ✅ NUEVO |
| 16 | **MARTIN ABENZA** | martin_abenza.py | ✅ | ✅ NUEVO |
| 17 | FELISA GOURMET | felisa.py | ✅ | ✅ OK |
| 18 | BODEGAS BORBOTON | borboton.py | ✅ | ✅ OK |
| 19 | ZUBELZU | zubelzu.py | ✅ | ✅ OK |
| 20 | EMJAMESA | emjamesa.py | ✅ | ✅ OK |
| 21 | LA MOLIENDA VERDE | molienda_verde.py | ✅ | ✅ OK |
| 22 | QUESERIA ZUCCA | zucca.py | ✅ | ✅ OK |
| 23 | YOIGO | yoigo.py | ✅ | ✅ OK |
| 24 | SEGURMA | segurma.py | ✅ | ✅ OK |
| 25 | SOM ENERGIA | som_energia.py | ✅ | ✅ OK |
| 26 | LUCERA | lucera.py | ✅ | ✅ OK |
| 27 | TRUCCO | trucco.py | ✅ | ✅ OK |
| 28 | VINOS DE ARGANZA | arganza.py | ✅ | ✅ OK |
| 29 | HERNANDEZ | hernandez.py | ✅ | ✅ OK |
| 30 | FABEIRO | fabeiro.py | ✅ | ✅ OK |
| ... | ... | ... | ... | ... |

**Total: 80+ extractores funcionando**

---

## 🔧 VARIANTES DE NOMBRES

| Extractor | Variantes registradas |
|-----------|----------------------|
| MARTIN ABENZA | MARTIN ABENZA, MARTIN ARBENZA, EL MODESTO, CONSERVAS EL MODESTO |
| DISTRIBUCIONES LAVAPIES | DISTRIBUCIONES LAVAPIES, LAVAPIES |
| MIGUEZ CAL | MIGUEZ CAL, FORPLAN |
| ISTA | ISTA |
| CVNE | CVNE, CUNE |
| QUESOS FELIX | QUESOS FELIX |

---

## 📝 CHANGELOG PROVEEDORES

| Fecha | Cambio |
|-------|--------|
| **2025-12-19 tarde** | **+6 extractores: ISTA, CVNE, QUESOS FELIX, MIGUEZ CAL, LAVAPIES, MARTIN ABENZA** |
| 2025-12-19 mañana | BM refactorizado. +5: MOLLETES, ECOFICUS, SABORES, BARRA DULCE |
| 2025-12-18 | FABEIRO nuevo. 8 extractores a pdfplumber. |

---

*Última actualización: 19/12/2025 tarde*
