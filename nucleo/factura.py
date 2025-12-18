"""
Clase Factura - Modelo de datos principal.

Esta clase representa una factura procesada con todas sus líneas
y metadatos extraídos del PDF.

Uso:
    from nucleo.factura import Factura, LineaFactura
    
    factura = Factura(
        archivo='2001_CERES_TF.pdf',
        proveedor='CERES',
        fecha='15/12/2025',
        ...
    )
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class LineaFactura:
    """
    Representa una línea de producto en una factura.
    
    Atributos obligatorios:
        articulo: Nombre/descripción del producto
        base: Importe SIN IVA
        iva: Porcentaje de IVA (4, 10, 21)
    
    Atributos opcionales:
        codigo: Código del producto
        cantidad: Cantidad de unidades
        precio_ud: Precio unitario
        categoria: Categoría asignada
        id_categoria: ID de categoría del diccionario
    """
    articulo: str
    base: float
    iva: int
    codigo: str = ''
    cantidad: float = 1.0
    precio_ud: float = 0.0
    categoria: str = ''
    id_categoria: int = 0
    
    @property
    def total(self) -> float:
        """Calcula el total de la línea (base + IVA)."""
        return round(self.base * (1 + self.iva / 100), 2)
    
    @property
    def cuota_iva(self) -> float:
        """Calcula la cuota de IVA."""
        return round(self.base * self.iva / 100, 2)
    
    def to_dict(self) -> dict:
        """Convierte la línea a diccionario."""
        return {
            'articulo': self.articulo,
            'codigo': self.codigo,
            'categoria': self.categoria,
            'id_categoria': self.id_categoria,
            'cantidad': self.cantidad,
            'precio_ud': self.precio_ud,
            'base': self.base,
            'iva': self.iva,
            'total': self.total,
        }


@dataclass
class Factura:
    """
    Representa una factura completa procesada.
    
    Atributos del archivo:
        archivo: Nombre del archivo PDF
        numero: Número extraído del nombre (ej: 2001)
        ruta: Ruta completa al archivo
    
    Atributos del proveedor:
        proveedor: Nombre del proveedor
        cif: CIF del proveedor
        iban: IBAN del proveedor
    
    Atributos de la factura:
        fecha: Fecha de la factura (DD/MM/YYYY)
        referencia: Número de referencia/factura
        total: Total de la factura
    
    Líneas y estado:
        lineas: Lista de LineaFactura
        cuadre: Estado del cuadre ('OK', 'DESCUADRE_X.XX', 'SIN_TOTAL', etc.)
        errores: Lista de errores encontrados
    """
    # Archivo
    archivo: str
    numero: int = 0
    ruta: str = ''
    
    # Proveedor
    proveedor: str = ''
    cif: str = ''
    iban: str = ''
    
    # Datos factura
    fecha: str = ''
    referencia: str = ''
    total: Optional[float] = None
    
    # Líneas
    lineas: List[LineaFactura] = field(default_factory=list)
    
    # Estado
    cuadre: str = ''
    errores: List[str] = field(default_factory=list)
    
    # Metadatos
    metodo_pdf: str = 'pypdf'
    texto_raw: str = ''
    procesado_at: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    @property
    def num_lineas(self) -> int:
        """Número de líneas de la factura."""
        return len(self.lineas)
    
    @property
    def tiene_lineas(self) -> bool:
        """Indica si la factura tiene líneas extraídas."""
        return len(self.lineas) > 0
    
    @property
    def total_calculado(self) -> float:
        """Suma de los totales de todas las líneas."""
        return round(sum(linea.total for linea in self.lineas), 2)
    
    @property
    def base_total(self) -> float:
        """Suma de las bases de todas las líneas."""
        return round(sum(linea.base for linea in self.lineas), 2)
    
    @property
    def iva_total(self) -> float:
        """Suma de las cuotas de IVA de todas las líneas."""
        return round(sum(linea.cuota_iva for linea in self.lineas), 2)
    
    @property
    def es_ok(self) -> bool:
        """Indica si la factura se procesó correctamente."""
        return self.cuadre == 'OK'
    
    @property
    def tiene_errores(self) -> bool:
        """Indica si la factura tiene errores."""
        return len(self.errores) > 0
    
    def agregar_linea(self, linea: LineaFactura):
        """Agrega una línea a la factura."""
        self.lineas.append(linea)
    
    def agregar_linea_dict(self, datos: dict):
        """
        Agrega una línea desde un diccionario.
        
        Args:
            datos: Diccionario con al menos 'articulo', 'base', 'iva'
        """
        linea = LineaFactura(
            articulo=datos.get('articulo', ''),
            base=float(datos.get('base', 0)),
            iva=int(datos.get('iva', 21)),
            codigo=datos.get('codigo', ''),
            cantidad=float(datos.get('cantidad', 1)),
            precio_ud=float(datos.get('precio_ud', 0)),
            categoria=datos.get('categoria', ''),
            id_categoria=int(datos.get('id_categoria', 0)),
        )
        self.lineas.append(linea)
    
    def agregar_error(self, error: str):
        """Agrega un error a la lista."""
        if error not in self.errores:
            self.errores.append(error)
    
    def to_dict(self) -> dict:
        """Convierte la factura a diccionario."""
        return {
            'archivo': self.archivo,
            'numero': self.numero,
            'proveedor': self.proveedor,
            'cif': self.cif,
            'iban': self.iban,
            'fecha': self.fecha,
            'referencia': self.referencia,
            'total': self.total,
            'total_calculado': self.total_calculado,
            'num_lineas': self.num_lineas,
            'cuadre': self.cuadre,
            'errores': self.errores,
        }
    
    def to_filas_excel(self) -> List[dict]:
        """
        Convierte la factura a filas para Excel.
        
        Returns:
            Lista de diccionarios, uno por cada línea de la factura.
            Si no hay líneas, devuelve una fila con los datos básicos.
        """
        if not self.lineas:
            # Factura sin líneas: una fila con datos básicos
            return [{
                '#': self.numero,
                'FECHA': self.fecha,
                'PROVEEDOR': self.proveedor,
                'REF': self.referencia,
                'CIF': self.cif,
                'ARTICULO': '',
                'CODIGO': '',
                'CATEGORIA': '',
                'ID_CAT': '',
                'BASE': '',
                'IVA': '',
                'TOTAL': '',
                'TOTAL FAC': self.total,
                'CUADRE': self.cuadre,
                'IBAN': self.iban,
                'ARCHIVO': self.archivo,
            }]
        
        # Factura con líneas: una fila por línea
        filas = []
        for linea in self.lineas:
            filas.append({
                '#': self.numero,
                'FECHA': self.fecha,
                'PROVEEDOR': self.proveedor,
                'REF': self.referencia,
                'CIF': self.cif,
                'ARTICULO': linea.articulo,
                'CODIGO': linea.codigo,
                'CATEGORIA': linea.categoria,
                'ID_CAT': linea.id_categoria,
                'BASE': linea.base,
                'IVA': linea.iva,
                'TOTAL': linea.total,
                'TOTAL FAC': self.total,
                'CUADRE': self.cuadre,
                'IBAN': self.iban,
                'ARCHIVO': self.archivo,
            })
        
        return filas
    
    def __str__(self) -> str:
        """Representación en texto de la factura."""
        estado = '✅' if self.es_ok else '⚠️'
        return f"{estado} {self.archivo}: {self.proveedor} | {self.fecha} | {self.num_lineas} líneas | {self.cuadre}"
    
    def __repr__(self) -> str:
        return f"Factura(archivo='{self.archivo}', proveedor='{self.proveedor}', lineas={self.num_lineas})"
