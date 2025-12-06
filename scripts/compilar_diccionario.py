#!/usr/bin/env python3

"""
Compilación del diccionario a JSON inmutable con Version y SHA.

Uso:
  python scripts/compilar_diccionario.py --dict "/ruta/DiccionarioProveedoresCategoria.xlsx" --out "./diccionario_compilado.json" [--version 2025.09.08.01]

Pasos:
  1) Carga tolerante de REGLAS/CATEGORIAS/OVERLAYS.
  2) Normaliza y ordena reglas (Proveedor, Prioridad asc, TipoMatch EXACT→SUBSTR→REGEX, ArticuloPattern).
  3) Genera estructura JSON canónica + SHA256 del contenido.
  4) Guarda a disco y muestra resumen.

Nota: se recomienda ejecutar antes el validador.
"""
from __future__ import annotations

import argparse, os, sys, re, json, hashlib
from datetime import datetime
from typing import List, Dict, Any, Tuple
import pandas as pd
import unicodedata

ALLOWED_MATCH = {"EXACT", "SUBSTR", "REGEX"}
MATCH_ORDER = {"EXACT": 0, "SUBSTR": 1, "REGEX": 2}

# ───────── utilidades ─────────
def _strip_accents(s: str) -> str:
    if s is None:
        return ""
    return "".join(c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn")

def _norm_provider(s: str) -> str:
    s = _strip_accents(s).upper()
    s = re.sub(r"[^A-Z0-9 ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

REGLAS_COL_ALIASES = {
    "Proveedor": {"proveedor", "provider"},
    "ArticuloPattern": {"articulopattern", "articulo", "artículo", "pattern", "patron", "patrón", "regex", "keyword", "palabra"},
    "Categoria": {"categoria", "categoría", "category"},
    "TipoMatch": {"tipomatch", "tipo", "match"},
    "TipoIVA": {"tipoiva", "iva"},
    "Prioridad": {"prioridad", "prio", "orden"},
    "Activa": {"activa", "activo", "enabled"},
    "ValidaDesde": {"validadesde", "desde"},
    "ValidaHasta": {"validahasta", "hasta"},
    "Notas": {"notas", "nota", "comments"},
}


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    mapping: Dict[str, str] = {}
    lower = {re.sub(r"[ _]", "", _strip_accents(str(c)).lower()): c for c in df.columns}
    for target, aliases in REGLAS_COL_ALIASES.items():
        for a in {target.lower(), *_strip_accents(target).lower().split(), *aliases}:
            key = re.sub(r"[ _]", "", _strip_accents(a).lower())
            if key in lower:
                mapping[lower[key]] = target
                break
    out = df.rename(columns=mapping).copy()
    return out


def _load_excel(path: str) -> Tuple[pd.DataFrame, pd.DataFrame | None, pd.DataFrame | None]:
    xls = pd.ExcelFile(path)
    sheet_names = {s.lower(): s for s in xls.sheet_names}

    reglas_sheet = sheet_names.get("reglas")
    categorias_sheet = sheet_names.get("categorias")
    overlays_sheet = sheet_names.get("overlays")

    if reglas_sheet:
        df_rules = pd.read_excel(path, sheet_name=reglas_sheet)
    else:
        df_rules = pd.read_excel(path, sheet_name=0)  # compat formato antiguo
    df_rules = _normalize_columns(df_rules)

    df_cat = pd.read_excel(path, sheet_name=categorias_sheet) if categorias_sheet else None
    df_ovl = pd.read_excel(path, sheet_name=overlays_sheet) if overlays_sheet else None
    return df_rules, df_cat, df_ovl


def _now_version() -> str:
    # YYYY.MM.DD.nn (nn=01 por defecto)
    base = datetime.now().strftime("%Y.%m.%d")
    return base + ".01"


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _hash_sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dict", required=True, help="Ruta al Excel DiccionarioProveedoresCategoria.xlsx")
    ap.add_argument("--out", required=True, help="Ruta de salida del JSON compilado")
    ap.add_argument("--version", help="Versión explícita (si no, se autogenera)")
    args = ap.parse_args()

    if not os.path.exists(args.dict):
        print(f"ERROR: No existe el archivo: {args.dict}")
        sys.exit(2)

    df_rules, df_cat, df_ovl = _load_excel(args.dict)

    # Normalizar contenido y defaults
    df = df_rules.copy()
    df = _normalize_columns(df)

    df["Proveedor"] = df["Proveedor"].fillna("").map(_norm_provider)
    df["ArticuloPattern"] = df["ArticuloPattern"].fillna("").astype(str).str.strip()
    df["Categoria"] = df["Categoria"].fillna("").astype(str).str.strip()
    df["TipoMatch"] = df.get("TipoMatch", "SUBSTR").fillna("SUBSTR").astype(str).str.upper().str.strip()
    df["TipoMatch"] = df["TipoMatch"].where(df["TipoMatch"].isin(ALLOWED_MATCH), "SUBSTR")
    df["Prioridad"] = pd.to_numeric(df.get("Prioridad", 10), errors="coerce").fillna(10).astype(int)
    df["Activa"] = df.get("Activa", True)
    df["Activa"] = df["Activa"].map(lambda v: str(v).strip().lower() not in {"false", "0", "no", "nan", ""})

    # Filtrar filas mínimas y activas
    df = df[(df["Proveedor"] != "") & (df["ArticuloPattern"] != "") & (df["Categoria"] != "") & (df["Activa"])]

    # Orden estable para ejecución: Proveedor, Prioridad asc, TipoMatch (EXACT→SUBSTR→REGEX), ArticuloPattern
    df["_match_order"] = df["TipoMatch"].map(MATCH_ORDER)
    df = df.sort_values(["Proveedor", "Prioridad", "_match_order", "ArticuloPattern"], kind="stable").drop(columns=["_match_order"])

    # Preparar artefacto
    compiled: Dict[str, Any] = {
        "version": args.version or _now_version(),
        "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "source_excel": os.path.abspath(args.dict),
        "rules": df.to_dict(orient="records"),
        "categories": None,
        "overlays": None,
    }

    if df_cat is not None:
        compiled["categories"] = df_cat.to_dict(orient="records")
    if df_ovl is not None:
        compiled["overlays"] = df_ovl.to_dict(orient="records")

    canon = _canonical_json(compiled)
    sha = _hash_sha256(canon)
    compiled["sha256"] = sha

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(compiled, f, ensure_ascii=False, indent=2)

    print("Compilado OK")
    print(f"  Versión:   {compiled['version']}")
    print(f"  Reglas:    {len(compiled['rules'])}")
    print(f"  SHA256:    {compiled['sha256']}")
    print(f"  Salida:    {os.path.abspath(args.out)}")

if __name__ == "__main__":
    main()
