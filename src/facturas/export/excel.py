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

    cols = [c for c in preferred if c in df.columns] + [c for c in df.columns if c not in preferred]
    return df.loc[:, cols]


def exportar_a_excel(
    df: pd.DataFrame,
    path: str,
    metadata: Optional[Dict[str, str]] = None,
    include_es_portes: bool = False,
) -> str:
    """
    Exporta a Excel en dos hojas: Lineas y Metadata.
    - Renombra/crea siempre la columna 'Observaciones' (antes 'Flags').
    - Permite excluir portes salvo que `include_es_portes=True`.
    - Aplica autofiltro y anchos cómodos.
    Devuelve la ruta final escrita (por si se renombra por archivo bloqueado).
    """
    # 1) Asegurar columna Observaciones
    if "Flags" in df.columns and "Observaciones" not in df.columns:
        df = df.rename(columns={"Flags": "Observaciones"})
    if "Observaciones" not in df.columns:
        df["Observaciones"] = ""

    # 2) Filtrar portes si procede
    if not include_es_portes and "EsPortes" in df.columns:
        df = df[df["EsPortes"] != True].copy()  # noqa: E712

    # 3) Orden de columnas sugerido
    df = _order_columns(df, include_es_portes)

    # 4) Escritor y formato
    def _write(target_path: str):
        with pd.ExcelWriter(target_path, engine="xlsxwriter") as writer:
            # Hoja de líneas
            df.to_excel(writer, sheet_name="Lineas", index=False)

            wb = writer.book
            ws = writer.sheets["Lineas"]

            # Formato número con coma para BaseImponible si existe
            if "BaseImponible" in df.columns:
                money_fmt = wb.add_format({"num_format": "#,##0.00"})
                col_idx = df.columns.get_loc("BaseImponible")
                ws.set_column(col_idx, col_idx, 12, money_fmt)

            # Anchos razonables
            for i, col in enumerate(df.columns):
                width = 12
                if col in ("Descripcion", "Observaciones"):
                    width = 60 if col == "Descripcion" else 30
                elif col in ("Proveedor", "Categoria"):
                    width = 18
                ws.set_column(i, i, width)

            # Autofiltro
            ws.autofilter(0, 0, max(0, len(df)), max(0, len(df.columns) - 1))

            # Hoja de metadata
            if metadata:
                meta_df = pd.DataFrame(list(metadata.items()), columns=["Campo", "Valor"])
                meta_df.to_excel(writer, sheet_name="Metadata", index=False)
                ws2 = writer.sheets["Metadata"]
                ws2.set_column(0, 0, 24)
                ws2.set_column(1, 1, 60)

    final_path = _safe_write(path, _write)
    return final_path
