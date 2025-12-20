from __future__ import annotations
from pathlib import Path


def run_dir(runs_dir: Path, run_id: str) -> Path:
    return runs_dir / run_id

def raw_dir(run_dir: Path) -> Path:
    return run_dir / "raw"


def dataset_dir(run_dir: Path, event_name: str) -> Path:
    return run_dir / "dataset" / event_name


def dataset_split_basepath(run_dir: Path, event_name: str, split: str) -> Path:
    return dataset_dir(run_dir, event_name) / split


def dataset_split_path(run_dir: Path, event_name: str, split: str, fmt: str = "parquet") -> Path:
    return dataset_split_basepath(run_dir, event_name, split).with_suffix(f".{fmt}")

def raw_table_basepath(run_dir: Path, event_name: str) -> Path:
    return raw_dir(run_dir) / event_name

def raw_table_path(run_dir: Path, event_name: str, fmt: str = "parquet") -> Path:
    return raw_table_basepath(run_dir, event_name).with_suffix(f".{fmt}")

def manifest_path(run_dir: Path) -> Path:
    return run_dir / "manifest.json"


def reports_dir(run_dir: Path) -> Path:
    return run_dir / "reports"


def summary_path(run_dir: Path) -> Path:
    return reports_dir(run_dir) / "summary.md"
