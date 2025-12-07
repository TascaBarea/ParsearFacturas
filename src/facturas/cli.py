# -*- coding: utf-8 -*-
"""
CLI para procesar facturas (no interactiva):
- NUNCA pide datos por consola.
- Si no hay total detectado y no se pasa --total, no reconcilia y marca estado.
- Mantiene el flujo: detectar cabecera, líneas, IVA por línea, portes y exportar a Excel.

Ejecución típica:
    python -m src.facturas.cli "ruta\a\factura.pdf" --pretty
    python -m src.facturas.cli "ruta\a\factura.pdf" --lines --excel out\factura.xlsx --outdir out
    python -m src.facturas.cli "ruta\a\factura.pdf" --lines --reconcile --total 293,15
"""
from __future__ import annotations

import argparse
import json
import os
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

# --- Lector PDF (PyPDF2 / pypdf) ---
_PDF_IMPORT_ERROR = None
try:
    from PyPDF2 import PdfReader  # type: ignore
except Exception as _e1:  # pragma: no cover
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception as _e2:  # pragma: no cover
        PdfReader = None  # type: ignore
        _PDF_IMPORT_ERROR = (_e1, _e2)

# --- Módulos del proyecto (imports relativos) ---
try:
    from .detect_blocks import detect_blocks_minimal  # type: ignore
except Exception:  # pragma: no cover
    detect_blocks_minimal = None  # type: ignore

try:
    from .parse_lines import parse_lines_text  # type: ignore
except Exception:  # pragma: no cover
    parse_lines_text = None  # type: ignore

try:
    from .iva_logic import detect_iva_tipo  # type: ignore
except Exception:  # pragma: no cover
    def detect_iva_tipo(descripcion: str, proveedor: str = "", fecha: str = "") -> int:
        return 21

try:
    from .portes_logic import detectar_lineas_portes  # type: ignore
except Exception:  # pragma: no cover
    def detectar_lineas_portes(descripciones: List[str]) -> List[int]:
        idx = []
        for i, d in enumerate(descripciones):
            if isinstance(d, str) and ("PORTE" in d.upper() or "TRANSP" in d.upper()):
                idx.append(i)
        return idx

try:
    from .reconcile import reconciliar_totales, detectar_total_con_iva  # type: ignore
except Exception:  # pragma: no cover
    def detectar_total_con_iva(texto: str) -> str:
        # heurística mínima
        m = re.search(r"(\d{1,3}(?:\.\d{3})*,\d{2})\b", texto)
        return m.group(1) if m else ""
    def reconciliar_totales(bases: List[str], total_con_iva: str, ivas: List[int]):
        return bases, "NO_RECONCILE"

try:
    from .export.excel import exportar_a_excel  # type: ignore
except Exception:  # pragma: no cover
    exportar_a_excel = None  # type: ignore

try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None  # type: ignore


# ===================== utilidades =====================

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


def _read_first_page_text(pdf_path: str) -> str:
    if PdfReader is None:
        raise RuntimeError(
            "No se pudo importar el lector PDF (PyPDF2/pypdf).\n"
            "Instala pypdf (recomendado):  python -m pip install pypdf\n"
            f"Detalle: {_PDF_IMPORT_ERROR!r}"
        )
    reader = PdfReader(pdf_path)
    if len(reader.pages) == 0:
        return ""
    txt = reader.pages[0].extract_text() or ""
    return re.sub(r"[ \t]+", " ", txt)


