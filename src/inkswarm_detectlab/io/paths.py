from __future__ import annotations
from pathlib import Path

def raw_dir(run_dir: Path) -> Path:
    return run_dir / "raw"

def raw_table_basepath(run_dir: Path, event_name: str) -> Path:
    return raw_dir(run_dir) / event_name

def raw_table_path(run_dir: Path, event_name: str, fmt: str = "parquet") -> Path:
    return raw_table_basepath(run_dir, event_name).with_suffix(f".{fmt}")

def manifest_path(run_dir: Path) -> Path:
    return run_dir / "manifest.json"
