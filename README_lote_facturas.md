# Procesamiento Lote de Facturas - Script Batch

Este documento describe el funcionamiento y uso del script `procesar_lote.bat`, destinado al procesamiento automatizado de facturas en formato PDF de un proveedor específico.

---

## Objetivo

Ejecutar de forma automatizada el análisis de facturas PDF utilizando los overlays configurados, el diccionario oficial de categorías y el cálculo de cuadre por IVA. Genera como salida los archivos TSV y CSV correspondientes, junto con un log del proceso.

---

## Requisitos previos

- Entorno Python configurado (preferiblemente en entorno virtual).
- Estructura de proyecto conforme a:

```
ParsearFacturas-main/
├── samples/
│   └── <PROVEEDOR>/
│       └── *.pdf
├── out/
├── src/
│   └── facturas/
│       └── cli.py
└── procesar_lote.bat
```

- PDFs ubicados en `samples/<PROVEEDOR>/`
- Overlay funcional para el proveedor (`MERCADONA.yml`, etc.)
- Archivo `Diccionario_Proveedores_y_Categorias.xlsx` cargado correctamente por el sistema.

---

## Uso del script

1. Abrir la consola de comandos (CMD) y ubicarse en la raíz del proyecto:
   ```
   cd C:\_ARCHIVOS\TRABAJO\Facturas\ParsearFacturas-main
   ```

2. Ejecutar el script:
   ```
   procesar_lote.bat
   ```

3. Introducir el nombre del proveedor al ser solicitado (ej: `MERCADONA`).

4. Confirmar si se desea continuar con el procesamiento de los archivos encontrados.

5. En caso de existir archivos TSV previos, confirmar si se desea sobrescribirlos.

---

## Salidas generadas

Por cada ejecución se generan los siguientes archivos en:

```
out/<PROVEEDOR>/
├── <PROVEEDOR>_consolidado_dicc-<hash>.tsv
├── <PROVEEDOR>_resumen_dicc-<hash>.csv
└── log_<PROVEEDOR>_<fecha>.txt
```

- **TSV**: Contiene las líneas de productos parseadas por factura.
- **CSV resumen**: Consolidado por categoría y tipo de IVA.
- **Log**: Registro completo de la ejecución (útil para depuración y auditoría).

---

## Consideraciones

- El script valida que existan PDFs antes de procesar.
- Toda interacción se realiza por consola.
- Utiliza nombres de carpeta sensibles a mayúsculas/minúsculas.
- La carpeta `out/<PROVEEDOR>/` se crea si no existe.
- Se evita sobrescritura accidental mediante confirmación interactiva.

---

## Mantenimiento

- Este script puede ser ampliado para aceptar argumentos por línea de comandos.
- Se recomienda guardar este archivo `.bat` con codificación UTF-8 con BOM para evitar errores de caracteres en CMD.
- Cualquier cambio en la estructura de carpetas debe reflejarse en el script.

---

## Autoría

Desarrollado como parte del sistema de procesamiento semiautomático de gastos para proveedores frecuentes. Versión inicial: septiembre 2025.

---

## Contacto

Para sugerencias o mantenimiento, contactar al responsable del módulo `facturas.cli` o al coordinador del proyecto de automatización contable.