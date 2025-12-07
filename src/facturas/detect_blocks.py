# src/facturas/detect_blocks.py
from __future__ import annotations
import re
from typing import Dict, List, Optional

# Soporte pypdf / PyPDF2
_PDF_IMPORT_ERROR = None
try:
    from PyPDF2 import PdfReader
except Exception as _e1:
    try:
        from pypdf import PdfReader
    except Exception as _e2:
        PdfReader = None
        _PDF_IMPORT_ERROR = (_e1, _e2)

# nÂº europeo: 1.234,56 o 12,34
EU_MONEY_RX = re.compile(r"\b\d{1,3}(?:\.\d{3})*,\d{2}\b")

HEADER_HINTS = [
    "factura", "cliente", "proveedor", "fecha", "albarÃ¡n", "albaran",
    "nÂº", "numero", "artÃ­culo", "articulo", "descripciÃ³n", "descripcion",
    "cantidad", "precio", "total", "iva", "base imponible"
]

FOOTER_HINTS = [
    "total factura", "base imponible", "cuota iva", "importe total", "pago",
    "forma de pago", "observaciones", "vencimiento", "firma"
]

def _extract_all_lines(pdf_path: str) -> List[str]:
    if PdfReader is None:
        raise RuntimeError(
            "No se pudo importar PyPDF2/pypdf. Instala pypdf:  python -m pip install pypdf\n"
            f"Detalle: {_PDF_IMPORT_ERROR!r}"
        )
    reader = PdfReader(pdf_path)
    lines: List[str] = []
    for page in reader.pages:
        txt = page.extract_text() or ""
        for raw in txt.splitlines():
            s = " ".join(raw.split()).strip()
            if s:
                lines.append(s)
    return lines


def _looks_like_header(line: str) -> bool:
    l = line.lower()
    if any(k in l for k in HEADER_HINTS):
        if not EU_MONEY_RX.search(l):
            return True
    return False


def _looks_like_footer(line: str) -> bool:
    l = line.lower()
    if any(k in l for k in FOOTER_HINTS):
        return True
    return False


def _is_candidate_detail(line: str) -> bool:
    if not EU_MONEY_RX.search(line):
        return False
    if _looks_like_header(line) or _looks_like_footer(line):
        return False
    if line.lower().startswith("total "):
        return False
    return True


def _provider_specific_skip(line: str, provider: Optional[str]) -> bool:
    if not provider:
        return False
    l = (provider or "").upper()
    s = line.lower()

    if "CERES" in l:
        if "albar" in s or "cliente" in s or "pedido" in s:
            if not EU_MONEY_RX.search(s):
                return True
    if "FABEIRO" in l:
        if "cliente" in s or "proveedor" in s:
            if not EU_MONEY_RX.search(s):
                return True
    return False


def detect_blocks_minimal(pdf_path: str, provider: Optional[str] = None) -> Dict[str, List[str]]:
    raw_lines = _extract_all_lines(pdf_path)

    cleaned: List[str] = []
    for ln in raw_lines:
        if len(ln) < 6 and not any(ch.isdigit() for ch in ln):
            continue
        cleaned.append(ln)

    candidates: List[str] = []
    for ln in cleaned:
        if _provider_specific_skip(ln, provider):
            continue
        if _is_candidate_detail(ln):
            candidates.append(ln)

    seen = set()
    out: List[str] = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            out.append(c)

    return {"lines_text": out}

