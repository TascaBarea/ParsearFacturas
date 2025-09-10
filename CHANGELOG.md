# Changelog
Todos los cambios relevantes del proyecto se documentan aquí.

## [0.2.0] - 2025-09-11
### Añadido
- CLI (`cli.py`) confirmada como punto de entrada. Soporta flags `--lines`, `--excel`, `--tsv`, `--pretty`, `--outdir`, `--no-reconcile`.
- Funciones nuevas en `patterns_loader.py`: `apply_overlay_lines`, `parse_line_with_overlay`, `mark_is_portes`.

### Cambiado
- `patterns_loader.py` ahora:
  - Resuelve rutas de `patterns/` con fallback.
  - Acepta `start_after`/`stop_before` como lista o string.
  - Incluye normalización de texto (acentos, NBSP, espacios).
  - Regex de fallback: captura último importe europeo en cada línea.
  - Manejo flexible de números (`decimal`, `thousands`).
- Overlay **CERES** afinado:
  - Filtra cabeceras, albaranes y pies de factura.
  - `regex_linea` estable con último importe europeo.
  - Salida limpia con bases de productos.

### Decidido
- No se retocarán los ~50 overlays de golpe.
- Se reforzará el parser genérico y se usarán métricas por documento.
- Se priorizan overlays para proveedores top: **BM, CERES, YOIGO/ISTA, SOM/LUCERA, LIDL, MAKRO**, más casos especiales (**PANIFIESTO**, **AY MADRE LA FRUTA**).
- Se acepta que un 10–15% de facturas se revisen manualmente (~30–45 por trimestre).

### Próximos pasos
- Implementar métricas (`parsed_ratio`, `confidence_mean`, etc.) con salida JSON/CSV.
- Script batch para ranking por proveedor en un trimestre.
- Afinar overlays de BM y YOIGO/ISTA/SOM/LUCERA.
- Activar reconciliación con freno por confianza y tolerancia de diferencia.
