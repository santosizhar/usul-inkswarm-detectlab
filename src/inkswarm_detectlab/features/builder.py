from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Tuple

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Window:
    label: str
    td: timedelta


def _parse_windows(windows: list[str]) -> list[Window]:
    out: list[Window] = []
    for w in windows:
        s = w.strip().lower()
        if s.endswith("h"):
            n = int(s[:-1])
            out.append(Window(label=f"{n}h", td=timedelta(hours=n)))
        elif s.endswith("d"):
            n = int(s[:-1])
            out.append(Window(label=f"{n}d", td=timedelta(days=n)))
        else:
            raise ValueError(f"Unsupported window: {w!r} (use like 1h,6h,24h,7d)")
    return out


def _ensure_dt(df: pd.DataFrame) -> pd.Series:
    ts = df["event_ts"]
    if pd.api.types.is_datetime64_any_dtype(ts):
        return ts
    return pd.to_datetime(ts, errors="raise")


def _bool_int(s: pd.Series) -> pd.Series:
    return s.astype(bool).astype(np.int64)


def _rolling_sum_by_time(
    df: pd.DataFrame,
    *,
    group_key: str,
    value_col: str,
    window: str,
    strict_past_only: bool,
) -> np.ndarray:
    """Time-based rolling sum per group, aligned to df row order.

    Requirement: df must already be globally sorted by event_ts (and stable tie-breakers).
    closed='left' enforces strict past-only (excludes current timestamp).
    """
    d = df[[group_key, "event_ts", value_col]].copy()
    d["event_ts"] = _ensure_dt(d).values
    d = d.set_index("event_ts")
    closed = "left" if strict_past_only else "both"
    s = (
        d.groupby(group_key, sort=False)[value_col]
        .rolling(window, closed=closed)
        .sum()
        .reset_index(level=0, drop=True)
    )
    return s.fillna(0.0).to_numpy()


def _rolling_cnt_by_time(
    df: pd.DataFrame,
    *,
    group_key: str,
    window: str,
    strict_past_only: bool,
) -> np.ndarray:
    d = df[[group_key, "event_ts"]].copy()
    d["event_ts"] = _ensure_dt(d).values
    d = d.set_index("event_ts")
    closed = "left" if strict_past_only else "both"
    s = (
        d.groupby(group_key, sort=False)[group_key]
        .rolling(window, closed=closed)
        .count()
        .reset_index(level=0, drop=True)
    )
    return s.fillna(0.0).to_numpy()


def _rolling_unique_count_strict(
    df: pd.DataFrame,
    *,
    group_key: str,
    value_key: str,
    window_td: timedelta,
) -> Tuple[np.ndarray, pd.DataFrame]:
    """Strict past-only unique count per group using a timestamp-batched sliding window.

    Deterministic and treats same-timestamp events as not visible to each other.
    Returns (counts_aligned_to_sorted_df, sorted_df_used_for_computation).
    """
    d = df[[group_key, "event_ts", "event_id", value_key]].copy()
    d["event_ts"] = _ensure_dt(d).values
    d[group_key] = d[group_key].astype("string")
    d[value_key] = d[value_key].astype("string").fillna("<NA>")
    d = d.sort_values([group_key, "event_ts", "event_id"], kind="mergesort").reset_index(drop=True)

    out = np.zeros(len(d), dtype=np.int64)

    win_ns = np.timedelta64(int(window_td.total_seconds() * 1_000_000_000), "ns")

    for _, g in d.groupby(group_key, sort=False):
        idxs = g.index.to_numpy()
        ts = g["event_ts"].to_numpy()
        vals = g[value_key].to_numpy()

        left = 0
        counts: dict[str, int] = {}

        unique_ts, start_pos = np.unique(ts, return_index=True)
        start_pos = list(start_pos) + [len(ts)]
        for b in range(len(unique_ts)):
            b_start = start_pos[b]
            b_end = start_pos[b + 1]
            t = unique_ts[b]

            expire_before = t - win_ns
            while left < b_start and ts[left] <= expire_before:
                v = vals[left]
                c = counts.get(v, 0) - 1
                if c <= 0:
                    counts.pop(v, None)
                else:
                    counts[v] = c
                left += 1

            out[idxs[b_start:b_end]] = len(counts)

            for j in range(b_start, b_end):
                v = vals[j]
                counts[v] = counts.get(v, 0) + 1

    return out, d


