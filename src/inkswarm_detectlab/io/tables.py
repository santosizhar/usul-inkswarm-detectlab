from __future__ import annotations
from pathlib import Path
import pandas as pd


def write_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)

def read_parquet(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)

def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)

def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)

def read_auto(base_path_no_ext: Path) -> pd.DataFrame:
    pq = base_path_no_ext.with_suffix(".parquet")
    if pq.exists():
        return read_parquet(pq)
    csv = base_path_no_ext.with_suffix(".csv")
    if csv.exists():
        return read_csv(csv)
    raise FileNotFoundError(f"No table found for {base_path_no_ext} (.parquet/.csv)")


def write_auto(df: pd.DataFrame, base_path_no_ext: Path) -> tuple[Path, str, str | None]:
    """Write parquet if possible, otherwise fall back to CSV.

    Returns: (actual_path, format, note)
      - format: 'parquet' or 'csv'
      - note: None on parquet success, otherwise the parquet failure reason (short)
    """
    pq = base_path_no_ext.with_suffix(".parquet")
    try:
        write_parquet(df, pq)
        return pq, "parquet", None
    except Exception as e:
        # Keep the note short and stable-ish for summary/manifest.
        note = f"parquet_failed:{e.__class__.__name__}"
        csv = base_path_no_ext.with_suffix(".csv")
        write_csv(df, csv)
        return csv, "csv", note
