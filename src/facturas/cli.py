# src/facturas/cli.py
import argparse
import json
import os
import re
import unicodedata
from datetime import datetime
from typing import Optional

# ───────────────────────── PDF reader (PyPDF2 / pypdf) ─────────────────────────
_PDF_IMPORT_ERROR = None
try:
    from PyPDF2 import PdfReader
except Exception as _e1:
    try:
        from pypdf import PdfReader
    except Exception as _e2:
        PdfReader = None
        _PDF_IMPORT_ERROR = (_e1, _e2)

# ─────────────────────────── Módulos del proyecto ────────────────────────────
from facturas.detect_blocks import detect_blocks_minimal
from facturas.parse_lines import parse_lines_text
from facturas.iva_logic import detect_iva_tipo
from facturas.portes_logic import detectar_lineas_portes
from facturas.reconcile import reconciliar_totales, detectar_total_con_iva
from facturas.export.excel import exportar_a_excel
import pandas as pd

# ───────────────────────────── Utilidades comunes ─────────────────────────────
def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def _normalize_token(s: str) -> str:
    up = _strip_accents(s.upper())
    return re.sub(r"[^A-Z0-9 ]+", " ", up).strip()

KNOWN_PROVIDERS = {
    "FABEIRO", "CERES", "SEGURMA", "MERCADONA", "MAKRO", "MARITA", "LICORES MADRUENO", "MADRUENO"
}

PROVIDER_PRETTY = {
    "LICORES MADRUENO": "LICORES MADRUEÑO",
    "MADRUENO": "LICORES MADRUEÑO",
}

# ───────────────────────────── Detección cabecera ─────────────────────────────
def _read_first_page_text(pdf_path: str) -> str:
    if PdfReader is None:
        raise RuntimeError("No se pudo importar el lector PDF (PyPDF2/pypdf).\n"
                           "Instala pypdf (recomendado):  python -m pip install pypdf\n"
                           f"Detalle: {_PDF_IMPORT_ERROR!r}")
    reader = PdfReader(pdf_path)
    if len(reader.pages) == 0:
        return ""
    txt = reader.pages[0].extract_text() or ""
    return re.sub(r"[ \t]+", " ", txt)

def _detect_date(text: str) -> Optional[str]:
    patterns = [r"\b(\d{1,2})[\/\-\.\s](\d{1,2})[\/\-\.\s](\d{2,4})\b"]
    for pat in patterns:
        m = re.search(pat, text)
        if not m:
            continue
        d, mth, y = m.groups()
        try:
            d_i, m_i, y_i = int(d), int(mth), int(y)
            if y_i > 1999:
                y_i = y_i % 100
            _ = datetime.strptime(f"{d_i:02d}-{m_i:02d}-{y_i:02d}", "%d-%m-%y")
            return f"{d_i:02d}-{m_i:02d}-{y_i:02d}"
        except Exception:
            continue
    return None

def _detect_ref(text: str) -> Optional[str]:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    joined = "\n".join(lines)
    patterns = [
        r"(?:FACTURA(?:\s*N[ºO]|\s*NUM\.?)?|N[ºO]\s*FACTURA|NUM\.?\s*FACTURA|REF\.?|REFERENCIA|SERIE)[:\s\-]*([A-Z0-9][A-Z0-9\/\-\.\_]{3,})",
        r"\b(20\d{2}[/\-]\d{2}[/\-][A-Z0-9\-]{3,})\b",
    ]
    for pat in patterns:
        m = re.search(pat, joined, re.IGNORECASE)
        if m:
            ref = m.group(1).strip(" .,#;")
            if len(ref) < 4 and not any(ch.isdigit() for ch in ref):
                continue
            return ref
    return None

def _pretty_provider(norm: str) -> str:
    return PROVIDER_PRETTY.get(norm, norm)

def _detect_provider_from_filename(path: str) -> Optional[str]:
    base = os.path.basename(path)
    name, _ = os.path.splitext(base)
    norm = _normalize_token(name)
    for prov in KNOWN_PROVIDERS:
        if prov in norm:
            return _pretty_provider(prov)
    tokens = norm.split()
    for tok in reversed(tokens):
        if len(tok) >= 5 and tok.isalpha():
            return _pretty_provider(tok)
    return None

