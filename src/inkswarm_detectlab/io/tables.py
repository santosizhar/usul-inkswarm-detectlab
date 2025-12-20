from __future__ import annotations
from pathlib import Path
import pandas as pd

def write_parquet(df: pd.DataFrame, path: Path) -> None:
    df.to_parquet(path, index=False)

def read_parquet(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)

def write_csv(df: pd.DataFrame, path: Path) -> None:
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
