"""
Extractor para BERZAL HERMANOS S.A.

Proveedor de jamones y embutidos.
CIF: A78490182
IBAN: ES75 0049 1500 0520 1004 9174

Formato factura:
- Tabla con CODIGO (6 dígitos), CONCEPTO, IVA, IMPORTE
- IVA puede ser 4%, 10% o 21%

Creado: 18/12/2025
Migrado de: migracion_historico_2025_v3_57.py (líneas 2208-2274)
"""
from extractores.base import ExtractorBase
from extractores import registrar
from typing import List, Dict
import re


@registrar('BERZAL', 'BERZAL HERMANOS')
class ExtractorBerzal(ExtractorBase):
    """Extractor para facturas de BERZAL HERMANOS S.A."""
    
    nombre = 'BERZAL HERMANOS'
    cif = 'A78490182'
    iban = 'ES75 0049 1500 0520 1004 9174'
    metodo_pdf = 'pypdf'  # Funciona con ambos
    
    def extraer_lineas(self, texto: str) -> List[Dict]:
        """
        Extrae líneas de facturas BERZAL.
        
        Soporta dos formatos:
        - pypdf: puede tener espacios internos en números
        - pdfplumber: formato más limpio con U/K al final
        """
        lineas = []
        
        # Preprocesar: eliminar UN espacio entre dígitos
        # "1 0" -> "10", "1 8,90" -> "18,90"
        texto_limpio = re.sub(r'(\d) (\d)', r'\1\2', texto)
        texto_limpio = re.sub(r'(\d) ([,\.])', r'\1\2', texto_limpio)
        texto_limpio = re.sub(r'([,\.]) (\d)', r'\1\2', texto_limpio)
        
        # Patrón 1: pdfplumber - CODIGO ... U/K IVA IMPORTE (al final de línea)
        patron_pdfplumber = re.compile(
            r'^(\d{6})\s+'                    # Código 6 dígitos
            r'(.+?)\s+'                        # Concepto (lazy)
            r'[UK]\s+'                         # Unidad (U o K)
            r'(\d{1,2})\s+'                    # IVA (10, 21, 4)
            r'(\d{1,4}[,\.]\d{2})$',           # Importe (final de línea)
            re.MULTILINE
        )
        
        # Patrón 2: pypdf - CODIGO CONCEPTO IVA IMPORTE
        patron_pypdf = re.compile(
            r'^(\d{6})\s+'                    # Código 6 dígitos
            r'(.+?)\s+'                        # Concepto (lazy)
            r'(\d{1,2})\s+'                    # IVA (10, 21, 4)
            r'(\d{1,4}[,\.]\d{2})',            # Importe
            re.MULTILINE
        )
        
        # Intentar primero con pdfplumber (más específico)
        for match in patron_pdfplumber.finditer(texto):
            codigo, concepto_raw, iva, importe = match.groups()
            concepto = concepto_raw.strip()
            
            # Limpiar concepto si tiene números extra
            match_fin = re.search(r'\s+\d+[.,]\d+\s+\d+', concepto)
            if match_fin:
                concepto = concepto[:match_fin.start()].strip()
            
            lineas.append({
                'codigo': codigo,
                'articulo': concepto,
                'iva': int(iva),
                'base': self._convertir_importe(importe)
            })
        
        # Si no encontró nada, intentar con pypdf
        if not lineas:
            for match in patron_pypdf.finditer(texto_limpio):
                codigo, concepto, iva, importe = match.groups()
                lineas.append({
                    'codigo': codigo,
                    'articulo': concepto.strip(),
                    'iva': int(iva),
                    'base': self._convertir_importe(importe)
                })
        
        return lineas
