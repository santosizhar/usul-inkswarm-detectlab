from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def _normalize_manifest_path(path: Path) -> Path:
    """Accept either a run directory or an explicit manifest.json path."""
    path = Path(path)
    if path.is_dir():
        return path / "manifest.json"
    return path


def write_manifest(path: Path, manifest: Dict[str, Any]) -> None:
    mpath = _normalize_manifest_path(path)
    mpath.parent.mkdir(parents=True, exist_ok=True)
    mpath.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_manifest(path: Path) -> Dict[str, Any]:
    mpath = _normalize_manifest_path(path)
    return json.loads(mpath.read_text(encoding="utf-8"))
