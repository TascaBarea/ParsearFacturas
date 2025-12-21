# PROVEEDORES - Estado de Extractores

**Actualizado:** 21/12/2025 | **Versión:** v4.4

---

## 📊 RESUMEN

| Estado | Cantidad | % |
|--------|----------|---|
| ✅ Con extractor funcionando | **~100** | ~90% |
| ⚠️ Parcial/OCR | 8 | 7% |
| ❌ Sin extractor | ~5 | 3% |
| **Total proveedores activos** | **~113** | 100% |

---

## ✅ NUEVOS EN SESIÓN 21/12/2025 (12 extractores)

| # | Proveedor | CIF | IBAN | Facturas | Método |
|---|-----------|-----|------|----------|--------|
| 1 | **QUESERIA ZUCCA** | B42861948 | ES23 2100 5192 5702 0004 5025 | 7/7 ✅ | pdfplumber |
| 2 | **PANRUJE** | B13858014 | ES19 0081 5344 2800 0261 4066 | 6/6 ✅ | pdfplumber |
| 3 | **GRUPO DISBER** | B43489039 | ES53 0182 5561 4802 0150 7382 | 4/4 ✅ | pdfplumber |
| 4 | **LIDL** | A60195278 | - (tarjeta) | 5/5 ✅ | pdfplumber |
| 5 | **LA ROSQUILLERIA** | B86556081 | ES66 0081 0238 0400 0119 8704 | 7/7 ✅ | OCR |
| 6 | **GADITAUN** | 34007216Z | ES19 0081 0259 1000 0163 8268 | 5/5 ✅ | OCR |
| 7 | **DE LUIS** | B87893681 | ES68 0049 5117 5027 1600 3797 | 5/5 ✅ | híbrido |
| 8 | **MANIPULADOS ABELLAN** | B30243737 | ES06 2100 8321 0413 0018 3503 | 6/6 ✅ | OCR |
| 9 | **ECOMS/DIA** | B72738602 | - (efectivo) | 6/8 ✅ | híbrido |
| 10 | **MARITA COSTA** | 48207369J | ES78 2100 6398 7002 0001 9653 | 9/9 ✅ | pdfplumber |
| 11 | **SERRÍN NO CHAN** | B87214755 | ES88 0049 6650 1329 1001 8834 | 7/7 ✅ | pdfplumber |
| 12 | **FISHGOURMET** | B85975126 | ES57 2100 2127 1502 0045 4128 | 5/5 ✅ | OCR |

**Total sesión: 72/74 facturas validadas (97%)**

### Características especiales

| Proveedor | IVA | Peculiaridad |
|-----------|-----|--------------|
| ZUCCA | 4%/10% | Quesos artesanales, IVA mixto |
| PANRUJE | 4% | Pan y rosquillas |
| DISBER | 10%/21% | Distribuidor alimentación |
| LIDL | variable | Tickets supermercado |
| LA ROSQUILLERIA | 4%/10%/21% | OCR, envío separado al 21% |
| GADITAUN | 10% | OCR, conservas Cádiz |
| DE LUIS | 10%/21% | Híbrido pdfplumber+OCR |
| ABELLAN | 10% | OCR, conservas vegetales |
| ECOMS | variable | Tickets DIA, híbrido |
| MARITA COSTA | 4%/10%/21% | AOVE y gourmet |
| SERRÍN NO CHAN | 4%/10%/21% | Ultramarinos gallegos |
| FISHGOURMET | 10% | OCR, ahumados pescado |

---

## ✅ SESIÓN 20/12/2025 (6 extractores)

| Proveedor | CIF | Facturas | Método |
|-----------|-----|----------|--------|
| MANIPULADOS ABELLAN | B30243737 | 6/6 ✅ | OCR |
| LA ROSQUILLERIA | B86556081 | 5/5 ✅ | OCR |
| FABEIRO | B79992079 | 8/8 ✅ | pdfplumber |
| KINEMA | F84600022 | 5/5 ✅ | pdfplumber |
| SILVA CORDERO | B09861535 | 8/8 ✅ | pdfplumber |
| ARTESANOS MOLLETE | B93662708 | 6/6 ✅ | pdfplumber |

---

## ✅ SESIÓN 19/12/2025 (12 extractores)

| Proveedor | CIF | Estado |
|-----------|-----|--------|
| ISTA | B80580850 | ✅ |
| CVNE | A31001897 | ✅ |
| QUESOS FELIX | B47440136 | ✅ |
| MIGUEZ CAL | B79868006 | ✅ |
| DISTRIBUCIONES LAVAPIES | F88424072 | ✅ |
| MARTIN ABENZA | 74305431K | ✅ |
| BM SUPERMERCADOS | B81506623 | ✅ (refactorizado) |
| ECOFICUS | B06870935 | ✅ |
| SABORES DE PATERNA | 28622953N | ✅ |
| LA BARRA DULCE | B19981141 | ✅ |

---

## 🔴 PENDIENTES PRIORITARIOS

| # | Proveedor | Facturas | Error | Impacto |
|---|-----------|----------|-------|---------|
| 1 | **JIMELUZ** | 14 | SIN_TOTAL/DESCUADRE | ALTO |
| 2 | **PIFEMA** | 4 | DESCUADRE ~100€ | MEDIO |
| 3 | **LA PURISIMA** | 3 | SIN_TOTAL | BAJO |
| 4 | **GRUPO KUAI** | 2 | SIN_LINEAS | BAJO |

---

