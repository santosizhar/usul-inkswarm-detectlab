from __future__ import annotations

from pathlib import Path

from ..config import AppConfig
from ..io.manifest import read_manifest, write_manifest
from ..io.tables import read_parquet, read_csv, write_parquet
from ..io.paths import run_dir as run_dir_for, manifest_path


def parquetify_run(cfg: AppConfig, *, run_id: str, force: bool = False) -> Path:
    """Convert legacy CSV artifacts in a run to Parquet.

    This command exists to support the transition to Parquet-mandatory (D-0005).

    Behavior:
    - Reads `runs/<run_id>/manifest.json`
    - For each artifact whose path ends with `.csv` (or marked format 'csv'):
        - reads the CSV
        - writes a `.parquet` next to it
        - updates manifest entry to point to the `.parquet`
    - CSV files are **not deleted** (migration tool; keeps originals).
    """

    rdir = run_dir_for(cfg, run_id)
    mpath = manifest_path(cfg, run_id)
    manifest = read_manifest(mpath)
    artifacts = manifest.get("artifacts", {})

    updated = False

    for key, meta in list(artifacts.items()):
        p = rdir / meta.get("path", "")
        fmt = (meta.get("format") or "").lower()

        # Only process legacy CSV entries.
        if fmt != "csv" and not str(p).endswith(".csv"):
            continue

        csv_path = p if str(p).endswith(".csv") else p.with_suffix(".csv")
        base = csv_path.with_suffix("")  # path without extension
        target = base.with_suffix(".parquet")

        if not csv_path.exists():
            # Nothing to convert; leave manifest as-is.
            continue

        if target.exists() and not force:
            continue

        # parquetify is the one place we intentionally support legacy CSV reads.
        df = read_csv(csv_path)
        write_parquet(df, target)

        meta2 = dict(meta)
        meta2["path"] = str(target.relative_to(cfg.paths.runs_dir))
        meta2["format"] = "parquet"
        meta2["note"] = None
        artifacts[key] = meta2
        updated = True

    if updated:
        manifest["artifacts"] = artifacts
        write_manifest(mpath, manifest)

    return rdir
