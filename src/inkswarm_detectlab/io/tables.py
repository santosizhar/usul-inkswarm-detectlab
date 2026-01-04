from __future__ import annotations

from pathlib import Path

import pandas as pd


# D-0005: Parquet is mandatory.
# CSV helpers remain ONLY for legacy conversion (dataset parquetify).


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
    """Read a parquet table from a base path without extension.

    For D-0005+ pipelines, only .parquet is accepted.
    """
    pq = base_path_no_ext.with_suffix(".parquet")
    if pq.exists():
        return read_parquet(pq)
    raise FileNotFoundError(f"No parquet table found for {base_path_no_ext} (.parquet)")


def read_auto_legacy(base_path_no_ext: Path) -> pd.DataFrame:
    """Legacy reader: resolves parquet first, then csv.

    Only used by the explicit `dataset parquetify` command.
    """
    pq = base_path_no_ext.with_suffix(".parquet")
    if pq.exists():
        return read_parquet(pq)
    csv = base_path_no_ext.with_suffix(".csv")
    if csv.exists():
        return read_csv(csv)
    raise FileNotFoundError(f"No table found for {base_path_no_ext} (.parquet/.csv)")


def write_auto(df: pd.DataFrame, base_path_no_ext: Path) -> tuple[Path, str, str | None]:
    """Write parquet only (D-0005+). Returns: (path, format, note)."""
    pq = base_path_no_ext.with_suffix(".parquet")
    try:
        write_parquet(df, pq)
    except ImportError as e:
        raise ImportError(
            "Parquet is mandatory. Install a parquet engine (pyarrow) and retry."
        ) from e
    return pq, "parquet", None
