# ---------- main.py ----------
"""
Punto de entrada simple para ejecutar el CLI del paquete sin recordar el -m.
Uso:
    python main.py "C:\\ruta\\a\\factura.pdf" --lines --outdir out --pretty
"""

import sys, os

# Añadimos la carpeta src al sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from facturas.cli import main as cli_main

if __name__ == "__main__":
    cli_main()

