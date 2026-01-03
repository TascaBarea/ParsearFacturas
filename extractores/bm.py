"""
Extractor para BM SUPERMERCADOS (DISTRIBUCION SUPERMERCADOS, SL).
CIF: B20099586 | Método pago: Tarjeta (no SEPA)

Tickets de supermercado con IVA mixto (4%, 10%, 21%).
El IVA no viene por línea - se deduce de:
1. Reglas específicas por producto (OLIVA→4%, GIRASOL→10%, etc.)
2. Sección del ticket (FRUTERÍA, CARNICERÍA, etc.)
3. Diccionario de productos
4. Validación final con cuadro fiscal

IMPORTANTE: Los importes de líneas INCLUYEN IVA.
Se convierten a BASE dividiendo por (1 + tipo/100).

Reglas IVA España 2024-2025:
- ACEITE OLIVA → 4% (superreducido)
- ACEITE GIRASOL → 10%
- AZUCAR → 10%
- HUEVOS, LECHE, YOGUR, QUESO, PAN, PASTA, ARROZ → 4%
- FRUTAS, VERDURAS → 4%
- CARNES, PESCADOS → 10%
- DROGUERÍA, MENAJE → 21%
- BOLSAS → 21%

Creado: 01/01/2026
Corregido: 01/01/2026 - Bug regex TOTAL COMPRA
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict, Optional, Tuple
import re
import pandas as pd
from pathlib import Path


@registrar('BM SUPERMERCADOS', 'BM', 'DISTRIBUCION SUPERMERCADOS', 'SUPERMERCADOS BM')
class ExtractorBM(ExtractorBase):
    """Extractor para tickets de BM SUPERMERCADOS."""
    
    nombre = 'BM SUPERMERCADOS'
    cif = 'B20099586'
    iban = None  # No aplica - pago con tarjeta
    metodo_pdf = 'pdfplumber'
    
    # Diccionario de productos (se carga una vez)
    _diccionario = None
    
    def __init__(self):
        """Inicializa el extractor y carga el diccionario."""
        super().__init__()
        self._cargar_diccionario()
    
    def _cargar_diccionario(self):
        """Carga el diccionario de productos BM."""
        if ExtractorBM._diccionario is not None:
            return
        
        posibles_rutas = [
            Path('DiccionarioProveedoresCategoria.xlsx'),
            Path('../DiccionarioProveedoresCategoria.xlsx'),
            Path('data/DiccionarioProveedoresCategoria.xlsx'),
        ]
        
        for ruta in posibles_rutas:
            if ruta.exists():
                try:
                    df = pd.read_excel(ruta, sheet_name='Articulos')
                    bm_df = df[df['PROVEEDOR'].str.contains('BM', case=False, na=False)]
                    ExtractorBM._diccionario = {}
                    for _, row in bm_df.iterrows():
                        art = str(row['ARTICULO']).strip().upper()
                        ExtractorBM._diccionario[art] = {
                            'iva': int(row['TIPO_IVA']) if pd.notna(row['TIPO_IVA']) else 10,
                            'categoria': str(row['CATEGORIA']) if pd.notna(row['CATEGORIA']) else 'SIN CATEGORÍA'
                        }
                    return
                except Exception:
                    pass
        
        ExtractorBM._diccionario = {}
    
    def _convertir_importe(self, texto: str) -> float:
        """Convierte texto a float (formato europeo)."""
        if not texto:
            return 0.0
        texto = str(texto).strip().replace('€', '').replace(' ', '')
        if ',' in texto and '.' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            texto = texto.replace(',', '.')
        try:
            return float(texto)
        except:
            return 0.0
    
    def _determinar_iva(self, producto: str, seccion: str) -> Tuple[int, str]:
        """
        Determina IVA y categoría según reglas españolas 2024-2025.
        PRIORIDAD: Reglas producto > Sección > Diccionario > Default
        """
        producto_upper = producto.upper()
        seccion_upper = seccion.upper().replace('Í', 'I').replace('Ó', 'O')
        
        # === REGLAS ESPECÍFICAS POR PRODUCTO ===
        
        # BOLSA siempre 21%
        if 'BOLSA' in producto_upper:
            return 21, 'BOLSAS'
        
        # ACEITE DE OLIVA → 4% (superreducido)
        if 'OLIVA' in producto_upper and ('ACT' in producto_upper or 'ACEITE' in producto_upper):
            return 4, 'ACEITE DE OLIVA'
        
        # ACEITE DE GIRASOL/OTROS → 10%
        if 'GIRASOL' in producto_upper:
            return 10, 'ACEITE DE GIRASOL'
        
        # Productos básicos IVA 4%
        KEYWORDS_4 = ['HUEVO', 'LECHE ', 'YOGUR', 'QUESO', 'PAN ', 'HARINA', 
                      'PASTA', 'ARROZ', 'PATATA', 'ZANAHORIA', 'CANONIGO',
                      'FRUTA', 'VERDURA', 'LEGUMBRE']
        for kw in KEYWORDS_4:
            if kw in producto_upper:
                return 4, 'ALIMENTACIÓN BÁSICA'
        
        # === REGLAS POR SECCIÓN ===
        if 'DROG' in seccion_upper or 'PERFUM' in seccion_upper:
            return 21, 'DROGUERÍA'
        elif 'HOGAR' in seccion_upper or 'MENAJE' in seccion_upper:
            return 21, 'MENAJE'
        elif 'FRUTER' in seccion_upper:
            return 4, 'FRUTAS Y VERDURAS'
        elif 'CARNIC' in seccion_upper or 'CHARCUTER' in seccion_upper:
            return 10, 'CARNICERÍA'
        elif 'PESCAD' in seccion_upper:
            return 10, 'PESCADERÍA'
        
        # === DICCIONARIO ===
        if ExtractorBM._diccionario:
            if producto_upper in ExtractorBM._diccionario:
                d = ExtractorBM._diccionario[producto_upper]
                return d['iva'], d['categoria']
            
            # Fuzzy match
            for art, data in ExtractorBM._diccionario.items():
                if len(producto_upper) >= 5:
                    if (producto_upper.startswith(art[:min(len(art), len(producto_upper)-2)]) or 
                        art.startswith(producto_upper[:min(len(producto_upper), len(art)-2)])):
                        return data['iva'], data['categoria']
        
        # Default alimentación
        return 10, 'ALIMENTACIÓN'
    
    def extraer_cuadro_fiscal(self, texto: str) -> List[Dict]:
        """Extrae el cuadro fiscal del ticket."""
        desglose = []
        for m in re.finditer(r'(\d+)[.,](\d+)%\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)', texto):
            tipo_ent, tipo_dec, base, iva, req, total = m.groups()
            desglose.append({
                'tipo': int(tipo_ent),
                'base': self._convertir_importe(base),
                'iva': self._convertir_importe(iva),
                'total': self._convertir_importe(total)
            })
        return desglose
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """Extrae líneas de producto del ticket."""
        lineas = []
        seccion_actual = 'ALIMENTACIÓN'
        texto_lineas = texto.split('\n')
        
        # Palabras a ignorar
        skip_words = ['TOTAL', 'TARJETA', 'EFECTIVO', 'CAMBIO', 'TICKET', 'AHORRO', 'PUNTO', 
                      'CUENTA BM', 'Tipo', 'Base', '---', '***', 'CIF:', 'FACTURA', 'atendió',
                      'devolución', 'Le atendió', 'COPIA PARA', 'APP ', 'ENTREGADO', 'POR COMPRAR', 
                      'ACUMULADO', 'conseguido', 'NUMERO DE', 'Cliente', 'NIF', 'Nombre', 
                      'Domicilio', 'Población', 'Teléfono', 'atención', 'GRACIAS', 'DUQUE DE ALBA', 
                      'JAIME', 'UD/KG', 'Vencimientos', 'SEC/', 'COMERCIO', 'TITULAR', 'ARC',
                      'AID', 'APLICACION', 'VALIDACION', 'OPER', 'IMPORTE', 'N.SEC']
        
        i = 0
        while i < len(texto_lineas):
            linea = texto_lineas[i].strip()
            
            # Cambio de sección
            if linea.startswith('- ') and linea.endswith(' -'):
                seccion_actual = linea.strip('- ').strip()
                i += 1
                continue
            
            # Promoción/descuento → aplicar al artículo anterior
            if 'Promoción' in linea or 'Promocion' in linea:
                m_promo = re.search(r'(-?[\d.,]+)$', linea)
                if m_promo and lineas:
                    descuento = self._convertir_importe(m_promo.group(1))
                    lineas[-1]['importe_iva_inc'] = round(lineas[-1]['importe_iva_inc'] + descuento, 2)
                i += 1
                continue
            
            # Ignorar líneas no relevantes
            if any(x in linea for x in skip_words):
                i += 1
                continue
            
            # Patrón granel: CANT DESC PRECIO_UD IMPORTE
            m_granel = re.match(r'^([\d.,]+)\s+(.+?)\s+([\d.,]+)\s+([\d.,]+)$', linea)
            if m_granel:
                cant, desc, precio_ud, importe = m_granel.groups()
                cantidad = self._convertir_importe(cant)
                importe_con_iva = self._convertir_importe(importe)
                
                if importe_con_iva > 0 and len(desc) > 2 and '%' not in desc:
                    iva, categoria = self._determinar_iva(desc, seccion_actual)
                    lineas.append({
                        'articulo': desc.strip()[:50],
                        'cantidad': cantidad,
                        'precio_ud': self._convertir_importe(precio_ud),
                        'iva': iva,
                        'importe_iva_inc': importe_con_iva,
                        'categoria': categoria
                    })
                i += 1
                continue
            
            # Patrón normal: CANT DESC IMPORTE
            m_normal = re.match(r'^(\d+)\s+(.+?)\s+([\d.,]+)$', linea)
            if m_normal:
                cant, desc, importe = m_normal.groups()
                cantidad = int(cant)
                importe_con_iva = self._convertir_importe(importe)
                
                if '%' not in desc and importe_con_iva > 0 and len(desc) > 2:
                    desc = re.sub(r'\s*\*\s*$', '', desc).strip()
                    iva, categoria = self._determinar_iva(desc, seccion_actual)
                    lineas.append({
                        'articulo': desc[:50],
                        'cantidad': cantidad,
                        'precio_ud': round(importe_con_iva / cantidad, 2) if cantidad > 0 else importe_con_iva,
                        'iva': iva,
                        'importe_iva_inc': importe_con_iva,
                        'categoria': categoria
                    })
                i += 1
                continue
            
            # Patrón sin cantidad: DESC IMPORTE (una sola unidad)
            m_simple = re.match(r'^([A-Za-zÁÉÍÓÚÑáéíóúñ\s\-]+?)\s+(\d+[.,]\d{2})$', linea)
            if m_simple:
                desc, importe = m_simple.groups()
                importe_con_iva = self._convertir_importe(importe)
                
                if importe_con_iva > 0 and len(desc.strip()) > 2:
                    iva, categoria = self._determinar_iva(desc, seccion_actual)
                    lineas.append({
                        'articulo': desc.strip()[:50],
                        'cantidad': 1,
                        'precio_ud': importe_con_iva,
                        'iva': iva,
                        'importe_iva_inc': importe_con_iva,
                        'categoria': categoria
                    })
                i += 1
                continue
            
            i += 1
        
        # Convertir importes (IVA incluido) a bases (sin IVA)
        for l in lineas:
            factor = 1 + l['iva'] / 100
            l['base'] = round(l['importe_iva_inc'] / factor, 2)
        
        return lineas
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """Extrae total del ticket."""
        # CORREGIDO: Buscar número después de "TOTAL COMPRA" evitando capturar puntos sueltos
        # Patrón: "TOTAL COMPRA" seguido de cualquier cosa no-dígito, luego un número con decimales
        m = re.search(r'TOTAL COMPRA[^\d]*(\d+[.,]\d{2})', texto)
        if m:
            return self._convertir_importe(m.group(1))
        
        # Alternativa: buscar "TOTAL COMPRA (iva incl.)" específicamente
        m2 = re.search(r'TOTAL COMPRA \(iva incl\.\)\s*(\d+[.,]\d{2})', texto)
        if m2:
            return self._convertir_importe(m2.group(1))
        
        # Alternativa: suma del cuadro fiscal
        cuadro = self.extraer_cuadro_fiscal(texto)
        if cuadro:
            return round(sum(d['total'] for d in cuadro), 2)
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha del ticket en formato DD-MM-YY."""
        m = re.search(r'(\d{2})[/-](\d{2})[/-](\d{2})\s', texto)
        if m:
            dia, mes, año = m.groups()
            return f"{dia}-{mes}-{año}"
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae número de factura."""
        m = re.search(r'Datos FACTURA:\s*(\S+)', texto)
        if m:
            return m.group(1)
        m2 = re.search(r'FACTURA SIMPLIFICADA:\s*(\S+)', texto)
        if m2:
            return m2.group(1)
        return None
    
    # Alias
    extraer_referencia = extraer_numero_factura
