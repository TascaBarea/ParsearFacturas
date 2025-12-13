# ESTADO DEL PROYECTO - ParsearFacturas
## Migración Histórico 2025

**Última actualización:** 12/12/2025  
**Versión actual:** v3.50  
**Archivo:** `migracion_historico_2025_v3_50.py`

---

## 📊 RESUMEN EJECUTIVO

| Métrica | Valor | Porcentaje |
|---------|-------|------------|
| Total facturas 1T25 | 252 | 100% |
| Con líneas extraídas | 188 | 74.6% |
| Total líneas | 706 | - |
| IBANs disponibles | 111 | - |
| CUADRE_PENDIENTE | ~13 | ~5.2% |
| PDF_SIN_TEXTO | 24 | 9.5% |
| SIN_LINEAS | ~25 | ~9.9% |

---

## 🔧 CAMBIOS v3.48 → v3.50 (12/12/2025)

### Sesión de hoy - Extractores corregidos:

#### 1. CERES ✅ (v3.48)
- **Problema:** Facturas 19/19 mostraban CUADRE_PENDIENTE
- **Solución:** Extractor reescrito con doble patrón para productos con/sin descuento
- **Resultado:** 19/19 facturas OK

#### 2. FELISA GOURMET ✅ (v3.48)
- **Problema:** 4/4 facturas con CUADRE_PENDIENTE
- **Solución:** Patrón mejorado para código pegado al importe
- **Resultado:** 4/4 facturas OK

#### 3. DISTRIBUCIONES LAVAPIES ✅ (v3.49)
- **Problema:** Multi-IVA (21% y 10%) no se podía distribuir correctamente entre productos
- **Solución:** Extraer bases declaradas del PDF directamente:
  ```
  BASE IMP. AL 21% 62,40 IVA 21% 13,10
  BASE IMP. AL 10% 65,70 IVA 10% 6,57
  ```
- **Resultado:** 3/3 facturas OK

#### 4. BERZAL ✅ (v3.50)
- **Problema:** pypdf extrae con espacios internos en números (`1 0` en vez de `10`, `1 8,90` en vez de `18,90`)
- **Solución:** 
  1. Preprocesamiento de texto: eliminar UN espacio entre dígitos
  2. Extracción de total: buscar antes de fecha DD/MM/YY
  3. Patrón dual pypdf/pdfplumber
- **Código clave:**
  ```python
  # Preprocesar: "1 0" → "10", "1 8,90" → "18,90"
  texto_limpio = re.sub(r'(\d) (\d)', r'\1\2', texto)
  texto_limpio = re.sub(r'(\d) ([,\.])', r'\1\2', texto_limpio)
  texto_limpio = re.sub(r'([,\.]) (\d)', r'\1\2', texto_limpio)
  ```
- **Resultado:** 2/2 facturas OK (1001, 1158)

### Descubrimiento técnico importante:

**pypdf vs pdfplumber - Diferencias de extracción:**

| PDF | pdfplumber | pypdf |
|-----|------------|-------|
| BERZAL | `... U 10 5,48` | `... 10 5,48 ...` (orden diferente) |
| BERZAL | `250 grs 10` | `250 grs 1 0` (espacios internos) |

**Conclusión:** pypdf puede introducir espacios dentro de números. Solución: preprocesar texto eliminando espacios simples entre dígitos.

---

## ⚠️ CUADRE_PENDIENTE (13 facturas, 7 proveedores)

| Proveedor | Facturas | Causa | Estado |
|-----------|----------|-------|--------|
| BENJAMIN ORTEGA | 1189, 1199, 1213 | Retención 19% IRPF | Pendiente |
| JAIME FERNANDEZ | 1190, 1201, 1215 | Retención 19% IRPF | Pendiente |
| ECOFICUS | 1083, 1143 | Por investigar | Pendiente |
| ZUBELZU | 1141, 1188 | Por investigar | Pendiente |
| LA MOLIENDA VERDE | 1066 | Por investigar | Pendiente |
| EMJAMESA | 1173 | Por investigar | Pendiente |
| PC COMPONENTES | 1243 | Por investigar | Pendiente |

### Nota sobre alquileres (BENJAMIN ORTEGA, JAIME FERNANDEZ):
Estos proveedores emiten facturas de alquiler con **retención del 19% IRPF**:
- Fórmula: `Total a pagar = Base + IVA 21% - Retención 19%`
- Requieren extractor especial que maneje la retención

---

## ✅ PROVEEDORES FUNCIONANDO (v3.50)