def build_login_features(
    login_df: pd.DataFrame,
    *,
    windows: list[str],
    entities: list[str],
    strict_past_only: bool,
    include_support: bool,
) -> tuple[pd.DataFrame, list[str]]:
    """Build safe, leakage-aware rolling features for login_attempt."""
    df = login_df.copy()
    df["event_ts"] = _ensure_dt(df)
    df["event_id"] = df["event_id"].astype("string")
    df["user_id"] = df["user_id"].astype("string")
    if "session_id" in df.columns:
        df["session_id"] = df["session_id"].astype("string")

    # Global stable order (required for determinism)
    df = df.sort_values(["event_ts", "user_id", "event_id"], kind="mergesort").reset_index(drop=True)

    # Outcome indicators
    df["_is_success"] = (df["login_result"] == "success").astype(np.int64)
    df["_is_failure"] = (df["login_result"] == "failure").astype(np.int64)
    df["_is_challenge"] = (df["login_result"] == "challenge").astype(np.int64)
    df["_is_lockout"] = (df["login_result"] == "lockout").astype(np.int64)

    if "support_contacted" in df.columns:
        df["_support_contacted"] = _bool_int(df["support_contacted"])
    else:
        df["_support_contacted"] = 0

    for c in ["support_cost_usd", "support_wait_seconds", "support_handle_seconds"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)

    ws = _parse_windows(windows)
    feature_cols: list[str] = []

    def add_rates(prefix: str, cnt_col: str, s_col: str, f_col: str, c_col: str, l_col: str):
        denom = df[cnt_col].replace(0, np.nan)
        df[f"{prefix}success_rate"] = (df[s_col] / denom).fillna(0.0)
        df[f"{prefix}failure_rate"] = (df[f_col] / denom).fillna(0.0)
        df[f"{prefix}challenge_rate"] = (df[c_col] / denom).fillna(0.0)
        df[f"{prefix}lockout_rate"] = (df[l_col] / denom).fillna(0.0)
        feature_cols.extend(
            [f"{prefix}success_rate", f"{prefix}failure_rate", f"{prefix}challenge_rate", f"{prefix}lockout_rate"]
        )

    for ent in entities:
        if ent == "user":
            gkey = "user_id"
            uniq_a = "ip_hash"
            uniq_b = "device_fingerprint_hash"
        elif ent == "ip":
            gkey = "ip_hash"
            uniq_a = "user_id"
            uniq_b = "device_fingerprint_hash"
        elif ent == "device":
            gkey = "device_fingerprint_hash"
            uniq_a = "user_id"
            uniq_b = "ip_hash"
        else:
            raise ValueError(f"Unknown entity: {ent}")

        if gkey not in df.columns:
            continue

        df[gkey] = df[gkey].astype("string").fillna("<NA>")

        for w in ws:
            prefix = f"{ent}_{w.label}__"

            cnt_name = f"{prefix}attempt_cnt"
            df[cnt_name] = _rolling_cnt_by_time(df, group_key=gkey, window=w.label, strict_past_only=strict_past_only)
            feature_cols.append(cnt_name)

            s_name = f"{prefix}success_cnt"
            f_name = f"{prefix}failure_cnt"
            c_name = f"{prefix}challenge_cnt"
            l_name = f"{prefix}lockout_cnt"

            df[s_name] = _rolling_sum_by_time(df, group_key=gkey, value_col="_is_success", window=w.label, strict_past_only=strict_past_only)
            df[f_name] = _rolling_sum_by_time(df, group_key=gkey, value_col="_is_failure", window=w.label, strict_past_only=strict_past_only)
            df[c_name] = _rolling_sum_by_time(df, group_key=gkey, value_col="_is_challenge", window=w.label, strict_past_only=strict_past_only)
            df[l_name] = _rolling_sum_by_time(df, group_key=gkey, value_col="_is_lockout", window=w.label, strict_past_only=strict_past_only)
            feature_cols.extend([s_name, f_name, c_name, l_name])

            add_rates(prefix, cnt_name, s_name, f_name, c_name, l_name)

            if strict_past_only:
                if uniq_a in df.columns:
                    arr, d_sorted = _rolling_unique_count_strict(df, group_key=gkey, value_key=uniq_a, window_td=w.td)
                    tmp = pd.DataFrame({"event_id": d_sorted["event_id"], f"{prefix}uniq_{uniq_a}_cnt": arr})
                    df = df.merge(tmp, on="event_id", how="left", validate="one_to_one")
                    feature_cols.append(f"{prefix}uniq_{uniq_a}_cnt")
                if uniq_b in df.columns:
                    arr, d_sorted = _rolling_unique_count_strict(df, group_key=gkey, value_key=uniq_b, window_td=w.td)
                    tmp = pd.DataFrame({"event_id": d_sorted["event_id"], f"{prefix}uniq_{uniq_b}_cnt": arr})
                    df = df.merge(tmp, on="event_id", how="left", validate="one_to_one")
                    feature_cols.append(f"{prefix}uniq_{uniq_b}_cnt")

            if include_support and "support_contacted" in df.columns:
                sc = f"{prefix}support_contacted_cnt"
                df[sc] = _rolling_sum_by_time(df, group_key=gkey, value_col="_support_contacted", window=w.label, strict_past_only=strict_past_only)
                feature_cols.append(sc)

                if "support_cost_usd" in df.columns:
                    ssum = f"{prefix}support_cost_usd_sum"
                    df[ssum] = _rolling_sum_by_time(df, group_key=gkey, value_col="support_cost_usd", window=w.label, strict_past_only=strict_past_only)
                    feature_cols.append(ssum)

                if "support_wait_seconds" in df.columns:
                    wsum = f"{prefix}support_wait_seconds_sum"
                    df[wsum] = _rolling_sum_by_time(df, group_key=gkey, value_col="support_wait_seconds", window=w.label, strict_past_only=strict_past_only)
                    feature_cols.append(wsum)

                if "support_handle_seconds" in df.columns:
                    hsum = f"{prefix}support_handle_seconds_sum"
                    df[hsum] = _rolling_sum_by_time(df, group_key=gkey, value_col="support_handle_seconds", window=w.label, strict_past_only=strict_past_only)
                    feature_cols.append(hsum)

    # Cleanup temp
    df.drop(columns=["_is_success", "_is_failure", "_is_challenge", "_is_lockout", "_support_contacted"], inplace=True, errors="ignore")

    for c in feature_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)

    return df, feature_cols
