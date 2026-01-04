"""Cache inspection + maintenance helpers.

Dependency-free utilities used by the CLI.

Feature cache layout:
  <cache_dir>/features/<feature_key>/

Each key directory may contain a `meta.json` written by the caching layer.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional


@dataclass(frozen=True)
class FeatureCacheEntry:
    feature_key: str
    path: Path
    created_at: Optional[datetime]
    last_used_at: Optional[datetime]
    source_run_id: Optional[str]
    complete: bool
    size_bytes: int


def _parse_dt(value: Any) -> Optional[datetime]:
    if not value or not isinstance(value, str):
        return None
    s = value.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _dir_size_bytes(path: Path) -> int:
    total = 0
    try:
        for p in path.rglob("*"):
            if p.is_file():
                try:
                    total += p.stat().st_size
                except OSError:
                    continue
    except FileNotFoundError:
        return 0
    return total


def _safe_read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def iter_feature_cache_entries(cache_dir: Path) -> list[FeatureCacheEntry]:
    """Enumerate feature cache keys under `cache_dir/features`.

    Returns entries sorted by (created_at desc, feature_key asc).
    """
    root = Path(cache_dir) / "features"
    if not root.exists():
        return []

    entries: list[FeatureCacheEntry] = []
    for key_dir in root.iterdir():
        if not key_dir.is_dir():
            continue
        meta_path = key_dir / "meta.json"
        meta = _safe_read_json(meta_path) if meta_path.exists() else {}

        entries.append(
            FeatureCacheEntry(
                feature_key=str(meta.get("feature_key") or key_dir.name),
                path=key_dir,
                created_at=_parse_dt(meta.get("created_at")),
                last_used_at=_parse_dt(meta.get("last_used_at")),
                source_run_id=meta.get("source_run_id"),
                complete=bool(meta.get("complete", False)),
                size_bytes=_dir_size_bytes(key_dir),
            )
        )

    def sort_key(e: FeatureCacheEntry):
        created = e.created_at or datetime(1970, 1, 1, tzinfo=timezone.utc)
        return (-created.timestamp(), e.feature_key)

    return sorted(entries, key=sort_key)


@dataclass(frozen=True)
class PruneResult:
    deleted: list[Path]
    kept: list[Path]


def _safe_rmtree(path: Path) -> None:
    """Best-effort deletion."""
    try:
        shutil.rmtree(path)
    except FileNotFoundError:
        return
    except PermissionError:
        # Try to make writable on Windows
        try:
            for p in path.rglob("*"):
                try:
                    p.chmod(0o700)
                except Exception:
                    pass
            shutil.rmtree(path)
        except Exception:
            raise


def prune_feature_cache(
    cache_dir: Path,
    *,
    older_than_days: Optional[int] = None,
    keep_latest: Optional[int] = None,
    dry_run: bool = True,
) -> PruneResult:
    """Prune feature cache keys.

    - If `older_than_days` is provided, deletes entries whose created_at is older
      than now - older_than_days. Entries missing created_at are treated as old.
    - If `keep_latest` is provided, keeps the N newest entries.
    - `dry_run=True` returns the plan without deleting.
    """
    entries = iter_feature_cache_entries(Path(cache_dir))

    # Age filter
    if older_than_days is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=int(older_than_days))

        def is_old(e: FeatureCacheEntry) -> bool:
            if e.created_at is None:
                return True
            return e.created_at < cutoff

        candidates = [e for e in entries if is_old(e)]
    else:
        candidates = list(entries)

    # Protect newest N
    protected: set[Path] = set()
    if keep_latest is not None and int(keep_latest) > 0:
        protected = {e.path for e in entries[: int(keep_latest)]}

    deleted_paths = [e.path for e in candidates if e.path not in protected]
    kept_paths = [e.path for e in entries if e.path not in set(deleted_paths)]

    if not dry_run:
        for p in deleted_paths:
            _safe_rmtree(p)

    return PruneResult(deleted=deleted_paths, kept=kept_paths)
