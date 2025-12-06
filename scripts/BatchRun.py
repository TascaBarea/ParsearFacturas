import os, json, argparse, csv, subprocess, sys
from collections import defaultdict

def run_cli(pdf, outdir):
    cmd = [sys.executable, "-m", "src.facturas.cli", pdf, "--lines", "--no-reconcile", "--outdir", outdir]
    subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def find_metrics(outdir):
    for f in os.listdir(outdir):
        if f.startswith("metrics_") and f.endswith(".json"):
            with open(os.path.join(outdir, f), "r", encoding="utf-8") as fh:
                yield json.load(fh)

def aggregate(metrics_iter):
    byprov = defaultdict(lambda: {"docs":0, "lineas":0, "ok":0, "parsed_sum":0.0, "flags_sum":0.0})
    rows = []
    for m in metrics_iter:
        prov = m.get("Proveedor") or "DESCONOCIDO"
        byprov[prov]["docs"] += 1
        byprov[prov]["lineas"] += int(m.get("Lineas",0))
        ok = 1 if float(m.get("ParsedRatio",0)) >= 0.8 else 0
        byprov[prov]["ok"] += ok
        byprov[prov]["parsed_sum"] += float(m.get("ParsedRatio",0))
        byprov[prov]["flags_sum"] += float(m.get("FlagsRatio",0))
        rows.append(m)
    agg = []
    for prov, d in byprov.items():
        docs = d["docs"]
        agg.append({
            "Proveedor": prov,
            "Docs": docs,
            "ParsedRatioMedio": round(d["parsed_sum"]/docs, 3),
            "FlagsRatioMedio": round(d["flags_sum"]/docs, 3),
            "OK>=0.8": d["ok"],
            "LineasTotales": d["lineas"],
        })
    agg.sort(key=lambda r: (-r["Docs"], -r["ParsedRatioMedio"]))
    return rows, agg

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Carpeta con PDFs/JPGs")
    ap.add_argument("--outdir", required=True, help="Carpeta salida (metrics/Excel)")
    ap.add_argument("--csv", default="ranking_proveedores.csv")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    # 1) Ejecutar CLI por cada archivo
    for root, _, files in os.walk(args.input):
        for fn in files:
            if fn.lower().endswith((".pdf",".jpg",".jpeg",".png")):
                run_cli(os.path.join(root, fn), args.outdir)

    # 2) Agregar métricas
    rows, agg = aggregate(find_metrics(args.outdir))

    # 3) Guardar ranking
    csv_path = os.path.join(args.outdir, args.csv)
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(agg[0].keys()) if agg else ["Proveedor","Docs","ParsedRatioMedio","FlagsRatioMedio","OK>=0.8","LineasTotales"])
        w.writeheader()
        for r in agg:
            w.writerow(r)

    print(f"Listo: ranking en {csv_path}. Top 10 proveedores:")
    for r in agg[:10]:
        print(f" - {r['Proveedor']}: docs={r['Docs']}, parsed={r['ParsedRatioMedio']}, OK>=0.8={r['OK>=0.8']}")

if __name__ == "__main__":
    main()
