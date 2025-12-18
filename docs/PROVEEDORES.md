# PROVEEDORES - Estado de Extractores

**Actualizado:** 17/12/2025 | **Versión:** v3.56

---

## 📊 RESUMEN

| Estado | Cantidad | % |
|--------|----------|---|
| ✅ Con extractor | 68+ | 70% |
| ⚠️ OCR (parcial) | 6 | 6% |
| ❌ Sin extractor | ~23 | 24% |
| **Total** | **97** | 100% |

---

## 📈 TOP 10 PROVEEDORES POR VOLUMEN (2024)

| # | Proveedor | Fact/año | % Total | Estado |
|---|-----------|----------|---------|--------|
| 1 | JIMELUZ | 215 | 19.5% | ⚠️ OCR pendiente |
| 2 | BM SUPERMERCADOS | 147 | 13.3% | ✅ |
| 3 | CERES | 102 | 9.2% | ✅ |
| 4 | LA ROSQUILLERIA | 21 | 1.9% | ✅ v3.55 OCR |
| 5 | DISTRIBUCIONES LAVAPIES | 20 | 1.8% | ✅ v3.54 |
| 6 | LIDL | 18 | 1.6% | ✅ v3.54 |
| 7 | SABORES DE PATERNA | 16 | 1.4% | ✅ |
| 8 | MIGUEZ CAL | 15 | 1.4% | ✅ |
| 9 | ALCAMPO | 14 | 1.3% | ❌ (TJ) |
| 10 | BENJAMIN ORTEGA | 13 | 1.2% | ✅ |

**TOP 3 = 42% de todas las facturas**

---

## ✅ ARREGLADOS EN v3.56 (17/12/2025)

| Proveedor | Facturas | Cambio |
|-----------|----------|--------|
| **ECOMS/DIA** | 5/7 ✅ | Nuevo extractor dual (OCR + PDF digital) |
| **BODEGAS BORBOTON** | 10/10 ✅ | Fix orden patrones extraer_total() |
| **MARITA COSTA** | 4/4 ✅ | Añadido patrón TOTAL: antes de IBARRAKO |
| **LA ROSQUILLERIA** | 2/2 ✅ | Confirmado funcionando con OCR |

### Correcciones técnicas v3.56

- Nuevo `extraer_lineas_ecoms()` con soporte dual OCR/digital
- Reordenamiento patrones en `extraer_total()`: específicos antes de genéricos
- Añadido ECOMS/DIA a DATOS_PROVEEDORES y CIF_TO_PROVEEDOR
- Fix: IBARRAKO ya no captura importes de línea de producto

---

## ✅ EXTRACTORES FUNCIONANDO (68+)

