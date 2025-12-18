# ESTADO DEL PROYECTO - Migración Histórico 2025

**Última actualización:** 2025-12-13 (sesión nocturna)
**Versión actual:** 3.52

---

## 📊 MÉTRICAS ACTUALES

### 1T25
| Métrica | Valor |
|---------|-------|
| Facturas procesadas | 185/252 (73.4%) |
| Total líneas extraídas | 701 |
| IBANs detectados | 113 |

### 2T25
| Métrica | Valor |
|---------|-------|
| Facturas procesadas | 180/307 (58.6%) |
| Total líneas extraídas | 717 |
| IBANs detectados | 100 |

---

## ✅ SESIÓN 2025-12-13 (nocturna): v3.52

### Cambios realizados

#### 1. Nuevos extractores
- **PC COMPONENTES**: Formato `Código Artículo Precio Uds Total` con IVA 21%
- **CARRASCAL (Jose Luis Sánchez)**: Fallback condicional para formato especial

#### 2. Mejoras en `extraer_total()`
- **Patrón CARRASCAL**: Total aparece ANTES de "TOTAL FACTURA" (no después)
  - Fallback condicional: solo aplica si detecta "Jose Luis", "CARRASCAL" o CIF "07951036M"
- **Exclusión de porcentajes**: Patrón `(?!\s*%)` para no capturar IVA como total
  - Ejemplo: evita capturar "10,00%" cuando aparece justo después de "TOTAL FACTURA"
- **Formato americano**: Soporte para punto decimal (90.83 en lugar de 90,83)
- **Patrón "Euros"**: Añadido `(\d+[.,]\d{2})\s*Euros` para MOLIENDA VERDE

#### 3. Compatibilidad pypdf vs pdfplumber
- **Decisión**: Mantener **pypdf** como extractor principal (73.4% vs 62.3% con pdfplumber)
- **Motivo**: Los extractores fueron desarrollados con pypdf; pdfplumber genera texto diferente
- **Futuro**: Implementar sistema dual (pypdf primero, pdfplumber como fallback)

#### 4. Protección buscar_categoria()
- Fix error `'float' object has no attribute 'upper'`
- Conversión automática a string para valores no-string del diccionario

### Facturas arregladas
| Proveedor | Facturas | Problema | Solución |
|-----------|----------|----------|----------|
| PC COMPONENTES | 1243 | Sin extractor | Nuevo extractor específico |
| CARRASCAL | 1160, 1245 | Total antes de etiqueta | Fallback condicional |
| MOLIENDA VERDE | 1066 | Formato "243,00 Euros" | Nuevo patrón regex |

---

## ⚠️ CUADRE_PENDIENTE (proveedores problemáticos)

### 1T25 (11 facturas)
| Proveedor | Cantidad | Notas |
|-----------|----------|-------|
| DISTRIBUCIONES LAVAPIES | 3 | Formato complejo |
| BODEGAS BORBOTON | 4 | Formato complejo |
| IBARRAKO PIPARRAK | 2 | Pendiente investigar |
| LA MOLIENDA VERDE 4T24 | 1 | Formato antiguo diferente |

### 2T25 (13+ facturas)
| Proveedor | Cantidad | Notas |
|-----------|----------|-------|
| DISTRIBUCIONES LAVAPIES | 6 | Mismo problema que 1T |
| BODEGAS BORBOTON | 3 | Mismo problema que 1T |
| CERES | 3 | Algunos con cuadre pendiente |
| SERRIN NO CHAN | 2 | Formato variable |
| FELISA GOURMET | 1 | Cuadre pendiente |

---

## 📋 PRÓXIMOS PASOS

1. **Arreglar extractores pendientes**: DISTRIBUCIONES LAVAPIES, BODEGAS BORBOTON, IBARRAKO
2. **Implementar sistema dual pypdf/pdfplumber**: 
   - Intentar con pypdf primero
   - Si falla o SIN_LINEAS, reintentar con pdfplumber
3. **Procesar 3T25 y 4T25**: Validar extractores con más datos
4. **Reducir PDF_SIN_TEXTO**: Muchos PDFs son escaneados (necesitan OCR)

---

## 🔧 CAMBIOS TÉCNICOS v3.52

### Nuevo extractor PC COMPONENTES
```python
def extraer_lineas_pc_componentes(texto: str) -> List[Dict]:
    # Formato: Código Artículo Precio Uds Total
    # Total = BASE (sin IVA), IVA siempre 21%
    patron_linea = re.compile(r'^(\d+)\s+(.+?)\s+([-\d.]+)\s+(\d+)\s+([-\d.]+)$', re.MULTILINE)
```

### Fallback CARRASCAL en extraer_total()
```python
# Solo aplica si es factura CARRASCAL
if 'Jose Luis' in texto or 'CARRASCAL' in texto.upper() or '07951036M' in texto:
    patron_carrascal = re.compile(r'(\d+[.,]\d{3})\s*€\s*\n.*?TOTAL\s*FACTURA', re.DOTALL)
```

### Patrón anti-porcentaje
```python
# NO captura si el número va seguido de % (sería porcentaje IVA, no total)
r'(?:TOTAL\s*FACTURA|...)[:\s]*(\d+[.,]\d{2})(?!\s*%)\s*€?'
```

---

## 📁 ARCHIVOS DEL PROYECTO

```
ParsearFacturas-main/
├── src/migracion/
│   ├── migracion_historico_2025_v3_52.py  # ← VERSIÓN ACTUAL
│   └── outputs/
│       ├── Facturas_1T25.xlsx
│       ├── Facturas_2T25.xlsx
│       └── log_migracion_*.txt
├── docs/
│   ├── ESTADO_PROYECTO.md      # ← ESTE ARCHIVO
│   ├── INFORME_EJECUTIVO_PROYECTO.md
│   ├── PROVEEDORES.md
│   └── Portes.md
└── DiccionarioProveedoresCategoria.xlsx
```

---

## 📝 CHANGELOG RESUMIDO

| Versión | Fecha | Cambios principales |
|---------|-------|---------------------|
| **v3.52** | **2025-12-13** | **PC COMPONENTES, CARRASCAL, fix extraer_total()** |
| v3.51 | 2025-12-13 | Retención IRPF, BERZAL fix, ECOFICUS portes |
| v3.49 | 2025-12-12 | BERZAL y LAVAPIES fix cuadre |
| v3.41 | - | DISBER y ADELL extractores |
| v3.40 | - | FELISA GOURMET corregido |
| v3.39 | - | CERES: SOUSAS y PLASTICO |

---

## 🔑 DECISIONES TÉCNICAS

1. **PDF extractor**: pypdf (no pdfplumber) - mejor compatibilidad con extractores actuales
2. **Portes/Transporte**: NUNCA como línea aparte, siempre repartidos proporcionalmente
3. **Retención IRPF**: Campo separado en línea, se resta en validación de cuadre
4. **Tolerancia cuadre**: 0.05€ (5 céntimos)
5. **Formato decimal**: Soportar tanto europeo (coma) como americano (punto)

---

## 🚨 PROBLEMAS CONOCIDOS

1. **PDF_SIN_TEXTO**: ~20% de facturas son escaneados sin OCR
2. **DISTRIBUCIONES LAVAPIES**: Extractor no cuadra (formato complejo)
3. **BODEGAS BORBOTON**: Extractor no cuadra (formato complejo)
4. **pdfplumber**: Incompatible con extractores actuales (genera texto diferente)