def _detect_provider_from_text(text: str) -> Optional[str]:
    head = "\n".join(text.splitlines()[:10])
    norm = _normalize_token(head)
    for prov in KNOWN_PROVIDERS:
        if prov in norm:
            return _pretty_provider(prov)
    candidates = [l.strip() for l in norm.splitlines() if l.strip()]
    candidates.sort(key=len, reverse=True)
    for l in candidates:
        if sum(c.isalpha() for c in l) >= 6 and sum(c.isdigit() for c in l) <= 2:
            return _pretty_provider(l)
    return None

def _first_4_digits_from_filename(path: str) -> str:
    base = os.path.basename(path)
    m = re.search(r"\b(\d{3,4})\b", base)
    return m.group(1) if m else ""

def scan_pdf(pdf_path: str) -> dict:
    txt = _read_first_page_text(pdf_path)
    proveedor = _detect_provider_from_filename(pdf_path) or _detect_provider_from_text(txt) or ""
    fecha = _detect_date(txt) or ""
    ref = _detect_ref(txt) or ""
    return {
        "Archivo": os.path.basename(pdf_path),
        "NumeroArchivo": _first_4_digits_from_filename(pdf_path),
        "Proveedor": proveedor,
        "Fecha": fecha,
        "NºFactura": ref,
    }

def main():
    parser = argparse.ArgumentParser(description="Scan de cabecera y (opcional) líneas de factura.")
    parser.add_argument("pdf", help="Ruta al PDF de la factura")
    parser.add_argument("--lines", action="store_true", help="Incluir también líneas de producto")
    parser.add_argument("--pretty", action="store_true", help="Imprime JSON con indentación")
    parser.add_argument("--keep-portes", action="store_true", help="No elimina líneas de portes")
    parser.add_argument("--excel", help="Ruta del Excel de salida")
    parser.add_argument("--outdir", help="Carpeta de salida para Excel")
    args = parser.parse_args()

    if not os.path.exists(args.pdf):
        raise SystemExit(f"No existe el archivo: {args.pdf}")

    header = scan_pdf(args.pdf)

    if args.lines:
        blocks = detect_blocks_minimal(args.pdf, provider=header.get("Proveedor"))
        rows = parse_lines_text(blocks["lines_text"])

        descripciones = [r.get("Descripcion", "") for r in rows]
        portes_idx = detectar_lineas_portes(descripciones)

        for i, r in enumerate(rows):
            r["EsPortes"] = i in portes_idx

        if portes_idx and not args.keep_portes:
            rows = [r for r in rows if not r.get("EsPortes")]

        for r in rows:
            tipo = detect_iva_tipo(r.get("Descripcion", ""), header.get("Proveedor", ""), header.get("Fecha", ""))
            r["TipoIVA"] = tipo

        total_con_iva = detectar_total_con_iva(blocks["lines_text"])
        if not total_con_iva:
            total_con_iva = input("Introduce el total con IVA (formato 123,45): ").strip()

        bases = [r.get("BaseImponible", "") for r in rows]
        ivas = [r.get("TipoIVA", 0) or 0 for r in rows]
        bases_ajustadas, estado = reconciliar_totales(bases, total_con_iva, ivas)
        for i, b in enumerate(bases_ajustadas):
            rows[i]["BaseImponible"] = b
        for r in rows:
            if "Categoria" not in r:
                r["Categoria"] = "REVISAR"

        result = {"Header": header, "Lineas": rows, "Reconciliacion": estado}

        if args.excel or args.outdir:
            if args.excel:
                xlsx_path = args.excel
            else:
                prov = (header.get("Proveedor") or "PROVEEDOR").upper().replace(" ", "_")
                ref = header.get("NºFactura") or header.get("NumeroArchivo") or "SINREF"
                base = f"factura_{prov}_{ref}.xlsx"
                outdir = args.outdir or "."
                os.makedirs(outdir, exist_ok=True)
                xlsx_path = os.path.join(outdir, base)

            metadata = {
                "Archivo": header.get("Archivo", ""),
                "Proveedor": header.get("Proveedor", ""),
                "Fecha": header.get("Fecha", ""),
                "NºFactura": header.get("NºFactura", ""),
                "Lineas": len(rows),
                "Reconciliacion": estado,
            }

            exportar_a_excel(
                pd.DataFrame(rows),
                xlsx_path,
                metadata=metadata,
                include_es_portes=args.keep_portes
            )

            result["Excel"] = xlsx_path

    else:
        result = header

    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
