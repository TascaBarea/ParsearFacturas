"""
Extractor para QUESOS DE CATI COOP. V.

Cooperativa de quesos de cabra de Catí (Castellón).
CIF: F12499455
IBAN: ES89 2100 7363 72 1100030799

Productos: Quesos de cabra (Catiabrigo, Pañoleta, Catipell)
IVA: 4% (quesos)

NOTA: El PDF tiene caracteres duplicados en algunas zonas
(ej: "BBaasseess" en lugar de "Bases"). Se usa función
deduplicar_texto() para limpiar.

Estrategia: Usar cuadro fiscal para garantizar cuadre.

Creado: 01/01/2026
Validado: 6/6 facturas (1T25-4T25)
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar('QUESOS DEL CATI', 'QUESOS DE CATI', 'QUESOS CATI', 'CATI')
class ExtractorQuesosCati(ExtractorBase):
    """Extractor para facturas de Quesos de Catí."""
    
    nombre = 'QUESOS DEL CATI'
    cif = 'F12499455'
    iban = 'ES89 2100 7363 72 1100030799'
    metodo_pdf = 'pdfplumber'
    
    def _convertir_importe(self, texto: str) -> float:
        """Convierte texto a float (formato europeo)."""
        if not texto:
            return 0.0
        texto = str(texto).strip().replace(' ', '')
        if '.' in texto and ',' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            texto = texto.replace(',', '.')
        try:
            return float(texto)
        except:
            return 0.0
    
    def _deduplicar_texto(self, texto: str) -> str:
        """
        Quita caracteres duplicados consecutivos.
        Ej: 'BBaasseess ddee II..VV..AA..' -> 'Bases de I.V.A.'
        """
        resultado = []
        i = 0
        while i < len(texto):
            if i + 1 < len(texto) and texto[i] == texto[i+1]:
                resultado.append(texto[i])
                i += 2
            else:
                resultado.append(texto[i])
                i += 1
        return ''.join(resultado)
    
    def extraer_cuadro_fiscal(self, texto: str) -> Optional[Dict]:
        """
        Extrae base, IVA y cuota del cuadro fiscal.
        
        Formato (puede estar duplicado):
        Bases de I.V.A. %IVA Cuotas IVA Cuotas Recargo
        283,91 4,00 11,36
        """
        texto_limpio = self._deduplicar_texto(texto)
        
        # Buscar línea con BASE IVA% CUOTA después de "Bases de I.V.A."
        m = re.search(
            r'Bases de I\.V\.A\.\s*%IVA\s*Cuotas IVA.*?([\d,]+)\s+([\d,]+)\s+([\d,]+)',
            texto_limpio, re.DOTALL
        )
        
        if m:
            base = self._convertir_importe(m.group(1))
            iva_pct = self._convertir_importe(m.group(2))
            cuota = self._convertir_importe(m.group(3))
            
            return {
                'base': base,
                'iva_pct': iva_pct,
                'cuota': cuota,
                'total': round(base + cuota, 2)
            }
        
        return None
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Genera línea basada en el cuadro fiscal.
        QUESOS DE CATI solo tiene IVA 4% (quesos de cabra).
        """
        lineas = []
        cuadro = self.extraer_cuadro_fiscal(texto)
        
        if cuadro:
            lineas.append({
                'articulo': 'QUESOS DE CABRA CATI (IVA 4%)',
                'base': cuadro['base'],
                'iva': 4,
                'categoria': 'QUESOS',
                'cantidad': 1,
                'precio_ud': cuadro['base']
            })
        
        return lineas
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """Extrae el total de la factura."""
        texto_limpio = self._deduplicar_texto(texto)
        
        # Método 1: "TOTAL FACTURA EUROS" + número
        m = re.search(r'TOTAL FACTURA EUROS\s*([\d,.]+)', texto_limpio)
        if m:
            return self._convertir_importe(m.group(1))
        
        # Método 2: Vencimientos e Importes: DD/MM/YYYY XXX
        m2 = re.search(r'Vencimientos e Importes\s*:\s*[\d/]+\s+([\d,.]+)', texto_limpio)
        if m2:
            return self._convertir_importe(m2.group(1))
        
        # Método 3: Calcular desde cuadro fiscal
        cuadro = self.extraer_cuadro_fiscal(texto)
        if cuadro:
            return cuadro['total']
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        texto_limpio = self._deduplicar_texto(texto)
        
        # Buscar "Fecha: DD/MM/YYYY"
        m = re.search(r'Fecha:\s*(\d{2})/(\d{2})/(\d{4})', texto_limpio)
        if m:
            dia, mes, año = m.groups()
            return f"{dia}/{mes}/{año}"
        
        return None
    
    def extraer_referencia(self, texto: str) -> Optional[str]:
        """Extrae número de factura."""
        texto_limpio = self._deduplicar_texto(texto)
        
        # Buscar "Número FRA: XXXX"
        m = re.search(r'Número FRA:\s*(\d+)', texto_limpio)
        if m:
            return m.group(1)
        
        return None
