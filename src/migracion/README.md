# Migración Histórico 2025

## Propósito

Script de **uso único** para procesar las facturas existentes en Dropbox (1T25, 2T25) y generar el archivo `Facturas_Recibidas_25.xlsx` con la misma estructura que el histórico 2024.

**Este script solo se ejecuta una vez.** Después de la migración inicial, las nuevas facturas se procesan automáticamente con el módulo `gmail`.

## Qué hace

1. **Lee PDFs y JPGs** de las carpetas de Dropbox (1T25, 2T25, etc.)
2. **Extrae datos** de cada factura:
   - `#` (del nombre del archivo)
   - Fecha de factura
   - Referencia/Número de factura
   - CIF del proveedor
   - IBAN (si existe y es transferencia)
   - Total
3. **Genera** `Facturas_Recibidas_25.xlsx` con la estructura del 2024
4. **Genera** un log con:
   - IBANs encontrados (para actualizar MAESTROS)
   - Facturas con datos pendientes

## Instalación

```bash
pip install pypdf pandas openpyxl
# Opcional para OCR de imágenes escaneadas:
pip install pillow pytesseract
```

## Uso

### Procesar un trimestre:
```bash
python -m src.migracion.migracion_historico_2025 \
    --input "D:\Dropbox\Facturas\1T25" \
    --output "Facturas_Recibidas_25.xlsx"
```

### Procesar varios trimestres:
```bash
python -m src.migracion.migracion_historico_2025 \
    --input "D:\Dropbox\Facturas\1T25" "D:\Dropbox\Facturas\2T25" \
    --output "Facturas_Recibidas_25.xlsx"
```

### Con diccionario de categorías:
```bash
python -m src.migracion.migracion_historico_2025 \
    --input "D:\Dropbox\Facturas\1T25" \
    --output "Facturas_Recibidas_25.xlsx" \
    --diccionario "DiccionarioProveedoresCategoria.xlsx"
```

## Formato de nombre de archivo esperado

```
1001_1T25_0101_PROVEEDOR_TF.pdf
│    │    │    │         │
│    │    │    │         └── Método pago: TF/TR/RC/TJ/EF
│    │    │    └── Nombre del proveedor
│    │    └── Fecha: MMDD
│    └── Trimestre: 1T25, 2T25, etc.
└── Número correlativo (asignado por gestoría)
```

## Salidas

| Archivo | Descripción |
|---------|-------------|
| `Facturas_Recibidas_25.xlsx` | Histórico de líneas (misma estructura que 2024) |
| `log_migracion_YYYYMMDD_HHMM.txt` | Resumen: IBANs encontrados, facturas con alertas |

## Estructura del Excel generado

| # | FECHA | REF | PROVEEDOR | ARTICULO | CATEGORIA | TIPO IVA | BASE (€) |
|---|-------|-----|-----------|----------|-----------|----------|----------|
| 1001 | 01-01-25 | A/2025/001 | BERZAL | VER FACTURA | PENDIENTE | | 125.50 |

**Nota:** En esta versión inicial, ARTICULO y CATEGORIA quedan como pendientes. La extracción detallada de líneas se implementará en una fase posterior.

## Alertas

El script genera alertas para:
- `CIF_PENDIENTE`: No se pudo extraer el CIF del PDF
- `IBAN_PENDIENTE`: Factura TF/TR sin IBAN visible
- `FECHA_PENDIENTE`: No se pudo extraer la fecha

## Después de la migración

1. Revisa el log para ver los IBANs encontrados
2. Actualiza MAESTROS con los nuevos IBANs
3. Revisa las facturas con alertas manualmente
4. A partir de ahora, usa el módulo `gmail` para procesar nuevas facturas

## Limitaciones actuales

- No extrae líneas detalladas (solo total por factura)
- Algunos formatos de CIF/fecha pueden no detectarse
- JPGs requieren OCR (pytesseract) instalado
