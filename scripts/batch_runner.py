# -*- coding: utf-8 -*-
"""
Batch runner con selector de carpeta (opcional), robusto y sin romper la CLI batch.
- Si usas --ask-dir (y no pasas --input), abre un diálogo (tkinter) para elegir carpeta.
- Recuerda la última ruta en ~/.facturas_config.json.
- Llama a la CLI no interactiva por cada fichero y captura su JSON.
- Escribe errores con context manager, revisa returncode, y solo marca Excel si realmente existe.
- Genera resumen CSV con columnas: Archivo, Proveedor, Fecha, NºFactura, Reconciliacion, Excel.

Uso típico:
  python scripts/batch_runner.py --ask-dir --out out --excel
  python scripts/batch_runner.py --input "C:\\Users\\TU\\Dropbox\\Facturas\\1T25" --out out --excel --reconcile
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

CONFIG_PATH = Path.home() / ".facturas_config.json"
EXTS = {".pdf", ".jpg", ".jpeg", ".png"}


def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_config(cfg: Dict[str, Any]) -> None:
    try:
        CONFIG_PATH.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def guess_dropbox_default() -> Optional[Path]:
    candidates = [
        Path.home() / "Dropbox",
        Path.home() / "Dropbox (Personal)",
        Path.home() / "Dropbox (Empresa)",
        Path.home() / "OneDrive" / "Dropbox",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def ask_directory(initial: Optional[Path]) -> Optional[Path]:
    """Devuelve una carpeta elegida por el usuario. GUI si hay tkinter; si no, consola."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk(); root.withdraw()
        init = str(initial) if initial and initial.exists() else str(Path.home())
        chosen = filedialog.askdirectory(initialdir=init, title="Selecciona la carpeta con facturas")
        try:
            root.update(); root.destroy()
        except Exception:
            pass
        return Path(chosen) if chosen else None
    except Exception:
        try:
            p = input(f"Carpeta con facturas [{initial or ''}]: ").strip().strip('"')
            if not p and initial:
                return initial
            return Path(p) if p else None
        except EOFError:
            return None


def run_cli_one(pdf: Path, outdir: Path, excel: bool, reconcile: bool, total: Optional[str]) -> Dict[str, Any]:
    """Lanza la CLI por un fichero y devuelve un dict normalizado para el resumen."""
    cmd: List[str] = [sys.executable, "-m", "src.facturas.cli", str(pdf), "--lines"]
    if reconcile:
        cmd.append("--reconcile")
    if total:
        cmd += ["--total", total]
    cmd += ["--outdir", str(outdir)]

    xlsx_path: Optional[Path] = None
    if excel:
        safe_base = re.sub(r"[^\w\-]+", "_", pdf.stem)
        xlsx_path = outdir / f"{safe_base}.xlsx"
        cmd += ["--excel", str(xlsx_path)]

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if proc.stderr or proc.returncode != 0:
        with (outdir / "errors.log").open("a", encoding="utf-8") as fh:
            fh.write(f"[{pdf.name}] returncode={proc.returncode}\n")
            if proc.stderr:
                fh.write(proc.stderr + "\n")

    # Parsear stdout -> JSON
    try:
        obj = json.loads(proc.stdout)
    except Exception:
        snippet = (proc.stdout or "")[:400].replace("\n", "\\n")
        with (outdir / "errores_resumen.txt").open("a", encoding="utf-8") as fh:
            fh.write(f"ERROR JSON: {pdf} :: stdout[:400]={snippet}\n")
        obj = {}

    # Normalizar header/estado
    if isinstance(obj, dict) and "Header" in obj and isinstance(obj["Header"], dict):
        hdr = obj["Header"]
        estado = obj.get("Reconciliacion") or obj.get("Estado") or ""
    elif isinstance(obj, dict):
        hdr = obj
        estado = obj.get("Estado") or ""
    else:
        hdr = {}
        estado = ""

    # Solo afirmar Excel si realmente existe
    excel_str = ""
    if excel and xlsx_path and xlsx_path.exists():
        excel_str = str(xlsx_path)

    return {
        "Archivo": hdr.get("Archivo", pdf.name),
        "Proveedor": hdr.get("Proveedor", ""),
        "Fecha": hdr.get("Fecha", ""),
        "NºFactura": hdr.get("NºFactura", ""),
        "Reconciliacion": estado,
        "Excel": excel_str,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Lanzador batch para la CLI de facturas")
    ap.add_argument("--input", help="Carpeta con facturas (PDF/JPG/PNG)")
    ap.add_argument("--ask-dir", action="store_true", help="Preguntar/seleccionar carpeta si no se pasa --input")
    ap.add_argument("--out", default="out", help="Carpeta de salida (default: out)")
    ap.add_argument("--excel", action="store_true", help="Generar Excel por factura")
    ap.add_argument("--reconcile", action="store_true", help="Intentar reconciliar si hay total")
    ap.add_argument("--total", help="Total con IVA para forzar reconciliación (opcional)")
    args = ap.parse_args()

    cfg = load_config()

    input_dir: Optional[Path] = Path(args.input) if args.input else None
    if not input_dir and args.ask_dir:
        default = Path(cfg.get("last_input_dir")) if cfg.get("last_input_dir") else guess_dropbox_default()
        input_dir = ask_directory(default)
    if not input_dir:
        ap.error("Necesitas --input o usar --ask-dir para seleccionar carpeta.")
    if not input_dir.exists():
        ap.error(f"No existe la carpeta: {input_dir}")

    outdir = Path(args.out); outdir.mkdir(parents=True, exist_ok=True)

    # Guardar última carpeta usada
    cfg["last_input_dir"] = str(input_dir)
    save_config(cfg)

    files = [p for p in input_dir.rglob("*") if p.is_file() and p.suffix.lower() in EXTS]
    files.sort()
    print(f"Procesando {len(files)} ficheros de {input_dir}…")

    rows: List[Dict[str, Any]] = []
    for i, pdf in enumerate(files, 1):
        print(f"[{i}/{len(files)}] {pdf}")
        try:
            row = run_cli_one(pdf, outdir, args.excel, args.reconcile, args.total)
        except Exception:
            row = {
                "Archivo": pdf.name,
                "Proveedor": "",
                "Fecha": "",
                "NºFactura": "",
                "Reconciliacion": "ERROR",
                "Excel": "",
            }
        rows.append(row)

    csv_path = outdir / "resumen_batch.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["Archivo","Proveedor","Fecha","NºFactura","Reconciliacion","Excel"])
        w.writeheader()
        w.writerows(rows)

    ok = sum(1 for r in rows if r.get("Reconciliacion", "") != "ERROR")
    err = sum(1 for r in rows if r.get("Reconciliacion", "") == "ERROR")

    print("---------------------------------------------")
    print(f"Listo. Resumen: {csv_path}")
    print(f"Éxitos: {ok}  |  Errores: {err}  |  Total: {len(rows)}")
    print(f"Errores detallados (si los hubo): {outdir / 'errors.log'}")


if __name__ == "__main__":
    main()