## 📋 TODOS LOS EXTRACTORES POR ARCHIVO

### Nuevos (21/12/2025)
| Archivo | Proveedor | CIF |
|---------|-----------|-----|
| `zucca.py` | QUESERIA ZUCCA, FORMAGGIARTE | B42861948 |
| `panruje.py` | PANRUJE | B13858014 |
| `grupo_disber.py` | GRUPO DISBER, DISBER | B43489039 |
| `lidl.py` | LIDL | A60195278 |
| `la_rosquilleria.py` | LA ROSQUILLERIA, ROSQUILLERIA | B86556081 |
| `gaditaun.py` | GADITAUN, MARIA LINAREJOS | 34007216Z |
| `de_luis.py` | DE LUIS, SABORES UNICOS | B87893681 |
| `manipulados_abellan.py` | MANIPULADOS ABELLAN, ABELLAN | B30243737 |
| `ecoms.py` | ECOMS, DIA, ECOMS SUPERMARKET | B72738602 |
| `marita_costa.py` | MARITA COSTA | 48207369J |
| `serrin_no_chan.py` | SERRÍN NO CHAN, SERRIN | B87214755 |
| `fishgourmet.py` | FISHGOURMET | B85975126 |

### Anteriores funcionando
| Archivo | Proveedores |
|---------|-------------|
| `bm.py` | BM SUPERMERCADOS |
| `ceres.py` | CERES |
| `madrueño.py` | LICORES MADRUEÑO |
| `bernal.py` | JAMONES BERNAL |
| `berzal.py` | BERZAL HERMANOS |
| `fabeiro.py` | FABEIRO |
| `francisco_guerra.py` | FRANCISCO GUERRA |
| `felisa.py` | FELISA GOURMET |
| `borboton.py` | BODEGAS BORBOTON |
| `zubelzu.py` | ZUBELZU, IBARRAKO PIPARRAK |
| `emjamesa.py` | EMJAMESA |
| `molienda_verde.py` | LA MOLIENDA VERDE |
| `kinema.py` | KINEMA |
| `silva_cordero.py` | SILVA CORDERO, QUESOS ACEHUCHE |
| `artesanos_mollete.py` | ARTESANOS DEL MOLLETE, MOLLETES |
| `yoigo.py` | YOIGO, XFERA |
| `segurma.py` | SEGURMA |
| `som_energia.py` | SOM ENERGIA |
| `lucera.py` | LUCERA |
| `trucco.py` | TRUCCO, ISAAC RODRIGUEZ |
| `arganza.py` | VINOS DE ARGANZA |
| `hernandez.py` | HERNANDEZ |
| `jimeluz.py` | JIMELUZ (parcial) |
| `ista.py` | ISTA |
| `cvne.py` | CVNE, CUNE |
| `quesos_felix.py` | QUESOS FELIX |
| `miguez_cal.py` | MIGUEZ CAL, FORPLAN |
| `distribuciones_lavapies.py` | DISTRIBUCIONES LAVAPIES |
| `martin_abenza.py` | MARTIN ABENZA, EL MODESTO |
| `ecoficus.py` | ECOFICUS |
| `sabores_paterna.py` | SABORES DE PATERNA |
| `la_barra_dulce.py` | LA BARRA DULCE |

---

## 🔧 VARIANTES DE NOMBRES REGISTRADAS

| Extractor | Variantes en @registrar() |
|-----------|--------------------------|
| ZUCCA | QUESERIA ZUCCA, ZUCCA, FORMAGGIARTE |
| PANRUJE | PANRUJE |
| DISBER | GRUPO DISBER, DISBER, DISTRIBUCIONES DISBER |
| ROSQUILLERIA | LA ROSQUILLERIA, ROSQUILLERIA, LAS ROSQUILLAS EL TORRO |
| GADITAUN | GADITAUN, MARIA LINAREJOS, MARTINEZ RODRIGUEZ MARIA |
| DE LUIS | DE LUIS, DE LUIS SABORES UNICOS, SABORES UNICOS |
| ABELLAN | MANIPULADOS ABELLAN, ABELLAN, PRODUCTOS MANIPULADOS |
| ECOMS | ECOMS, ECOMS SUPERMARKET, DIA, GRUPO DIA |
| MARITA COSTA | MARITA COSTA, COSTA DELGADO MARIA PILAR |
| SERRIN | SERRÍN NO CHAN, SERRIN NO CHAN, SERRIN |
| FISHGOURMET | FISHGOURMET, FISH GOURMET |

---

## 📝 CHANGELOG PROVEEDORES

| Fecha | Cambio |
|-------|--------|
| **2025-12-21** | **+12 extractores: ZUCCA, PANRUJE, DISBER, LIDL, ROSQUILLERIA, GADITAUN, DE LUIS, ABELLAN, ECOMS, MARITA COSTA, SERRIN, FISHGOURMET** |
| 2025-12-20 | +6 extractores: MANIPULADOS ABELLAN (OCR), LA ROSQUILLERIA (OCR), FABEIRO, KINEMA, SILVA CORDERO, ARTESANOS MOLLETE |
| 2025-12-19 tarde | +6 extractores: ISTA, CVNE, QUESOS FELIX, MIGUEZ CAL, LAVAPIES, MARTIN ABENZA |
| 2025-12-19 mañana | BM refactorizado. +4: ECOFICUS, SABORES, BARRA DULCE |
| 2025-12-18 | FABEIRO nuevo. 8 extractores a pdfplumber. |

---

*Última actualización: 21/12/2025*
