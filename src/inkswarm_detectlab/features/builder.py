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
    include_cross_event: bool = False,
    checkout_df: pd.DataFrame | None = None,
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



# Cross-event context (checkout history as context for login)
if include_cross_event and (checkout_df is not None) and (len(checkout_df) > 0):
    df, extra_cols = add_cross_event_context(
        df,
        checkout_df,
        other_event="checkout_attempt",
        windows=windows,
        entities=entities,
        strict_past_only=strict_past_only,
    )
    feature_cols.extend(extra_cols)
    # Cleanup temp
    df.drop(columns=["_is_success", "_is_failure", "_is_challenge", "_is_lockout", "_support_contacted"], inplace=True, errors="ignore")

    for c in feature_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)

    return df, feature_cols


# -----------------------------
# D-0007: FeatureLab v1 (checkout_attempt + cross-event context)
# -----------------------------

def _cross_event_window_sums(
    base: pd.DataFrame,
    other: pd.DataFrame,
    *,
    group_key: str,
    value_cols: list[str],
    window_td: timedelta,
) -> dict[str, np.ndarray]:
    """Windowed sums of `value_cols` from `other`, aligned to rows of `base`.

    Interval is [t-window, t) (strict past-only) via searchsorted(..., side='left').
    Both frames must contain: group_key, event_ts.
    Returns numpy arrays aligned to the original base row order.
    """
    b = base[[group_key, "event_ts", "event_id"]].copy()
    b["event_ts"] = _ensure_dt(b).values
    b = b.reset_index().rename(columns={"index": "_base_idx"})
    b[group_key] = b[group_key].astype("string").fillna("<NA>")
    b = b.sort_values([group_key, "event_ts", "event_id"], kind="mergesort").reset_index(drop=True)

    o = other[[group_key, "event_ts"] + value_cols].copy()
    o["event_ts"] = _ensure_dt(o).values
    o[group_key] = o[group_key].astype("string").fillna("<NA>")
    o = o.sort_values([group_key, "event_ts"], kind="mergesort").reset_index(drop=True)

    out_sorted = {c: np.zeros(len(b), dtype=np.float64) for c in value_cols}

    ogroups = {k: g for k, g in o.groupby(group_key, sort=False)}
    win_ns = np.timedelta64(int(window_td.total_seconds() * 1_000_000_000), "ns")

    for k, bg in b.groupby(group_key, sort=False):
        idxs = bg.index.to_numpy()
        ts = bg["event_ts"].to_numpy()
        og = ogroups.get(k)
        if og is None or len(og) == 0:
            continue
        ots = og["event_ts"].to_numpy()

        right = np.searchsorted(ots, ts, side="left")  # exclude >= t
        left = np.searchsorted(ots, ts - win_ns, side="left")  # include == t-window

        for col in value_cols:
            arr = pd.to_numeric(og[col], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
            csum = np.concatenate(([0.0], np.cumsum(arr)))
            out_sorted[col][idxs] = csum[right] - csum[left]

    # Align back to original base row order
    base_idx_sorted_to_orig = b["_base_idx"].to_numpy()
    aligned: dict[str, np.ndarray] = {}
    for col, arr in out_sorted.items():
        a2 = np.zeros(len(base), dtype=np.float64)
        a2[base_idx_sorted_to_orig] = arr
        aligned[col] = a2
    return aligned


def add_cross_event_context(
    base_df: pd.DataFrame,
    other_df: pd.DataFrame,
    *,
    other_event: str,
    windows: list[str],
    entities: list[str],
    strict_past_only: bool,
) -> tuple[pd.DataFrame, list[str]]:
    """Add cross-event history features to base_df using other_df.

    Column naming:
        cross__<other_event>__<entity>_<window>__<metric>

    Metrics included:
    - event_cnt
    - per-outcome counts (+ rates)
    - (checkout only) payment_value_sum (+ payment_value_mean)
    """
    df = base_df.copy()
    other = other_df.copy()
    df["event_ts"] = _ensure_dt(df)
    other["event_ts"] = _ensure_dt(other)

    # Define other-side signals.
    if other_event == "login_attempt":
        other["_success"] = (other["login_result"] == "success").astype(np.int64)
        other["_failure"] = (other["login_result"] == "failure").astype(np.int64)
        other["_challenge"] = (other["login_result"] == "challenge").astype(np.int64)
        other["_lockout"] = (other["login_result"] == "lockout").astype(np.int64)
        value_cols = ["_one", "_success", "_failure", "_challenge", "_lockout"]
        other["_one"] = 1.0
        outcome_cols = ["_success", "_failure", "_challenge", "_lockout"]
        payment_col = None
    elif other_event == "checkout_attempt":
        other["_success"] = (other["checkout_result"] == "success").astype(np.int64)
        other["_failure"] = (other["checkout_result"] == "failure").astype(np.int64)
        other["_review"] = (other["checkout_result"] == "review").astype(np.int64)
        other["_adverse"] = ((other["_failure"] == 1) | (other["_review"] == 1)).astype(np.int64)
        other["_one"] = 1.0
        value_cols = ["_one", "_success", "_failure", "_review", "_adverse"]
        outcome_cols = ["_success", "_failure", "_review", "_adverse"]
        if "payment_value" in other.columns:
            other["payment_value"] = pd.to_numeric(other["payment_value"], errors="coerce").fillna(0.0)
            value_cols.append("payment_value")
            payment_col = "payment_value"
        else:
            payment_col = None
    else:
        raise ValueError(f"Unsupported other_event={other_event!r}")

    ws = _parse_windows(windows)
    added: list[str] = []

    for ent in entities:
        if ent == "user":
            gkey = "user_id"
        elif ent == "ip":
            gkey = "ip_hash"
        elif ent == "device":
            gkey = "device_fingerprint_hash"
        else:
            raise ValueError(f"Unknown entity: {ent}")

        if gkey not in df.columns or gkey not in other.columns:
            continue

        df[gkey] = df[gkey].astype("string").fillna("<NA>")
        other[gkey] = other[gkey].astype("string").fillna("<NA>")

        for w in ws:
            prefix = f"cross__{other_event}__{ent}_{w.label}__"
            sums = _cross_event_window_sums(df, other, group_key=gkey, value_cols=value_cols, window_td=w.td)

            cnt_name = f"{prefix}event_cnt"
            df[cnt_name] = sums["_one"]
            added.append(cnt_name)

            denom = df[cnt_name].replace(0, np.nan)
            for oc in outcome_cols:
                name = f"{prefix}{oc.lstrip('_')}_cnt"
                df[name] = sums[oc]
                added.append(name)
                rname = f"{prefix}{oc.lstrip('_')}_rate"
                df[rname] = (df[name] / denom).fillna(0.0)
                added.append(rname)

            if payment_col:
                ps = f"{prefix}payment_value_sum"
                pm = f"{prefix}payment_value_mean"
                df[ps] = sums[payment_col]
                df[pm] = (df[ps] / denom).fillna(0.0)
                added.extend([ps, pm])

    return df, added


def build_checkout_features(
    checkout_df: pd.DataFrame,
    *,
    windows: list[str],
    entities: list[str],
    strict_past_only: bool,
    include_cross_event: bool,
    login_df: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, list[str]]:
    """Build safe, leakage-aware rolling features for checkout_attempt."""
    df = checkout_df.copy()
    df["event_ts"] = _ensure_dt(df)
    df["event_id"] = df["event_id"].astype("string")
    df["user_id"] = df["user_id"].astype("string")
    if "session_id" in df.columns:
        df["session_id"] = df["session_id"].astype("string")

    # Global stable order
    df = df.sort_values(["event_ts", "user_id", "event_id"], kind="mergesort").reset_index(drop=True)

    # Outcome indicators
    df["_is_success"] = (df["checkout_result"] == "success").astype(np.int64)
    df["_is_failure"] = (df["checkout_result"] == "failure").astype(np.int64)
    df["_is_review"] = (df["checkout_result"] == "review").astype(np.int64)
    df["_is_adverse"] = ((df["_is_failure"] == 1) | (df["_is_review"] == 1)).astype(np.int64)

    # Numeric signals
    for c in ["payment_value", "basket_size"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)

    ws = _parse_windows(windows)
    feature_cols: list[str] = []

    def add_rates(prefix: str, cnt_col: str, s_col: str, f_col: str, r_col: str):
        denom = df[cnt_col].replace(0, np.nan)
        df[f"{prefix}success_rate"] = (df[s_col] / denom).fillna(0.0)
        df[f"{prefix}failure_rate"] = (df[f_col] / denom).fillna(0.0)
        df[f"{prefix}review_rate"] = (df[r_col] / denom).fillna(0.0)
        feature_cols.extend([f"{prefix}success_rate", f"{prefix}failure_rate", f"{prefix}review_rate"])

    for ent in entities:
        if ent == "user":
            gkey = "user_id"
            uniq_a = "ip_hash"
            uniq_b = "device_fingerprint_hash"
            uniq_c = "credit_card_hash"
        elif ent == "ip":
            gkey = "ip_hash"
            uniq_a = "user_id"
            uniq_b = "device_fingerprint_hash"
            uniq_c = None
        elif ent == "device":
            gkey = "device_fingerprint_hash"
            uniq_a = "user_id"
            uniq_b = "ip_hash"
            uniq_c = None
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
            r_name = f"{prefix}review_cnt"
            a_name = f"{prefix}adverse_cnt"

            df[s_name] = _rolling_sum_by_time(df, group_key=gkey, value_col="_is_success", window=w.label, strict_past_only=strict_past_only)
            df[f_name] = _rolling_sum_by_time(df, group_key=gkey, value_col="_is_failure", window=w.label, strict_past_only=strict_past_only)
            df[r_name] = _rolling_sum_by_time(df, group_key=gkey, value_col="_is_review", window=w.label, strict_past_only=strict_past_only)
            df[a_name] = _rolling_sum_by_time(df, group_key=gkey, value_col="_is_adverse", window=w.label, strict_past_only=strict_past_only)
            feature_cols.extend([s_name, f_name, r_name, a_name])

            add_rates(prefix, cnt_name, s_name, f_name, r_name)

            # Payment / basket aggregates (sum + mean)
            if "payment_value" in df.columns:
                pv_sum = f"{prefix}payment_value_sum"
                df[pv_sum] = _rolling_sum_by_time(df, group_key=gkey, value_col="payment_value", window=w.label, strict_past_only=strict_past_only)
                feature_cols.append(pv_sum)
                pv_mean = f"{prefix}payment_value_mean"
                df[pv_mean] = (df[pv_sum] / df[cnt_name].replace(0, np.nan)).fillna(0.0)
                feature_cols.append(pv_mean)

            if "basket_size" in df.columns:
                bs_sum = f"{prefix}basket_size_sum"
                df[bs_sum] = _rolling_sum_by_time(df, group_key=gkey, value_col="basket_size", window=w.label, strict_past_only=strict_past_only)
                feature_cols.append(bs_sum)
                bs_mean = f"{prefix}basket_size_mean"
                df[bs_mean] = (df[bs_sum] / df[cnt_name].replace(0, np.nan)).fillna(0.0)
                feature_cols.append(bs_mean)

            # Unique counts (strict only)
            if strict_past_only:
                for uniq in [uniq_a, uniq_b, uniq_c]:
                    if uniq and uniq in df.columns:
                        arr, d_sorted = _rolling_unique_count_strict(df, group_key=gkey, value_key=uniq, window_td=w.td)
                        tmp = pd.DataFrame({"event_id": d_sorted["event_id"], f"{prefix}uniq_{uniq}_cnt": arr})
                        df = df.merge(tmp, on="event_id", how="left", validate="one_to_one")
                        feature_cols.append(f"{prefix}uniq_{uniq}_cnt")

    # Cross-event context (login history as context for checkout)
    if include_cross_event and (login_df is not None) and (len(login_df) > 0):
        df, extra_cols = add_cross_event_context(
            df,
            login_df,
            other_event="login_attempt",
            windows=windows,
            entities=entities,
            strict_past_only=strict_past_only,
        )
        feature_cols.extend(extra_cols)

    # Cleanup temp
    df.drop(columns=["_is_success", "_is_failure", "_is_review", "_is_adverse"], inplace=True, errors="ignore")
    for c in feature_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    return df, feature_cols
