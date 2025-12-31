"""
Clase base para todos los extractores de facturas.

Todos los extractores deben heredar de ExtractorBase e implementar
el método extraer_lineas().

Ejemplo:
    from extractores.base import ExtractorBase
    from extractores import registrar
    
    @registrar('MI PROVEEDOR')
    class ExtractorMiProveedor(ExtractorBase):
        nombre = 'MI PROVEEDOR'
        cif = 'B12345678'
        iban = 'ES00 0000 0000 00'
        
        def extraer_lineas(self, texto: str) -> List[Dict]:
            lineas = []
            # ... lógica de extracción
            return lineas
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import re


class ExtractorBase(ABC):
    """
    Clase base abstracta para extractores de facturas.
    
    Atributos de clase (sobrescribir en subclases):
        nombre: Nombre del proveedor
        cif: CIF del proveedor
        iban: IBAN del proveedor (vacío si pago tarjeta/efectivo)
        metodo_pdf: Método de extracción ('pypdf', 'pdfplumber', 'ocr')
    """
    
    # === ATRIBUTOS DE CLASE (sobrescribir en subclases) ===
    nombre: str = ''
    cif: str = ''
    iban: str = ''
    metodo_pdf: str = 'pypdf'  # 'pypdf', 'pdfplumber', 'ocr'
    
    # === MÉTODO ABSTRACTO (obligatorio implementar) ===
    
    @abstractmethod
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae las líneas de producto de la factura.
        
        Args:
            texto: Texto extraído del PDF
            
        Returns:
            Lista de diccionarios con las líneas:
            [
                {
                    'articulo': str,      # Nombre del producto (obligatorio)
                    'base': float,        # Importe SIN IVA (obligatorio)
                    'iva': int,           # Porcentaje IVA: 4, 10 o 21 (obligatorio)
                    'codigo': str,        # Código producto (opcional)
                    'cantidad': float,    # Cantidad (opcional)
                    'precio_ud': float,   # Precio unitario (opcional)
                },
                ...
            ]
        """
        pass
    
    # === MÉTODOS OPCIONALES (pueden sobrescribirse) ===
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """
        Extrae el total de la factura.
        
        Por defecto usa patrones genéricos. Sobrescribir si el formato
        del proveedor es especial.
        
        Args:
            texto: Texto extraído del PDF
            
        Returns:
            Total de la factura o None si no se encuentra
        """
        # Patrones ordenados de más específico a más genérico
        patrones = [
            # TOTAL €: 890,08
            r'TOTAL\s*€[:\s]*(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})',
            # TOTAL FACTURA: 123,45
            r'TOTAL\s*FACTURA[:\s]*(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})',
            # TOTAL A PAGAR: 123,45
            r'TOTAL\s*A\s*PAGAR[:\s]*(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})',
            # TOTAL: 123,45 €
            r'\bTOTAL[:\s]+(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*€',
            # TOTAL 123,45
            r'\bTOTAL[:\s]+(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})',
        ]
        
        for patron in patrones:
            match = re.search(patron, texto, re.IGNORECASE | re.MULTILINE)
            if match:
                total_str = match.group(1)
                return self._convertir_importe(total_str)
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """
        Extrae la fecha de la factura.
        
        Por defecto busca formato DD/MM/YYYY. Sobrescribir si el formato
        del proveedor es diferente.
        
        Args:
            texto: Texto extraído del PDF
            
        Returns:
            Fecha en formato DD/MM/YYYY o None si no se encuentra
        """
        # Patrón estándar DD/MM/YYYY
        patron = r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})'
        match = re.search(patron, texto)
        
        if match:
            dia = match.group(1).zfill(2)
            mes = match.group(2).zfill(2)
            año = match.group(3)
            return f"{dia}/{mes}/{año}"
        
        return None
    
    def extraer_referencia(self, texto: str) -> Optional[str]:
        """
        Extrae el número de referencia/factura.
        
        IMPORTANTE: Si la subclase define extraer_numero_factura(), 
        se usa automáticamente ese método. Esto permite compatibilidad
        con extractores que usen cualquiera de los dos nombres.
        
        Args:
            texto: Texto extraído del PDF
            
        Returns:
            Número de referencia o None si no se encuentra
        """
        # =========================================================
        # COMPATIBILIDAD: Si la subclase define extraer_numero_factura,
        # usarlo automáticamente (fix bug 29/12/2025)
        # =========================================================
        if hasattr(self, 'extraer_numero_factura'):
            resultado = self.extraer_numero_factura(texto)
            if resultado:
                return resultado
        
        # Fallback: patrones genéricos
        patrones = [
            r'(?:Factura|Fra|Nº|Número)[:\s]*([A-Z]?\d{4,10})',
            r'(?:FACTURA|FRA|Nº)[:\s]*([A-Z]?\d{4,10})',
        ]
        
        for patron in patrones:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    # === MÉTODOS DE UTILIDAD ===
    
    def _convertir_importe(self, importe_str: str) -> float:
        """
        Convierte un string de importe a float.
        
        Maneja formatos:
        - 1.234,56 (español)
        - 1,234.56 (americano)
        - 1234.56 (sin separador miles)
        
        Args:
            importe_str: String con el importe
            
        Returns:
            Importe como float
        """
        # Limpiar espacios
        importe_str = importe_str.strip()
        
        # Formato español: 1.234,56
        if ',' in importe_str and '.' in importe_str:
            # Determinar cuál es el decimal
            pos_coma = importe_str.rfind(',')
            pos_punto = importe_str.rfind('.')
            
            if pos_coma > pos_punto:
                # Formato español: punto = miles, coma = decimal
                importe_str = importe_str.replace('.', '').replace(',', '.')
            else:
                # Formato americano: coma = miles, punto = decimal
                importe_str = importe_str.replace(',', '')
        elif ',' in importe_str:
            # Solo coma: es decimal
            importe_str = importe_str.replace(',', '.')
        
        return float(importe_str)
    
    def _limpiar_texto(self, texto: str) -> str:
        """
        Limpia el texto extraído del PDF.
        
        Args:
            texto: Texto a limpiar
            
        Returns:
            Texto limpio
        """
        # Eliminar múltiples espacios
        texto = re.sub(r' +', ' ', texto)
        # Eliminar múltiples saltos de línea
        texto = re.sub(r'\n+', '\n', texto)
        return texto.strip()
    
    def _calcular_base_desde_total(self, total: float, iva: int) -> float:
        """
        Calcula la base imponible a partir del total con IVA.
        
        Args:
            total: Total con IVA incluido
            iva: Porcentaje de IVA (4, 10, 21)
            
        Returns:
            Base imponible (sin IVA)
        """
        return round(total / (1 + iva / 100), 2)
    
    def _calcular_total_desde_base(self, base: float, iva: int) -> float:
        """
        Calcula el total con IVA a partir de la base.
        
        Args:
            base: Base imponible (sin IVA)
            iva: Porcentaje de IVA (4, 10, 21)
            
        Returns:
            Total con IVA incluido
        """
        return round(base * (1 + iva / 100), 2)


# Función auxiliar para el decorador registrar (importada desde __init__)
def registrar(*nombres_proveedor):
    """
    Decorador para registrar extractores.
    
    Este es un placeholder - la función real está en extractores/__init__.py
    Se reimporta aquí para conveniencia.
    """
    from extractores import registrar as _registrar
    return _registrar(*nombres_proveedor)
