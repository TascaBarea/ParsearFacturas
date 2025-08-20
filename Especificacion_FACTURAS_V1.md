# Proyecto FACTURAS — Especificación funcional y técnica (Documento vivo V1)

> Objetivo: antes de escribir código, dejar una especificación clara, comprobable y con ejemplos para que sea fácil implementar, probar y mantener.

---

## 1) Visión y alcance
- **Propósito**: extraer información de facturas PDF (y/o imágenes) y producir una **tabla de líneas** normalizada y un **Excel final** con hoja `Metadata`.
- **Alcance V1**: facturas multi-formato, mezcla de IVAs, descuentos y portes, duplicados, abonos y redondeo.
- **Fuera de alcance V1**: e-factura XML, SII, integración contable automática.

## 2) Glosario
- **NumeroArchivo**: dígitos iniciales del PDF (3–4).
- **Proveedor (normalizado)**: MAYÚSCULAS, sin acentos, sin puntos, SL/SA unificados.
- **Línea**: cada artículo/servicio con su tipo de IVA.
- **EsAbono**: factura rectificativa → bases negativas.

## 3) Entradas y supuestos
- **Formato**: PDFs, posible OCR.
- **Fecha**: de emisión (DD-MM-AA). Si falta → vacío + flag `FechaPendiente`.
- **Nº factura**: campo libre. Si falta → vacío + flag `NFacturaPendiente`.
- **Totales**: se validan contra suma de líneas (umbral 0,00 €).

## 4) Tabla final
**Columnas**: NumeroArchivo, Fecha, NºFactura, Proveedor, Descripcion, BaseImponible, TipoIVA, Observaciones.  
**Formato**: números `1234.56`, 2 decimales, sin miles/€, redondeo half-up.  
**TipoIVA**: {0,4,10,21} y también {2,5} si Fecha < 01-01-2025.

## 5) Reglas de cálculo y Portes
- **Bases por línea**: usar base si viene, o Cantidad×PU; prorratear descuentos/portes.
- **IVA permitido**: 0/4/10/21 (+2,+5 si < 2025).
- **Cuadre**: umbral 0,00 €, ajustar en línea mayor base.
- **Abonos**: bases negativas, flag `EsAbono`.

### Tipología de Portes
1. **Línea con IVA normal (21%, 10%, 4%)** → mantener como línea independiente.  
   Ej.: Coop. Montbrió, Emjamesa, PC Componentes.  
2. **Línea con IVA 0%** (inversión sujeto pasivo o exenta) → mantener con TipoIVA=0.  
   Ej.: Makro.  
3. **Pie de factura con importe** → generar línea adicional con base e IVA.  
   Ej.: Silva Cordero, Ecoficus, Ángel y Loli.  
4. **Porte vacío / 0,00** → no añadir; si procede, prorratear proporcionalmente entre bases de producto.  
   Ej.: El Modesto, Quesos Félix, Pifema.  
5. **Sin porte** → no se genera línea.  
   Ej.: Adell, De Luis.  

### 📊 Tabla resumen de casos de PORTES
| Caso                        | Acción                                 | Ejemplos                    |
|-----------------------------|----------------------------------------|-----------------------------|
| Línea con IVA normal        | Mantener como línea independiente      | Coop. Montbrió, Emjamesa    |
| Línea con IVA 0%            | Mantener con TipoIVA=0                 | Makro                       |
| Pie con importe             | Crear línea adicional                  | Silva Cordero, Ecoficus     |
| Porte 0,00                  | No añadir; prorratear                  | El Modesto, Quesos Félix    |
| Sin porte                   | Nada                                   | Adell, De Luis              |

## 6) Duplicados
- **Entre PDFs**: Proveedor+Fecha+NºFactura+ImporteTotal. Conservar más reciente, otros → `DuplicadoDescartado`.
- **Dentro de un PDF**: descartar repeticiones idénticas (“ES COPIA”).

## 7) Normalización de proveedor
- MAYÚSCULAS, sin acentos, sin puntos, unificar sufijos (SL/SA).
- Mantener `ProveedorOriginal` sólo en JSON crudo.

## 8) Salida Excel
- Un único fichero por lote: `LineasFacturas<Periodo>.xlsx`.
- Periodo = trimestre. Si mezcla → año. Si mezcla años → rango.
- Hoja `Metadata`: periodo, nº proveedores, nº facturas/líneas, desglose IVA, incidencias.

## 9) Pipeline
Ingesta → OCR → Parsing → Normalización → Cálculo → Cuadre → Abonos → Duplicados → Tabla → Excel → Registro.

## 10) Ordenación y primera columna
- Primera columna = `XXXX` o `XXX` sin guion.
- Orden: NumeroArchivo ascendente.

## 11) Extracto rápido
Cuando se pida solo resumen: NombreArchivo, Proveedor, Fecha (DDMMAA), NºFactura, Base, TipoIVA, Subtotal.

## 12) Ejemplos
- **Prorrateo portes aceite/chicharrón**.  
- **Abono con bases negativas**.

## 13) Validaciones duras
- Números deben ser numéricos.
- Fechas válidas dayfirst.
- IVA fuera conjunto permitido → `IVA_Pendiente`.

## 14) Trazabilidad
- `facturas_usadas` con motivo/protocolo.
- `CLASIFICACION_DETALLE` con score si fuzzy matching.

## 15) Estándares de código
- Archivos PascalCase.
- Evitar `SettingWithCopyWarning`.
- Mensajes accionables.

## 16) Lista de decisiones
- 2025-08-12: Umbral cuadre = 0,00.
- 2025-08-12: IVA permitido 0/4/10/21 (+2/+5 si < 2025).
- 2025-08-15: ProveedorOriginal/DescripcionOriginal solo en JSON.
- 2025-08-15: IVA faltante = IVA_Pendiente.

## 17) Puntos abiertos
1. Columna inicial: XXXX sin guion (cerrado).  
2. Duplicados internos: pendiente.  
3. Nombre Excel multi-año: mayoría o rango.  
4. Ejemplo portes paso a paso (tests).

## 18) Checklist de aceptación
- Excel con Metadata.  
- Formato numérico correcto.  
- Orden correcto.  
- Dedupe inter-PDF aplicado.  
- Flags incidencias.  
- Abonos con flag.  
- IVA validado.  
- AjusteRedondeo aplicado.

## 19) Roadmap
- V1.0: parsing+normalización+Excel.  
- V1.1: intra-PDF, Excel multi-año, portes test.  
- V1.2: telefono_yoigo.  
- V1.3: fuzzy matching con score.
