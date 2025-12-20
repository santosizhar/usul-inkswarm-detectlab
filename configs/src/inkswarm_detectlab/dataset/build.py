from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from ..config.models import DatasetBuildConfig
from ..utils.time import BA_TZ


@dataclass(frozen=True)
class SplitResult:
    train: pd.DataFrame
    time_eval: pd.DataFrame
    user_holdout: pd.DataFrame
    boundary_ts: pd.Timestamp
    holdout_users: set[str]


def _choose_holdout_users(users: np.ndarray, frac: float, rng: np.random.Generator) -> set[str]:
    unique = np.unique(users.astype(str))
    n = int(np.round(len(unique) * frac))
    n = max(1, min(len(unique), n))
    chosen = rng.choice(unique, size=n, replace=False)
    return set(str(x) for x in chosen)


def build_splits(df: pd.DataFrame, cfg: DatasetBuildConfig, rng: np.random.Generator) -> SplitResult:
    """Leakage-aware split: 15% user holdout + 85% time split for remainder.

    - user_holdout = all rows for selected holdout users
    - train/time_eval are mutually exclusive and exclude holdout users
    """
    if df.empty:
        boundary = pd.Timestamp.now(tz=BA_TZ)
        return SplitResult(df.copy(), df.copy(), df.copy(), boundary, set())

    if "user_id" not in df.columns or "event_ts" not in df.columns:
        raise ValueError("DataFrame must contain user_id and event_ts")

    users = df["user_id"].astype(str).values
    holdout_users = _choose_holdout_users(users, cfg.user_holdout, rng)
    is_holdout = df["user_id"].astype(str).isin(holdout_users)

    holdout_df = df[is_holdout].copy()
    remaining = df[~is_holdout].copy()

    # time boundary based on time range (not count) for robustness.
    # We compute and apply the boundary in Buenos Aires local time for interpretability.
    ts = pd.to_datetime(remaining["event_ts"], errors="raise", utc=False)
    if getattr(ts.dt, "tz", None) is None:
        ts = ts.dt.tz_localize(BA_TZ)
    else:
        ts = ts.dt.tz_convert(BA_TZ)

    tmin = ts.min()
    tmax = ts.max()
    boundary = pd.Timestamp(tmin + (tmax - tmin) * float(cfg.time_split))

    train_df = remaining[ts < boundary].copy()
    eval_df = remaining[ts >= boundary].copy()

    return SplitResult(train=train_df, time_eval=eval_df, user_holdout=holdout_df, boundary_ts=boundary, holdout_users=holdout_users)
