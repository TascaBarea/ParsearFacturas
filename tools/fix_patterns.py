# tools/fix_patterns.py
from __future__ import annotations
import re
from pathlib import Path
from typing import Optional, Tuple

try:
    from ruamel.yaml import YAML
except Exception:
    YAML = None  # si faltara la lib, aun así aplicamos fixes de texto

DATE_REGEX_GENERIC = r"\b\d{2}[-/]\d{2}[-/]\d{2,4}\b|\b\d{1,2}\s+de\s+[A-Za-zÁÉÍÓÚáéíóú]+\s+de\s+\d{4}\b"
NFACT_REGEX_GENERIC = r"[A-Z0-9/-]{3,}"

def quote_if_needed(val: str) -> str:
    v = val.strip()
    if not v:
        return "null"
    if v.lower() in {"null", "none", "~"}:
        return "null"
    if v[0] in "'\"":
        return v
    # comillas simples YAML; duplicar comillas simples internas
    return "'" + v.replace("'", "''") + "'"

def fix_lines(text: str) -> Tuple[str, bool]:
    """
    Pasa línea a línea:
      - detecta bloque actual (fecha/numero_factura/lineas)
      - repara regex: los cita y sustituye basura (\\1, '''\\1, etc.) por defaults
    """
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    ctx: Optional[str] = None
    changed = False

    # normaliza comillas “inteligentes”
    rep_pairs = {
        "“": '"', "”": '"', "‘": "'", "’": "'",
    }
    for k, v in rep_pairs.items():
        if k in text:
            text = text.replace(k, v)
            lines = text.split("\n")
            changed = True

    for i, ln in enumerate(lines):
        s = ln.strip()

        # detectar cambio de contexto
        if re.match(r"^\s*fecha\s*:\s*$", ln):
            ctx = "fecha"
        elif re.match(r"^\s*numero_factura\s*:\s*$", ln):
            ctx = "numero"
        elif re.match(r"^\s*lineas\s*:\s*$", ln):
            ctx = "lineas"
        elif re.match(r"^\s*[A-Za-z0-9_]+\s*:\s*$", ln) and not re.match(r"^\s*(find|direction|regex|region)\s*:\s*$", s):
            # salida de sub-bloque
            # (si abre otra key de nivel similar, reseteamos contexto)
            if not s.startswith(("find:", "direction:", "regex:", "region:")):
                # heurística simple
                pass

        m = re.match(r"^(\s*regex:\s*)(.*)$", ln)
        if not m:
            continue

        indent, raw_val = m.group(1), m.group(2).strip()

        # si se ve basura típica del replace anterior, sustituimos por defaults
        suspicious = (raw_val == "" or "\\1" in raw_val or "'''" in raw_val)
        if ctx == "fecha" and suspicious:
            new_val = quote_if_needed(DATE_REGEX_GENERIC)
        elif ctx == "numero" and suspicious:
            new_val = quote_if_needed(NFACT_REGEX_GENERIC)
        else:
            # solo citar si no está citado
            new_val = quote_if_needed(raw_val)

        if new_val != raw_val:
            lines[i] = f"{indent}{new_val}"
            changed = True

    # citar también regex que hayan quedado sin comillas por si se escapó alguno
    def _quote_any_regex(m):
        indent, val = m.group(1), m.group(2)
        q = quote_if_needed(val)
        if q != val:
            nonlocal_changed[0] = True
        return f"{indent}{q}"

    nonlocal_changed = [False]
    tmp = "\n".join(lines)
    tmp = re.sub(r"(?m)^(\s*regex:\s*)([^'\"][^\n]*)$", _quote_any_regex, tmp)
    if nonlocal_changed[0]:
        changed = True

    return tmp, changed

SKELETON_TMPL = """proveedor: "{prov}"
{aliases}
anchors:
  fecha:
    find: ["Fecha"]
    direction: "right"
    regex: '{date_regex}'
  numero_factura:
    find: ["Factura"]
    direction: "right"
    regex: '{nfac_regex}'
  lineas:
    find: ["Descripción", "Importe"]
    region: "lines"

rules:
  - NormalizarTextos
  - UnicaLineaPorProducto

descripcion:
  mode: "original"

iva_default: 21
grouping: lineas

portes:
  mode: "prorratear"

precedence:
  force_pattern_over_dictionary: false
"""

def build_skeleton_from(text: str) -> str:
    prov = "PROVEEDOR"
    m = re.search(r'^\s*proveedor:\s*"?([^"\n]+)"?', text, re.M)
    if m:
        prov = m.group(1).strip()

    aliases_line = ""
    am = re.search(r'^\s*aliases:\s*(\[.*\])', text, re.M)
    if am:
        aliases_line = f"aliases: {am.group(1)}"
    else:
        aliases_line = 'aliases: null'

    return SKELETON_TMPL.format(
        prov=prov,
        aliases=aliases_line,
        date_regex=DATE_REGEX_GENERIC,
        nfac_regex=NFACT_REGEX_GENERIC,
    )

def yaml_is_valid(text: str) -> bool:
    if YAML is None:
        # si no hay ruamel, no podemos validar aquí;
        # dejamos que el validador oficial lo haga después
        return True
    try:
        y = YAML(typ="safe")
        y.load(text)
        return True
    except Exception:
        return False

def process_file(path: Path, make_backup: bool = True) -> str:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    # paso 1: intentamos arreglar en caliente
    fixed, changed = fix_lines(raw)
    if changed and yaml_is_valid(fixed):
        if make_backup:
            path.with_suffix(path.suffix + ".bak").write_text(raw, encoding="utf-8")
        path.write_text(fixed, encoding="utf-8")
        return "[patched]"

    # si todavía no es válido, intentamos parche + validar de nuevo
    if not yaml_is_valid(fixed):
        # paso 2: reconstrucción con esqueleto estándar
        skeleton = build_skeleton_from(raw)
        if yaml_is_valid(skeleton):
            if make_backup:
                path.with_suffix(path.suffix + ".bak").write_text(raw, encoding="utf-8")
            path.write_text(skeleton, encoding="utf-8")
            return "[rebuilt]"
        else:
            return "[failed]"

    # nada que cambiar (ya estaba bien)
    return "[ok]"

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Auto-fixer de patrones YAML")
    ap.add_argument("dir", nargs="?", default="patterns", help="Directorio con .yml")
    ap.add_argument("--no-backup", action="store_true", help="No crear .bak")
    args = ap.parse_args()

    base = Path(args.dir)
    files = sorted(base.glob("*.yml"))
    if not files:
        print(f"(no se encontraron YAML en {base})")
        return

    ok = patched = rebuilt = failed = 0
    for p in files:
        status = process_file(p, make_backup=not args.no_backup)
        if status == "[ok]":
            ok += 1
        elif status == "[patched]":
            patched += 1
        elif status == "[rebuilt]":
            rebuilt += 1
        else:
            failed += 1
        print(f"{status} {p}")

    print("\n──────── Resumen ────────")
    print(f"✓ ok:        {ok}")
    print(f"✎ patched:   {patched}")
    print(f"♺ rebuilt:   {rebuilt}")
    print(f"✗ failed:    {failed}")

if __name__ == "__main__":
    main()
