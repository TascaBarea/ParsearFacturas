#!/usr/bin/env python3

"""
Validador del diccionario de categorías.

Uso:
  python scripts/validar_diccionario.py --dict "/ruta/DiccionarioProveedoresCategoria.xlsx" [--strict]

Qué comprueba:
  - Esquema mínimo de la hoja REGLAS (o compatibilidad con formato antiguo PROVEEDOR/ARTICULO/CATEGORIA/TIPO).
  - Normalización de proveedor, campos obligatorios, tipos.
  - Categorías válidas (si existe hoja CATEGORIAS).
  - Duplicados exactos (Proveedor+Patrón+TipoMatch activos).
  - Solapes entre SUBSTR para mismo proveedor (patrones que se contienen) y conflicto de prioridad.
  - Fechas válidas (ValidaDesde/ValidaHasta) y estado Activa coherente.

Salida:
  - Código de salida 0 si no hay ERRORES (puede haber WARNINGs).
  - Un resumen legible por pantalla.
  - Reporte detallado en el mismo directorio que el Excel: "<excel>.validacion.txt".
"""
from __future__ import annotations

import argparse, os, sys, re, json, hashlib
from datetime import datetime
from typing import List, Dict, Any, Tuple
import pandas as pd
import unicodedata

ALLOWED_MATCH = {"EXACT", "SUBSTR", "REGEX"}

