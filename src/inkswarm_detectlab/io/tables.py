from __future__ import annotations

from pathlib import Path
import pandas as pd


_PARQUET_HELP = (
    "Parquet is mandatory as of D-0005. Install the parquet engine and retry.\n"
    "Recommended: `uv pip install pyarrow` (or ensure project deps are installed).\n"
    "If you are working with an older run that only has CSV artifacts, run:\n"
    "  `uv run detectlab dataset parquetify -c <config.yaml> --run-id <RUN_ID> --force`\n"
)


def write_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        df.to_parquet(path, index=False)
    except Exception as e:
        # Pandas raises ImportError/ValueError when no parquet engine is available.
        raise RuntimeError(f"Failed to write Parquet to {path}: {e}\n\n{_PARQUET_HELP}") from e


def read_parquet(path: Path) -> pd.DataFrame:
    try:
        return pd.read_parquet(path)
    except Exception as e:
        raise RuntimeError(f"Failed to read Parquet from {path}: {e}\n\n{_PARQUET_HELP}") from e


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def read_auto(base_path_no_ext: Path) -> pd.DataFrame:
    """Read Parquet only.

    If a legacy CSV exists, fail closed with instructions to run `dataset parquetify`.
    """
    pq = base_path_no_ext.with_suffix(".parquet")
    if pq.exists():
        return read_parquet(pq)

    csv = base_path_no_ext.with_suffix(".csv")
    if csv.exists():
        raise RuntimeError(
            f"Legacy CSV artifact detected: {csv}.\n\n{_PARQUET_HELP}"
        )

    raise FileNotFoundError(f"No table found for {base_path_no_ext} (.parquet expected)")


def write_auto(df: pd.DataFrame, base_path_no_ext: Path) -> tuple[Path, str, str | None]:
    """Write Parquet only (mandatory as of D-0005).

    Returns: (actual_path, format, note) — kept for backward compatibility.
      - format: always 'parquet'
      - note: always None
    """
    pq = base_path_no_ext.with_suffix(".parquet")
    write_parquet(df, pq)
    return pq, "parquet", None
