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
8. **Exportación** a Excel con hoja `Metadata`.

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
