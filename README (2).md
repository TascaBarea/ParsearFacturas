# ParsearFacturas

## 📌 Objetivo del proyecto
El proyecto **FACTURAS** tiene como finalidad automatizar la extracción, normalización y validación de datos de facturas PDF (y escaneadas vía OCR) para generar una tabla unificada y un Excel consolidado con metadatos.

## 📑 Documentación principal
La especificación completa del sistema se encuentra en:

- [`Especificacion_FACTURAS_V1.md`](./Especificacion_FACTURAS_V1.md)

Además, en la carpeta `docs/` se podrán mantener copias en Word/PDF para distribución offline.

## 🚀 Flujo de trabajo (resumen)
1. **Ingesta** de facturas (PDF/imagen).
2. **OCR** si es necesario.
3. **Parsing** de cabeceras, líneas y totales.
4. **Normalización** de proveedor, fechas y números.
5. **Cálculo** de bases, prorrateo de portes, validación de IVA.
6. **Cuadre** contra totales y ajuste de redondeos.
7. **Abonos y duplicados** gestionados con flags específicos.
8. **Exportación** a Excel con hoja `Metadata` (salida oficial).

## 📊 Estructura de la tabla de salida
Columnas (en este orden):
- **NumeroArchivo** (3–4 dígitos iniciales del nombre del PDF, sin guiones)
- **Fecha** (DD‑MM‑AA)
- **NºFactura** (tal cual figura en el documento, sin normalizar)
- **Proveedor** (normalizado: MAYÚSCULAS, sin acentos, sin puntos, SL/SA unificado)
- **Descripcion** (texto de la línea; limpieza mínima OCR)
- **BaseImponible** (formato europeo con **coma decimal**: `1234,56`, 2 decimales)
- **TipoIVA** (entero: {0, 2, 4, 5, 7,5, 10, 21} si Fecha < 01‑01‑2025; desde 2025: {0, 4, 10, 21})
- **Observaciones** (flags: `FechaPendiente`, `NFacturaPendiente`, `IVA_Pendiente`, `EsAbono`, `DuplicadoDescartado`, `AjusteRedondeo`, `BaseCalculada`, `OCR_Requerido`)

> Nota: **Se elimina la columna “Categoría”** de la tabla final. Si se requiere clasificación, se mantiene solo en trazabilidad/auditoría (`CLASIFICACION_DETALLE`).

## 🧾 Reglas clave
- **IVA (precedencia)**: Línea > Resumen (solo para validar o rellenar) > Reglas/Patrón proveedor > `IVA_Pendiente`
- **Portes (regla global)**: Eliminar la línea de portes y **prorratear** su importe entre artículos **manteniendo el IVA de cada línea** y **cuadrando** al total con IVA. Las excepciones se definen por patrón.
- **Base desde total con IVA**: permitir cálculo inverso cuando haga falta; marcar `BaseCalculada`.
- **Duplicados**: Proveedor+Fecha+NºFactura+ImporteTotal; warning auxiliar por NºFactura repetido.
- **Abonos**: bases negativas + `EsAbono`.
- **Formato**: salida con **coma decimal** `1234,56`; sin separador de miles.

## 📤 Salidas
- **Oficial**: **Excel** único por lote (`LineasFacturas<Periodo>.xlsx`) con hoja `Metadata`.
- **Diagnóstico (opcional)**: **TSV** plano para depuración rápida (flag CLI), columnas idénticas a la tabla.

## 📂 Estructura del repositorio
```
ParsearFacturas/
├── Especificacion_FACTURAS_V1.md   # Documento vivo en Markdown
├── README.md                       # Introducción al proyecto
├── docs/                           # Documentos Word/PDF complementarios
└── src/                            # Código fuente (cuando iniciemos la implementación)
```

## ✅ Estado actual
- Especificación funcional cerrada (V1).
- Reglas detalladas para: IVAs, portes, duplicados, abonos y validaciones.
- Pendiente de iniciar implementación en Python.

## 📌 Próximos pasos
- V1.0: parsing + normalización + export Excel.
- V1.1: intra-PDF duplicados y Excel multi-año.
- V1.2: módulo `telefono_yoigo`.
- V1.3: fuzzy matching con score en clasificación.

---

✍️ *Documento mantenido en colaboración con ChatGPT para asegurar consistencia y trazabilidad.*
