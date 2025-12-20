from __future__ import annotations
import hashlib, json
from typing import Any

def stable_hash_dict(d: dict[str, Any]) -> str:
    payload = json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
