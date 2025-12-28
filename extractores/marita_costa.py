# -*- coding: utf-8 -*-
"""
Extractor para MARITA COSTA VILELA

Distribuidora de productos gourmet
NIF: 48207369J (autonoma)
Ubicacion: Valdemoro, Madrid
Tel: 665 14 06 10

Productos típicos:
- AOVE Nobleza del Sur (4% IVA)
- Picos de Jamón Lucía (4% IVA - pan)
- Patés Lucas (10% IVA): atún, sardina
- Cookies Milola (10% IVA)
- Torreznos La Rústica (10% IVA)
- Patatas Quillo (10% IVA)

Tipos de IVA:
- 4%: Aceite de oliva virgen extra, Pan (picos de jamón)
- 10%: Alimentación general

IBAN: ES78 2100 6398 7002 0001 9653

Creado: 20/12/2025
Actualizado: 28/12/2025 - Corregido patrón para códigos con espacios y líneas multilínea
"""
# from extractores.base import ExtractorBase
# from extractores import registrar
from typing import List, Dict, Optional
import re
import pdfplumber


# @registrar('MARITA COSTA', 'MARITA', 'COSTA VILELA')
class ExtractorMaritaCosta:  # (ExtractorBase):
    """Extractor para facturas de MARITA COSTA VILELA."""
    
    nombre = 'MARITA COSTA VILELA'
    cif = '48207369J'
    iban = 'ES78 2100 6398 7002 0001 9653'
    metodo_pdf = 'pdfplumber'
    categoria_fija = 'GOURMET'
    
    def _convertir_europeo(self, texto: str) -> float:
        """Convierte formato europeo (1.234,56) a float."""
        if not texto:
            return 0.0
        texto = str(texto).strip()
        texto = texto.replace('\u20ac', '').replace('€', '')
        texto = texto.replace('EUR', '').replace('eur', '')
        texto = texto.replace(' ', '').strip()
        
        if '.' in texto and ',' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            texto = texto.replace(',', '.')
        try:
            return float(texto)
        except:
            return 0.0
    
    def _determinar_iva(self, codigo: str, descripcion: str) -> int:
        """
        Determina el IVA según el producto.
        
        IVA 4%:
        - AOVE (aceite de oliva)
        - PICOS DE JAMÓN (pan)
        
        IVA 10%:
        - Todo lo demás (patés, cookies, torreznos, patatas, etc.)
        """
        codigo_upper = codigo.upper()
        descripcion_upper = descripcion.upper()
        
        # IVA 4%: AOVE
        if 'AOVE' in codigo_upper or 'AOVE' in descripcion_upper:
            return 4
        
        # IVA 4%: Picos de jamón (pan)
        if 'PICO' in descripcion_upper and 'JAM' in descripcion_upper:
            return 4
        if codigo_upper.startswith('PQLPJ'):  # Código específico de picos
            return 4
        
        # IVA 10%: Todo lo demás
        return 10
    
    def extraer_texto(self, pdf_path: str) -> str:
        """Extrae texto del PDF."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                texto = pdf.pages[0].extract_text()
                return texto or ''
        except:
            return ''
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de producto.
        
        Formatos soportados:
        1. Código sin espacios: AOVENOV500 AOVE NOBLEZA DEL SUR NOVO 500ML 12,00 13,2000€ 158,40€ 158,40€
        2. Código con espacios: LR 010 LA RUSTICA TORREZNOS DE SORIA 200GR 10,00 3,5500€ 35,50€ 35,50€
        3. Líneas de continuación (sin código): 140G - CL180925S 8,00 3,2100€ 25,68€ 25,68€
        """
        lineas = []
        lineas_texto = texto.split('\n')
        
        # Patrón principal: buscar líneas con formato CANTIDAD PRECIO€ SUBTOTAL€ TOTAL€
        # Captura todo lo que está antes como código+descripción
        patron = re.compile(
            r'^(.+?)\s+'                     # Código + Descripción (todo junto)
            r'(\d+[,.]?\d*)\s+'              # Cantidad
            r'([\d,]+)€\s+'                  # Precio unitario
            r'([\d,]+)€\s+'                  # Subtotal
            r'([\d,]+)€$'                    # Total
        )
        
        ultimo_codigo = None
        
        for linea in lineas_texto:
            linea = linea.strip()
            
            # Ignorar líneas que no son productos
            if not linea or 'TOTAL:' in linea or 'Albarán:' in linea:
                continue
            if 'Vencimientos' in linea or 'ARTÍCULO' in linea:
                continue
            if not '€' in linea:
                continue
            
            match = patron.match(linea)
            if match:
                prefijo = match.group(1).strip()
                cantidad = self._convertir_europeo(match.group(2))
                precio = self._convertir_europeo(match.group(3))
                importe = self._convertir_europeo(match.group(5))
                
                if importe < 1.0:
                    continue
                
                # Separar código de descripción
                codigo, descripcion = self._separar_codigo_descripcion(prefijo)
                
                if not codigo:
                    # Línea de continuación - usar último código conocido
                    codigo = ultimo_codigo or 'CONT'
                    descripcion = prefijo
                else:
                    ultimo_codigo = codigo
                
                # Limpiar descripción
                descripcion = self._limpiar_descripcion(descripcion)
                
                # Determinar IVA
                iva = self._determinar_iva(codigo, descripcion)
                
                lineas.append({
                    'codigo': codigo,
                    'articulo': descripcion[:50],
                    'cantidad': int(cantidad) if cantidad == int(cantidad) else cantidad,
                    'precio_ud': precio,
                    'iva': iva,
                    'base': importe
                })
        
        return lineas
    
    def _separar_codigo_descripcion(self, prefijo: str) -> tuple:
        """
        Separa código de descripción.
        
        Casos:
        - "AOVENOV500 AOVE NOBLEZA..." → ("AOVENOV500", "AOVE NOBLEZA...")
        - "LR 010 LA RUSTICA..." → ("LR 010", "LA RUSTICA...")
        - "140G - CL180925S" → (None, "140G - CL180925S")
        """
        # Caso 1: Código con espacio (ej: "LR 010", "LB 5002")
        match_espacio = re.match(r'^([A-Z]{2,3}\s+\d{3,4})\s+(.+)$', prefijo)
        if match_espacio:
            return match_espacio.group(1), match_espacio.group(2)
        
        # Caso 2: Código normal (empieza con letras, puede tener números)
        match_normal = re.match(r'^([A-Z][A-Z0-9]{2,})\s+(.+)$', prefijo)
        if match_normal:
            codigo = match_normal.group(1)
            resto = match_normal.group(2)
            # Verificar que el código no es parte de la descripción
            if len(codigo) >= 4 and len(codigo) <= 15:
                return codigo, resto
        
        # Caso 3: Línea de continuación (empieza con número o descripción)
        if prefijo[0].isdigit() or not prefijo[0].isupper():
            return None, prefijo
        
        # Caso 4: Intentar separar por primer espacio si parece código
        partes = prefijo.split(' ', 1)
        if len(partes) == 2 and len(partes[0]) >= 4:
            return partes[0], partes[1]
        
        return None, prefijo
    
    def _limpiar_descripcion(self, desc: str) -> str:
        """Limpia la descripción de lotes y caracteres extra."""
        # Quitar lotes (formato: - XXXXXX o - L###X)
        desc = re.sub(r'\s*-\s*[A-Z0-9]+$', '', desc)
        desc = re.sub(r'\s*-\s*L\d+[A-Z]?$', '', desc)
        desc = re.sub(r'\s*-\s*\d{6}$', '', desc)
        # Normalizar espacios
        desc = ' '.join(desc.split())
        return desc
    
    def extraer_desglose_iva(self, texto: str) -> List[Dict]:
        """
        Extrae desglose de IVA del resumen.
        
        Formato:
        TIPO BASE I.V.A R.E. PRONTO PAGO DESC. I.R.P.F.
        10,00 188,34 18,83
        4,00 367,20 14,69
        """
        desglose = []
        
        # Patrón: TIPO BASE IVA
        for m in re.finditer(
            r'^(\d+)[,.](\d{2})\s+([\d,.]+)\s+([\d,.]+)\s*$',
            texto,
            re.MULTILINE
        ):
            tipo = int(m.group(1))
            base = self._convertir_europeo(m.group(3))
            iva = self._convertir_europeo(m.group(4))
            if base > 0 and tipo in [4, 10, 21]:
                desglose.append({
                    'tipo': tipo,
                    'base': base,
                    'iva': iva
                })
        
        return desglose
    
    def extraer_total(self, texto: str) -> Optional[float]:
        """
        Extrae total de la factura.
        
        Estrategia:
        1. Buscar "TOTAL:" seguido de importe
        2. Si no, calcular desde desglose IVA (más fiable)
        """
        # Método 1: Buscar total directo
        m = re.search(r'TOTAL:\s*([\d,.]+)€?', texto)
        if m:
            total = self._convertir_europeo(m.group(1))
            if total > 10:
                return total
        
        # Método 2: Calcular desde desglose IVA (más fiable)
        desglose = self.extraer_desglose_iva(texto)
        if desglose:
            return round(sum(d['base'] + d['iva'] for d in desglose), 2)
        
        return None
    
    def extraer_fecha(self, texto: str) -> Optional[str]:
        """Extrae fecha de la factura."""
        m = re.search(r'(\d{2}/\d{2}/\d{4})', texto)
        if m:
            return m.group(1)
        return None
    
    def extraer_numero_factura(self, texto: str) -> Optional[str]:
        """Extrae número de factura."""
        # Formato: "Factura 1 NUMERO 1 FECHA"
        m = re.search(r'Factura\s+\d+\s+(\d+)\s+\d+\s+\d{2}/\d{2}/\d{4}', texto)
        if m:
            return m.group(1)
        return None


