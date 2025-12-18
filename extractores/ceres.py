"""
Extractor para CERES (Cervezas artesanas).

Proveedor de cervezas y bebidas.
CIF: B83478669
IBAN: (adeudo - no necesita)

Formato factura:
- Tabla con CODIGO, DESCRIPCION, UDS, PRECIO, DTO, IVA, IMPORTE
- Productos con descuento y sin descuento
- Envases retornables (CE99xxxx)
- IVA 21% o 10%

Creado: 18/12/2025
Migrado de: migracion_historico_2025_v3_57.py (líneas 2604-2810)
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict
import re


@registrar('CERES', 'CERES CERVEZA', 'CERES CERVEZAS')
class ExtractorCeres(ExtractorBase):
    """Extractor para facturas de CERES."""
    
    nombre = 'CERES'
    cif = 'B83478669'
    iban = ''  # Adeudo
    metodo_pdf = 'pdfplumber'  # Mejor para tablas
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de facturas CERES.
        
        Formato columnas: CODIGO DESC UDS PRECIO DTO IVA IMPORTE
        """
        lineas = []
        codigos_procesados = set()
        
        # Patrón con descuento
        patron_con_dto = re.compile(
            r'^([A-Z0-9]{6})\s+'           # Código (6 chars)
            r'(.+?)\s+'                     # Descripción
            r'(-?\d+)\s+'                   # Unidades
            r'(\d+[,\.]\d+)\s+'             # Precio/Ud
            r'(\d+[,\.]?\d*)\s+'            # Descuento %
            r'(21|10)\s+'                   # IVA
            r'(-?\d+[,\.]\d+)',             # Importe
            re.MULTILINE
        )
        
        # Patrón sin descuento
        patron_sin_dto = re.compile(
            r'^([A-Z0-9]{6})\s+'           # Código
            r'(.+?)\s+'                     # Descripción
            r'(-?\d+)\s+'                   # Unidades
            r'(\d+[,\.]\d+)?\s*'            # Precio (opcional)
            r'(21|10)\s+'                   # IVA
            r'(-?\d+[,\.]\d+)',             # Importe
            re.MULTILINE
        )
        
        # Patrón envases litros
        patron_envase = re.compile(
            r'^(CE99\d{4})\s+'              # Código CE99xxxx
            r'(ENVASE\s+\d+\s*lit\.?)\s+'   # Descripción
            r'(-?\d+)\s+'                   # Unidades
            r'(\d+)\s+'                     # Precio (entero)
            r'(21|10)\s+'                   # IVA
            r'(-?\d+[,\.]\d+)',             # Importe
            re.MULTILINE
        )
        
        # Patrón envases ALH
        patron_envase_alh = re.compile(
            r'^(CE99\d{4})\s+'              # Código CE99xxxx
            r'(ENVASE\s+\d/\d\s+ALH)\s+'    # ENVASE 1/5 ALH
            r'(-?\d+)\s+'                   # Unidades
            r'(\d+[,\.]\d+)\s+'             # Precio
            r'(21|10)\s+'                   # IVA
            r'(-?\d+[,\.]\d+)',             # Importe
            re.MULTILINE
        )
        
        # Patrón CE99 genérico
        patron_ce99_generico = re.compile(
            r'^(CE99\d{4})\s+'              # Código CE99xxxx
            r'(.+?)\s+'                     # Descripción
            r'(-?\d+)\s+'                   # Unidades
            r'(\d+)\s+'                     # Precio (entero)
            r'(21|10)\s+'                   # IVA
            r'(-?\d+[,\.]\d+)',             # Importe
            re.MULTILINE
        )
        
        # Extraer con descuento
        for m in patron_con_dto.finditer(texto):
            codigo, desc, uds, precio, dto, iva, importe = m.groups()
            desc_limpia = desc.strip()
            
            if 'Albarán' in desc_limpia or 'Descripcion' in desc_limpia:
                continue
            
            importe_val = self._convertir_importe(importe)
            key = (codigo, importe_val)
            if key in codigos_procesados:
                continue
            codigos_procesados.add(key)
            
            lineas.append({
                'codigo': codigo,
                'articulo': desc_limpia,
                'cantidad': abs(int(uds)),
                'precio_ud': self._convertir_importe(precio),
                'iva': int(iva),
                'base': importe_val
            })
        
        # Extraer sin descuento
        for m in patron_sin_dto.finditer(texto):
            codigo, desc, uds, precio, iva, importe = m.groups()
            desc_limpia = desc.strip()
            
            if 'Albarán' in desc_limpia or 'Descripcion' in desc_limpia:
                continue
            if 'ENVASE' in desc_limpia.upper():
                continue
            
            importe_val = self._convertir_importe(importe)
            key = (codigo, importe_val)
            if key in codigos_procesados:
                continue
            
            if importe_val == 0:
                continue
                
            codigos_procesados.add(key)
            precio_ud = self._convertir_importe(precio) if precio else 0
            
            lineas.append({
                'codigo': codigo,
                'articulo': desc_limpia,
                'cantidad': abs(int(uds)),
                'precio_ud': precio_ud,
                'iva': int(iva),
                'base': importe_val
            })
        
        # Extraer envases
        for m in patron_envase.finditer(texto):
            codigo, desc, uds, precio, iva, importe = m.groups()
            importe_val = self._convertir_importe(importe)
            key = (codigo, importe_val)
            if key in codigos_procesados:
                continue
            codigos_procesados.add(key)
            
            lineas.append({
                'codigo': codigo,
                'articulo': desc.strip(),
                'cantidad': abs(int(uds)),
                'precio_ud': float(precio),
                'iva': int(iva),
                'base': importe_val
            })
        
        # Extraer envases ALH
        for m in patron_envase_alh.finditer(texto):
            codigo, desc, uds, precio, iva, importe = m.groups()
            importe_val = self._convertir_importe(importe)
            key = (codigo, importe_val)
            if key in codigos_procesados:
                continue
            codigos_procesados.add(key)
            
            lineas.append({
                'codigo': codigo,
                'articulo': desc.strip(),
                'cantidad': abs(int(uds)),
                'precio_ud': self._convertir_importe(precio),
                'iva': int(iva),
                'base': importe_val
            })
        
        # Extraer CE99 genérico
        for m in patron_ce99_generico.finditer(texto):
            codigo, desc, uds, precio, iva, importe = m.groups()
            desc_limpia = desc.strip()
            
            if 'ENVASE' in desc_limpia.upper():
                continue
                
            importe_val = self._convertir_importe(importe)
            key = (codigo, importe_val)
            if key in codigos_procesados:
                continue
            codigos_procesados.add(key)
            
            lineas.append({
                'codigo': codigo,
                'articulo': desc_limpia,
                'cantidad': abs(int(uds)),
                'precio_ud': float(precio),
                'iva': int(iva),
                'base': importe_val
            })
        
        # CLA (caja retornable)
        cla_match = re.search(r'CLA:\s*(\d+)', texto)
        if cla_match:
            cla_cantidad = int(cla_match.group(1))
            if cla_cantidad > 0:
                lineas.append({
                    'codigo': 'CLA',
                    'articulo': 'CAJA RETORNABLE',
                    'cantidad': cla_cantidad,
                    'precio_ud': 1.0,
                    'iva': 21,
                    'base': float(cla_cantidad)
                })
        
        return lineas
