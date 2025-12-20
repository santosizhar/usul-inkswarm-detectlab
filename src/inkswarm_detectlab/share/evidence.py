from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Tuple
import hashlib


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _copy_if_exists(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def _copy_tree(src_dir: Path, dst_dir: Path, *, patterns: List[str]) -> List[Path]:
    copied: List[Path] = []
    if not src_dir.exists():
        return copied
    dst_dir.mkdir(parents=True, exist_ok=True)
    for pat in patterns:
        for src in src_dir.glob(pat):
            if src.is_file():
                rel = src.relative_to(src_dir)
                dst = dst_dir / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                copied.append(dst)
    return copied


def export_evidence_bundle(*, run_dir: Path) -> Path:
    """Create a tidy, shareable evidence layout under runs/<run_id>/share/.

    This is intended for non-technical recipients:
      - open share/ui_bundle/index.html
      - read share/reports/mvp_handover.md
      - optionally inspect share/meta/manifest.json + ui_summary.json
      - logs live under share/logs/
    """
    share_root = run_dir / "share"
    share_root.mkdir(parents=True, exist_ok=True)

    # Expected sources
    ui_bundle = share_root / "ui_bundle"  # already produced by UI exporter
    reports_src = run_dir / "reports"
    logs_src = run_dir / "logs"
    meta_src = run_dir  # manifest/summary live at root; ui summary under ui/

    # Targets
    reports_dst = share_root / "reports"
    logs_dst = share_root / "logs"
    meta_dst = share_root / "meta"

    copied_files: List[Path] = []

    # Reports (markdown)
    copied_files += _copy_tree(reports_src, reports_dst, patterns=["*.md", "*.json"])

    # Baseline/model reports that are not already in /reports
    copied_files += _copy_tree(run_dir / "models", reports_dst / "models", patterns=["**/*.md", "**/*.json"])

    # Logs
    copied_files += _copy_tree(logs_src, logs_dst, patterns=["*.log", "*.txt"])

    # Meta essentials
    copied_files += [p for p in [
        meta_src / "manifest.json",
        meta_src / "summary.json",
    ] if _copy_if_exists(p, meta_dst / p.name)]

    ui_summary = run_dir / "ui" / "ui_summary.json"
    _copy_if_exists(ui_summary, meta_dst / "ui_summary.json")
    if (meta_dst / "ui_summary.json").exists():
        copied_files.append(meta_dst / "ui_summary.json")

    # Small README for recipients
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
    copied_files.append(readme)

    # Evidence manifest (hashes so two exports are comparable)
    # We hash files inside share/ excluding the UI bundle assets (large) except index.html + app.js.
    manifest: Dict[str, Any] = {
        "schema_version": 1,
        "root": str(share_root),
        "files": [],
    }

    def _should_hash(p: Path) -> bool:
        try:
            rel = p.relative_to(share_root).as_posix()
        except Exception:
            return False
        if rel.startswith("ui_bundle/"):
            return rel in {"ui_bundle/index.html", "ui_bundle/app.js", "ui_bundle/style.css"}
        return True

    for p in sorted([x for x in share_root.rglob("*") if x.is_file()]):
        if not _should_hash(p):
            continue
        rel = p.relative_to(share_root).as_posix()
        manifest["files"].append({"path": rel, "sha256": _sha256(p), "bytes": p.stat().st_size})

    (share_root / "evidence_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return share_root
