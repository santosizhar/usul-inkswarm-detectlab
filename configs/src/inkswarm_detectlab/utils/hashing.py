from __future__ import annotations
import hashlib, json
from typing import Any

import pandas as pd

def stable_hash_dict(d: dict[str, Any]) -> str:
    # Important: configs may contain Path / date objects.
    # We stringify unknown objects deterministically for hashing.
    payload = json.dumps(
        d,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def stable_hash_df(df: pd.DataFrame, sort_keys: list[str] | None = None, column_order: list[str] | None = None) -> str:
    """Deterministic content hash for a DataFrame.

    Canonicalization:
    - sort rows by sort_keys (stable)
    - enforce a fixed column order
    - hash the canonicalized values using pandas' stable row hashing
    """
    if df is None:
        return hashlib.sha256(b"<none>").hexdigest()

    d = df.copy(deep=False)
    if sort_keys:
        keys = [k for k in sort_keys if k in d.columns]
        if keys:
            d = d.sort_values(by=keys, kind="mergesort", na_position="last")
    if column_order:
        cols = [c for c in column_order if c in d.columns]
    else:
        cols = sorted(list(d.columns))
    d = d[cols]

    # Normalize datetimes to ISO-like comparable representation by converting tz-aware to UTC ns.
    for c in d.columns:
        if pd.api.types.is_datetime64_any_dtype(d[c]):
            try:
                d[c] = pd.to_datetime(d[c], utc=True).astype("int64")
            except Exception:
                # fall back to string repr
                d[c] = d[c].astype(str)

    h = pd.util.hash_pandas_object(d, index=False).values
    return hashlib.sha256(h.tobytes()).hexdigest()
