# ESTADO ACTUAL - ParsearFacturas

**Versión:** v3.50 | **Fecha:** 13/12/2025

---

## 📊 RESUMEN

| Métrica | Valor |
|---------|-------|
| Facturas procesadas | 188/252 (74.6%) |
| Extractores funcionando | 60 |
| CUADRE_PENDIENTE | 13 |
| PDF_SIN_TEXTO (OCR) | 24 |
| IBANs completos | 46/97 proveedores |

---

## ✅ ÚLTIMA SESIÓN (12/12/2025)

**Arreglados:**
- CERES (19/19 facturas) - doble patrón con/sin descuento
- FELISA GOURMET (4/4) - código pegado al importe
- LAVAPIES (3/3) - bases declaradas multi-IVA
- BERZAL (2/2) - preprocesamiento espacios pypdf

**Descubrimiento:** pypdf puede meter espacios dentro de números (`1 0` en vez de `10`). Solución: preprocesar texto.

---

## ⚠️ PENDIENTE ARREGLAR

| Proveedor | Facturas | Problema |
|-----------|----------|----------|
| BENJAMIN ORTEGA | 3 | Retención 19% IRPF |
| JAIME FERNANDEZ | 3 | Retención 19% IRPF |
| ECOFICUS | 2 | Por investigar |
| ZUBELZU | 2 | Por investigar |
| LA MOLIENDA VERDE | 1 | Por investigar |
| EMJAMESA | 1 | Por investigar |
| PC COMPONENTES | 1 | Por investigar |

---

## 🎯 PRÓXIMO PASO

**Opción elegida:** A (Consolidar)

1. ~~Completar MAESTRO_PROVEEDORES.xlsx~~ ✅
2. **Documentación** ← ESTAMOS AQUÍ
3. Arreglar alquileres (BENJAMIN/JAIME) - retención IRPF
4. Investigar ECOFICUS, ZUBELZU

---

## 📁 ARCHIVOS CLAVE

```
src/migracion/
  migracion_historico_2025_v3_50.py  ← SCRIPT ACTUAL
  versiones_antiguas/                 ← Mover aquí v3.1-v3.49

docs/
  LEEME_PRIMERO.md    ← Checklist sesiones
  ESTADO_ACTUAL.md    ← Este archivo
  PROVEEDORES.md      ← Lista de extractores
```

---

## 📝 NOTAS TÉCNICAS RÁPIDAS

**Para diagnosticar un proveedor:**
```python
from pypdf import PdfReader
texto = PdfReader('factura.pdf').pages[0].extract_text()
print(texto)
```

**Lección clave:** pypdf vs pdfplumber extraen diferente. Probar ambos.

---

*Este documento se actualiza cada sesión. Ver histórico en git.*