def _detect_date(text: str) -> Optional[str]:
    # Guion al final del conjunto: [-/.\s] o [./\s-] para evitar rangos
    patterns = [
        r"\b(\d{1,2})[-/.\s](\d{1,2})[-/.\s](\d{2,4})\b",  # DD/MM/YY(YY), DD-MM-YY, etc.
        r"\b(\d{4})[-/.\s](\d{1,2})[-/.\s](\d{1,2})\b",    # ISO: YYYY-MM-DD
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if not m:
            continue
        g1, g2, g3 = m.groups()
        try:
            # soporta tanto DD/MM/YY como YYYY/MM/DD
            if len(g1) == 4:  # ISO
                y_i, m_i, d_i = int(g1), int(g2), int(g3)
            else:
                d_i, m_i, y_i = int(g1), int(g2), int(g3)
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
        r"(?:FACTURA(?:\s*N[º°oO]|\s*NUM\.? )?|N[º°oO]\s*FACTURA|NUM\.?\s*FACTURA|REF\.?|REFERENCIA|SERIE)[:\s\-]*([A-Z0-9][A-Z0-9\/\-\.\_]{3,})",
        r"\b(20\d{2}[\/\-]\d{2}[\/\-][A-Z0-9\-]{3,})\b",
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


# ===================== CLI =====================

def main():
    parser = argparse.ArgumentParser(description="Scan de cabecera y (opcional) líneas de factura.")
    parser.add_argument("pdf", help="Ruta al PDF/JPG de la factura")
    parser.add_argument("--lines", action="store_true", help="Incluir también líneas de producto")
    parser.add_argument("--pretty", action="store_true", help="Imprime JSON legible")
    parser.add_argument("--keep-portes", action="store_true", help="No elimina líneas de portes")
    parser.add_argument("--excel", help="Ruta del Excel de salida")
    parser.add_argument("--outdir", help="Carpeta de salida para Excel")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--reconcile", action="store_true", help="Intentar cuadrar si hay total detectado o se pasa con --total")
    group.add_argument("--no-reconcile", action="store_true", help="No reconciliar aunque haya total")

    parser.add_argument("--total", help="Total con IVA (coma o punto). Si falta, no se reconcilia")

    args = parser.parse_args()

    if not os.path.exists(args.pdf):
        raise SystemExit(f"No existe el archivo: {args.pdf}")

    header = scan_pdf(args.pdf)

    result: Dict[str, Any]

    if args.lines:
        # 1) Bloques y líneas
        if detect_blocks_minimal is None:
            raise SystemExit("detect_blocks_minimal no disponible en este entorno")
        blocks = detect_blocks_minimal(args.pdf, provider=header.get("Proveedor"))
        lines_text = blocks["lines_text"]
        rows = parse_lines_text(lines_text) if parse_lines_text else []  # list[dict]

        # 2) Marcar portes y filtrar si procede
        descripciones = [r.get("Descripcion", "") for r in rows]
        portes_idx = detectar_lineas_portes(descripciones)
        for i, r in enumerate(rows):
            r["EsPortes"] = i in portes_idx
        if portes_idx and not args.keep_portes:
            rows = [r for r in rows if not r.get("EsPortes")]

        # 3) Tipo de IVA por línea
        for r in rows:
            tipo = detect_iva_tipo(r.get("Descripcion", ""), header.get("Proveedor", ""), header.get("Fecha", ""))
            r["TipoIVA"] = tipo

        # 4) Reconciliación NO interactiva
        estado = "NO_RECONCILE"
        total_cli = (args.total or "").strip()
        total_detectado = detectar_total_con_iva(blocks.get("full_text") or lines_text or "") if detectar_total_con_iva else ""
        total_con_iva = total_cli or total_detectado

        if args.reconcile and not args.no_reconcile:
            if total_con_iva:
                bases = [r.get("BaseImponible", "") for r in rows]
                ivas = [r.get("TipoIVA", 0) or 0 for r in rows]
                bases_ajustadas, estado = reconciliar_totales(bases, total_con_iva, ivas)
                for i, b in enumerate(bases_ajustadas):
                    rows[i]["BaseImponible"] = b
            else:
                estado = "NO_RECONCILE_MISSING_TOTAL"

        # 5) Categoría por defecto si falta
        for r in rows:
            if "Categoria" not in r:
                r["Categoria"] = "REVISAR"

        result = {"Header": header, "Lineas": rows, "Reconciliacion": estado}

        # 6) Export a Excel
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

            if exportar_a_excel and pd is not None:
                exportar_a_excel(pd.DataFrame(rows), xlsx_path, metadata=metadata, include_es_portes=args.keep_portes)  # type: ignore
            elif pd is not None:
                pd.DataFrame(rows).to_excel(xlsx_path, index=False)
            else:
                raise SystemExit("No hay exportador Excel disponible (falta pandas)")

        # añade ruta Excel si existe
        if args.excel or args.outdir:
            result["Excel"] = xlsx_path

    else:
        result = header  # solo cabecera

    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()





