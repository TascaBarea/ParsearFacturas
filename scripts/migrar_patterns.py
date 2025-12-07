# scripts/migrar_patterns.py
"""
Migrador de overlays YAML de proveedor al esquema estándar (docs/patterns.md).

Convierte claves antiguas típicas:
- proveedor                -> provider
- anchors.fecha.regex      -> date.regex
- anchors.numero_factura.regex -> ref.regex
- anchors.lineas.find      -> lines.start_after / lines.stop_before (heurística)
- rules (NormalizarTextos) -> lines.normalize.drop_units / drop_codes
- iva_default              -> iva.default
- portes.mode: prorratear  -> portes.keywords (PORTES/TRANSPORTE/ENVÍO)

Mantiene intactas regex existentes cuando es posible y NO borra campos
que no reconoce (los copia en un bloque `_legacy` para referencia).

Uso:
  python scripts/migrar_patterns.py --in patterns --out patterns

Esto sobrescribe el YAML destino **tras** crear una copia de seguridad:
  <nombre>.yml.bak_migracion

Recomendación: después de migrar, ejecuta el validador:
  python scripts/validar_patterns.py --dir patterns --strict
"""
from __future__ import annotations

import argparse
from pathlib import Path
from datetime import datetime
from typing import Any, Dict
import sys
import re

try:
    from ruamel.yaml import YAML
except Exception:
    print("Falta dependencia: ruamel.yaml. Instala con: pip install ruamel.yaml", file=sys.stderr)
    sys.exit(1)


def _norm_txt(s: str) -> str:
    s = (s or "").strip()
    return s


def _migrate_one(data: Dict[str, Any]) -> Dict[str, Any]:
    new: Dict[str, Any] = {}
    legacy: Dict[str, Any] = {}

    # 1) provider / aliases
    provider = data.get("provider") or data.get("proveedor") or data.get("Proveedor")
    if isinstance(provider, str) and provider.strip():
        new["provider"] = provider.strip()
    else:
        # si no hay provider, lo dejamos vacío; el validador lo advertirá
        new["provider"] = ""

    if isinstance(data.get("aliases"), list):
        new["aliases"] = [str(a) for a in data.get("aliases")]

    # 2) date / ref (anchors.*.regex)
    anchors = data.get("anchors") or {}
    if isinstance(anchors, dict):
        fecha = anchors.get("fecha") or anchors.get("date") or {}
        if isinstance(fecha, dict) and fecha.get("regex"):
            new.setdefault("date", {})["regex"] = str(fecha["regex"]).strip()
        numero = anchors.get("numero_factura") or anchors.get("ref") or {}
        if isinstance(numero, dict) and numero.get("regex"):
            new.setdefault("ref", {})["regex"] = str(numero["regex"]).strip()

        # lineas/find -> start_after/stop_before (heurística simple)
        lineas = anchors.get("lineas") or {}
        finds = lineas.get("find") if isinstance(lineas, dict) else None
        if isinstance(finds, list) and finds:
            sa = _norm_txt(finds[0])
            if sa:
                new.setdefault("lines", {})["start_after"] = sa
            if len(finds) >= 2:
                sb = _norm_txt(finds[1])
                if sb:
                    new.setdefault("lines", {})["stop_before"] = sb

    # 3) regex_linea: algunos esquemas antiguos metían un regex genérico en anchors.lineas.pattern
    try:
        maybe_pat = anchors.get("lineas", {}).get("pattern")
        if isinstance(maybe_pat, str) and maybe_pat.strip():
            new.setdefault("lines", {})["regex_linea"] = maybe_pat.strip()
    except Exception:
        pass

    # 4) rules -> normalizaciones
    rules = data.get("rules")
    if isinstance(rules, list) and rules:
        norm = {}
        if any(str(r).lower().startswith("normalizar") for r in rules):
            norm["drop_units"] = True
            norm["drop_codes"] = True
        if norm:
            new.setdefault("lines", {})["normalize"] = norm

    # 5) iva_default
    iva_def = data.get("iva_default")
    if isinstance(iva_def, int):
        new.setdefault("iva", {})["default"] = iva_def

    # 6) portes.mode
    portes = data.get("portes") or {}
    if isinstance(portes, dict) and str(portes.get("mode", "")).lower().startswith("prorrate"):
        new.setdefault("portes", {})["keywords"] = ["PORTES", "TRANSPORTE", "ENVÍO"]

    # 7) numbers (si no hay, añadir por defecto EU)
    new.setdefault("numbers", {}).setdefault("decimal", ",")
    new.setdefault("numbers", {}).setdefault("thousands", ".")

    # 8) regex_linea genérica si no hay ninguna
    lines = new.setdefault("lines", {})
    if not lines.get("regex_linea"):
        lines["regex_linea"] = (
            r"^(?P<descripcion>.+?)\s+(?P<base>(?:\d{1,3}(?:\.\d{3})*,\d{2})|(?:\d+,\d{2})|(?:\d+\.\d{2}))$"
        )

    # Copiamos cualquier cosa no mapeada en _legacy para referencia
    for k, v in data.items():
        if k in {"provider", "proveedor", "Proveedor", "aliases", "anchors", "rules", "iva_default", "portes"}:
            continue
        legacy[k] = v
    if anchors:
        # además, guardamos anchors original para rastreo
        legacy["anchors"] = anchors
    if rules:
        legacy["rules"] = rules
    if portes:
        legacy.setdefault("portes", portes)

    if legacy:
        new["_legacy"] = legacy

    return new


