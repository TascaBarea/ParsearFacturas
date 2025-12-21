# 📖 CÓMO AÑADIR UN EXTRACTOR NUEVO

**Versión:** 4.3
**Última actualización:** 20/12/2025

---

## 🎯 RESUMEN RÁPIDO

```
1. Copia la plantilla: extractores/_plantilla.py → extractores/nuevo_proveedor.py
2. Cambia el nombre, CIF y variantes
3. Implementa extraer_lineas() → SIEMPRE líneas individuales
4. Prueba: python tests/probar_extractor.py "PROVEEDOR" factura.pdf
5. ¡Listo! El extractor se registra automáticamente
```

---

## 🔑 REGLAS CRÍTICAS

### 1. SIEMPRE pdfplumber (OCR solo para escaneados)
```python
metodo_pdf = 'pdfplumber'  # SIEMPRE
metodo_pdf = 'ocr'         # SOLO si es imagen/escaneado
```

### 2. SIEMPRE líneas individuales
**1 artículo = 1 línea en el Excel**

❌ MAL (desglose fiscal agrupado):
```python
lineas.append({
    'articulo': 'PRODUCTOS VARIOS IVA 21%',
    'base': 646.55,
    'iva': 21
})
```

✅ BIEN (líneas individuales):
```python
lineas.append({
    'codigo': '1594',
    'articulo': 'FEVER-TREE',
    'cantidad': 24,
    'precio_ud': 0.80,
    'iva': 21,
    'base': 19.20
})
```

### 3. Columnas obligatorias
```python
{
    'codigo': str,       # Código del producto ('' si no hay)
    'articulo': str,     # Nombre del artículo (max 50 chars)
    'cantidad': int/float,  # Unidades
    'precio_ud': float,  # Precio unitario
    'iva': int,          # 4, 10 o 21
    'base': float        # Importe SIN IVA
}
```

### 4. Incluir TODAS las variantes del nombre
```python
@registrar('PROVEEDOR', 'VARIANTE1', 'VARIANTE2', 'VARIANTE3')
```

### 5. Portes: distribuir proporcionalmente
```python
# Si hay portes, distribuir entre productos
if portes > 0:
    base_productos = sum(l['base'] for l in lineas)
    for linea in lineas:
        proporcion = linea['base'] / base_productos
        linea['base'] += portes * proporcion
```

---

## 📝 PLANTILLA COMPLETA

```python
"""
Extractor para [NOMBRE PROVEEDOR]

[Descripción del proveedor]
CIF: [CIF]

Formato factura (pdfplumber):
[Describir formato]

IVA: [Tipos aplicables]

Creado: [FECHA]
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re
import pdfplumber


@registrar('PROVEEDOR', 'VARIANTE1', 'VARIANTE2')
class ExtractorProveedor(ExtractorBase):
    """Extractor para facturas de PROVEEDOR."""
    
    nombre = 'PROVEEDOR'
    cif = 'B12345678'
    iban = 'ES00 0000 0000 0000 0000 0000'
    metodo_pdf = 'pdfplumber'
    
    def extraer_texto_pdfplumber(self, pdf_path: str) -> str:
        """Extrae texto del PDF."""
        texto_completo = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    texto = page.extract_text()
                    if texto:
                        texto_completo.append(texto)
        except Exception as e:
            pass
        return '\n'.join(texto_completo)
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas INDIVIDUALES de productos.
        
        IMPORTANTE: 1 artículo = 1 línea
        """
        lineas = []
        
        # Patrón para líneas de producto
        patron_linea = re.compile(
            r'^(\d{4,6})\s+'              # Código
            r'(.+?)\s+'                    # Descripción
            r'(\d+)\s+'                    # Cantidad
            r'(\d+,\d{2})\s+'              # Precio
            r'(\d+,\d{2})$'                # Importe
        , re.MULTILINE)
        
        for match in patron_linea.finditer(texto):
            codigo = match.group(1)
            descripcion = match.group(2).strip()
            cantidad = int(match.group(3))
            precio = self._convertir_europeo(match.group(4))
            importe = self._convertir_europeo(match.group(5))
            
            # Filtrar cabeceras
            if any(x in descripcion.upper() for x in ['DESCRIPCION', 'TOTAL']):
                continue
            
            if importe < 1.0:
                continue
            
            lineas.append({
                'codigo': codigo,
                'articulo': descripcion[:50],
                'cantidad': cantidad,
                'precio_ud': round(precio, 2),
                'iva': 21,  # O el IVA que corresponda
                'base': round(importe, 2)
            })
        
        return lineas
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo (1.234,56) a float."""
        if not texto:
            return 0.0
        texto = texto.strip()
        if '.' in texto and ',' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            texto = texto.replace(',', '.')
        try:
            return float(texto)
        except:
            return 0.0
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """Extrae total de la factura."""
        patron = re.search(r'TOTAL[:\s]+(\d+,\d{2})\s*€', texto, re.IGNORECASE)
        if patron:
            return self._convertir_europeo(patron.group(1))
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        patron = re.search(r'(\d{2}/\d{2}/\d{4})', texto)
        if patron:
            return patron.group(1)
        return None
```

