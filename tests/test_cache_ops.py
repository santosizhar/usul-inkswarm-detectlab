from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from pathlib import Path

from inkswarm_detectlab.cache.ops import iter_feature_cache_entries, prune_feature_cache


def _mk_entry(cache_dir: Path, key: str, *, created_at: datetime | None) -> Path:
    d = cache_dir / "features" / key
    d.mkdir(parents=True, exist_ok=True)
    # Add some payload to size calc
    (d / "payload.bin").write_bytes(b"x" * 10)
    meta = {
        "feature_key": key,
        "created_at": created_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z") if created_at else None,
        "last_used_at": None,
        "source_run_id": "RUN_X",
        "complete": True,
    }
    (d / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    return d


def test_iter_feature_cache_entries_sorts_newest_first(tmp_path: Path) -> None:
    cache_dir = tmp_path / "_cache"
    now = datetime.now(timezone.utc)

    _mk_entry(cache_dir, "k1", created_at=now - timedelta(days=10))
    _mk_entry(cache_dir, "k2", created_at=now - timedelta(days=1))
    _mk_entry(cache_dir, "k3", created_at=now - timedelta(days=5))

    entries = iter_feature_cache_entries(cache_dir)
    assert [e.feature_key for e in entries] == ["k2", "k3", "k1"]
    assert all(e.size_bytes > 0 for e in entries)


def test_prune_feature_cache_older_than_respects_keep_latest(tmp_path: Path) -> None:
    cache_dir = tmp_path / "_cache"
    now = datetime.now(timezone.utc)

    _mk_entry(cache_dir, "newest", created_at=now - timedelta(days=1))
    _mk_entry(cache_dir, "mid", created_at=now - timedelta(days=20))
    _mk_entry(cache_dir, "oldest", created_at=now - timedelta(days=40))

    # Older-than 30 should delete only "oldest" ... unless protected by keep_latest.
    plan = prune_feature_cache(cache_dir, older_than_days=30, keep_latest=1, dry_run=True)
    assert (cache_dir / "features" / "newest") in plan.kept
    assert (cache_dir / "features" / "mid") in plan.kept
    assert (cache_dir / "features" / "oldest") in plan.deleted

    # Actually delete
    res = prune_feature_cache(cache_dir, older_than_days=30, keep_latest=1, dry_run=False)
    assert not (cache_dir / "features" / "oldest").exists()
    assert (cache_dir / "features" / "newest").exists()
    assert (cache_dir / "features" / "mid").exists()