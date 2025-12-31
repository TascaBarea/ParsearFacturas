# PROVEEDORES - Estado de Extractores

**Actualizado:** 31/12/2025 | **Versión:** v5.4

---

## 📊 RESUMEN

| Estado | Cantidad | % |
|--------|----------|---|
| ✅ Con extractor funcionando | **~140** | ~95% |
| ⚠️ Parcial/OCR | ~5 | 3% |
| ❌ Sin extractor | ~3 | 2% |
| **Total proveedores activos** | **~148** | 100% |

---

## ✅ SESIÓN 31/12/2025 (1 nuevo + 2 mejorados)

| # | Proveedor | CIF | IBAN | Facturas | Método |
|---|-----------|-----|------|----------|--------|
| 1 | **DISTRIBUCIONES LAVAPIES** | F88424072 | ES39 3035 0376 14 3760011213 | 13/13 ✅ | pdfplumber |
| 2 | BODEGAS MUÑOZ MARTIN | E83182683 | ES62 0049 5184 11 2016002766 | 4/4 ✅ | **híbrido** |
| 3 | LOS GREDALES | B83594150 | ES82 2103 7178 2800 3001 2932 | 5/5 ✅ | pdfplumber |

### Características especiales

| Proveedor | IVA | Peculiaridad |
|-----------|-----|--------------|
| **LAVAPIES** | 10%/21% | ⚠️ **IVA deducido de factura** - Proveedor con errores frecuentes. Algoritmo subset-sum para determinar IVA. Genera avisos de discrepancia. |
| BODEGAS MUÑOZ | 21% | **Híbrido pdfplumber+OCR** - Algunas facturas escaneadas |
| LOS GREDALES | 21% | Líneas individuales con categorías (SAUVIGNON, SYRAH, CABERNET...) |

### Productos LAVAPIES

| REF | Producto | IVA esperado | Categoría |
|-----|----------|--------------|-----------|
| AGUVIC | AGUA VICHY CATALAN | 10% | AGUA CON GAS |
| ZULINMA/PE/TO | ZUMOS LINDA | 10% | ZUMOS |
| REFSIFG/SIFT | SIFONES | 10% | SIFON |
| ZUMMOG1 | MOSTO GREIP | 21% | MOSTO |
| REFCAS1 | GASEOSA CASERA | 21% | GASEOSA |
| REFREV2 | REVOLTOSA LIMON | 21% | REFRESCO DE LIMON |
| REFFRIX | FRIXEN COLA | 21% | REFRESCO DE COLA |
| PALESZE/CO | PALESTINA | 21% | REFRESCO DE COLA |
| SCHT15 | SCHWEPPES TÓNICA | 21% | TONICA |
| REFSEV | SEVEN UP | 21% | REFRESCO DE LIMON |

---

## ✅ SESIÓN 30/12/2025 (4 corregidos)

| # | Proveedor | CIF | Estado | Cambio |
|---|-----------|-----|--------|--------|
| 1 | DE LUIS | B78380685 | ✅ | Deduplicación + total |
| 2 | ALFARERIA TALAVERANA | B45007374 | ✅ | Descuento/portes |
| 3 | PORVAZ | E36131709 | ✅ | Bug Ñ en ZAMBURIÑA |
| 4 | INMAREPRO | B86310109 | ✅ NUEVO | Mantenimiento extintores |

---

## ✅ SESIÓN 29/12/2025 (Bugs corregidos)

| Proveedor | Problema | Solución |
|-----------|----------|----------|
| DEBORA GARCIA | IRPF mal calculado | Fórmula corregida |
| FELISA | No detectaba alias | Alias añadido en @registrar |
| HERNÁNDEZ BODEGA | Encoding Ñ | UTF-8 correcto |
| SILVA CORDERO | IVA mixto | Separación 10%/21% |
| **base.py** | extraer_referencia vacío | Llama a extraer_numero_factura automáticamente |

---

## ✅ SESIÓN 28/12/2025 (6 nuevos)

