# ParsearFacturas

![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![tests](https://github.com/TascaBarea/ParsearFacturas/actions/workflows/tests.yml/badge.svg)

---

## 🚀 Objetivo del proyecto
Automatizar la extracción y clasificación de datos de facturas en PDF de múltiples proveedores, para alimentar una base de datos de gastos.

---

## 📦 Ejemplo de uso

Procesar una factura PDF y exportar a Excel:

```bash
python src/facturas/cli.py ./samples/3001_FABEIRO.pdf
```

El resultado se guarda en un archivo Excel con nombre derivado del PDF de entrada, por ejemplo:

- `3001_FABEIRO.xlsx`
- `3002_CERES.xlsx`
- `3003_SEGURMA.xlsx`

Cada archivo contiene:
- Hoja **Líneas** → artículos normalizados con IVA, categoría y base.  
- Hoja **Metadata** → proveedor, fecha, totales.  

---

## ✅ Estado actual
- Lógica de IVA, portes y cuadre de totales implementada.  
- Exportador a Excel funcional.  
- Tests básicos con `pytest`.  
- CI configurado en GitHub Actions.  

---

## 📌 Próximos pasos
- Implementar overlays por proveedor especial (ej. CERES con “CLA: 1 €”).  
- Ampliar cobertura de tests con casos reales.  
- Desarrollar CLI simplificado (`scan.py`).  
- Añadir badge de coverage (cuando haya más tests).  

---

## 🚀 Cómo ejecutar

Tienes **dos formas de lanzar el parser de facturas**:

### 1. Forma estándar (canónica en Python)
Recomendada para entornos profesionales y cuando se use el proyecto en otros equipos:
```bash
python -m src.facturas.cli "C:\ruta\a\factura.pdf" --lines --outdir out --pretty
```

### 2. Forma simplificada (wrapper `main.py`)
Más cómoda en Windows, útil para el día a día:
```bash
python main.py "C:\ruta\a\factura.pdf" --lines --outdir out --pretty
```

👉 Ambas opciones generan un Excel en la carpeta `out\\` con las columnas:  
`NumeroArchivo | Fecha | NºFactura | Proveedor | Descripcion | Categoria | TipoIVA | BaseImponible | Observaciones`.

---
## 🗂 Flujo de trabajo interno

El plan de desarrollo por micro-tareas se documenta en [readme FACTURAS.txt](./readme%20FACTURAS.txt).  
Allí se detallan pasos como:
- Detección de proveedor, fecha y nº de factura
- Parseo de líneas
- Aplicación de IVA y portes
- Cuadre contra totales
- Exportación a Excel
- Overlays específicos (ej. CERES)
- Pruebas y validación


## 📑 Documentación completa
La especificación detallada del sistema está en:  
- [`Especificacion_FACTURAS_V1.md`](./Especificacion_FACTURAS_V1.md)

---

## 📜 Licencia
Este proyecto está bajo licencia **MIT**.  
Eres libre de usarlo, modificarlo y distribuirlo citando la autoría.