---

## 📋 PATRONES COMUNES

### Tabla estándar
```python
# CODIGO DESCRIPCION CANTIDAD PRECIO IMPORTE
r'^(\d{4,6})\s+(.+?)\s+(\d+)\s+(\d+,\d{2})\s+(\d+,\d{2})$'
```

### Con precio 3 decimales
```python
# 01071 MZ LATAS 5 KG 3 19,900 59,70
r'^(\d{4,6})\s+(.+?)\s+(\d+)\s+(\d+,\d{2,3})\s+(\d+,\d{2})$'
```

### Con cantidad decimal (kg)
```python
# CA0005 ANCHOA 10,00% 12,0000 24,0000 288,00
r'^([A-Z]{2}\d{4})\s+(.+?)\s+(\d+,\d{4})\s+(\d+,\d{4})\s+(\d+,\d{2})$'
```

### Formato europeo (punto miles, coma decimal)
```python
def _convertir_europeo(self, texto):
    texto = texto.replace('.', '').replace(',', '.')
    return float(texto)
```

---

## ⚠️ ERRORES COMUNES

### 1. "Extractor no encontrado"
**Causa:** El nombre en `@registrar()` no coincide
**Solución:** Añadir más variantes

### 2. "No se encontraron líneas"  
**Causa:** Patrón regex incorrecto
**Solución:** Probar con `--debug` y ajustar patrón

### 3. "Solo 1 línea con desglose"
**Causa:** Extractor usa desglose fiscal en vez de líneas
**Solución:** REHACER para extraer líneas individuales

### 4. "Total no cuadra"
**Causa:** Base mal calculada o portes no distribuidos
**Solución:** Verificar si hay portes y distribuirlos

### 5. "IVA incorrecto"
**Causa:** IVA hardcodeado cuando es variable
**Solución:** Detectar IVA real del PDF

---

## 🧪 TESTING

```cmd
# Test rápido
python tests/probar_extractor.py "PROVEEDOR" "factura.pdf"

# Con debug (ver texto extraído)
python tests/probar_extractor.py "PROVEEDOR" "factura.pdf" --debug
```

---

## 📚 EJEMPLOS REALES

### OCR (facturas escaneadas)
- `manipulados_abellan.py` - Conservas vegetales
- `la_rosquilleria.py` - Rosquillas
- `jimeluz.py` - Tickets

### IVA mixto
- `fabeiro.py` - 10% ibéricos, 4% quesos
- `distribuciones_lavapies.py` - 10%/21% bebidas

### Con portes
- `silva_cordero.py` - Portes 21% distribuidos

### Categoría fija
- `kinema.py` - Siempre categoría GESTORIA

---

*Última actualización: 20/12/2025 - Añadidos ejemplos OCR y portes*
