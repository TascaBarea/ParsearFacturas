# PROVEEDORES - Estado de Extractores

**Actualizado:** 13/12/2025 | **Versión:** v3.50

---

## 📊 RESUMEN

| Estado | Cantidad |
|--------|----------|
| ✅ Con extractor | 59 |
| ⚠️ CUADRE_PENDIENTE | 7 |
| ❌ PDF_SIN_TEXTO (OCR) | 11 |
| ⬜ Sin extractor | ~20 |

---

## ✅ EXTRACTORES FUNCIONANDO (59)

| # | Proveedor | Función | Notas |
|---|-----------|---------|-------|
| 1 | ABBATI CAFE | `extraer_lineas_abbati` | |
| 2 | ANA CABALLO | `extraer_lineas_ana_caballo` | |
| 3 | ANGEL Y LOLI | `extraer_lineas_angel_y_loli` | |
| 4 | ARGANZA (Vinos) | `extraer_lineas_arganza` | |
| 5 | BARRA DULCE | `extraer_lineas_barra_dulce` | |
| 6 | BERNAL (Jamones) | `extraer_lineas_bernal` | |
| 7 | BERZAL | `extraer_lineas_berzal` | v3.50 - preprocesa espacios |
| 8 | BIELLEBI | `extraer_lineas_biellebi` | IBAN italiano |
| 9 | BM SUPERMERCADOS | `extraer_lineas_bm` | Resumen fiscal |
| 10 | BM PRODUCTOS | `extraer_lineas_bm_productos` | Detalle productos |
| 11 | BORBOTON | `extraer_lineas_borboton` | |
| 12 | CARLOS NAVAS | `extraer_lineas_carlos_navas` | Quesería |
| 13 | CERES | `extraer_lineas_ceres` | v3.48 - doble patrón |
| 14 | CONTROLPLAGA | `extraer_lineas_controlplaga` | |
| 15 | CVNE | `extraer_lineas_cvne` | |
| 16 | DISBER | `extraer_lineas_disber` | |
| 17 | FABEIRO | `extraer_lineas_fabeiro` | |
| 18 | FELISA GOURMET | `extraer_lineas_felisa` | v3.48 - código pegado |
| 19 | FERRIOL | `extraer_lineas_ferriol` | Embutidos |
| 20 | FRANCISCO GUERRA | `extraer_lineas_francisco_guerra` | ~15 líneas |
| 21 | GRUPO CAMPERO | `extraer_lineas_grupo_campero` | |
| 22 | IBARRAKO PIPARRAK | `extraer_lineas_ibarrako_piparrak` | |
| 23 | ISTA | `extraer_lineas_ista` | Domiciliación |
| 24 | JULIO GARCIA VIVAS | `extraer_lineas_julio_garcia_vivas` | |
| 25 | KINEMA | `extraer_lineas_kinema` | Cooperativa |
| 26 | LAVAPIES | `extraer_lineas_lavapies` | v3.49 - bases declaradas |
| 27 | LICORES MADRUEÑO | `extraer_lineas_licores_madrueño` | ~30 líneas, domiciliación |
| 28 | LUCERA | `extraer_lineas_lucera` | Energía |
| 29 | MARITA COSTA | `extraer_lineas_marita_costa` | |
| 30 | MARTIN ABENZA | `extraer_lineas_martin_abenza` | El Modesto |
| 31 | MIGUEZ CAL | `extraer_lineas_miguez_cal` | Forplan |
| 32 | MOLLETES | `extraer_lineas_molletes` | |
| 33 | MRM | `extraer_lineas_mrm` | Industrias Cárnicas |
| 34 | MUÑOZ MARTIN | `extraer_lineas_munoz_martin` | Bodegas |
| 35 | OPENAI | `extraer_lineas_openai` | |
| 36 | PANIFIESTO | `extraer_lineas_panifiesto` | |
| 37 | PANRUJE | `extraer_lineas_panruje` | La Ermita |
| 38 | PILAR RODRIGUEZ | `extraer_lineas_pilar_rodriguez` | El Majadal |
| 39 | PORVAZ | `extraer_lineas_porvaz` | Conservas Tito |
| 40 | PRODUCTOS ADELL | `extraer_lineas_productos_adell` | Croquellanas |
| 41 | PURISIMA | `extraer_lineas_purisima` | Bodegas |
| 42 | QUESOS CATI | `extraer_lineas_quesos_cati` | |
| 43 | QUESOS FELIX | `extraer_lineas_quesos_felix` | Armando Sanz |
| 44 | QUESOS NAVAS | `extraer_lineas_quesos_navas` | |
| 45 | QUESOS ROYCA | `extraer_lineas_quesos_royca` | |
| 46 | SABORES PATERNA | `extraer_lineas_sabores_paterna` | |
| 47 | SEGURMA | `extraer_lineas_segurma` | |
| 48 | SERRIN NO CHAN | `extraer_lineas_serrin` | ~20 líneas |
| 49 | SOM ENERGIA | `extraer_lineas_som_energia` | |
| 50 | TRUCCO | `extraer_lineas_trucco` | Isaac Rodriguez |
| 51 | YOIGO | `extraer_lineas_yoigo` | Xfera |
| 52 | ZUCCA | `extraer_lineas_zucca` | Formaggiarte |
| 53 | GENERICO | `extraer_lineas_generico` | Fallback |