| Proveedor | Facturas | Notas |
|-----------|----------|-------|
| CERES | 19 | Doble patrón con/sin descuento |
| FELISA GOURMET | 4 | Código pegado al importe |
| DISTRIBUCIONES LAVAPIES | 3 | Bases declaradas multi-IVA |
| BERZAL | 2 | Preprocesamiento espacios pypdf |
| LICORES MADRUEÑO | 3 | ~30 líneas por factura |
| BM SUPERMERCADOS | 28 | Resumen fiscal |
| SABORES DE PATERNA | 6 | Patrón específico |
| FRANCISCO GUERRA | 3 | ~15 líneas por factura |
| SERRIN NO CHAN | 2 | ~20 líneas por factura |
| Y muchos más... | | |

---

## 📋 PDF_SIN_TEXTO (24 facturas)

Facturas escaneadas o imágenes que requieren OCR:
- JIMELUZ (5)
- LA ROSQUILLERIA (5)
- MANIPULADOS ABELLAN (3)
- FISH GOURMET (2)
- MARIA LINAREJOS GADITAUN (2)
- MEDIA MARKT (2)
- EL CORTE INGLÉS (1)
- CASA DEL DUQUE (1)
- IMCASA (2)
- FERRETERIA HOYOS (1)

---

## 📋 SIN_LINEAS (~25 facturas)

Facturas con texto pero sin extractor implementado o con formato no reconocido.

---

## 🎯 PRÓXIMOS PASOS

### Prioridad Alta:
1. **Alquileres:** Implementar extractor para facturas con retención 19% IRPF (BENJAMIN ORTEGA, JAIME FERNANDEZ)
2. **ECOFICUS, ZUBELZU:** Analizar y corregir extractores

### Prioridad Media:
3. **LA MOLIENDA VERDE:** Investigar descuadre
4. **EMJAMESA, PC COMPONENTES:** Investigar descuadre

### Prioridad Baja:
5. **PDF_SIN_TEXTO:** Implementar OCR para facturas escaneadas
6. **SIN_LINEAS:** Crear extractores para proveedores faltantes

---

## 📁 ARCHIVOS DE TRABAJO

| Archivo | Descripción |
|---------|-------------|
| `migracion_historico_2025_v3_50.py` | Script principal de migración |
| `Facturas_1T25.xlsx` | Último resultado de procesamiento |
| `log_migracion_20251212_*.txt` | Logs de ejecución |

---

## 📝 LECCIONES APRENDIDAS

### Sesión 12/12/2025 (v3.48-v3.50):

1. **pypdf espacios internos:** pypdf puede introducir espacios dentro de números (`1 0` en vez de `10`). Solución: preprocesar con `re.sub(r'(\d) (\d)', r'\1\2', texto)`

2. **Multi-IVA sin distribución:** Cuando una factura tiene productos con diferentes IVAs pero no indica cuál es cuál, usar las bases declaradas en el resumen fiscal

3. **Orden de patrones pypdf/pdfplumber:** Probar primero el patrón más específico (pdfplumber) y luego el genérico (pypdf)

4. **Total antes de fecha:** En BERZAL, el total aparece justo antes de la fecha (`80,84\n01/01/25`)

### Sesiones anteriores:

5. **pypdf vs PyPDF2:** pypdf elimina espacios que PyPDF2 preserva - los patrones deben manejar ambos

6. **Word boundaries:** Usar `\b` para evitar matches parciales (ej: "Total" vs "Subtotal")

7. **CIF con variantes:** Algunos proveedores usan guiones en el CIF (B-12711636 vs B12711636)

8. **Orden de patrones:** Los patrones más específicos deben ir PRIMERO en la lista

9. **Porte sin IVA:** Algunos proveedores (MARTIN ABENZA) no aplican IVA al porte

---

## 📈 HISTORIAL DE VERSIONES

| Versión | Fecha | Cambios principales |
|---------|-------|---------------------|
| v3.50 | 12/12/2025 | Fix BERZAL (preprocesamiento espacios pypdf) |
| v3.49 | 12/12/2025 | Fix LAVAPIES (bases declaradas multi-IVA), inicio BERZAL |
| v3.48 | 12/12/2025 | Fix CERES (19/19), FELISA (4/4) |
| v3.41 | 12/12/2025 | Fix ADELL, DISBER, FELISA, CERES, MARTIN ABENZA |
| v3.40 | 12/12/2025 | Fix FELISA GOURMET código pegado |
| v3.39 | 12/12/2025 | Fix CERES productos sin descuento |

---

## 🔍 DIAGNÓSTICO RÁPIDO

Para diagnosticar un proveedor con CUADRE_PENDIENTE:

```python
# 1. Extraer texto con pypdf
from pypdf import PdfReader
reader = PdfReader('factura.pdf')
texto = reader.pages[0].extract_text()
print(texto)

# 2. Buscar total
import re
for m in re.finditer(r'TOTAL.{0,50}', texto):
    print(m.group())

# 3. Probar patrón de líneas
patron = re.compile(r'tu_patron_aqui', re.MULTILINE)
for m in patron.finditer(texto):
    print(m.groups())
```

---

*Documento actualizado - ParsearFacturas v3.50*