# ───────── utilidades ─────────
def _strip_accents(s: str) -> str:
    if s is None:
        return ""
    return "".join(c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn")

def _norm_provider(s: str) -> str:
    s = _strip_accents(s).upper()
    s = re.sub(r"[^A-Z0-9 ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    if not s:
        return s
    return s

# ───────── carga tolerante ─────────
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

    # Hoja REGLAS o compat antigua
    reglas_sheet = sheet_names.get("reglas")
    categorias_sheet = sheet_names.get("categorias")
    overlays_sheet = sheet_names.get("overlays")

    if reglas_sheet:
        df_rules = pd.read_excel(path, sheet_name=reglas_sheet)
        df_rules = _normalize_columns(df_rules)
    else:
        # Compatibilidad con formato antiguo
        df_rules = pd.read_excel(path, sheet_name=0)
        df_rules = _normalize_columns(df_rules)
        # Defaults para columnas nuevas
        if "TipoMatch" not in df_rules.columns:
            df_rules["TipoMatch"] = "SUBSTR"
        if "Prioridad" not in df_rules.columns:
            df_rules["Prioridad"] = 10
        if "Activa" not in df_rules.columns:
            df_rules["Activa"] = True

    df_cat = pd.read_excel(path, sheet_name=categorias_sheet) if categorias_sheet else None
    df_ovl = pd.read_excel(path, sheet_name=overlays_sheet) if overlays_sheet else None
    return df_rules, df_cat, df_ovl


# ───────── validaciones ─────────
def _validate(df_rules: pd.DataFrame, df_cat: pd.DataFrame | None, strict: bool) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warns: List[str] = []

    # Campos obligatorios mínimos
    required = ["Proveedor", "ArticuloPattern", "Categoria", "TipoMatch"]
    for c in required:
        if c not in df_rules.columns:
            errors.append(f"Falta columna obligatoria: {c}")

    if errors:
        return errors, warns

    # Normalizar campos
    df = df_rules.copy()
    df["Proveedor"] = df["Proveedor"].fillna("").map(_norm_provider)
    df["ArticuloPattern"] = df["ArticuloPattern"].fillna("").astype(str).str.strip()
    df["Categoria"] = df["Categoria"].fillna("").astype(str).str.strip()
    df["TipoMatch"] = df["TipoMatch"].fillna("").astype(str).str.upper().str.strip()
    if "Prioridad" in df.columns:
        df["Prioridad"] = pd.to_numeric(df["Prioridad"], errors="coerce").fillna(10).astype(int)
    else:
        df["Prioridad"] = 10
    if "Activa" in df.columns:
        df["Activa"] = df["Activa"].map(lambda v: str(v).strip().lower() not in {"false", "0", "no", "nan", ""})
    else:
        df["Activa"] = True

    # Filtros básicos
    null_rows = df[(df["Proveedor"] == "") | (df["ArticuloPattern"] == "") | (df["Categoria"] == "")]
    for i, r in null_rows.iterrows():
        errors.append(f"Fila {i}: campos vacíos en Proveedor/ArticuloPattern/Categoria")

    # Tipos de match válidos
    bad_match = df[~df["TipoMatch"].isin(ALLOWED_MATCH)]
    for i, r in bad_match.iterrows():
        errors.append(f"Fila {i}: TipoMatch inválido '{r['TipoMatch']}' (permitidos: {sorted(ALLOWED_MATCH)})")

    # Categorías válidas (si hay hoja CATEGORIAS)
    if df_cat is not None and not df_cat.empty:
        cat_col = None
        for c in df_cat.columns:
            if re.sub(r"[ _]", "", _strip_accents(c).lower()) in {"categoria", "categorias", "categoría"}:
                cat_col = c
                break
        if cat_col:
            cats_valid = {str(x).strip() for x in df_cat[cat_col].dropna().unique()}
            bad_cat = df[~df["Categoria"].isin(cats_valid)]
            for i, r in bad_cat.iterrows():
                errors.append(f"Fila {i}: Categoria '{r['Categoria']}' no está en hoja CATEGORIAS")
        else:
            warns.append("Hoja CATEGORIAS presente pero no se encontró columna 'Categoria'")

    # Duplicados exactos activos
    dup_mask = df[df["Activa"]].duplicated(subset=["Proveedor", "ArticuloPattern", "TipoMatch"], keep=False)
    dups = df[df["Activa"] & dup_mask]
    for i, r in dups.iterrows():
        warns.append(f"Duplicado activo: Proveedor='{r['Proveedor']}', Patron='{r['ArticuloPattern']}', Tipo='{r['TipoMatch']}' (revisar Prioridad/Activa)")

    # Solapes SUBSTR por proveedor
    substr = df[(df["Activa"]) & (df["TipoMatch"] == "SUBSTR")]
    by_prov = substr.groupby("Proveedor")
    for prov, grp in by_prov:
        pats = grp[["ArticuloPattern", "Prioridad"]].values.tolist()
        for i in range(len(pats)):
            p1, pr1 = pats[i]
            for j in range(i+1, len(pats)):
                p2, pr2 = pats[j]
                if not p1 or not p2:
                    continue
                if p1 in p2 or p2 in p1:
                    # Reglas se pisan: si la más específica no tiene PRIORIDAD menor, avisar
                    if len(p1) > len(p2):
                        spec, sp_pr, gen, gn_pr = p1, pr1, p2, pr2
                    else:
                        spec, sp_pr, gen, gn_pr = p2, pr2, p1, pr1
                    if sp_pr >= gn_pr:
                        warns.append(f"Solape SUBSTR en '{prov}': '{spec}' contiene '{gen}' pero Prioridad {sp_pr} ≥ {gn_pr} (ajustar Prioridad)")

    # Fechas
    for col in ("ValidaDesde", "ValidaHasta"):
        if col in df.columns:
            for i, v in df[col].items():
                if pd.isna(v) or str(v).strip() == "":
                    continue
                ok = False
                for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d-%m-%y"):
                    try:
                        _ = datetime.strptime(str(v).split(" ")[0], fmt)
                        ok = True
                        break
                    except Exception:
                        pass
                if not ok:
                    warns.append(f"Fila {i}: fecha inválida en {col}: '{v}'")

    # Strict → solapes/duplicados elevan a error
    if strict:
        errors.extend([f"[STRICT] {w}" for w in warns])
        warns = []

    return errors, warns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dict", required=True, help="Ruta al Excel DiccionarioProveedoresCategoria.xlsx")
    ap.add_argument("--strict", action="store_true", help="Tratar warnings como errores")
    args = ap.parse_args()

    path = args.dict
    if not os.path.exists(path):
        print(f"ERROR: No existe el archivo: {path}")
        sys.exit(2)

    df_rules, df_cat, df_ovl = _load_excel(path)
    errors, warns = _validate(df_rules, df_cat, args.strict)

    # Reporte
    report_lines = []
    report_lines.append(f"Archivo: {path}")
    report_lines.append(f"Filas reglas: {len(df_rules)}")
    report_lines.append(f"Categorias hoja: {0 if df_cat is None else len(df_cat)}")
    report_lines.append("")
    report_lines.append(f"ERRORES ({len(errors)}):")
    report_lines.extend(["  - " + e for e in errors])
    report_lines.append("")
    report_lines.append(f"WARNINGS ({len(warns)}):")
    report_lines.extend(["  - " + w for w in warns])

    text = "\n".join(report_lines)
    print(text)

    # Guardar .validacion.txt junto al Excel
    out_txt = os.path.splitext(path)[0] + ".validacion.txt"
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write(text)

    sys.exit(0 if not errors else 1)

if __name__ == "__main__":
    main()
