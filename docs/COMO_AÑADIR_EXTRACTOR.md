# 📖 CÓMO AÑADIR UN EXTRACTOR NUEVO

**Versión:** 4.0
**Última actualización:** 18/12/2025

---

## 🎯 RESUMEN RÁPIDO

```
1. Copia la plantilla: extractores/_plantilla.py → extractores/nuevo_proveedor.py
2. Cambia el nombre y CIF
3. Implementa extraer_lineas()
4. Prueba: python tests/probar_extractor.py NUEVO_PROVEEDOR factura.pdf
5. ¡Listo! El extractor se registra automáticamente
```

---

## 📝 PASO A PASO DETALLADO

### Paso 1: Copiar plantilla

```cmd
cd C:\_ARCHIVOS\TRABAJO\Facturas\ParsearFacturas-main
copy extractores\_plantilla.py extractores\nuevo_proveedor.py
```

### Paso 2: Editar el archivo

Abre `extractores/nuevo_proveedor.py` en VS Code:

```python
"""
Extractor para NUEVO PROVEEDOR
Creado: DD/MM/YYYY
"""
from extractores.base import ExtractorBase, registrar
from typing import List, Dict
import re

@registrar('NUEVO PROVEEDOR')  # ← Cambiar nombre (como aparece en facturas)
class ExtractorNuevoProveedor(ExtractorBase):
    """Extractor para facturas de NUEVO PROVEEDOR."""
    
    nombre = 'NUEVO PROVEEDOR'
    cif = 'B12345678'           # ← Cambiar CIF real
    iban = 'ES00 0000 0000 00'  # ← Cambiar IBAN real (vacío si pago tarjeta)
    metodo_pdf = 'pypdf'        # ← 'pypdf', 'pdfplumber' u 'ocr'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae las líneas de la factura.
        
        Debe devolver lista de diccionarios:
        [
            {'articulo': 'Producto 1', 'base': 10.00, 'iva': 21},
            {'articulo': 'Producto 2', 'base': 5.50, 'iva': 10},
        ]
        """
        lineas = []
        
        # TODO: Implementar lógica de extracción
        # Ejemplo básico:
        patron = r'(\d+)\s+(.+?)\s+(\d+[.,]\d{2})\s*€'
        for match in re.finditer(patron, texto):
            cantidad = int(match.group(1))
            descripcion = match.group(2).strip()
            importe = float(match.group(3).replace(',', '.'))
            
            lineas.append({
                'articulo': descripcion,
                'base': round(importe / 1.21, 2),  # Asumir IVA 21%
                'iva': 21
            })
        
        return lineas
```

### Paso 3: Probar el extractor

```cmd
python tests/probar_extractor.py "NUEVO PROVEEDOR" "ruta/a/factura.pdf"
```

Salida esperada:
```
=== TEST EXTRACTOR: NUEVO PROVEEDOR ===
Archivo: factura.pdf
Método PDF: pypdf

Texto extraído: 1523 caracteres

Líneas encontradas: 3
  1. Producto A - Base: 10.00€ - IVA: 21%
  2. Producto B - Base: 5.50€ - IVA: 10%
  3. Producto C - Base: 3.25€ - IVA: 4%

Total calculado: 22.75€ (sin IVA)
Total con IVA: 26.47€

✅ Extractor funcionando correctamente
```

### Paso 4: ¡Listo!

El extractor se registra automáticamente. La próxima vez que ejecutes:
```cmd
python main.py -i "carpeta_facturas" -d "diccionario.xlsx"
```

Las facturas de NUEVO PROVEEDOR se procesarán automáticamente.

---

## 📋 PLANTILLA COMPLETA

