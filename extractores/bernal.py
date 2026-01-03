"""
Extractor para JAMONES Y EMBUTIDOS BERNAL SLU

Jamones ibéricos y embutidos de bellota.
CIF: B67784231
IBAN: ES49 2100 7191 2902 0003 7620

Formato factura (pdfplumber):
CÓDIGO DESCRIPCIÓN_PARCIAL C.SEC UNIDADES PRECIO %DES %IVA IMPORTE
DESCRIPCIÓN_CONTINUACIÓN
Lotes: XXX;

Ejemplo:
EM-MORCRE MORCILLA RECTA DE 0,00 1,370 12,7300 0,00 10,00 17,440
BELLOTA 100% IBÉRICA
Lotes: 3252;

IVA: 10% productos, 21% portes

IMPORTANTE: La columna IMPORTE de la factura es la BASE (sin IVA).
El sistema espera el importe CON IVA para el cuadre.

Creado: 19/12/2025
Corregido: 27/12/2025 - Patrón regex mejorado, descripciones completas
Corregido: 02/01/2026 - FIX CRÍTICO: Calcular importe CON IVA (línea 96)
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re
import pdfplumber


@registrar('JAMONES BERNAL', 'BERNAL', 'JAMONES Y EMBUTIDOS BERNAL', 'EMBUTIDOS BERNAL')
class ExtractorBernal(ExtractorBase):
    """Extractor para facturas de JAMONES BERNAL."""
    
    nombre = 'JAMONES BERNAL'
    cif = 'B67784231'
    iban = 'ES49 2100 7191 2902 0003 7620'
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas individuales de productos.
        
        Formato:
        CÓDIGO DESCRIPCIÓN_PARCIAL C.SEC UNIDADES PRECIO %DES %IVA IMPORTE
        DESCRIPCIÓN_CONTINUACIÓN (opcional)
        Lotes: XXX;
        
        NOTA: La columna IMPORTE es la BASE (sin IVA).
        Calculamos el importe con IVA para el cuadre.
        """
        lineas = []
        lineas_texto = texto.split('\n')
        
        # Patrón para líneas de producto
        # CÓDIGO DESC CSEC UNID PRECIO %DES %IVA IMPORTE
        patron = re.compile(
            r'^([A-Z]{1,3}-[A-Z0-9]+)\s+'          # Código (ej: EM-MORCRE, LO-JABELL, P-PORTES)
            r'(.+?)\s+'                             # Descripción (parcial)
            r'(\d+,\d{2})\s+'                       # C.Sec (cantidad)
            r'(\d+,\d{3})\s+'                       # Unidades (peso/unidades)
            r'(\d+,\d{4})\s+'                       # Precio unitario
            r'(\d+,\d{2})\s+'                       # %Descuento
            r'(\d+,\d{2})\s+'                       # %IVA
            r'(\d+,\d{3})$'                         # Importe (BASE sin IVA)
        )
        
        for i, linea in enumerate(lineas_texto):
            match = patron.match(linea.strip())
            if match:
                codigo = match.group(1)
                descripcion = match.group(2).strip()
                csec = self._convertir_europeo(match.group(3))
                unidades = self._convertir_europeo(match.group(4))
                precio = self._convertir_europeo(match.group(5))
                iva = int(self._convertir_europeo(match.group(7)))
                importe_base = self._convertir_europeo(match.group(8))  # BASE sin IVA
                
                # Buscar continuación de descripción en línea siguiente
                if i + 1 < len(lineas_texto):
                    linea_siguiente = lineas_texto[i + 1].strip()
                    # Si no es un código ni "Lotes:" ni línea vacía, es continuación
                    if (linea_siguiente and 
                        not re.match(r'^[A-Z]{1,3}-[A-Z0-9]+\s+', linea_siguiente) and
                        not linea_siguiente.startswith('Lotes:') and
                        not linea_siguiente.startswith('%Desc')):
                        descripcion = f"{descripcion} {linea_siguiente}"
                
                # Limpiar descripción
                descripcion = re.sub(r'\s+', ' ', descripcion).strip()
                
                # Filtrar líneas con importe muy bajo (excepto ajustes)
                if importe_base < 0.50:
                    continue
                
                # Determinar cantidad: usar C.Sec si > 0, sino Unidades
                cantidad = csec if csec > 0 else unidades
                
                # CORRECCIÓN 02/01/2026: Calcular importe CON IVA
                # La factura muestra la BASE, pero el sistema necesita el total con IVA
                importe_con_iva = importe_base * (1 + iva / 100)
                
                lineas.append({
                    'codigo': codigo,
                    'articulo': descripcion[:50],
                    'cantidad': int(cantidad) if cantidad == int(cantidad) else round(cantidad, 3),
                    'precio_ud': round(precio, 2),
                    'iva': iva,
                    'base': round(importe_con_iva, 2)  # CORREGIDO: Importe CON IVA
                })
        
        return lineas
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo (1.234,56) a float."""
        if not texto:
            return 0.0
        texto = str(texto).strip()
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
        patron = re.search(r'Total\s+Factura:\s*([\d.,]+)\s*€', texto, re.IGNORECASE)
        if patron:
            return self._convertir_europeo(patron.group(1))
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de expedición."""
        patron = re.search(r'expedición\s*/\s*emisión:\s*(\d{2}/\d{2}/\d{2})', texto)
        if patron:
            fecha = patron.group(1)
            # Convertir 19/11/25 a 19/11/2025
            partes = fecha.split('/')
            if len(partes) == 3 and len(partes[2]) == 2:
                return f"{partes[0]}/{partes[1]}/20{partes[2]}"
            return fecha
        return None
