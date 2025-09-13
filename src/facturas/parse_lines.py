# src/facturas/parse_lines.py
from __future__ import annotations
from typing import List, Dict
import re

# ========== Utilidades de importe/regex ==========

# Importe europeo: 1.234,56 o 12,34
EU_AMOUNT = r"(?:\d{1,3}(?:\.\d{3})*,\d{2}|\d+,\d{2})"

# ...importe(s) al final de la lÃ­nea
EU_AMOUNT_AT_END = re.compile(rf"(?:\s|^)({EU_AMOUNT})\s*$")

# LÃ­nea que contiene SOLO importes (uno o varios, separados por espacios)
ONLY_AMOUNTS_RE = re.compile(rf"^\s*(?:{EU_AMOUNT})(?:\s+{EU_AMOUNT})*\s*$")

# Variantes â€œceroâ€ repetidas
ZERO_LINE_RE = re.compile(r"^\s*(?:0|0,00|0.00)(?:\s+0|(?:\s+0[,\.]0+))*\s*$")

# ========== Palabras clave para filtrar ruido ==========

NOISE_KEYWORDS = [
    # totales / sumatorios
    "total", "base imponible", "sumas", "suma", "subtotal",
    "iva", "impuesto", "impuestos", "recargo", "retenciÃ³n", "retencion",
    "cuadre", "redondeo",

    # descuentos / bonificaciones
    "dto", "descuento", "bonificaciÃ³n", "bonificacion",

    # pagos / administrativos
    "pago", "forma de pago", "vencimiento", "domiciliaciÃ³n", "domiciliacion",
    "transferencia", "observaciones", "nota", "comentarios",

    # legales / protecciÃ³n de datos (CERES mete estos textos)
    "protecciÃ³n de datos", "proteccion de datos", "rgpd", "aepd",
    "comunicaciones a terceros", "comunicacion a terceros", "terceros",
]

# Palabras que SÃ queremos conservar aunque la base sea 0,00
EXCEPT_0_KEEP = ["porte", "portes", "transporte", "envÃ­o", "envio", "mensajerÃ­a", "mensajeria", "gastos envÃ­o", "gastos envio"]

def _norm_text(x) -> str:
    return "" if x is None else str(x).strip()

def _norm_eu_amount(x: str) -> str:
    """
    Devuelve importe con coma y 2 decimales si es convertible; si no, deja el texto tal cual.
    """
    if not x:
        return ""
    s = x.strip()
    try:
        val = float(s.replace(".", "").replace(",", "."))
        return f"{val:0.2f}".replace(".", ",")
    except Exception:
        return s

def _is_noise(desc: str) -> bool:
    d = desc.lower()
    return any(k in d for k in NOISE_KEYWORDS)

def _looks_like_shipping(desc: str) -> bool:
    d = desc.lower()
    return any(k in d for k in EXCEPT_0_KEEP)

def parse_lines_text(lines_text: List[str]) -> List[Dict[str, str]]:
    """
    A partir del bloque de texto de lÃ­neas, crea filas con:
      - Descripcion
      - Categoria (por defecto REVISAR)
      - BaseImponible (si hay un importe europeo al final)
      - TipoIVA (vacÃ­o; lo rellenarÃ¡n otras reglas)
    Aplica un filtro fuerte para eliminar totales, resÃºmenes de IVA y textos legales.
    """
    rows: List[Dict[str, str]] = []

    # 1) ConstrucciÃ³n bÃ¡sica de filas
    for raw in lines_text or []:
        txt = _norm_text(raw)
        if not txt:
            continue

        # Si la lÃ­nea es SOLO importes o es una "lÃ­nea cero" repetida â†’ descartar
        if ONLY_AMOUNTS_RE.match(txt) or ZERO_LINE_RE.match(txt):
            continue

        # Si contiene palabras de ruido (totales, legales, etc.) â†’ descartar
        if _is_noise(txt):
            continue

        # Detectar importe al final (base imponible)
        base = ""
        m = EU_AMOUNT_AT_END.search(txt)
        if m:
            base = m.group(1)

        rows.append({
            "Descripcion": txt,
            "Categoria": "REVISAR",
            "BaseImponible": _norm_eu_amount(base),
            "TipoIVA": "",
        })

    # 2) Filtro adicional: si BaseImponible es 0 y no parece portes, descartar
    filtradas: List[Dict[str, str]] = []
    for r in rows:
        desc = _norm_text(r.get("Descripcion"))
        base = _norm_text(r.get("BaseImponible"))

        # sin descripciÃ³n Ãºtil
        if not desc:
            continue

        # Si base es cero, solo conservamos si parece portes/transporte
        if base in ("0", "0,00", "0.00", ""):
            if _looks_like_shipping(desc):
                filtradas.append(r)
            else:
                # si no hay base pero la descripciÃ³n es claramente un artÃ­culo vÃ¡lido (con cÃ³digos, uds, etc.)
                # intentamos conservar; si quieres mÃ¡s agresivo, comenta la lÃ­nea siguiente
                if re.search(r"\b\d{2,}\b", desc) or re.search(r"\buds?\b", desc.lower()):
                    filtradas.append(r)
                # si no, lo descartamos
        else:
            filtradas.append(r)

    return filtradas




