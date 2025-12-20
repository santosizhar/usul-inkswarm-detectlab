from __future__ import annotations

from typing import Sequence

import pandas as pd

from ..schemas.base import EventSchema


def canonical_column_order(df: pd.DataFrame, schema: EventSchema | None) -> list[str]:
    """Return a deterministic column order.

    - If schema provided: schema columns first (schema order), then extras alphabetically.
    - Else: all columns alphabetically.
    """
    cols = list(df.columns)
    if schema is None:
        return sorted(cols)
    schema_cols = [c for c in schema.column_names() if c in df.columns]
    extras = sorted([c for c in cols if c not in set(schema_cols)])
    return schema_cols + extras


def canonicalize_df(
    df: pd.DataFrame,
    *,
    sort_keys: Sequence[str] | None = None,
    schema: EventSchema | None = None,
) -> pd.DataFrame:
    """Canonicalize a dataframe for determinism.

    - Stable sort by sort_keys (only keys present), using mergesort.
    - Deterministic column ordering.
    """
    d = df.copy(deep=False)
    if sort_keys:
        keys = [k for k in sort_keys if k in d.columns]
        if keys:
            d = d.sort_values(by=keys, kind="mergesort", na_position="last")
    cols = canonical_column_order(d, schema)
    return d[cols]