def main():
    parser = argparse.ArgumentParser(description="Parser facturas con overlay + diccionario + cuadre por IVA")
    parser.add_argument("pdfs", nargs="*", help="rutas a PDFs a procesar (opcional si usas --in-dir)")
 (admite comodines)")
    parser.add_argument("--provider", required=False, help="Proveedor (ej. JIMELUZ, MARITA)")
    parser.add_argument("--diccionario", default=r"C:\\_ARCHIVOS\\TRABAJO\\Facturas\\ParsearFacturas-main\\DiccionarioProveedoresCategoria.xlsx",
                        help="Ruta al Excel del diccionario")

    # Opciones de proceso
    parser.add_argument("--lines", action="store_true", help="Extraer líneas de producto")
    parser.add_argument("--pretty", action="store_true", help="Mostrar TSV por pantalla")
    parser.add_argument("--abort-on-dict-change", action="store_true",
                        help="Abortar si el diccionario cambia de hash durante el lote")

    # NUEVO: recolección robusta de PDFs
    parser.add_argument("--in-dir", type=Path, nargs="*", default=[],
                        help="Carpetas a escanear además de los patrones posicionales")
    parser.add_argument("--contains", type=str, default="",
                        help="Filtrar PDFs por texto en el nombre (sin acentos, case-insensitive)")
    parser.add_argument("--recurse", action="store_true",
                        help="Buscar recursivamente dentro de --in-dir")
    parser.add_argument("--list", action="store_true",
                        help="Solo listar los PDFs que se procesarían y salir")

    # Salidas (unificadas a out/)
    parser.add_argument("--tsv-out", type=Path, default=DEFAULT_OUTDIR,
                        help="Carpeta para TSV consolidado (por defecto: out/)")
    parser.add_argument("--resumen-out", type=Path, default=DEFAULT_OUTDIR,
                        help="Carpeta para CSV resumen por factura (por defecto: out/)")
    parser.add_argument("--excel-out", type=Path, default=DEFAULT_OUTDIR / "facturas.xlsx",
                        help="Ruta para exportar Excel (por defecto: out/facturas.xlsx)")

    args = parser.parse_args()
    if not args.list and not args.provider:
        raise SystemExit("--provider es obligatorio salvo con --list")

    # Recolectar PDFs de patrones y carpetas
    input_patterns = args.pdfs
    pdf_list = collect_pdfs(input_patterns, args.in_dir, contains=args.contains, recurse=args.recurse)

    # Solo listar y salir
    if args.list:
        if not pdf_list:
            print("No se encontraron PDFs con los criterios dados.")
        else:
            print("PDFs a procesar:")
            for p in pdf_list:
                print(" -", p)
        return

    if not pdf_list:
        raise SystemExit("No se encontraron PDFs. Revisa patrones, --in-dir o --contains.")

    if pd is None:
        raise SystemExit("pandas es requerido para este CLI")

    # Cargar diccionario filtrado por proveedor
    mapping, dic_hash = load_diccionario(args.diccionario, args.provider)

    all_rows: List[Dict[str, Any]] = []
    resumen_rows: List[Dict[str, Any]] = []

    # Procesar PDFs
    for pdf_path in pdf_list:
        if not os.path.exists(pdf_path):
            raise SystemExit(f"No existe el archivo: {pdf_path}")

        # Fail-fast si cambia el diccionario
        cur_hash = file_sha256(args.diccionario)
        if cur_hash != dic_hash:
            if getattr(args, "abort_on_dict_change", False):
                raise SystemExit("Diccionario modificado durante el lote. Aborto (fail-fast).")
            else:
                mapping, dic_hash = load_diccionario(args.diccionario, args.provider)

        if detect_blocks_minimal is None:
            raise SystemExit("detect_blocks_minimal no disponible en este entorno")
        blocks = detect_blocks_minimal(pdf_path, provider=args.provider)

        lines_raw = blocks.get("lines_text") or []
        if isinstance(lines_raw, str):
            lines_raw = lines_raw.splitlines()

        full_text  = _coerce_text(blocks.get("full_text"))
        lines_join = _coerce_text(lines_raw)
        header     = blocks.get("header", {}) or {}
        fecha = header.get("fecha") or header.get("FECHA") or ""
        ref   = header.get("ref")   or header.get("REF")   or ""

        if not args.lines:
            continue
        if parse_lines_text is None:
            raise SystemExit("parse_lines_text no disponible en este entorno")

        rows = parse_lines_text(lines_raw)

        out_lines: List[Dict[str, Any]] = []
        for r in rows:
            desc = r.get("Descripcion", "") or ""
            base = r.get("BaseImponible") or r.get("Base") or r.get("Importe") or ""

            # 1) Filtrar pies/totales
            desc_norm = normalize_txt(desc).replace(" ", "")
            if any(k in desc_norm for k in ["SUMAYSIGUE","TOTALALBRUTO","TOTALBRUTO","TOTALFACTURA","IMPUESTOS","IVA","BASEIMPONIBLE"]):
                continue

            # 2) Normalizar base a float
            try:
                base_val = float(str(base).replace('.', '').replace(',', '.')) if str(base) else 0.0
            except Exception:
                base_val = 0.0

            # 3) Limpieza MARITA
            art = desc
            if args.provider.upper().startswith("MARITA"):
                art = marita_clean_descripcion(art)

            # 4) Clasificación
            categoria, iva = match_flexible(art, mapping)

            out_lines.append({
                "#": Path(pdf_path).stem.split()[0],
                "FECHA": fecha,
                "REF": ref,
                "PROVEEDOR": args.provider.upper(),
                "ARTÍCULO": art,
                "DESCRIPCIÓN": categoria,
                "TIPO IVA": iva,
                "BASE": round(base_val, 2),
            })

        df_fac = pd.DataFrame(out_lines)
        expected = parse_pie_bases_por_iva((full_text or "") + "\n" + (lines_join or ""))

        # Fallback: total base + IVA único detectado en líneas
        if expected is None:
            ivas_presentes = set()
            if (df_fac is not None) and (not df_fac.empty) and ("TIPO IVA" in df_fac.columns):
                serie_iva = df_fac["TIPO IVA"].dropna().astype(str)
                ivas_presentes = {int(v) for v in serie_iva if v.isdigit() and int(v) > 0}
            total_base = parse_total_base((full_text or "") + "\n" + (lines_join or ""))
            if len(ivas_presentes) == 1 and (total_base is not None):
                unico_iva = next(iter(ivas_presentes))
                expected = {unico_iva: float(total_base)}

        status, sospechosos = cuadre_por_factura(df_fac, expected, tol=0.02)
        df_fac["STATUS"] = status
        all_rows.extend(df_fac.to_dict(orient="records"))

        if expected is None:
            resumen_rows.append({"FACTURA": Path(pdf_path).stem.split()[0], "STATUS": status, "OBS": "No se pudo leer pie de IVA"})
        else:
            for iva, base_exp in expected.items():
                base_cal = df_fac[df_fac["TIPO IVA"]==iva]["BASE"].sum()
                resumen_rows.append({
                    "FACTURA": Path(pdf_path).stem.split()[0],
                    "IVA": iva,
                    "BASE_ESPERADO": round(base_exp,2),
                    "BASE_CALCULADO": round(float(base_cal),2),
                    "DIF": round(float(base_cal)-float(base_exp),2),
                    "STATUS": status,
                })

    df_all = pd.DataFrame(all_rows)
    df_res = pd.DataFrame(resumen_rows)

    # --- Salida TSV / CSV / Excel (todo a out/) ---
    args.tsv_out.mkdir(parents=True, exist_ok=True)
    tsv_path = args.tsv_out / f"{args.provider}_consolidado_dicc-{dic_hash[:8]}.tsv"
    df_all.to_csv(tsv_path, sep="\t", index=False)
    print(f"Guardado TSV en {tsv_path}")

    args.resumen_out.mkdir(parents=True, exist_ok=True)
    res_path = args.resumen_out / f"{args.provider}_resumen_dicc-{dic_hash[:8]}.csv"
    df_res.to_csv(res_path, index=False)
    print(f"Guardado resumen en {res_path}")

    if args.excel_out:
        if exportar_excel is None:
            print("[AVISO] exportar_excel no disponible; instala dependencias de Excel.")
        else:
            df_excel = df_all.rename(columns={
                "#": "NumeroArchivo",
                "FECHA": "Fecha",
                "REF": "NºFactura",
                "PROVEEDOR": "Proveedor",
                "ARTÍCULO": "Descripcion",
                "DESCRIPCIÓN": "Categoria",
                "TIPO IVA": "TipoIVA",
                "BASE": "BaseImponible",
                "STATUS": "Observaciones",
            })
            metadata = {
                "Proveedor": args.provider.upper(),
                "FechaExport": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "ArchivosProcesados": len(pdf_list),
                "HashDiccionario": dic_hash,
            }
            exportar_excel(df_excel, path=str(args.excel_out), metadata=metadata, include_es_portes=False)
            print(f"Guardado Excel en {args.excel_out}")



if __name__ == "__main__":
    main()
