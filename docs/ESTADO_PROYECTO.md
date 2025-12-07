# ESTADO DEL PROYECTO - PARSEAR FACTURAS
> **Última actualización**: 2025-12-07
> **Versión script migración**: v3.4
> **Versión repo ParsearFacturas**: v0.2.0

---

## 🚨 INSTRUCCIONES OBLIGATORIAS

### Al INICIAR sesión con Claude:
```
1. git pull (asegurar última versión)
2. Subir este archivo (ESTADO_PROYECTO.md) a Claude
3. Decir: "Continúo proyecto facturas, contexto adjunto"
```

### Al FINALIZAR sesión con Claude:
```
1. Pedir a Claude: "Actualiza ESTADO_PROYECTO.md con los cambios de hoy"
2. Descargar el archivo actualizado
3. Ejecutar:
   git add .
   git commit -m "sesión YYYY-MM-DD: [descripción breve]"
   git push
```

### ❌ PROHIBIDO:
- Crear archivos `.bak`, `.bak2`, `.backup`
- Modificar código sin actualizar este documento
- Crear nuevas estructuras YAML sin documentar

---

## 📁 ESTRUCTURA DEL PROYECTO

```
ParsearFacturas/                    ← REPO GITHUB (privado)
├── .github/workflows/              # CI con pytest
├── docs/
│   ├── ESTADO_PROYECTO.md          # ⭐ ESTE ARCHIVO - FUENTE DE VERDAD
│   └── MEJORAS_V2.md
├── patterns/                       # YAMLs de proveedores
│   ├── _PLANTILLA.yml              # ⭐ Plantilla oficial v2
│   └── [PROVEEDOR].yml
├── src/
│   ├── facturas/                   # Código original (cli.py, patterns_loader.py)
│   └── migracion/                  # ⭐ NUEVO - Script migración
│       └── migracion_historico.py
└── tools/
```

---

## 🔄 DOS SISTEMAS (EN PROCESO DE UNIFICACIÓN)

| Sistema | Ubicación | Estado | Uso |
|---------|-----------|--------|-----|
| **Original** | `src/facturas/` | v0.2.0 | cli.py + patterns_loader.py |
| **Migración** | `src/migracion/` | v3.4 | Script monolítico, extractores nativos |

**Plan**: Migrar extractores nativos a YAML → Unificar en sistema original

---

## 📊 EXTRACTORES DISPONIBLES (v3.4)

### Extractores Nativos (Python)
| # | Proveedor | Función | Complejidad |
|---|-----------|---------|-------------|
| 1 | BERZAL | `extraer_lineas_berzal()` | Simple |
| 2 | LICORES MADRUEÑO | `extraer_lineas_madrueño()` | Media |
| 3 | SABORES DE PATERNA | `extraer_lineas_sabores()` | Media |
| 4 | FRANCISCO GUERRA | `extraer_lineas_guerra()` | Simple |
| 5 | EMJAMESA | `extraer_lineas_emjamesa()` | Simple |
| 6 | ZUCCA | `extraer_lineas_zucca()` | Simple |
| 7 | QUESOS NAVAS | `extraer_lineas_navas()` | Simple |
| 8 | CERES | `extraer_lineas_ceres()` | Simple |
| 9 | BM SUPERMERCADOS | `extraer_lineas_bm()` | **Compleja** |
| 10 | CVNE | `extraer_lineas_cvne()` | **Compleja** |
| 11 | JAMONES BERNAL | `extraer_lineas_bernal()` | Media |
| 12 | FELISA GOURMET | `extraer_lineas_felisa()` | Media |
| 13 | BODEGAS BORBOTÓN | `extraer_lineas_borboton()` | Media |
| 14 | VINOS DE ARGANZA | `extraer_lineas_arganza()` | Media |
| 15 | LA PURÍSIMA | `extraer_lineas_purisima()` | Media |
| 16 | MOLLETES ARTESANOS | `extraer_lineas_molletes()` | Simple |

### Candidatos a mantener como Python (muy complejos):
- BM SUPERMERCADOS (tickets, múltiples formatos)
- CVNE (formato multilínea)

### Candidatos a migrar a YAML (simples/medios):
- Todos los demás (14 proveedores)

---

## 📝 ESTRUCTURA YAML v2 (OFICIAL)