| # | Proveedor | CIF | Facturas | Método |
|---|-----------|-----|----------|--------|
| 1 | ECOMS SUPERMARKET | B72738602 | 9/14 | Híbrido (letras IVA) |
| 2 | VIRGEN DE LA SIERRA | F50019868 | 7/7 ✅ | Híbrido |
| 3 | MARITA COSTA | 48207369J | 7/7 ✅ | pdfplumber |
| 4 | CASA DEL DUQUE | B23613697 | 8/10 | OCR |
| 5 | CELONIS/MAKE | DE315052800 | 10/10 ✅ | pdfplumber |
| 6 | PIFEMA | B79048914 | 5/5 ✅ | pdfplumber |

---

## ✅ SESIÓN 26/12/2025 (16 nuevos)

| # | Proveedor | CIF | IVA | Método |
|---|-----------|-----|-----|--------|
| 1 | YOIGO | A81020715 | 21% | pdfplumber |
| 2 | SOM ENERGIA | F55091367 | 21% | pdfplumber |
| 3 | SEGURMA | B86414901 | 21% | pdfplumber |
| 4 | TRUCCO | 05247386M | 21% | pdfplumber |
| 5 | MRM | A80280845 | 10% | pdfplumber |
| 6 | BIELLEBI | IT06089700725 | 0% | pdfplumber |
| 7 | PANRUJE | B13858014 | 4% | pdfplumber |
| 8 | LA PURISIMA | F30005193 | 21% | pdfplumber |
| 9 | MERCADONA | A46103834 | Variable | pdfplumber |
| 10 | WEBEMPRESA | B65739856 | 21% | pdfplumber |
| 11 | OPENAI | EU372041333 | 0% | pdfplumber |
| 12 | ANTHROPIC | - (USA) | 0% | pdfplumber |
| 13 | LA ALACENA | B45776233 | 10% | pdfplumber |
| 14 | DEBORA GARCIA | 53401030Y | 21% | pdfplumber |
| 15 | BORBOTON | B09530601 | 21% | pdfplumber |
| 16 | LAVAPIES (v1) | F88424072 | 10%/21% | pdfplumber |

---

## 🔴 PENDIENTES PRIORITARIOS

| # | Proveedor | Errores | Tipo | Impacto |
|---|-----------|---------|------|---------|
| 1 | **BM SUPERMERCADOS** | 37 | DESCUADRE | ALTO |
| 2 | **JIMELUZ** | 19 | OCR | ALTO |
| 3 | **FELISA GOURMET** | 12 | DESCUADRE | MEDIO |
| 4 | **LA ROSQUILLERIA** | 10 | OCR | MEDIO |
| 5 | JAMONES BERNAL | 6 | DESCUADRE | BAJO |
| 6 | SILVA CORDERO | 5 | DESCUADRE | BAJO |

---

## 📋 EXTRACTORES POR ARCHIVO (Sesiones recientes)

### Sesión 31/12/2025
| Archivo | Proveedor | CIF |
|---------|-----------|-----|
| `lavapies.py` | DISTRIBUCIONES LAVAPIES | F88424072 |
| `bodegas_munoz.py` | BODEGAS MUÑOZ MARTIN | E83182683 |
| `gredales.py` | LOS GREDALES DE EL TOBOSO | B83594150 |

### Sesión 30/12/2025
| Archivo | Proveedor | CIF |
|---------|-----------|-----|
| `de_luis.py` | DE LUIS DISTRIBUCION | B78380685 |
| `alfareria.py` | ALFARERIA TALAVERANA | B45007374 |
| `porvaz.py` | CONSERVAS PORVAZ | E36131709 |
| `inmarepro.py` | INMAREPRO | B86310109 |

### Sesión 28/12/2025
| Archivo | Proveedor | CIF |
|---------|-----------|-----|
| `ecoms.py` | ECOMS SUPERMARKET | B72738602 |
| `virgen_de_la_sierra.py` | VIRGEN DE LA SIERRA | F50019868 |
| `marita_costa.py` | MARITA COSTA | 48207369J |
| `casa_del_duque.py` | CASA DEL DUQUE | B23613697 |
| `celonis.py` | CELONIS/MAKE | DE315052800 |
| `pifema.py` | PIFEMA | B79048914 |