# ============================================================
# CÓDIGO DE PRUEBA
# ============================================================

if __name__ == '__main__':
    import sys
    import glob
    import os
    
    extractor = ExtractorMaritaCosta()
    
    # Buscar PDFs de MARITA COSTA
    if len(sys.argv) > 1:
        pdfs = sys.argv[1:]
    else:
        pdfs = glob.glob('/mnt/user-data/uploads/*MARITA*.pdf')
    
    total_ok = 0
    total_facturas = 0
    
    for pdf_path in pdfs:
        if pdf_path.endswith('.py'):
            continue
        total_facturas += 1
        print(f"\n{'='*60}")
        print(f"ARCHIVO: {os.path.basename(pdf_path)}")
        print('='*60)
        
        texto = extractor.extraer_texto(pdf_path)
        
        if not texto:
            print("❌ Error: No se pudo extraer texto")
            continue
        
        fecha = extractor.extraer_fecha(texto)
        num_factura = extractor.extraer_numero_factura(texto)
        total = extractor.extraer_total(texto)
        lineas = extractor.extraer_lineas(texto)
        desglose = extractor.extraer_desglose_iva(texto)
        
        print(f"📅 Fecha: {fecha}")
        print(f"📄 Nº Factura: {num_factura}")
        print(f"💰 TOTAL: {total}€")
        
        if desglose:
            print(f"\n📊 CUADRO FISCAL:")
            total_calculado = 0
            for d in desglose:
                print(f"   IVA {d['tipo']}%: Base {d['base']}€ + IVA {d['iva']}€")
                total_calculado += d['base'] + d['iva']
        
        if lineas:
            print(f"\n📦 LÍNEAS ({len(lineas)}):")
            suma_bases = 0
            for i, linea in enumerate(lineas, 1):
                print(f"  {i}. [{linea['codigo']}] {linea['articulo']}")
                print(f"     {linea['cantidad']} x {linea['precio_ud']}€ = {linea['base']}€ (IVA {linea['iva']}%)")
                suma_bases += linea['base']
            
            print(f"\n   Suma líneas: {round(suma_bases, 2)}€")
            
            # Validación
            if desglose:
                suma_bases_fiscal = sum(d['base'] for d in desglose)
                diff_lineas = abs(suma_bases - suma_bases_fiscal)
                
                print(f"   Suma bases fiscal: {suma_bases_fiscal}€")
                
                if diff_lineas < 0.10:
                    print(f"   ✅ LÍNEAS CUADRAN CON CUADRO FISCAL")
                    total_ok += 1
                else:
                    print(f"   ❌ Diferencia: {diff_lineas:.2f}€")
        else:
            print("❌ No se extrajeron líneas")
    
    print(f"\n{'='*60}")
    print(f"RESUMEN: {total_ok}/{total_facturas} facturas OK")
    print('='*60)
