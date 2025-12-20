from __future__ import annotations

"""Share/evidence bundle builder.

A *share package* is the minimal folder you can zip and send to someone else.

Design goals:
- Self-contained: contains the UI bundle and the key reports.
- Comparable: writes an evidence_manifest.json with sha256 hashes so two exports
  can be compared in RR / determinism checks.
- Fail-soft: if optional artifacts are missing, keep going and include what exists.

Layout (created under runs/<run_id>/share/):
  share/
    README_SHARE.md
    evidence_manifest.json
    ui_bundle/...
    reports/...
    reports/models/...      (copied from runs/<run_id>/models)
    logs/...                (copied from runs/<run_id>/logs)
    meta/manifest.json      (copied from runs/<run_id>/manifest.json)
    meta/ui_summary.json    (copied from runs/<run_id>/ui/ui_summary.json)

Notes
-----
- The UI bundle is normally produced by `inkswarm_detectlab.ui.bundle.export_ui_bundle`
  into runs/<run_id>/share/ui_bundle/. This module does not generate the UI; it only
  packages and fingerprints evidence.
"""

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _copy_tree(src: Path, dst: Path) -> int:
    """Copy a directory tree into dst (dst will be created). Returns file count."""
    if not src.exists():
        return 0
    count = 0
    for p in sorted([x for x in src.rglob("*") if x.is_file()]):
        rel = p.relative_to(src)
        out = dst / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(p.read_bytes())
        count += 1
    return count


def _copy_file(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(src.read_bytes())
    return True


def _clear_share_dir(share_root: Path) -> None:
    """Remove previous share artifacts but keep ui_bundle/ if present."""
    if not share_root.exists():
        return
    for child in share_root.iterdir():
        if child.name == "ui_bundle":
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink(missing_ok=True)


def export_evidence_bundle(*, run_dir: Path, force: bool = True) -> Path:
    """Create/refresh runs/<run_id>/share evidence bundle.

    Parameters
    ----------
    run_dir:
        Path to runs/<run_id>.
    force:
        If True, refresh share/ (keeps ui_bundle/).
    """
    run_dir = Path(run_dir)
    if not run_dir.exists():
        raise FileNotFoundError(f"run_dir not found: {run_dir}")

    share_root = run_dir / "share"
    share_root.mkdir(parents=True, exist_ok=True)
    if force:
        _clear_share_dir(share_root)

    # 1) README_SHARE.md
    readme = share_root / "README_SHARE.md"
    readme_text = """# Inkswarm DetectLab — Share Package

This folder is meant to be sent as-is.

## Open this first
- `ui_bundle/index.html` (interactive, stakeholder-friendly)

## Then read
- `reports/mvp_handover.md` (plain-language interpretation)

## For deeper details (optional)
- `reports/` (pipeline outputs and diagnostics)
- `logs/` (if something failed or looks odd)
- `meta/manifest.json` and `meta/ui_summary.json` (machine-readable evidence)

If anything is missing, it usually means that step failed upstream — see `logs/`.
"""
    readme.write_text(readme_text, encoding="utf-8")

    # 2) UI bundle (expected at share/ui_bundle)
    ui_dst = share_root / "ui_bundle"
    if not ui_dst.exists():
        # Fallback: allow a bundle sitting at runs/<run_id>/ui_bundle
        ui_src = run_dir / "ui_bundle"
        _copy_tree(ui_src, ui_dst)

    # 3) Reports
    reports_dst = share_root / "reports"
    reports_src = run_dir / "reports"
    _copy_tree(reports_src, reports_dst)

    # 3b) Models under reports/models (matches RR evidence samples)
    models_src = run_dir / "models"
    models_dst = reports_dst / "models"
    _copy_tree(models_src, models_dst)

    # 4) Logs
    logs_src = run_dir / "logs"
    logs_dst = share_root / "logs"
    _copy_tree(logs_src, logs_dst)

    # 5) Meta: manifest + ui summary
    meta_dst = share_root / "meta"
    _copy_file(run_dir / "manifest.json", meta_dst / "manifest.json")
    _copy_file(run_dir / "ui" / "ui_summary.json", meta_dst / "ui_summary.json")

    # 6) Evidence manifest
    files: List[Dict[str, Any]] = []
    for p in sorted([x for x in share_root.rglob("*") if x.is_file()]):
        rel = p.relative_to(share_root).as_posix()
        if rel == "evidence_manifest.json":
            continue
        files.append({"path": rel, "sha256": _sha256(p), "bytes": p.stat().st_size})

    manifest: Dict[str, Any] = {
        "schema_version": 1,
        "root": str(share_root),
        "files": files,
    }
    (share_root / "evidence_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return share_root
