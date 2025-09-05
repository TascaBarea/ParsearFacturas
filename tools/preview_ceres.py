# tools/preview_ceres.py
from pathlib import Path
import re
import sys
from typing import Optional

from pdfminer.high_level import extract_text
from ruamel.yaml import YAML

# === CONFIG ===
PATTERN_FILE = Path("patterns/CERES.yml")

def load_ceres_pattern():
    yaml = YAML(typ="safe")
    data = yaml.load(PATTERN_FILE.read_text(encoding="utf-8"))
    # extraemos lo necesario para el smoke test
    def _regex_of(anchor_name: str) -> Optional[str]:
        anchors = data.get("anchors", {})
        a = anchors.get(anchor_name, {})
        return a.get("regex")

    return {
        "proveedor": data.get("proveedor"),
        "aliases": data.get("aliases"),
        "rx_fecha": _regex_of("fecha"),
        "rx_num": _regex_of("numero_factura"),
        "lineas_find": data.get("anchors", {}).get("lineas", {}).get("find", []),
    }

def find_first(regex: str, text: str) -> Optional[str]:
    if not regex:
        return None
    m = re.search(regex, text, flags=re.IGNORECASE)
    return m.group(0) if m else None

def contains_all(tokens, text: str) -> bool:
    return all((t.lower() in text.lower()) for t in tokens)

def preview_pdf(pdf_path: Path, cfg: dict):
    txt = extract_text(str(pdf_path)) or ""
    # compactar espacios múltiples
    text = re.sub(r"[ \t]+", " ", txt)

    fecha = find_first(cfg["rx_fecha"], text)
    num = find_first(cfg["rx_num"], text)
    has_lineas = contains_all(cfg["lineas_find"], text) if cfg["lineas_find"] else False

    print(f"\n📄 {pdf_path.name}")
    print(f"  Proveedor patrón: {cfg['proveedor']}  (aliases: {cfg['aliases']})")
    print(f"  Fecha encontrada: {fecha!r}")
    print(f"  Nº factura:       {num!r}")
    print(f"  Sección líneas:   {'SÍ' if has_lineas else 'NO'}")
    # muestra un trocito de texto alrededor de “Artículo/Descripción/Importe” si existe
    if has_lineas:
        idx = text.lower().find(cfg["lineas_find"][0].lower())
        snippet = text[max(0, idx-120): idx+120] if idx >= 0 else ""
        print("  Contexto líneas:  " + snippet.replace("\n", " ")[:240])

def main():
    if len(sys.argv) < 2:
        print("Uso: python tools/preview_ceres.py <carpeta_o_pdf1> [pdf2 ...]")
        sys.exit(1)

    cfg = load_ceres_pattern()
    for arg in sys.argv[1:]:
        p = Path(arg)
        if p.is_dir():
            for pdf in sorted(p.glob("*CERES*.pdf")):
                preview_pdf(pdf, cfg)
        elif p.is_file() and p.suffix.lower() == ".pdf":
            preview_pdf(p, cfg)
        else:
            print(f"(ignorado) {p}")

if __name__ == "__main__":
    main()
