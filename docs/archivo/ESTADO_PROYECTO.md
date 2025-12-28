# 📊 ESTADO DEL PROYECTO - ParsearFacturas

**Última actualización:** 26/12/2025  
**Versión actual:** v5.1  
**Repositorio:** https://github.com/TascaBarea/ParsearFacturas

---

## 🎯 MÉTRICAS ACTUALES

### Resultados v5.1 (26/12/2025)

| Trimestre | Facturas | Cuadre OK | % | Con Líneas | Importe |
|-----------|----------|-----------|---|------------|---------|
| 4T25 | 185 | 107 | **57.8%** | 154 (83.2%) | 61,454€ |

**Objetivo:** 80% cuadre OK

### Evolución histórica

| Versión | Fecha | Cuadre 1T25 | Cambio principal |
|---------|-------|-------------|------------------|
| v3.5 | 09/12/2025 | 42% | Baseline - 70 extractores |
| v4.0 | 18/12/2025 | 54% | Arquitectura modular @registrar |
| v4.5 | 21/12/2025 | ~70% | +20 extractores |
| v5.0 | 26/12/2025 | - | Normalización + prorrateo portes |
| **v5.1** | **26/12/2025** | **57.8% (4T)** | **+16 extractores nuevos** |

**Mejora total:** 42% → ~60% = **+18 puntos**

---

## ✅ SESIÓN 26/12/2025 - RESUMEN

### Extractores creados (16 nuevos)

| # | Proveedor | CIF | Categoría | IVA | Método |
|---|-----------|-----|-----------|-----|--------|
| 1 | YOIGO | A81020715 | TELEFONO Y COMUNICACIONES | 21% | pdfplumber |
| 2 | SOM ENERGIA | F55091367 | ELECTRICIDAD TASCA/COMESTIBLES | 21% | pdfplumber |
| 3 | SEGURMA | B86414901 | ALARMA | 21% | pdfplumber |
| 4 | TRUCCO | 05247386M | OTROS GASTOS | 21% | pdfplumber |
| 5 | MRM | A80280845 | Diccionario | 10% | pdfplumber |
| 6 | BIELLEBI | IT06089700725 | TARALLI/DULCES | 0% | pdfplumber |
| 7 | PANRUJE | B13858014 | ROSQUILLAS MARINERAS | 4% | pdfplumber |
| 8 | LA PURISIMA | F30005193 | Diccionario | 21% | pdfplumber |
| 9 | MERCADONA | A46103834 | Diccionario | Variable | pdfplumber |
| 10 | WEBEMPRESA | B65739856 | GASTOS VARIOS | 21% | pdfplumber |
| 11 | OPENAI | EU372041333 | GASTOS VARIOS | 0% | pdfplumber |
| 12 | ANTHROPIC | - (USA) | GASTOS VARIOS | 0% | pdfplumber |
| 13 | LAVAPIES | F88424072 | Diccionario | 10%/21% | pdfplumber |
| 14 | LA ALACENA | B45776233 | Diccionario | 10% | pdfplumber |
| 15 | DEBORA GARCIA | 53401030Y | Co2 GAS PARA LA CERVEZA | 21% | pdfplumber |
| 16 | BORBOTON | B09530601 | Diccionario | 21% | pdfplumber |

### Decisiones técnicas tomadas

1. **SOM ENERGIA:** Categoría según contrato (TASCA vs COMESTIBLES)
2. **BIELLEBI:** Regla categoría - si empieza por "TRECCE" → DULCES, sino TARALLI
3. **OPENAI:** Conversión USD→EUR via API frankfurter.app
4. **ANTHROPIC:** Manejo de ajustes negativos como línea neta
5. **Portes PANRUJE:** Se suman al artículo, no línea separada

### Archivos generados

Todos los extractores están en el repositorio:
https://github.com/TascaBarea/ParsearFacturas/tree/main/extractores

---

## ⚠️ ERRORES PENDIENTES (4T25)

### Por tipo de error

| Error | Cantidad | Acción |
|-------|----------|--------|
| FECHA_PENDIENTE | 9 | Mejorar extractor |
| SIN_TOTAL | 14 | Crear/arreglar extractor |
| DESCUADRE | 25 | Revisar extractor |
| CIF_PENDIENTE | 10 | Dar de alta proveedor |
| SIN_LINEAS | 7 | Crear extractor |
| PROVEEDOR_PENDIENTE | 5 | Nombrar archivo correctamente |

### Proveedores prioritarios

| Proveedor | Facturas | Error | Impacto |
|-----------|----------|-------|---------|
| HERNÁNDEZ | 1 | DESCUADRE gigante | Bug crítico |
| COOPERATIVA MONTBRIONE | 1 | DESCUADRE 245€ | Nuevo extractor |
| PIFEMA | 1 | DESCUADRE 266€ | Revisar |
| DE LUIS | 2 | DESCUADRE ~100€ | Revisar |
| SILVA CORDERO | 3 | DESCUADRE | Revisar |

### Extractores a revisar

Mencionados por el usuario:
- **SERRIN NO CHAN** - No funciona bien
- **SILVA CORDERO** - No funciona bien

---

## 📋 PRÓXIMOS PASOS

### Inmediato (próxima sesión)
- [ ] Arreglar SERRIN NO CHAN
- [ ] Arreglar SILVA CORDERO
- [ ] Investigar bug HERNÁNDEZ (descuadre gigante)

### Corto plazo
- [ ] Crear extractores para proveedores con SIN_TOTAL
- [ ] Dar de alta proveedores con CIF_PENDIENTE
- [ ] Llegar a 80% cuadre OK

### Medio plazo
- [ ] Integrar extractor Gmail
- [ ] Completar IBANs (actualmente ~25%)
- [ ] Generador SEPA con validación

---

## 📊 ESTADÍSTICAS GENERALES

| Métrica | Valor |
|---------|-------|
| Extractores totales | ~120 |
| Proveedores en diccionario | 50 |
| Artículos en diccionario | 904 |
| % PENDIENTES categoría | ~40% |

---

## 🔧 CONFIGURACIÓN ACTUAL

| Parámetro | Valor |
|-----------|-------|
| Fuzzy matching | 80% similitud |
| Tolerancia cuadre | 0.10€ |
| Método PDF default | pdfplumber |
| Diccionario | `datos/DiccionarioProveedoresCategoria.xlsx` |

---

## 📝 HISTORIAL DE SESIONES

| Fecha | Versión | Extractores | Destacado |
|-------|---------|-------------|-----------|
| 26/12/2025 | v5.1 | +16 | YOIGO, SOM, OPENAI, ANTHROPIC, BIELLEBI... |
| 21/12/2025 PM | v4.5 | +8 | JAIME FERNANDEZ, PANIFIESTO, JULIO GARCIA |
| 21/12/2025 AM | v4.4 | +12 | ZUCCA, ROSQUILLERIA, FISHGOURMET (OCR) |
| 20/12/2025 | v4.3 | +6 | FABEIRO, KINEMA, SILVA CORDERO |
| 19/12/2025 | v4.2 | +12 | BM refactorizado, bug IVA 0 |
| 18/12/2025 | v4.0 | - | Arquitectura modular |

---

*Actualizado: 26/12/2025 - Sesión extractores v5.1*