### Sesión 26/12/2025
| Archivo | Proveedor |
|---------|-----------|
| `yoigo.py` | YOIGO |
| `som_energia.py` | SOM ENERGIA |
| `segurma.py` | SEGURMA |
| `trucco.py` | TRUCCO |
| `mrm.py` | MRM |
| `biellebi.py` | BIELLEBI |
| `panruje.py` | PANRUJE |
| `la_purisima.py` | LA PURISIMA |
| `mercadona.py` | MERCADONA |
| `webempresa.py` | WEBEMPRESA |
| `openai.py` | OPENAI |
| `anthropic.py` | ANTHROPIC |
| `la_alacena.py` | LA ALACENA |
| `debora_garcia.py` | DEBORA GARCIA |
| `borboton.py` | BORBOTON |

### Sesiones anteriores (21/12/2025)
| Archivo | Proveedores |
|---------|-------------|
| `zucca.py` | QUESERIA ZUCCA |
| `lidl.py` | LIDL |
| `la_rosquilleria.py` | LA ROSQUILLERIA (OCR) |
| `gaditaun.py` | GADITAUN (OCR) |
| `manipulados_abellan.py` | MANIPULADOS ABELLAN (OCR) |
| `fishgourmet.py` | FISHGOURMET (OCR) |
| `jaime_fernandez.py` | JAIME FERNÁNDEZ (alquiler IRPF) |
| `benjamin_ortega.py` | BENJAMÍN ORTEGA (alquiler IRPF) |
| `ibarrako.py` | IBARRAKO PIPARRAK |
| `angel_loli.py` | ÁNGEL Y LOLI |
| `abbati.py` | ABBATI CAFFE |
| `panifiesto.py` | PANIFIESTO |
| `julio_garcia.py` | JULIO GARCIA (híbrido) |
| `productos_adell.py` | PRODUCTOS ADELL |

---

## 🔧 VARIANTES DE NOMBRES REGISTRADAS (nuevos)

| Extractor | Variantes en @registrar() |
|-----------|--------------------------|
| LAVAPIES | DISTRIBUCIONES LAVAPIES, LAVAPIES, DIST LAVAPIES |
| BODEGAS MUÑOZ | BODEGAS MUÑOZ MARTIN, BODEGAS MUNOZ, MUÑOZ MARTIN |
| LOS GREDALES | LOS GREDALES, GREDALES, LOS GREDALES DE EL TOBOSO |
| INMAREPRO | INMAREPRO, INMA REPRO |

---

## 📝 CHANGELOG PROVEEDORES

| Fecha | Cambio |
|-------|--------|
| **31/12/2025** | **+LAVAPIES (IVA deducido de factura), MUÑOZ OCR, GREDALES líneas** |
| 30/12/2025 | DE LUIS, ALFARERIA, PORVAZ corregidos. +INMAREPRO |
| 29/12/2025 | Bugs: DEBORA, FELISA, HERNÁNDEZ, SILVA. Fix base.py |
| 28/12/2025 | +6: ECOMS, VIRGEN, MARITA, CASA DUQUE, CELONIS, PIFEMA |
| 26/12/2025 | +16: YOIGO, SOM, OPENAI, ANTHROPIC, BIELLEBI... |
| 21/12/2025 PM | +8: JAIME, BENJAMIN, IBARRAKO, ANGEL LOLI, ABBATI, PANIFIESTO, JULIO GARCIA, ADELL |
| 21/12/2025 AM | +12: ZUCCA, PANRUJE, DISBER, LIDL, ROSQUILLERIA, GADITAUN, DE LUIS, ABELLAN, ECOMS, MARITA, SERRIN, FISHGOURMET |

---

*Última actualización: 31/12/2025*
