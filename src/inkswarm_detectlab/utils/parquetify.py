from __future__ import annotations

from pathlib import Path

from ..config import AppConfig
from ..io.manifest import read_manifest, write_manifest
from ..io.tables import read_auto_legacy, write_parquet
from ..io.paths import run_dir as run_dir_for, manifest_path


def parquetify_run(cfg: AppConfig, *, run_id: str, force: bool = False) -> Path:
    """Convert legacy CSV artifacts in a run to Parquet.

    D-0005 makes Parquet mandatory for new writes. This command remains as an
    explicit migration tool for:
      - older runs that still contain `.csv` artifacts
      - fixtures / historical outputs that need upgrading

    Behavior:
      - Reads `runs/<run_id>/manifest.json`
      - For each artifact whose path ends with `.csv`, reads it and writes a
        `.parquet` next to it
      - Updates manifest artifact entries to point to the parquet path/format
    """
    rdir = run_dir_for(cfg.paths.runs_dir, run_id)
    mpath = manifest_path(rdir)
    manifest = read_manifest(mpath)

    artifacts = manifest.get("artifacts", {}) or {}
    updated = False

    for key, meta in list(artifacts.items()):
        p_str = (meta or {}).get("path")
        fmt = (meta or {}).get("format")
        if not p_str:
            continue
        p = cfg.paths.runs_dir / p_str
        if fmt == "csv" or str(p).endswith(".csv"):
            base = p.with_suffix("")  # strip .csv
            target = base.with_suffix(".parquet")
            if target.exists() and not force:
                continue

            df = read_auto_legacy(base)  # legacy resolver: parquet first, then csv
            # IMPORTANT: write to the parquet *target* (with extension), not the base.
            write_parquet(df, target)

            meta2 = dict(meta)
            meta2["path"] = str(target.relative_to(cfg.paths.runs_dir))
            meta2["format"] = "parquet"
            # Clear any historical notes that were only about parquet/csv fallback.
            note = (meta2.get("note") or "").strip()
            if note.startswith("parquet_failed") or note.startswith("CSV fallback"):
                meta2["note"] = None
            artifacts[key] = meta2
            updated = True

    if updated:
        manifest["artifacts"] = artifacts
        write_manifest(mpath, manifest)

    return rdir
