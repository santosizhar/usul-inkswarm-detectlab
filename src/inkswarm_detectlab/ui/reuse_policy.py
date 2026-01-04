from __future__ import annotations

"""Centralized reuse policy (D-0024).

The pipeline components often follow fail-closed overwrite policies (raise if outputs exist unless force).
Notebook step wrappers therefore need a consistent way to decide:

- should we reuse existing outputs?
- or should we compute (possibly forcing overwrites)?

This module provides a manifest-first policy:
- prefer reusing when manifest["steps"][<step_name>] matches current config_hash AND expected outputs exist
- fall back to disk existence checks when manifest is missing or incomplete
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from ..io.manifest import read_manifest
from ..io.paths import manifest_path
from .step_contract import ReuseDecision


def _outputs_exist(expected: Dict[str, Path]) -> Tuple[bool, list[str]]:
    missing: list[str] = []
    for k, p in expected.items():
        p = Path(p)
        # Directories are considered "existing" if present.
        if k.endswith("_dir"):
            if not p.exists():
                missing.append(k)
            continue
        if not p.exists():
            missing.append(k)
    return (len(missing) == 0, missing)


def _get_manifest_step(manifest: Dict[str, Any], step_name: str) -> Optional[Dict[str, Any]]:
    steps = manifest.get("steps")
    if not isinstance(steps, dict):
        return None
    v = steps.get(step_name)
    return v if isinstance(v, dict) else None


def decide_reuse(
    *,
    run_dir: Path,
    step_name: str,
    current_config_hash: str,
    expected_outputs: Dict[str, Path],
    reuse_if_exists: bool,
    force: bool,
) -> ReuseDecision:
    """Return a ReuseDecision describing compute vs reuse vs skipped.

    NOTE:
    - This does not inspect the *contents* of artifacts; only presence + fingerprint match.
    - Wrappers may still choose to do additional checks (e.g., model discovery).
    """
    if force:
        return ReuseDecision(mode="compute", reason="force=True", used_manifest=False, forced=True)

    ok_outputs, missing = _outputs_exist(expected_outputs)
    if not reuse_if_exists:
        return ReuseDecision(
            mode="compute",
            reason="reuse_if_exists=False (manual override)",
            used_manifest=False,
            forced=False,
        )

    mpath = manifest_path(Path(run_dir))
    if not mpath.exists():
        if ok_outputs:
            return ReuseDecision(
                mode="reuse",
                reason="Expected outputs exist on disk (manifest missing).",
                used_manifest=False,
                forced=False,
            )
        return ReuseDecision(
            mode="compute",
            reason=f"Missing outputs on disk: {', '.join(missing)} (manifest missing).",
            used_manifest=False,
            forced=False,
        )

    try:
        manifest = read_manifest(mpath)
    except Exception:  # noqa: BLE001
        manifest = {}

    step = _get_manifest_step(manifest, step_name)
    if step and isinstance(step.get("inputs"), dict):
        prev_hash = step["inputs"].get("config_hash")
        if prev_hash == current_config_hash and ok_outputs:
            return ReuseDecision(
                mode="reuse",
                reason="Manifest step record matches current config hash and outputs exist.",
                used_manifest=True,
                forced=False,
            )

        if ok_outputs:
            # outputs exist but fingerprint mismatch; honor reuse_if_exists (BQ2=C) but warn via reason
            return ReuseDecision(
                mode="reuse",
                reason="Outputs exist, but manifest fingerprint differs/missing; reusing because reuse_if_exists=True.",
                used_manifest=True,
                forced=False,
            )

    if ok_outputs:
        return ReuseDecision(
            mode="reuse",
            reason="Expected outputs exist on disk (no usable manifest step record).",
            used_manifest=False,
            forced=False,
        )

    return ReuseDecision(
        mode="compute",
        reason=f"Missing outputs on disk: {', '.join(missing)}",
        used_manifest=bool(step),
        forced=False,
    )