---

## ⚠️ CUADRE_PENDIENTE (7 proveedores)

| Proveedor | Función | Problema | Facturas |
|-----------|---------|----------|----------|
| BENJAMIN ORTEGA | `extraer_lineas_alquiler_ortega` | Retención 19% IRPF | 3 |
| JAIME FERNANDEZ | `extraer_lineas_alquiler_fernandez` | Retención 19% IRPF | 3 |
| ECOFICUS | `extraer_lineas_ecoficus` | Por investigar | 2 |
| ZUBELZU | `extraer_lineas_zubelzu` | Por investigar | 2 |
| MOLIENDA VERDE | `extraer_lineas_molienda_verde` | Por investigar | 1 |
| EMJAMESA | `extraer_lineas_emjamesa` | Por investigar | 1 |
| PC COMPONENTES | - | Sin extractor | 1 |

---

## ❌ PDF_SIN_TEXTO - Requieren OCR (11 proveedores)

| Proveedor | Facturas | Notas |
|-----------|----------|-------|
| JIMELUZ | 5 | |
| LA ROSQUILLERIA | 5 | Tiene IBAN |
| MANIPULADOS ABELLAN | 3 | Tiene IBAN |
| FISH GOURMET | 2 | Tiene IBAN |
| MARIA LINAREJOS | 2 | |
| MEDIA MARKT | 2 | Pago tarjeta |
| IMCASA | 2 | |
| EL CORTE INGLÉS | 1 | Pago efectivo |
| CASA DEL DUQUE | 1 | |
| FERRETERIA HOYOS | 1 | |
| MILAGROS ALPENDEREZ | 1 | |

---

## ⬜ SIN EXTRACTOR (pago no-transferencia)

Estos proveedores no necesitan extractor porque se pagan por otros medios:

| Proveedor | Método pago |
|-----------|-------------|
| MAKRO | Tarjeta |
| LIDL | Tarjeta |
| AMAZON | Tarjeta |
| FNMT | Tarjeta |
| REGISTRO MERCANTIL | Retención |

---

## 🔧 CÓMO AÑADIR UN EXTRACTOR

1. Buscar en el script: `def extraer_lineas_`
2. Copiar un extractor similar
3. Modificar el patrón regex
4. Añadir al dispatcher (buscar `DISPATCHER_EXTRACTORES`)
5. Probar con factura real
6. Verificar cuadre = 0.00

---

*Generado automáticamente desde v3.50*
