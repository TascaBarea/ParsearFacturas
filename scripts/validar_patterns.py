# scripts/validar_patterns.py
"""
Validador de overlays YAML por proveedor (carpeta patterns/).

Comprueba:
  - Estructura mínima por archivo (provider, secciones conocidas)
  - Sintaxis de expresiones regulares (date.regex, ref.regex, lines.regex_linea, overrides.when)
  - Tipos de campo y valores permitidos (iva.default, numbers.decimal/thousands)
  - Colisiones de provider/aliases entre ficheros

Uso:
  python scripts/validar_patterns.py --dir patterns --strict

Exit codes:
  0  → OK
  2  → Warnings (si --strict, se retorna 1)
  1  → Errores
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple, Any

try:
    from ruamel.yaml import YAML
except Exception:
    print("Falta dependencia: ruamel.yaml. Instala con: pip install ruamel.yaml", file=sys.stderr)
    sys.exit(1)


@dataclass
class Issue:
    level: str  # 'ERROR' | 'WARN'
    file: Path
    message: str


@dataclass
class PatternFile:
    path: Path
    data: Dict[str, Any]


ALLOWED_IVA = {0, 2, 4, 5, 10, 21}
ALLOWED_DECIMAL = {",", "."}
ALLOWED_THOUSANDS = {".", ",", " ", ""}


def load_yaml(p: Path) -> Dict[str, Any]:
    yaml = YAML(typ="safe")
    with p.open("r", encoding="utf-8") as fh:
        return yaml.load(fh) or {}


def compile_regex(rx: str, file: Path, issues: List[Issue], field_name: str) -> None:
    if not isinstance(rx, str) or not rx.strip():
        issues.append(Issue("ERROR", file, f"{field_name}: debe ser cadena no vacía"))
        return
    try:
        re.compile(rx)
    except re.error as e:
        issues.append(Issue("ERROR", file, f"{field_name}: regex inválida → {e}"))


def validate_file(pf: PatternFile, issues: List[Issue]):
    path, data = pf.path, pf.data

    # provider
    provider = data.get("provider")
    if not isinstance(provider, str) or not provider.strip():
        issues.append(Issue("ERROR", path, "provider: requerido y debe ser cadena"))
    
    # aliases
    aliases = data.get("aliases", [])
    if aliases is None:
        aliases = []
    if not isinstance(aliases, list) or not all(isinstance(a, str) for a in aliases):
        issues.append(Issue("ERROR", path, "aliases: debe ser lista de cadenas (o ausente)"))

    # date / ref
    date = data.get("date", {}) or {}
    if not isinstance(date, dict):
        issues.append(Issue("ERROR", path, "date: debe ser objeto"))
    else:
        if "regex" in date:
            compile_regex(date.get("regex"), path, issues, "date.regex")

    ref = data.get("ref", {}) or {}
    if not isinstance(ref, dict):
        issues.append(Issue("ERROR", path, "ref: debe ser objeto"))
    else:
        if "regex" in ref:
            compile_regex(ref.get("regex"), path, issues, "ref.regex")

    # lines
    lines = data.get("lines", {}) or {}
    if not isinstance(lines, dict):
        issues.append(Issue("ERROR", path, "lines: debe ser objeto"))
    else:
        if "regex_linea" in lines:
            compile_regex(lines.get("regex_linea"), path, issues, "lines.regex_linea")
        for k in ("start_after", "stop_before"):
            v = lines.get(k)
            if v is not None and not isinstance(v, str):
                issues.append(Issue("WARN", path, f"lines.{k}: debería ser cadena"))
        ig = lines.get("ignore_if_contains", [])
        if ig is not None and (not isinstance(ig, list) or not all(isinstance(s, str) for s in ig)):
            issues.append(Issue("ERROR", path, "lines.ignore_if_contains: debe ser lista de cadenas"))
        norm = lines.get("normalize", {}) or {}
        if not isinstance(norm, dict):
            issues.append(Issue("ERROR", path, "lines.normalize: debe ser objeto"))
        else:
            for flag in ("drop_units", "drop_codes"):
                v = norm.get(flag)
                if v is not None and not isinstance(v, bool):
                    issues.append(Issue("WARN", path, f"lines.normalize.{flag}: debería ser booleano"))

    # portes
    portes = data.get("portes", {}) or {}
    if not isinstance(portes, dict):
        issues.append(Issue("ERROR", path, "portes: debe ser objeto"))
    else:
        kw = portes.get("keywords", [])
        if kw is not None and (not isinstance(kw, list) or not all(isinstance(s, str) for s in kw)):
            issues.append(Issue("ERROR", path, "portes.keywords: debe ser lista de cadenas"))

    # iva
    iva = data.get("iva", {}) or {}
    if not isinstance(iva, dict):
        issues.append(Issue("ERROR", path, "iva: debe ser objeto"))
    else:
        dv = iva.get("default")
        if dv is not None and (not isinstance(dv, int) or dv not in ALLOWED_IVA):
            issues.append(Issue("ERROR", path, f"iva.default: debe ser uno de {sorted(ALLOWED_IVA)}"))
        ov = iva.get("overrides", [])
        if ov is not None:
            if not isinstance(ov, list):
                issues.append(Issue("ERROR", path, "iva.overrides: debe ser lista"))
            else:
                for i, rule in enumerate(ov):
                    if not isinstance(rule, dict):
                        issues.append(Issue("ERROR", path, f"iva.overrides[{i}]: debe ser objeto"))
                        continue
                    when = rule.get("when")
                    tipo = rule.get("tipo")
                    if when is None or not isinstance(when, str):
                        issues.append(Issue("ERROR", path, f"iva.overrides[{i}].when: requerido (cadena)"))
                    else:
                        compile_regex(when, path, issues, f"iva.overrides[{i}].when")
                    if tipo is None or not isinstance(tipo, int) or tipo not in ALLOWED_IVA:
                        issues.append(Issue("ERROR", path, f"iva.overrides[{i}].tipo: debe ser uno de {sorted(ALLOWED_IVA)}"))

    # numbers
    numbers = data.get("numbers", {}) or {}
    if not isinstance(numbers, dict):
        issues.append(Issue("ERROR", path, "numbers: debe ser objeto"))
    else:
        dec = numbers.get("decimal")
        if dec is not None and dec not in ALLOWED_DECIMAL:
            issues.append(Issue("ERROR", path, f"numbers.decimal: debe ser uno de {sorted(ALLOWED_DECIMAL)}"))
        tho = numbers.get("thousands")
        if tho is not None and tho not in ALLOWED_THOUSANDS:
            issues.append(Issue("ERROR", path, f"numbers.thousands: debe ser uno de {sorted(ALLOWED_THOUSANDS)}"))


def collect_collisions(pfiles: List[PatternFile], issues: List[Issue]):
    providers: Dict[str, Path] = {}
    alias_owner: Dict[str, Path] = {}

    def norm(s: str) -> str:
        s_up = s.upper().strip()
        s_up = re.sub(r"[^A-Z0-9 ]+", " ", s_up)
        s_up = re.sub(r"\s+", " ", s_up)
        return s_up

    for pf in pfiles:
        prov = pf.data.get("provider")
        if isinstance(prov, str) and prov.strip():
            key = norm(prov)
            if key in providers and providers[key] != pf.path:
                issues.append(Issue("ERROR", pf.path, f"provider duplicado: '{prov}' ya en {providers[key].name}"))
            else:
                providers[key] = pf.path
        aliases = pf.data.get("aliases") or []
        if isinstance(aliases, list):
            for a in aliases:
                if not isinstance(a, str):
                    continue
                k = norm(a)
                owner = alias_owner.get(k)
                if owner and owner != pf.path:
                    issues.append(Issue("WARN", pf.path, f"alias '{a}' duplicado también en {owner.name}"))
                else:
                    alias_owner[k] = pf.path


def main():
    ap = argparse.ArgumentParser(description="Valida archivos YAML de patterns por proveedor")
    ap.add_argument("--dir", default="patterns", help="Carpeta con .yml (por defecto: patterns)")
    ap.add_argument("--strict", action="store_true", help="Tratar warnings como error (exit 1)")
    args = ap.parse_args()

    base = Path(args.dir)
    if not base.exists():
        print(f"No existe carpeta: {base}", file=sys.stderr)
        return 1

    ymls = sorted(list(base.glob("*.yml")))
    if not ymls:
        print(f"No se encontraron .yml en {base}")
        return 2

    issues: List[Issue] = []
    pfiles: List[PatternFile] = []

    for y in ymls:
        try:
            data = load_yaml(y)
            if not isinstance(data, dict):
                issues.append(Issue("ERROR", y, "El YAML raíz debe ser un objeto"))
                continue
            pf = PatternFile(path=y, data=data)
            pfiles.append(pf)
            validate_file(pf, issues)
        except Exception as e:
            issues.append(Issue("ERROR", y, f"Excepción leyendo YAML: {e}"))

    collect_collisions(pfiles, issues)

    errs = [x for x in issues if x.level == "ERROR"]
    warns = [x for x in issues if x.level == "WARN"]

    for it in issues:
        print(f"[{it.level}] {it.file.name}: {it.message}")

    if errs:
        print(f"\n✖ Errores: {len(errs)}  •  Warnings: {len(warns)}")
        return 1
    if warns:
        print(f"\n✔ Sin errores. Warnings: {len(warns)}")
        return 1 if args.strict else 2

    print("\n✔ OK: todos los patterns válidos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