| # | Proveedor | Función | Notas |
|---|-----------|---------|-------|
| 1 | ABBATI CAFE | `extraer_lineas_abbati` | |
| 2 | ANA CABALLO | `extraer_lineas_ana_caballo` | |
| 3 | ANGEL Y LOLI | `extraer_lineas_angel_y_loli` | v3.53 |
| 4 | ARGANZA (Vinos) | `extraer_lineas_arganza` | v3.56 OCR |
| 5 | BARRA DULCE | `extraer_lineas_barra_dulce` | |
| 6 | BENJAMIN ORTEGA | `extraer_lineas_alquiler_ortega` | Retención IRPF |
| 7 | BERNAL (Jamones) | `extraer_lineas_bernal` | |
| 8 | BERZAL | `extraer_lineas_berzal` | v3.50 |
| 9 | BIELLEBI | `extraer_lineas_biellebi` | IBAN italiano |
| 10 | BM SUPERMERCADOS | `extraer_lineas_bm` | 147 fact/año |
| 11 | **BORBOTON** | `extraer_lineas_borboton` | **v3.56 ✅ Fix total** |
| 12 | CARLOS NAVAS | `extraer_lineas_carlos_navas` | |
| 13 | CARRASCAL | `extraer_lineas_carrascal` | v3.52 |
| 14 | CERES | `extraer_lineas_ceres` | v3.56 fix envases ALH |
| 15 | CONTROLPLAGA | `extraer_lineas_controlplaga` | |
| 16 | CVNE | `extraer_lineas_cvne` | |
| 17 | DISBER | `extraer_lineas_disber` | |
| 18 | **ECOMS/DIA** | `extraer_lineas_ecoms` | **v3.56 ✅ Nuevo** |
| 19 | ECOFICUS | `extraer_lineas_ecoficus` | Con portes |
| 20 | EMJAMESA | `extraer_lineas_emjamesa` | v3.55 ✅ |
| 21 | FABEIRO | `extraer_lineas_fabeiro` | |
| 22 | FELISA GOURMET | `extraer_lineas_felisa` | v3.54 ✅ |
| 23 | FERRIOL | `extraer_lineas_ferriol` | v3.53 |
| 24 | FRANCISCO GUERRA | `extraer_lineas_francisco_guerra` | |
| 25 | GADITAUN | `extraer_lineas_gaditaun` | v3.56 ✅ |
| 26 | GREDALES | `extraer_lineas_gredales` | v3.56 ✅ |
| 27 | GRUPO CAMPERO | `extraer_lineas_grupo_campero` | |
| 28 | IBARRAKO PIPARRAK | `extraer_lineas_ibarrako` | v3.55 ✅ OCR |
| 29 | ISTA | `extraer_lineas_ista` | |
| 30 | JAIME FERNANDEZ | `extraer_lineas_alquiler_fernandez` | Retención IRPF |
| 31 | JULIO GARCIA VIVAS | `extraer_lineas_julio_garcia_vivas` | |
| 32 | KINEMA | `extraer_lineas_kinema` | |
| 33 | LAVAPIES | `extraer_lineas_lavapies` | v3.54 ✅ |
| 34 | LICORES MADRUÑO | `extraer_lineas_licores_madrueno` | |
| 35 | LIDL | `extraer_lineas_lidl` | v3.54 ✅ |
| 36 | LUCERA | `extraer_lineas_lucera` | |
| 37 | MANIPULADOS ABELLAN | `extraer_lineas_manipulados_abellan` | v3.55 ✅ OCR |
| 38 | **MARITA COSTA** | `extraer_lineas_marita_costa` | **v3.56 ✅ Fix total** |
| 39 | MARTIN ABENZA | `extraer_lineas_martin_abenza` | |
| 40 | MIGUEZ CAL | `extraer_lineas_miguez_cal` | |
| 41 | MOLIENDA VERDE | `extraer_lineas_molienda_verde` | v3.52 |
| 42 | MOLLETES | `extraer_lineas_molletes` | |
| 43 | MRM | `extraer_lineas_mrm` | |
| 44 | MUÑOZ MARTIN | `extraer_lineas_munoz_martin` | v3.54 ✅ |
| 45 | OPENAI | `extraer_lineas_openai` | v3.53 |
| 46 | PANIFIESTO | `extraer_lineas_panifiesto` | |
| 47 | PANRUJE | `extraer_lineas_panruje` | |
| 48 | PC COMPONENTES | `extraer_lineas_pc_componentes` | v3.52 |
| 49 | PILAR RODRIGUEZ | `extraer_lineas_pilar_rodriguez` | |
| 50 | PORVAZ | `extraer_lineas_porvaz` | |
| 51 | PRODUCTOS ADELL | `extraer_lineas_productos_adell` | |
| 52 | PURISIMA | `extraer_lineas_purisima` | |
| 53 | QUESOS CATI | `extraer_lineas_quesos_cati` | |
| 54 | QUESOS FELIX | `extraer_lineas_quesos_felix` | |
| 55 | QUESOS NAVAS | `extraer_lineas_quesos_navas` | |
| 56 | QUESOS ROYCA | `extraer_lineas_quesos_royca` | v3.53 |
| 57 | LA ROSQUILLERIA | `extraer_lineas_rosquilleria` | v3.55 ✅ OCR |
| 58 | SABORES PATERNA | `extraer_lineas_sabores_paterna` | |
| 59 | SEGURMA | `extraer_lineas_segurma` | |
| 60 | SERRIN NO CHAN | `extraer_lineas_serrin` | v3.56 ✅ |
| 61 | SILVA CORDERO | `extraer_lineas_silva_cordero` | v3.52 |
| 62 | SOM ENERGIA | `extraer_lineas_som_energia` | (CUADRE pendiente) |
| 63 | TRUCCO | `extraer_lineas_trucco` | |
| 64 | YOIGO | `extraer_lineas_yoigo` | |
| 65 | ZUCCA | `extraer_lineas_zucca` | |
| 66 | ZUBELZU | `extraer_lineas_zubelzu` | v3.54 ✅ |

