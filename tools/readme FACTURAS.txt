
---

## 🚀 Flujo de trabajo recomendado
1. **Micro-tareas**: cada sesión atacamos un paso concreto (ej: `scan` detecta fecha/nº).
2. **Lotes pequeños**: trabajar con 2–3 PDFs representativos, no 30 a la vez.
3. **Documentación viva** en GitHub: reglas, decisiones y ejemplos.
4. **Scripts locales** (`scan.bat`, tests) → procesas todo un trimestre en tu PC, yo solo reviso casos que fallan.
5. **Resumen inicial**: usar este documento como contexto para nuevos chats → menos consumo y más foco.

---

## ✅ Próximas micro-tareas sugeridas
1. **CLI — `scan` básico**
   - Detectar proveedor, fecha y nº de factura en 2–3 PDFs de ejemplo.
   - Mostrar resultados en JSON simple.

2. **Detección de tabla de líneas**
   - Implementar `detect_blocks.py` y `parse_lines.py`.
   - Probar en PDFs de CERES (cabeceras “Artículo / Descripción / Importe”).

3. **Aplicar IVA y Portes**
   - Añadir `iva_logic.py` y `portes_logic.py`.
   - Probar casos con IVA 21% y portes en pie.

4. **Cuadre contra totales**
   - Implementar `reconcile.py`.
   - Ajuste en línea de mayor base si descuadre.

5. **Exportar a Excel**
   - `export/excel.py` con hoja principal + `Metadata`.
   - Verificar formato numérico y flags.

6. **Overlays opcionales**
   - Probar con un proveedor difícil (ej. CERES con “CLA: 1 €”).
   - Añadir overlay en `overlays/registry.py`.

7. **Pruebas y validación**
   - Crear carpeta `samples/` con 5 PDFs representativos.
   - `pytest` de humo (1 test unitario + 1 e2e).

8. **Documentación**
   - Completar `docs/README.md` con ejemplos de uso en Windows.
   - Añadir ADR: decisión de motor genérico + overlays.

---

## 🚀 Flujo de trabajo recomendado
1. **Micro-tareas**: cada sesión atacamos un paso concreto (ej: `scan` detecta fecha/nº).
2. **Lotes pequeños**: trabajar con 2–3 PDFs representativos, no 30 a la vez.
3. **Documentación viva** en GitHub: reglas, decisiones y ejemplos.
4. **Scripts locales** (`scan.bat`, tests) → procesas todo un trimestre en tu PC, yo solo reviso casos que fallan.
5. **Resumen inicial**: usar este documento como contexto para nuevos chats → menos consumo y más foco.

---

## ✅ Próximas micro-tareas sugeridas
1. **CLI — `scan` básico**
   - Detectar proveedor, fecha y nº de factura en 2–3 PDFs de ejemplo.
   - Mostrar resultados en JSON simple.

2. **Detección de tabla de líneas**
   - Implementar `detect_blocks.py` y `parse_lines.py`.
   - Probar en PDFs de CERES (cabeceras “Artículo / Descripción / Importe”).

3. **Aplicar IVA y Portes**
   - Añadir `iva_logic.py` y `portes_logic.py`.
   - Probar casos con IVA 21% y portes en pie.

4. **Cuadre contra totales**
   - Implementar `reconcile.py`.
   - Ajuste en línea de mayor base si descuadre.

5. **Exportar a Excel**
   - `export/excel.py` con hoja principal + `Metadata`.
   - Verificar formato numérico y flags.

6. **Overlays opcionales**
   - Probar con un proveedor difícil (ej. CERES con “CLA: 1 €”).
   - Añadir overlay en `overlays/registry.py`.

7. **Pruebas y validación**
   - Crear carpeta `samples/` con 5 PDFs representativos.
   - `pytest` de humo (1 test unitario + 1 e2e).

8. **Documentación**
   - Completar `docs/README.md` con ejemplos de uso en Windows.
   - Añadir ADR: decisión de motor genérico + overlays.
