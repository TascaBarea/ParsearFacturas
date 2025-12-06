# src/facturas/export/excel.py
import os
import time
from typing import Optional, Dict

import pandas as pd

def _safe_write(path: str, write_fn):
    """Intenta escribir en `path`. Si está bloqueado, crea una copia con timestamp."""
    try:
        write_fn(path)
        return path
    except PermissionError:
        base, ext = os.path.splitext(path)
        new_path = f"{base}_{time.strftime('%Y%m%d_%H%M%S')}{ext}"
        write_fn(new_path)
        print(f"[AVISO] '{path}' estaba en uso. Guardado como: {new_path}")
        return new_path

def _order_columns(df: pd.DataFrame, include_es_portes: bool) -> pd.DataFrame:
    preferred = [
        "NumeroArchivo", "Fecha", "NºFactura", "Proveedor",
        "Descripcion", "Categoria", "TipoIVA", "BaseImponible", "Observaciones",
    ]
    if include_es_portes and "EsPortes" in df.columns:
        preferred.append("EsPortes")
    cols = [c for c in preferred if c in df.columns]
    return df.loc[:, cols]

def exportar_excel(
    df_all: pd.DataFrame,
    df_resumen: pd.DataFrame,
    path: str,
    metadata: Optional[Dict[str, str]] = None,
    include_es_portes: bool = False,
) -> str:
    """
    Exporta a Excel en tres hojas: Facturas, Resumen y Metadata.
    - Renombra/crea siempre la columna 'Observaciones'.
    - Muestra u oculta la columna 'EsPortes' según flag.
    - Formato numérico europeo y autofiltros.
    """
    if "Flags" in df_all.columns and "Observaciones" not in df_all.columns:
        df_all = df_all.rename(columns={"Flags": "Observaciones"})
    if "Observaciones" not in df_all.columns:
        df_all["Observaciones"] = ""

    if not include_es_portes and "EsPortes" in df_all.columns:
        df_all = df_all.drop(columns=["EsPortes"])

    df_all = _order_columns(df_all, include_es_portes)

    def _write(target_path: str):
        with pd.ExcelWriter(target_path, engine="xlsxwriter") as writer:
            # Hoja 1: Facturas
            df_all.to_excel(writer, sheet_name="Facturas", index=False)
            wb = writer.book
            ws1 = writer.sheets["Facturas"]

            if "BaseImponible" in df_all.columns:
                money_fmt = wb.add_format({"num_format": "#,##0.00"})
                col_idx = df_all.columns.get_loc("BaseImponible")
                ws1.set_column(col_idx, col_idx, 12, money_fmt)

            for i, col in enumerate(df_all.columns):
                width = 12
                if col in ("Descripcion", "Observaciones"):
                    width = 60 if col == "Descripcion" else 30
                elif col in ("Proveedor", "Categoria"):
                    width = 18
                ws1.set_column(i, i, width)
            ws1.autofilter(0, 0, max(0, len(df_all)), max(0, len(df_all.columns) - 1))

            # Hoja 2: Resumen
            df_resumen.to_excel(writer, sheet_name="Resumen", index=False)
            ws2 = writer.sheets["Resumen"]
            for i, col in enumerate(df_resumen.columns):
                width = 20 if "Base" in col else 15
                fmt = wb.add_format({"num_format": "#,##0.00"}) if "Base" in col else None
                ws2.set_column(i, i, width, fmt)
            ws2.autofilter(0, 0, max(0, len(df_resumen)), max(0, len(df_resumen.columns) - 1))

            # Hoja 3: Metadata
            if metadata:
                meta_df = pd.DataFrame(list(metadata.items()), columns=["Campo", "Valor"])
                meta_df.to_excel(writer, sheet_name="Metadata", index=False)
                ws3 = writer.sheets["Metadata"]
                ws3.set_column(0, 0, 24)
                ws3.set_column(1, 1, 60)

    return _safe_write(path, _write)