```python
"""
Extractor para [NOMBRE PROVEEDOR]
Creado: [FECHA]
Autor: [TU NOMBRE]

Formato factura:
- [Describir formato: tabla, líneas, etc.]
- [IVA aplicable: 21%, 10%, 4%]
- [Notas especiales]
"""
from extractores.base import ExtractorBase, registrar
from typing import List, Dict, Optional
import re


@registrar('[NOMBRE PROVEEDOR]')
class Extractor[NombreProveedor](ExtractorBase):
    """Extractor para facturas de [NOMBRE PROVEEDOR]."""
    
    # === CONFIGURACIÓN ===
    nombre = '[NOMBRE PROVEEDOR]'
    cif = '[CIF]'
    iban = '[IBAN]'  # Vacío '' si pago con tarjeta
    metodo_pdf = 'pypdf'  # 'pypdf', 'pdfplumber', 'ocr'
    
    # === EXTRACCIÓN DE LÍNEAS ===
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de producto de la factura.
        
        Returns:
            Lista de diccionarios con claves:
            - articulo: str (nombre del producto)
            - base: float (importe SIN IVA)
            - iva: int (porcentaje: 4, 10 o 21)
            - codigo: str (opcional, código producto)
            - cantidad: float (opcional)
            - precio_ud: float (opcional, precio unitario)
        """
        lineas = []
        
        # === TU CÓDIGO AQUÍ ===
        # Ejemplo: buscar patrón en el texto
        patron = r'...'
        for match in re.finditer(patron, texto, re.MULTILINE):
            lineas.append({
                'articulo': '...',
                'base': 0.00,
                'iva': 21
            })
        
        return lineas
    
    # === OPCIONAL: Sobrescribir extracción de total ===
    def extraer_total(self, texto: str) -> Optional[float]:
        """
        Sobrescribe si el formato de total es especial.
        Por defecto usa la función genérica.
        """
        # Ejemplo: buscar "TOTAL: 123,45€"
        match = re.search(r'TOTAL[:\s]+(\d+[.,]\d{2})\s*€', texto)
        if match:
            return float(match.group(1).replace(',', '.'))
        return None  # Usar método por defecto
```

---

## 🔍 EJEMPLOS DE PATRONES COMUNES

### Formato tabla: CÓDIGO | DESCRIPCIÓN | CANTIDAD | PRECIO | IMPORTE

```python
patron = r'^(\d{4,6})\s+(.+?)\s+(\d+)\s+(\d+[.,]\d{2})\s+(\d+[.,]\d{2})$'
for match in re.finditer(patron, texto, re.MULTILINE):
    codigo = match.group(1)
    descripcion = match.group(2).strip()
    cantidad = int(match.group(3))
    precio_ud = float(match.group(4).replace(',', '.'))
    importe = float(match.group(5).replace(',', '.'))
```

### Formato simple: DESCRIPCIÓN ... IMPORTE€

```python
patron = r'^(.+?)\s+(\d+[.,]\d{2})\s*€?\s*$'
```

### Formato con IVA explícito: PRODUCTO | BASE | IVA% | TOTAL

```python
patron = r'(.+?)\s+(\d+[.,]\d{2})\s+(\d+)%\s+(\d+[.,]\d{2})'
for match in re.finditer(patron, texto):
    base = float(match.group(2).replace(',', '.'))
    iva = int(match.group(3))
```

### Formato OCR (tickets escaneados)

```python
# OCR puede introducir errores: | → 1, O → 0, etc.
texto_limpio = texto.replace('|', '1').replace('O', '0')
patron = r'(\d+[.,]\d{2})'  # Patrón más flexible
```

---

## ⚠️ ERRORES COMUNES

### 1. "Extractor no encontrado"
**Causa:** El nombre en `@registrar('...')` no coincide con el proveedor
**Solución:** Usar exactamente el nombre que aparece en las facturas (mayúsculas)

### 2. "No se encontraron líneas"
**Causa:** El patrón regex no coincide con el formato
**Solución:** 
1. Imprimir el texto: `print(texto)`
2. Probar patrón en https://regex101.com
3. Ajustar patrón

### 3. "Total no cuadra"
**Causa:** Base mal calculada (con IVA incluido o sin incluir)
**Solución:** Verificar si el importe en factura es con o sin IVA

### 4. "Error de encoding"
**Causa:** PDF con caracteres especiales (ñ, €, etc.)
**Solución:** Usar `metodo_pdf = 'pdfplumber'` o `'ocr'`

---

## 🧪 TESTING

### Test rápido (1 factura)
```cmd
python tests/probar_extractor.py "PROVEEDOR" "factura.pdf"
```

### Test completo (todas las facturas de un proveedor)
```cmd
python tests/probar_extractor.py "PROVEEDOR" "carpeta_facturas/"
```

### Test con debug (ver texto extraído)
```cmd
python tests/probar_extractor.py "PROVEEDOR" "factura.pdf" --debug
```

---

## 📞 AYUDA

Si tienes problemas:
1. Revisa esta guía
2. Consulta extractores similares en `extractores/`
3. Sube la factura de ejemplo a Claude y pide ayuda

---

*Documento creado: 18/12/2025*
