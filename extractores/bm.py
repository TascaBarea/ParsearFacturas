"""
Extractor para BM SUPERMERCADOS.

Tickets de supermercado con desglose fiscal.
CIF: B20099586
IBAN: (pago tarjeta)

Formato factura:
- Tickets con líneas de productos
- Desglose fiscal al final: Tipo Base IVA Req Total
- IVA 4%, 10% o 21%

Creado: 18/12/2025
Migrado de: migracion_historico_2025_v3_57.py (líneas 2813-2983)
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict
import re


@registrar('BM', 'BM SUPERMERCADOS')
class ExtractorBM(ExtractorBase):
    """Extractor para tickets de BM SUPERMERCADOS."""
    
    nombre = 'BM SUPERMERCADOS'
    cif = 'B20099586'
    iban = ''  # Pago tarjeta
    metodo_pdf = 'pypdf'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de tickets BM.
        
        Estrategia: Usar el desglose fiscal del ticket que garantiza cuadre.
        """
        lineas = []
        
        # Patrón desglose fiscal: 10.00% 24.61 2.46 0.00 27.07
        patron_desglose = re.compile(
            r'^\s*(\d+)[,\.](\d{2})%\s+'  # Tipo IVA
            r'(\d+[,\.]\d{2})\s+'          # Base
            r'(\d+[,\.]\d{2})\s+'          # IVA
            r'(\d+[,\.]\d{2})\s+'          # Req
            r'(\d+[,\.]\d{2})',            # Total
            re.MULTILINE
        )
        
        for match in patron_desglose.finditer(texto):
            iva_entero = int(match.group(1))
            iva_decimal = int(match.group(2))
            base_str = match.group(3)
            
            iva = iva_entero if iva_decimal == 0 else iva_entero + iva_decimal / 100.0
            base = self._convertir_importe(base_str)
            
            if base > 0:
                if iva == 4 or iva == 4.0:
                    descripcion = "PRODUCTOS IVA SUPERREDUCIDO 4%"
                    iva_int = 4
                elif iva == 10 or iva == 10.0:
                    descripcion = "PRODUCTOS IVA REDUCIDO 10%"
                    iva_int = 10
                elif iva == 21 or iva == 21.0:
                    descripcion = "PRODUCTOS IVA GENERAL 21%"
                    iva_int = 21
                else:
                    descripcion = f"PRODUCTOS IVA {iva}%"
                    iva_int = int(iva)
                
                lineas.append({
                    'codigo': '',
                    'articulo': descripcion,
                    'iva': iva_int,
                    'base': base
                })
        
        # Fallback: extraer productos individuales
        if not lineas:
            lineas = self._extraer_productos(texto)
        
        return lineas
    
    def _extraer_productos(self, texto: str) -> List[Dict]:
        """Fallback: extrae productos individuales si no hay desglose."""
        lineas = []
        
        # Patrón líneas con peso
        patron_peso = re.compile(
            r'^\s*([\d,\.]+)\s+'
            r'([A-Z][A-Z0-9\s\.\,\(\)/\*\-]+?)\s+'
            r'(\d+[,\.]\d{2})\s+'
            r'(\d+[,\.]\d{2})\s*$',
            re.MULTILINE
        )
        
        # Patrón líneas simples
        patron_simple = re.compile(
            r'^\s*(\d+)\s+'
            r'([A-Z][A-Z0-9\s\.\,\(\)/\*\-]+?)\s+'
            r'(\d+[,\.]\d{2})\s*$',
            re.MULTILINE
        )
        
        # Palabras a ignorar
        ignorar = ['TOTAL', 'TARJETA', 'CUENTA', 'ACUMUL', 'TICKET', 
                   'FACTURA', 'ENTREGADO', 'CAMBIO', 'AHORRO', 'PROMOCION', 'PUNTO']
        
        for match in patron_peso.finditer(texto):
            cantidad, descripcion, precio_ud, importe = match.groups()
            desc = descripcion.strip()
            
            if any(x in desc.upper() for x in ignorar):
                continue
            
            pvp = self._convertir_importe(importe)
            iva = self._determinar_iva(desc)
            base = self._calcular_base_desde_total(pvp, iva)
            
            lineas.append({
                'codigo': '',
                'articulo': desc,
                'iva': iva,
                'base': base
            })
        
        for match in patron_simple.finditer(texto):
            cantidad, descripcion, importe = match.groups()
            desc = descripcion.strip()
            
            if any(x in desc.upper() for x in ignorar):
                continue
            
            if any(l['articulo'] == desc for l in lineas):
                continue
            
            pvp = self._convertir_importe(importe)
            iva = self._determinar_iva(desc)
            base = self._calcular_base_desde_total(pvp, iva)
            
            lineas.append({
                'codigo': '',
                'articulo': desc,
                'iva': iva,
                'base': base
            })
        
        return lineas
    
    def _determinar_iva(self, descripcion: str) -> int:
        """Determina el IVA según el producto."""
        desc_upper = descripcion.upper()
        
        # IVA 4%
        if any(x in desc_upper for x in [
            'PAN ', 'BARRA', 'HOGAZA', 'CHAPATA', 'MOLDE',
            'LECHE ', 'HUEVO', 'DOCENA',
            'CALABACIN', 'PLATANO', 'MANZANA', 'NARANJA', 'TOMATE',
            'PATATA', 'CEBOLLA', 'ZANAHORIA', 'LECHUGA',
            'QUESO', 'YOGUR', 'HARINA', 'ARROZ', 'ACEITE OLIVA'
        ]):
            return 4
        
        # IVA 21%
        if any(x in desc_upper for x in [
            'BOLSA', 'VAJILLA', 'LIMP', 'DETERGENTE', 'LEJIA',
            'PAPEL ', 'SERVILLETA', 'PILAS', 'BOMBILLA'
        ]):
            return 21
        
        return 10  # Por defecto alimentación