---

## ⚠️ PROVEEDORES OCR - Estado

| Proveedor | Fact/año | Estado | Notas |
|-----------|----------|--------|-------|
| **JIMELUZ** | **215** | ⚠️ Pendiente | Tickets físicos, necesita extractor |
| ECOMS/DIA | ~15 | ✅ v3.56 | 5/7 OK, 2 OCR muy malo |
| LA ROSQUILLERIA | ~21 | ✅ v3.55 | Funcionando |
| MANIPULADOS ABELLAN | ~12 | ✅ v3.55 | Funcionando |
| IBARRAKO PIPARRAK | ~6 | ✅ v3.55 | Funcionando |
| VINOS DE ARGANZA | ~4 | ✅ v3.56 | OCR con fallback |

---

## ❌ SIN EXTRACTOR (~23)

### Prioridad ALTA (muchas facturas)

| Proveedor | Fact/año | Método pago | Notas |
|-----------|----------|-------------|-------|
| **JIMELUZ** | **215** | TF | **#1 PRIORIDAD** |

### Prioridad BAJA (pocas facturas o pago no-TF)

| Proveedor | Método pago | Notas |
|-----------|-------------|-------|
| ALCAMPO | TJ | |
| AMAZON | TJ | |
| MAKRO | TJ | |
| FNMT | TJ | |
| BIG MAT | EF/TJ | |
| EL CORTE INGLÉS | EF | |
| ZARA HOME | TJ | |
| VICTORINO MARTIN | TJ | Pago tarjeta |
| CASA DEL DUQUE | TJ | Pago tarjeta |

---

## ⚠️ CUADRE_PENDIENTE (investigar)

| Proveedor | Facturas afectadas | Prioridad |
|-----------|-------------------|-----------|
| SOM ENERGIA | 5 | ALTA |
| LUCERA | 3 | BAJA |
| QUESOS FELIX | 3 | BAJA |

### Resueltos v3.56 ✅
- ~~BODEGAS BORBOTON~~ (10 facturas) → Fix orden patrones
- ~~MARITA COSTA~~ (4 facturas) → Añadido patrón TOTAL:
- ~~LA ROSQUILLERIA~~ (2 facturas) → Confirmado OK

---

## 📝 CHANGELOG PROVEEDORES

| Fecha | Cambio |
|-------|--------|
| **2025-12-17** | **+ECOMS/DIA nuevo. BORBOTON/MARITA fix. ROSQUILLERIA confirmado** |
| 2025-12-16 | +IBARRAKO, ABELLAN (OCR). +EMJAMESA fix. ROSQUILLERIA parcial |
| 2025-12-15 | +LIDL nuevo, BORBOTON/FELISA/LAVAPIES/ZUBELZU/MUÑOZ MARTIN |
| 2025-12-14 | +7 proveedores confirmados, LA ROSQUILLERIA OCR inicial |

---

## 🔧 PROVEEDORES CON CANTIDAD/PRECIO UNITARIO

| Proveedor | Versión |
|-----------|---------|
| LIDL | v3.54 ✅ |
| FELISA GOURMET | v3.54 ✅ |
| BODEGAS MUÑOZ MARTIN | v3.54 ✅ |
| CERES | v3.54 ✅ |
| BORBOTON | v3.54 ✅ |
| MANIPULADOS ABELLAN | v3.55 ✅ |
| IBARRAKO PIPARRAK | v3.55 ✅ |

---

*Última actualización: 17/12/2025 - Sesión ECOMS + BORBOTON + MARITA*
