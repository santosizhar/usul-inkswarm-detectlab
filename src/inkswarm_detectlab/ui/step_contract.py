from __future__ import annotations

"""Typed step results for notebook/CLI visibility (D-0023).

Design goals:
- Keep the pipeline architecture intact.
- Make each "step" return a structured result that can be:
  - printed in notebooks
  - persisted into the run manifest (manifest.json)
  - used to explain reuse vs recompute decisions

This module is stdlib-only (no pandas/numpy) to keep imports light.
"""

from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..io.manifest import read_manifest, write_manifest
from ..io.paths import manifest_path


@dataclass(frozen=True)
class ReuseDecision:
    """Describes whether a step reused artifacts or recomputed them."""
    mode: str  # compute|reuse|skipped
    reason: str
    used_manifest: bool = False
    forced: bool = False


@dataclass(frozen=True)
class StepInputs:
    cfg_path: str
    run_id: str
    config_hash: str
    params: Dict[str, Any] = field(default_factory=dict)
    toggles: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ArtifactRef:
    kind: str
    path: str
    exists: bool = False


@dataclass(frozen=True)
class StepResult:
    name: str
    status: str  # ok|skipped|fail|partial
    decision: ReuseDecision
    inputs: StepInputs
    outputs: Dict[str, ArtifactRef] = field(default_factory=dict)
    summary: Dict[str, Any] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        # asdict is safe; all fields are JSON-serializable by design
        return asdict(self)


def _artifact_ref(kind: str, path: Path) -> ArtifactRef:
    p = Path(path)
    return ArtifactRef(kind=kind, path=str(p), exists=p.exists())


def record_step_result(run_dir: Path, step: StepResult) -> Dict[str, Any]:
    """Persist the latest StepResult for a step into manifest.json.

    Storage format:
        manifest["steps"][<step_name>] = step.to_dict()

    We only store the latest result per step to keep the manifest small.
    """
    rdir = Path(run_dir)
    mpath = manifest_path(rdir)
    manifest: Dict[str, Any] = read_manifest(mpath) if mpath.exists() else {"artifacts": {}}
    steps = manifest.get("steps")
    if not isinstance(steps, dict):
        steps = {}
    steps[step.name] = step.to_dict()
    manifest["steps"] = steps
    write_manifest(mpath, manifest)
    return manifest


def expected_outputs_exist(outputs: Dict[str, Path]) -> bool:
    """Convenience helper for wrapper code."""
    return all(Path(p).exists() for p in outputs.values())
