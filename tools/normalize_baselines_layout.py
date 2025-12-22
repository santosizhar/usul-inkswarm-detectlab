"""Normalize baselines artifact layout.

This script converts the legacy flat layout:

    <baselines_dir>/<label>__<model>.joblib

into the v2 layout:

    <baselines_dir>/<model>/<label>.joblib

It is safe to run multiple times. By default it COPIES artifacts
(keeps the legacy files). Use --remove-legacy to delete legacy files
after copying.

Example:
    python tools/normalize_baselines_layout.py --baselines-dir runs/RR2_.../models/login_attempt/baselines
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def _parse_legacy_name(path: Path) -> tuple[str, str] | None:
    """Return (label, model) if filename matches legacy pattern."""
    if path.suffix != ".joblib":
        return None
    stem = path.stem
    if "__" not in stem:
        return None
    label, model = stem.rsplit("__", 1)
    if not label or not model:
        return None
    return label, model


def main() -> int:
    ap = argparse.ArgumentParser(description="Normalize baselines artifacts into <model>/<label>.joblib layout.")
    ap.add_argument(
        "--baselines-dir",
        required=True,
        help="Path to a baselines directory (the folder containing *.joblib artifacts).",
    )
    ap.add_argument("--dry-run", action="store_true", help="Print actions without writing.")
    ap.add_argument(
        "--remove-legacy",
        action="store_true",
        help="Remove legacy flat files after successfully copying to v2 layout.",
    )
    args = ap.parse_args()

    baselines_dir = Path(args.baselines_dir).expanduser().resolve()
    if not baselines_dir.exists() or not baselines_dir.is_dir():
        raise SystemExit(f"Not a directory: {baselines_dir}")

    legacy = [p for p in baselines_dir.glob("*.joblib") if "__" in p.stem]
    if not legacy:
        print(f"No legacy artifacts found under: {baselines_dir}")
        return 0

    made = 0
    skipped = 0
    for p in sorted(legacy):
        parsed = _parse_legacy_name(p)
        if not parsed:
            skipped += 1
            continue
        label, model = parsed
        dst_dir = baselines_dir / model
        dst = dst_dir / f"{label}.joblib"

        if dst.exists():
            print(f"SKIP: {dst} already exists (from {p.name})")
            skipped += 1
            continue

        print(f"COPY: {p.name} -> {dst.relative_to(baselines_dir)}")
        if not args.dry_run:
            dst_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)
            if args.remove_legacy:
                p.unlink(missing_ok=True)
        made += 1

    print(f"Done. created={made}, skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
