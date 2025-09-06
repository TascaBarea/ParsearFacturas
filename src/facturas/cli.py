# src/facturas/cli.py
import argparse
import json
import os
import re
from datetime import datetime

try:
    from PyPDF2 import PdfReader  # pip install PyPDF2
except Exception:
    PdfReader = None


KNOWN_PROVIDERS = {
    "FABEIRO", "CERES", "SEGURMA", "MERCADONA", "MAKRO", "MARITA",
    # añade aquí tus proveedores habituales…
}


def _read_first_page_text(pdf_path: str) -> str:
    if PdfReader is None:
        raise RuntimeError("PyPDF2 no está instalado. Ejecuta: pip install PyPDF2")
    reader = PdfReader(pdf_path)
    if len(reader.pages) == 0:
        return ""
    txt = reader.pages[0].extract_text() or ""
    # Normaliza espacios
    txt = re.sub(r"[ \t]+", " ", txt)
    return txt


def _detect_date(text: str) -> str | None:
    """
    Detecta fechas tipo 31-07-25, 31/07/2025, 31.07.2025, etc., y normaliza a DD-MM-AA.
    """
    patterns = [
        r"\b(\d{1,2})[\/\-\.\s](\d{1,2})[\/\-\.\s](\d{2,4})\b",
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            d, mth, y = m.groups()
            d = int(d)
            mth = int(mth)
            y = int(y)
            if y > 1999:  # 2025 -> 25
                y = y % 100
            try:
                # valida fecha
                _ = datetime.strptime(f"{d:02d}-{mth:02d}-{y:02d}", "%d-%m-%y")
                return f"{d:02d}-{mth:02d}-{y:02d}"
            except ValueError:
                continue
    return None


def _detect_ref(text: str) -> str | None:
    """
    Intenta capturar Nº de factura a partir de palabras clave:
    'Factura', 'Nº', 'Num', 'Ref', 'Serie', etc.
    """
    # Busca líneas cercanas a palabras clave
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    joined = "\n".join(lines)

    # 1) Expresiones frecuentes: FACTURA 12345, Nº 2025/07/0001, Ref: FAC-123, etc.
    candidates = [
        r"(?:FACTURA|FAC\.?|N[ºo]|NUM\.?|REF\.?|REFERENCIA|SERIE)[:\s\-]*([A-Z]?[\/\-\.\w]{4,})",
        r"(?:N[ºo]\s*FACTURA)[:\s\-]*([A-Z]?[\/\-\.\w]{4,})",
    ]
    for pat in candidates:
        m = re.search(pat, joined, re.IGNORECASE)
        if m:
            ref = m.group(1).strip()
            # limpieza suave
            ref = ref.strip(" .,#;")
            return ref

    # 2) fallback: patrón con barra-fecha típico: 2025/07/029363
    m2 = re.search(r"\b(20\d{2}[/\-]\d{2}[/\-]\w{3,})\b", joined)
    if m2:
        return m2.group(1)

    return None


def _detect_provider_from_filename(path: str) -> str | None:
    base = os.path.basename(path)
    name, _ = os.path.splitext(base)
    up = re.sub(r"[^A-Z0-9]+", " ", name.upper())
    for prov in KNOWN_PROVIDERS:
        if prov in up:
            return prov
    # si tiene algo tipo ..._FABEIRO, ... FABEIRO ...
    tokens = up.split()
    # heurística: último token en mayúsculas que parece proveedor conocido (>= 5 letras)
    for tok in reversed(tokens):
        if len(tok) >= 5 and tok.isalpha():
            return tok
    return None


def _detect_provider_from_text(text: str) -> str | None:
    head = "\n".join(text.splitlines()[:8]).upper()
    for prov in KNOWN_PROVIDERS:
        if prov in head:
            return prov
    # línea en mayúsculas “dominante”
    candidates = [l.strip() for l in head.splitlines() if l.strip()]
    candidates.sort(key=len, reverse=True)
    for l in candidates:
        # heurística: muchas letras mayúsculas y pocos dígitos → probable razón social
        if sum(c.isalpha() for c in l) >= 6 and sum(c.isdigit() for c in l) <= 2:
            # limpia basura
            clean = re.sub(r"[^A-ZÁÉÍÓÚÜÑ\s\.&]", "", l).strip()
            clean = re.sub(r"\s{2,}", " ", clean)
            if len(clean) >= 5:
                return clean
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
    parser = argparse.ArgumentParser(description="Scan mínimo de cabecera de factura (Proveedor, Fecha, NºFactura).")
    parser.add_argument("pdf", help="Ruta al PDF de la factura")
    parser.add_argument("--pretty", action="store_true", help="Imprime JSON con indentación")
    args = parser.parse_args()

    if not os.path.exists(args.pdf):
        raise SystemExit(f"No existe el archivo: {args.pdf}")

    result = scan_pdf(args.pdf)
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
