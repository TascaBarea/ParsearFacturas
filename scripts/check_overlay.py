# scripts/check_overlay.py
# Comprobación rápida de overlays migrados (carpeta patterns/).

from __future__ import annotations
import argparse
from pathlib import Path
import sys

# ── HACK: añadir la raíz del repo al sys.path ──────────────────────────────
# Estructura esperada:
#   <repo-root>/
#     scripts/check_overlay.py  ← este script
#     src/facturas/...
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Ahora ya podemos importar desde src.facturas.*
from src.facturas.patterns_loader import get_overlay_for
from src.facturas.detect_blocks import detect_blocks_minimal
from src.facturas.parse_lines import parse_lines_text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proveedor", help="Nombre del proveedor a buscar en patterns/")
    ap.add_argument("--pdf", help="Ruta a PDF para probar el overlay", default=None)
    args = ap.parse_args()

    if not args.proveedor and not args.pdf:
        ap.error("Debes indicar --proveedor y/o --pdf")

    if args.proveedor:
        ov = get_overlay_for(args.proveedor)
        if ov:
            print(f"Overlay encontrado para '{args.proveedor}': {ov.path}")
            print("Claves disponibles:", list(ov.data.keys()))
            if "lines" in ov.data:
                print("lines keys:", list((ov.data.get("lines") or {}).keys()))
        else:
            print(f"No hay overlay para: {args.proveedor}")

    if args.pdf:
        pdf = Path(args.pdf)
        if not pdf.exists():
            raise SystemExit(f"No existe el PDF: {pdf}")
        proveedor = args.proveedor or ""
        blocks = detect_blocks_minimal(str(pdf), provider=proveedor)
        print("\n== Detect Blocks ==")
        print("fecha_overlay:", blocks.get("fecha_overlay"))
        print("ref_overlay:", blocks.get("ref_overlay"))
        print("lines_text_len:", len(blocks.get("lines_text") or ""))
        print("full_text_len:", len(blocks.get("full_text") or ""))

        rows = parse_lines_text(blocks.get("lines_text") or "", proveedor)
        print("\n== Muestra de líneas parseadas ==")
        for r in rows[:10]:
            print(r)
        if not rows:
            print("(Sin líneas parseadas; PDF escaneado sin texto o patrón a ajustar)")


if __name__ == "__main__":
    main()
