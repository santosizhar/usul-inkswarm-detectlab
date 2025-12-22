from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

from ..config import AppConfig
from ..utils.hashing import stable_hash_dict


CACHE_VERSION = 1

# These are the run subtrees required to reuse the expensive data/feature build work cross-run.
RUN_CACHE_REQUIRED_RELS: tuple[str, ...] = (
    "dataset",
    "features",
)
RUN_CACHE_OPTIONAL_RELS: tuple[str, ...] = (
    "raw",
)


@dataclass(frozen=True)
class FeatureCacheInfo:
    cache_key: str
    cache_dir: Path
    is_hit: bool


def _strip_run_variability(cfg_dump: dict) -> dict:
    """Remove keys that can change between runs but do not affect feature computation."""
    d = dict(cfg_dump)
    # Run config contains run_id etc.
    run = dict(d.get("run", {}) or {})
    for k in ("run_id", "run_id_prefix", "run_id_strategy"):
        run.pop(k, None)
    d["run"] = run

    # paths are repo-local and can vary across machines; not part of the computation itself
    d.pop("paths", None)
    return d


def feature_cache_key(cfg: AppConfig) -> str:
    cfg_dump = cfg.model_dump()
    payload = {
        "cache_version": CACHE_VERSION,
        "cfg": _strip_run_variability(cfg_dump),
    }
    # keep the directory name short but stable
    return stable_hash_dict(payload)[:16]


def feature_cache_dir(cfg: AppConfig) -> Path:
    return Path(cfg.paths.cache_dir) / "features" / feature_cache_key(cfg)


def _ensure_all_present(base: Path, rels: Iterable[str]) -> bool:
    for rel in rels:
        if not (base / rel).exists():
            return False
    return True


def try_restore_feature_artifacts(
    cfg: AppConfig,
    run_dir: Path,
    *,
    force_rebuild: bool = False,
) -> FeatureCacheInfo:
    """Attempt to restore feature artifacts from shared cache into this run directory.

    Returns FeatureCacheInfo with is_hit=True on a successful restore.
    """
    cdir = feature_cache_dir(cfg)
    key = feature_cache_key(cfg)

    if force_rebuild:
        return FeatureCacheInfo(cache_key=key, cache_dir=cdir, is_hit=False)

    if not cdir.exists():
        return FeatureCacheInfo(cache_key=key, cache_dir=cdir, is_hit=False)

    if not _ensure_all_present(cdir, RUN_CACHE_REQUIRED_RELS):
        # cache is incomplete; ignore it (fail-closed)
        return FeatureCacheInfo(cache_key=key, cache_dir=cdir, is_hit=False)

    run_dir.mkdir(parents=True, exist_ok=True)    # Copy required subtrees (dataset + features). Raw is optional.
    for rel in RUN_CACHE_REQUIRED_RELS:
        src = cdir / rel
        dst = run_dir / rel
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)

    for rel in RUN_CACHE_OPTIONAL_RELS:
        src = cdir / rel
        if src.exists():
            dst = run_dir / rel
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)

    # Write a small marker for provenance

    marker = {
        "cache_version": CACHE_VERSION,
        "cache_key": key,
        "cache_dir": str(cdir),
        "restored_at": datetime.now(timezone.utc).isoformat(),
    }
    (run_dir / "feature_cache_hit.json").write_text(json.dumps(marker, indent=2), encoding="utf-8")

    return FeatureCacheInfo(cache_key=key, cache_dir=cdir, is_hit=True)


def save_feature_artifacts_to_cache(cfg: AppConfig, run_dir: Path) -> FeatureCacheInfo:
    """Save current run feature artifacts into the shared cache (best-effort).

    This overwrites any existing cache entry for the same key.
    """
    cdir = feature_cache_dir(cfg)
    key = feature_cache_key(cfg)

    if not _ensure_all_present(run_dir, RUN_CACHE_REQUIRED_RELS):
        # Do not create partial caches.
        return FeatureCacheInfo(cache_key=key, cache_dir=cdir, is_hit=False)

    tmp = cdir.with_name(cdir.name + ".tmp")
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True, exist_ok=True)    # Copy required subtrees (dataset + features). Raw is optional.
    for rel in RUN_CACHE_REQUIRED_RELS:
        shutil.copytree(run_dir / rel, tmp / rel)

    for rel in RUN_CACHE_OPTIONAL_RELS:
        if (run_dir / rel).exists():
            shutil.copytree(run_dir / rel, tmp / rel)

    meta = {

        "cache_version": CACHE_VERSION,
        "cache_key": key,
        "source_run_dir": str(run_dir),
        "source_run_id": getattr(cfg.run, "run_id", None),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    (tmp / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    if cdir.exists():
        shutil.rmtree(cdir)
    tmp.rename(cdir)

    return FeatureCacheInfo(cache_key=key, cache_dir=cdir, is_hit=False)
