import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader

def main():
    if len(sys.argv) < 2:
        print("USO: python ver_texto_factura.py RUTA_PDF")
        sys.exit(1)
    
    ruta = Path(sys.argv[1])
    if not ruta.exists():
        print("Archivo no encontrado:", ruta)
        sys.exit(1)
    
    reader = PdfReader(str(ruta))
    texto = ""
    for page in reader.pages:
        texto += page.extract_text() or ""
    
    print("=" * 70)
    print("TEXTO EXTRAIDO DE:", ruta.name)
    print("=" * 70)
    print(texto)
    print("=" * 70)

if __name__ == '__main__':
    main()
