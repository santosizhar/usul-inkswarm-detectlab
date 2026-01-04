from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import os
from typing import Dict, Optional


_COUNTER_FILENAME = ".run_counters.json"


def _load_counters(counter_path: Path) -> Dict[str, int]:
    try:
        if not counter_path.exists():
            return {}
        data = json.loads(counter_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {}
        out: Dict[str, int] = {}
        for k, v in data.items():
            if isinstance(k, str) and isinstance(v, int) and v >= 0:
                out[k] = v
        return out
    except Exception:
        # Fail-closed: if counters are corrupt, do not crash the whole pipeline.
        # Start fresh; the existence-check loop will still prevent collisions.
        return {}


def _save_counters(counter_path: Path, counters: Dict[str, int]) -> None:
    counter_path.parent.mkdir(parents=True, exist_ok=True)
    counter_path.write_text(json.dumps(counters, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def make_run_id_datehash(prefix: str, config_hash8: str) -> str:
    """Legacy: date-based run id, kept for backwards compatibility."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"{prefix}_{ts}_{config_hash8}"


def make_run_id(
    config_hash8: str,
    *,
    runs_dir: Path,
    prefix: str = "RUN",
    width: int = 4,
    counter_filename: str = _COUNTER_FILENAME,
) -> str:
    """Return a human-friendly sequential run id like PREFIX_0001.

    This replaces the older date-based scheme. The run id remains unique by:
      1) tracking the last used counter per prefix in runs_dir/.run_counters.json, and
      2) checking for collisions against existing run folders.

    You can always override the run id explicitly via config/CLI.
    """
    # allow env override without plumbing through config, handy for operators
    env_prefix = os.getenv("INKSWARM_RUN_ID_PREFIX")
    if env_prefix:
        prefix = env_prefix.strip()

    width = int(width)
    if width < 3:
        width = 3
    if width > 8:
        width = 8

    runs_dir = Path(runs_dir)
    runs_dir.mkdir(parents=True, exist_ok=True)
    counter_path = runs_dir / counter_filename

    counters = _load_counters(counter_path)
    n = int(counters.get(prefix, 0))

    # allocate next id; if folder exists, keep bumping until free
    while True:
        n += 1
        run_id = f"{prefix}_{n:0{width}d}"
        if not (runs_dir / run_id).exists():
            break

    counters[prefix] = n
    _save_counters(counter_path, counters)

    # NOTE: config_hash8 is intentionally not embedded in the id anymore.
    # It is still written to the run manifest for provenance.
    return run_id
