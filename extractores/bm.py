"""
Extractor para BM SUPERMERCADOS (DISTRIBUCION SUPERMERCADOS, SL)

Supermercado de barrio con formato ticket.
CIF: B20099586

Formato ticket (pdfplumber):
 - CARNICERíA-CHARCUTERíA -
 2.69 PECHUGA PAVO GRANEL 10.45 28.16
 
 - PESCADERíA -
 1 BOQUERON ALIÑADO A.IÑAKI 310 5.99

Cuadro fiscal:
 Tipo Base Iva Req Total
 10.00% 31.05 3.10 0.00 34.15
 21.00% 0.75 0.16 0.00 0.91

IVA: 4% (pan, frutas), 10% (alimentación), 21% (droguería)
Pago: Tarjeta

Creado: 26/12/2025
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional
import re


@registrar('BM', 'BM SUPERMERCADOS', 'DISTRIBUCION SUPERMERCADOS')
class ExtractorBM(ExtractorBase):
    """Extractor para tickets de BM SUPERMERCADOS."""
    
    nombre = 'BM'
    cif = 'B20099586'
    iban = ''  # Pago tarjeta
    metodo_pdf = 'pdfplumber'
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas individuales de productos del ticket.
        
        Formatos:
        - Con cantidad y precio: "2.69 PECHUGA PAVO GRANEL 10.45 28.16"
        - Solo cantidad 1: "1 BOQUERON ALIÑADO A.IÑAKI 310 5.99"
        - Sin cantidad explícita: "JAMON DUROC HOGUERA GR CENTR 3.15"
        """
        lineas = []
        seccion_actual = None
        
        # Mapeo de secciones a IVA
        # (aproximado, el IVA real viene del cuadro fiscal)
        iva_seccion = {
            'FRUTERÍA': 4,
            'PANADERÍA': 4,
            'CARNICERÍA': 10,
            'CHARCUTERÍA': 10,
            'PESCADERÍA': 10,
            'ALIMENTACIÓN': 10,
            'DROGUERÍA': 21,
            'PERFUMERÍA': 21,
            'HOGAR': 21,
            'MENAJE': 21,
        }
        
        for linea in texto.split('\n'):
            linea = linea.strip()
            if not linea:
                continue
            
            # Detectar sección (ej: "- CARNICERíA-CHARCUTERíA -")
            match_seccion = re.match(r'^-\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\-]+)\s*-$', linea)
            if match_seccion:
                seccion_texto = match_seccion.group(1).upper()
                for sec, iva in iva_seccion.items():
                    if sec in seccion_texto:
                        seccion_actual = iva
                        break
                continue
            
            # Ignorar líneas de totales y otros
            if any(x in linea.upper() for x in ['TOTAL', 'TARJETA', 'TICKET', 'FACTURA', 
                                                  'CLIENTE', 'GRACIAS', 'COMPRA', 'BM:',
                                                  'ACUMULADO', 'PUNTO', 'COLECCION',
                                                  'CUENTA BM', 'APP', 'DEVOLUC', 'CAJA',
                                                  'ATENDIÓ', 'FECHA', 'HORA', 'CENTRO',
                                                  'AUTORIZ', 'COMERCIO', 'TARJETA', 
                                                  'TITULAR', 'ARC', 'AID', 'APLICACION',
                                                  'VALIDACION', 'CHIP', 'OPER', 'IMPORTE',
                                                  'SEC.', 'CONTACTLES', '---', 'Tipo', 
                                                  'Base', 'Iva', 'Req', 'CIF:', 'NIF',
                                                  'DOMICILIO', 'POBLACIÓN', 'NOMBRE']):
                continue
            
            # Patrón 1: cantidad decimal + descripción + precio_ud + importe
            # "2.69 PECHUGA PAVO GRANEL 10.45 28.16"
            match1 = re.match(
                r'^(\d+[.,]\d{2})\s+([A-ZÁÉÍÓÚÑa-záéíóúñ0-9\s\.\,\-\/\(\)]+?)\s+(\d+[.,]\d{2})\s+(\d+[.,]\d{2})$',
                linea
            )
            if match1:
                cantidad = self._convertir_europeo(match1.group(1))
                descripcion = match1.group(2).strip()
                precio_ud = self._convertir_europeo(match1.group(3))
                importe = self._convertir_europeo(match1.group(4))
                
                if importe > 0 and len(descripcion) >= 3:
                    lineas.append({
                        'codigo': '',
                        'articulo': descripcion[:50],
                        'cantidad': round(cantidad, 3),
                        'precio_ud': round(precio_ud, 2),
                        'iva': seccion_actual or 10,
                        'base': round(importe / (1 + (seccion_actual or 10) / 100), 2)
                    })
                continue
            
            # Patrón 2: cantidad entera + descripción + importe
            # "1 BOQUERON ALIÑADO A.IÑAKI 310 5.99"
            match2 = re.match(
                r'^(\d+)\s+([A-ZÁÉÍÓÚÑa-záéíóúñ0-9\s\.\,\-\/\(\)]+?)\s+(\d+[.,]\d{2})$',
                linea
            )
            if match2:
                cantidad = int(match2.group(1))
                descripcion = match2.group(2).strip()
                importe = self._convertir_europeo(match2.group(3))
                
                if importe > 0 and len(descripcion) >= 3 and cantidad <= 100:
                    lineas.append({
                        'codigo': '',
                        'articulo': descripcion[:50],
                        'cantidad': cantidad,
                        'precio_ud': round(importe / cantidad, 2) if cantidad else importe,
                        'iva': seccion_actual or 10,
                        'base': round(importe / (1 + (seccion_actual or 10) / 100), 2)
                    })
                continue
            
            # Patrón 3: descripción + importe (cantidad implícita 1)
            # "JAMON DUROC HOGUERA GR CENTR 3.15"
            match3 = re.match(
                r'^([A-ZÁÉÍÓÚÑa-záéíóúñ][A-ZÁÉÍÓÚÑa-záéíóúñ0-9\s\.\,\-\/\(\)]+?)\s+(\d+[.,]\d{2})$',
                linea
            )
            if match3:
                descripcion = match3.group(1).strip()
                importe = self._convertir_europeo(match3.group(2))
                
                # Evitar líneas que son solo números o muy cortas
                if importe > 0 and len(descripcion) >= 5 and not descripcion.replace(' ', '').isdigit():
                    lineas.append({
                        'codigo': '',
                        'articulo': descripcion[:50],
                        'cantidad': 1,
                        'precio_ud': round(importe, 2),
                        'iva': seccion_actual or 10,
                        'base': round(importe / (1 + (seccion_actual or 10) / 100), 2)
                    })
                continue
        
        return lineas
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo a float."""
        if not texto:
            return 0.0
        texto = texto.strip()
        # En BM usan punto como decimal
        try:
            return float(texto.replace(',', '.'))
        except:
            return 0.0
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """Extrae total de la factura."""
        # Formato: "TOTAL COMPRA (iva incl.) 35.06"
        m = re.search(r'TOTAL COMPRA.*?(\d+[.,]\d{2})', texto, re.IGNORECASE)
        if m:
            return self._convertir_europeo(m.group(1))
        
        # Alternativa: "Total Factura XX,XX€"
        m = re.search(r'Total\s+Factura\s+(\d+[.,]\d{2})', texto, re.IGNORECASE)
        if m:
            return self._convertir_europeo(m.group(1))
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha del ticket."""
        # Formato: "24/10/25 14:13" o "06/09/25 15:08"
        m = re.search(r'(\d{2})/(\d{2})/(\d{2})\s+\d{2}:\d{2}', texto)
        if m:
            dia, mes, anio = m.group(1), m.group(2), m.group(3)
            return f"{dia}/{mes}/20{anio}"
        
        # Alternativa en datos factura: "24-10-25"
        m = re.search(r'(\d{2})-(\d{2})-(\d{2})', texto)
        if m:
            dia, mes, anio = m.group(1), m.group(2), m.group(3)
            return f"{dia}/{mes}/20{anio}"
        
        return None