```yaml
# _PLANTILLA.yml - Copiar para nuevos proveedores
extractor:
  version: "2.0"
  proveedor: "NOMBRE_PROVEEDOR"
  
  # Datos fiscales
  cif: "B12345678"
  iban: "ES00 0000 0000 0000 0000 0000"
  
  # Identificación automática
  match_if_contains:
    - "texto que aparece en factura"
    - "otro texto identificador"
  
  # Extracción de campos de cabecera
  campos:
    fecha:
      patron: '\b(\d{2}[/-]\d{2}[/-]\d{2,4})\b'
      formato_salida: "DD-MM-YY"
    
    numero_factura:
      patron: 'Factura[:\s]*([A-Z0-9/-]+)'
    
    total:
      patron: 'TOTAL[:\s]*([\d.,]+)'
  
  # Extracción de líneas
  lineas:
    inicio_despues: "DESCRIPCION"
    fin_antes: "TOTAL"
    patron: '^(\w+)\s+(.+?)\s+([\d,]+)\s+([\d,]+)$'
    # Grupos: 1=codigo, 2=articulo, 3=cantidad, 4=importe
    grupos:
      codigo: 1
      articulo: 2
      cantidad: 3
      importe: 4
    
    iva_default: 21
    
    # Excepciones de IVA
    iva_excepciones:
      - patron: "TRANSPORTE|PORTES"
        iva: 21
      - patron: "PAN|MOLLETE"
        iva: 4
  
  # Tratamiento de portes
  portes:
    modo: "prorratear"  # o "linea_separada" o "ignorar"
    patron: 'PORTES?\s+([\d,]+)'
  
  # Validaciones
  validaciones:
    cuadre_total:
      activo: true
      tolerancia: 0.02
```

---

## 🔧 ARCHIVOS CLAVE

| Archivo | Ubicación | Descripción |
|---------|-----------|-------------|
| `migracion_historico.py` | `src/migracion/` | Script principal v3.4 |
| `ESTADO_PROYECTO.md` | `docs/` | Este archivo |
| `_PLANTILLA.yml` | `patterns/` | Plantilla YAML oficial |
| `DiccionarioProveedoresCategoria.xlsx` | raíz o `data/` | Maestro artículos |

---

## 📅 HISTORIAL DE DECISIONES

### 2025-12-07
- **Decisión**: Opción C - Continuar migracion_v3.x y luego integrar
- **Motivo**: El script funciona, no romper lo que funciona
- **Acción**: Crear ESTADO_PROYECTO.md como fuente de verdad

### 2025-12-07
- **Añadido**: Extractores ARGANZA, PURÍSIMA, MOLLETES (v3.4)
- **Añadido**: Extractores BORBOTÓN, FELISA, BERNAL (v3.3)
- **Mejorado**: Parser nombres archivo (soporta 4T25_1127_...)

### 2025-09-11 (CHANGELOG original)
- **Versión**: v0.2.0 repo original
- **Añadido**: CLI, patterns_loader.py mejorado
- **Decidido**: No retocar 50 overlays de golpe

---

## 📋 PRÓXIMOS PASOS (PENDIENTES)

1. [ ] Subir `migracion_historico_v3.4.py` al repo en `src/migracion/`
2. [ ] Crear `patterns/_PLANTILLA.yml` en el repo
3. [ ] Migrar 3-5 extractores simples a YAML como prueba
4. [ ] Probar con carpeta completa 1T25 (252 facturas)
5. [ ] Documentar proveedores que faltan

---

## 🏢 PROVEEDORES PENDIENTES DE EXTRACTOR

*(Añadir aquí proveedores que den SIN_LINEAS)*

| Proveedor | Facturas aprox. | Prioridad |
|-----------|-----------------|-----------|
| ... | ... | ... |

---

## 📞 CIFs RECOPILADOS

```
MARTIN ARBENZA          | NIF: 74305431K
FRANCISCO GUERRA        | NIF: 50449614B
TRUCCO (Isaac Rodriguez)| NIF: 05247386M
MAKRO                   | CIF: A28647451   (pago tarjeta)
BENJAMIN ORTEGA         | NIF: 09342596L   | IBAN: ES3100495977552116066585
JAIME FERNANDEZ         | NIF: 07219971H   | IBAN: ES3100495977552116066585
ISTA METERING           | CIF: A50090133
AMAZON ESPAÑA           | CIF: W0184081H
VINOS DE ARGANZA        | CIF: B24416869   | IBAN: ES92 0081 5385 6500 0121 7327
LA PURISIMA             | CIF: F30005193   | IBAN: ES78 0081 0259 1000 0184 4495
MOLLETES ARTESANOS      | CIF: B93662708
BODEGAS BORBOTON        | CIF: B45851755   | IBAN: ES37 2100 1913 1902 0013 5677
FELISA GOURMET          | CIF: B72113897   | IBAN: ES68 0182 1076 9502 0169 3908
```

---

## ⚠️ ERRORES CONOCIDOS / LIMITACIONES

1. **BM tickets con espacios al inicio**: Algunas líneas no se capturan
2. **FELISA formato 1127**: Un PDF con formato irregular
3. **Nombres archivo sin trimestre**: Parser puede fallar

---

*Documento generado por Claude. Actualizar al final de cada sesión.*
