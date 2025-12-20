from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import json

import numpy as np
import pandas as pd

from ..config.models import AppConfig, SkynetSyntheticConfig
from ..utils.time import BA_TZ, ensure_ba


PLAYBOOKS = ["REPLICATORS", "THE_MULE", "THE_CHAMELEON"]


@dataclass(frozen=True)
class Campaign:
    campaign_id: str
    start_hour_index: int
    duration_hours: int
    campaign_type: str
    playbooks: tuple[str, ...]
    volume_multiplier: float
    attack_rate_multiplier: float

    def active_hours(self) -> range:
        return range(self.start_hour_index, self.start_hour_index + self.duration_hours)


def _default_hourly_factors() -> np.ndarray:
    # Night low, morning ramp, midday steady, evening higher
    # Shape: 24
    return np.array([
        0.35, 0.30, 0.28, 0.28, 0.32, 0.45,
        0.60, 0.75, 0.95, 1.10, 1.15, 1.12,
        1.00, 0.95, 0.92, 0.95, 1.05, 1.18,
        1.25, 1.18, 1.00, 0.80, 0.60, 0.45,
    ], dtype=float)


def _default_weekday_factors() -> np.ndarray:
    # Mon..Sun, weekend slightly lower volume but can be spikier via campaigns.
    return np.array([1.00, 1.02, 1.03, 1.02, 1.00, 0.90, 0.85], dtype=float)


def _choose_playbooks(rng: np.random.Generator, weights: dict[str, float]) -> tuple[str, ...]:
    # Each campaign includes 1-3 playbooks, with bias given by weights.
    pb = np.array(list(weights.keys()))
    w = np.array([float(weights[k]) for k in pb], dtype=float)
    w = w / w.sum()

    # Decide size: mostly single, sometimes pair, rarely triple.
    size = rng.choice([1, 2, 3], p=[0.65, 0.30, 0.05])
    chosen = rng.choice(pb, size=size, replace=False, p=w)
    # Keep stable order for determinism in hashing/summary
    order = {"REPLICATORS": 0, "THE_MULE": 1, "THE_CHAMELEON": 2}
    chosen = tuple(sorted((str(x) for x in chosen), key=lambda x: order.get(x, 99)))
    return chosen


def _campaign_effects(campaign_type: str) -> tuple[float, float]:
    # (volume_multiplier, attack_rate_multiplier)
    if campaign_type == "VOLUME_SPIKE":
        return 2.0, 1.0
    if campaign_type == "SHARE_SPIKE":
        return 1.0, 2.2
    if campaign_type == "MIXED_SPIKE":
        return 1.7, 1.8
    if campaign_type == "PERSISTENT_LOW":
        return 1.15, 1.35
    return 1.0, 1.0


def _schedule_campaigns(cfg: SkynetSyntheticConfig, rng: np.random.Generator) -> list[Campaign]:
    if not cfg.spikes.enabled or cfg.spikes.n_campaigns <= 0:
        return []

    total_hours = cfg.days * 24
    campaigns: list[Campaign] = []
    for i in range(cfg.spikes.n_campaigns):
        dur = int(rng.integers(cfg.spikes.duration_hours_min, cfg.spikes.duration_hours_max + 1))
        start = int(rng.integers(0, max(1, total_hours - dur)))
        ctype = str(rng.choice(cfg.spikes.campaign_types))
        playbooks = _choose_playbooks(rng, cfg.spikes.playbook_weights)
        vol_mul, atk_mul = _campaign_effects(ctype)
        campaigns.append(
            Campaign(
                campaign_id=f"C{i+1:02d}",
                start_hour_index=start,
                duration_hours=dur,
                campaign_type=ctype,
                playbooks=playbooks,
                volume_multiplier=float(vol_mul),
                attack_rate_multiplier=float(atk_mul),
            )
        )
    return campaigns


def _sample_attack_labels(
    rng: np.random.Generator,
    playbooks: tuple[str, ...] | None,
    p_pair: float,
    p_triple: float,
) -> tuple[bool, bool, bool]:
    """Return (replicators, mule, chameleon)."""
    if not playbooks:
        # baseline: single-label only
        label = rng.choice(PLAYBOOKS, p=[0.45, 0.20, 0.35])
        return (label == "REPLICATORS", label == "THE_MULE", label == "THE_CHAMELEON")

    # campaign-driven: allow overlaps that "make sense"
    pb = list(playbooks)
    if len(pb) == 1:
        label = pb[0]
        return (label == "REPLICATORS", label == "THE_MULE", label == "THE_CHAMELEON")

    u = rng.random()
    if len(pb) == 3 and u < p_triple:
        return True, True, True

    if u < p_triple + p_pair:
        a, b = rng.choice(pb, size=2, replace=False)
        return (a == "REPLICATORS" or b == "REPLICATORS", a == "THE_MULE" or b == "THE_MULE", a == "THE_CHAMELEON" or b == "THE_CHAMELEON")

    # otherwise single label from the campaign set
    label = rng.choice(pb)
    return (label == "REPLICATORS", label == "THE_MULE", label == "THE_CHAMELEON")


def generate_skynet(cfg: AppConfig, run_id: str, seed: int | None = None) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Generate SKYNET login_attempt + checkout_attempt raw tables.

    Deterministic for fixed (seed, config, run_id).
    """
    s = cfg.synthetic.skynet
    rng = np.random.default_rng(cfg.run.seed if seed is None else seed)

    start_dt = datetime.combine(s.start_date, datetime.min.time()).replace(tzinfo=BA_TZ)
    start_dt = ensure_ba(start_dt)
    total_hours = s.days * 24

    hourly_f = np.array(s.seasonality.hourly_factors, dtype=float) if s.seasonality.hourly_factors else _default_hourly_factors()
    weekday_f = np.array(s.seasonality.weekday_factors, dtype=float) if s.seasonality.weekday_factors else _default_weekday_factors()
    if hourly_f.shape[0] != 24:
        raise ValueError("seasonality.hourly_factors must have length 24")
    if weekday_f.shape[0] != 7:
        raise ValueError("seasonality.weekday_factors must have length 7")

    # user activity weights (stable skew)
    user_ids = np.array([f"user_{i:05d}" for i in range(s.n_users)], dtype=object)
    alpha = np.linspace(1.5, 0.25, s.n_users)
    weights = rng.dirichlet(alpha)

    campaigns = _schedule_campaigns(s, rng)
    active_by_hour: dict[int, list[Campaign]] = {h: [] for h in range(total_hours)}
    for c in campaigns:
        for h in c.active_hours():
            if 0 <= h < total_hours:
                active_by_hour[h].append(c)

    base_per_hour = s.login_events_per_day / 24.0

    # Precompute hour starts
    hour_starts = [start_dt + timedelta(hours=h) for h in range(total_hours)]

    all_rows = []
    event_counter = 0

    for h in range(total_hours):
        ts0 = hour_starts[h]
        hour = ts0.hour
        dow = ts0.weekday()
        intensity = base_per_hour * hourly_f[hour] * weekday_f[dow]
        attack_rate = float(s.attack_prevalence)

        # apply campaign effects
        camp_list = active_by_hour.get(h, [])
        if camp_list:
            # combine effects conservatively
            vol_mul = max(c.volume_multiplier for c in camp_list)
            atk_mul = max(c.attack_rate_multiplier for c in camp_list)
            intensity *= vol_mul
            attack_rate = min(0.95, attack_rate * atk_mul)
            # choose a primary campaign for label set (coherent)
            primary = camp_list[0]
            camp_playbooks = primary.playbooks
            camp_id = primary.campaign_id
        else:
            camp_playbooks = None
            camp_id = None

        n = int(rng.poisson(lam=max(0.0, intensity)))
        if n <= 0:
            continue

        # sample users
        users = rng.choice(user_ids, size=n, replace=True, p=weights)
        # per-event ts within hour
        offsets = rng.integers(0, 3600, size=n)
        event_ts = [ts0 + timedelta(seconds=int(o)) for o in offsets]

        for i in range(n):
            event_counter += 1
            eid = f"login_{event_counter:010d}"
            uid = str(users[i])
            is_attack = rng.random() < attack_rate

            if is_attack:
                rep, mule, cham = _sample_attack_labels(rng, camp_playbooks, s.spikes.p_pair_overlap, s.spikes.p_triple_overlap)
            else:
                rep = mule = cham = False

            benign = not (rep or mule or cham)
            is_fraud = not benign

            # Outcome shaping
            if benign:
                login_result = rng.choice(["success", "failure", "challenge", "lockout"], p=[0.80, 0.15, 0.04, 0.01])
            else:
                # attackers get more challenge/lockout
                login_result = rng.choice(["success", "failure", "challenge", "lockout"], p=[0.15, 0.40, 0.30, 0.15])

            failure_reason = None
            if login_result == "failure":
                failure_reason = rng.choice(["bad_password", "mfa_failed", "rate_limited", "other"], p=[0.55, 0.20, 0.20, 0.05])

            username_present = True
            mfa_used = bool(rng.random() < (0.35 if benign else 0.15))
            if not mfa_used:
                mfa_result = "not_applicable"
            else:
                mfa_result = rng.choice(["pass", "fail"], p=[0.92 if benign else 0.40, 0.08 if benign else 0.60])

            support_contacted = bool(rng.random() < (0.04 if benign else 0.18) + (0.06 if login_result in ("challenge", "lockout") else 0.0))
            if not support_contacted:
                support_channel = "none"
                support_responder_type = "none"
                support_wait_seconds = None
                support_handle_seconds = None
                support_cost_usd = None
                support_resolution = "none"
                support_offset_seconds = None
            else:
                support_channel = rng.choice(["chat", "email", "phone", "in_app"], p=[0.45, 0.20, 0.10, 0.25])
                support_responder_type = rng.choice(["bot", "agent"], p=[0.55, 0.45])
                support_wait_seconds = int(rng.choice([30, 60, 120, 240], p=[0.25, 0.35, 0.25, 0.15]))
                support_handle_seconds = int(rng.choice([60, 180, 300, 600], p=[0.20, 0.35, 0.30, 0.15]))
                support_cost_usd = float(0.25 + 0.002 * support_handle_seconds)
                support_resolution = rng.choice(["resolved", "unresolved", "escalated"], p=[0.70, 0.20, 0.10])
                support_offset_seconds = int(rng.choice([0, 60, 300, 900], p=[0.35, 0.30, 0.25, 0.10]))

            meta = {
                "campaign_id": camp_id,
                "playbooks": [p for p in ("REPLICATORS" if rep else None, "THE_MULE" if mule else None, "THE_CHAMELEON" if cham else None) if p],
            }

            all_rows.append(
                {
                    "run_id": run_id,
                    "event_id": eid,
                    "event_ts": event_ts[i],
                    "user_id": uid,
                    "session_id": f"sess_{abs(hash((uid, h))) % 100000:05d}",
                    "ip_hash": f"ip_{abs(hash((uid, 'ip'))) % 10000:04d}",
                    "device_fingerprint_hash": f"dev_{abs(hash((uid, 'dev'))) % 10000:04d}",
                    "country": "AR",
                    "is_fraud": bool(is_fraud),
                    "label_replicators": bool(rep),
                    "label_the_mule": bool(mule),
                    "label_the_chameleon": bool(cham),
                    "label_benign": bool(benign),
                    "metadata_json": json.dumps(meta, separators=(",", ":"), ensure_ascii=True),
                    "login_result": str(login_result),
                    "failure_reason": failure_reason,
                    "username_present": bool(username_present),
                    "mfa_used": bool(mfa_used),
                    "mfa_result": str(mfa_result),
                    "support_contacted": bool(support_contacted),
                    "support_channel": str(support_channel),
                    "support_responder_type": str(support_responder_type),
                    "support_wait_seconds": support_wait_seconds,
                    "support_handle_seconds": support_handle_seconds,
                    "support_cost_usd": support_cost_usd,
                    "support_resolution": str(support_resolution),
                    "support_offset_seconds": support_offset_seconds,
                }
            )

    login_df = pd.DataFrame(all_rows)
    if not login_df.empty:
        login_df["event_ts"] = pd.to_datetime(login_df["event_ts"], utc=False)

    # Checkout: mostly benign until SPACING GUILD.
    checkout_rows = []
    if s.checkout_events_per_day > 0:
        base_checkout_per_hour = s.checkout_events_per_day / 24.0
        checkout_counter = 0
        for h in range(total_hours):
            ts0 = hour_starts[h]
            hour = ts0.hour
            dow = ts0.weekday()
            intensity = base_checkout_per_hour * hourly_f[hour] * weekday_f[dow]
            n = int(rng.poisson(lam=max(0.0, intensity)))
            if n <= 0:
                continue
            users = rng.choice(user_ids, size=n, replace=True, p=weights)
            offsets = rng.integers(0, 3600, size=n)
            event_ts = [ts0 + timedelta(seconds=int(o)) for o in offsets]
            for i in range(n):
                checkout_counter += 1
                eid = f"checkout_{checkout_counter:010d}"
                uid = str(users[i])
                adverse = rng.random() < float(s.checkout_adverse_rate)
                if not adverse:
                    checkout_result = "success"
                    decline_reason = None
                else:
                    checkout_result = rng.choice(["failure", "review"], p=[0.80, 0.20])
                    if checkout_result == "review":
                        decline_reason = None
                    else:
                        decline_reason = rng.choice(["insufficient_funds", "network_error", "other"], p=[0.40, 0.35, 0.25])

                meta = {"campaign_id": None, "note": "fraud labels disabled until SPACING GUILD"}
                checkout_rows.append(
                    {
                        "run_id": run_id,
                        "event_id": eid,
                        "event_ts": event_ts[i],
                        "user_id": uid,
                        "session_id": f"sess_{abs(hash((uid, h))) % 100000:05d}",
                        "ip_hash": f"ip_{abs(hash((uid, 'ip'))) % 10000:04d}",
                        "device_fingerprint_hash": f"dev_{abs(hash((uid, 'dev'))) % 10000:04d}",
                        "country": "AR",
                        "is_fraud": False,
                        "metadata_json": json.dumps(meta, separators=(",", ":"), ensure_ascii=True),
                        "payment_value": float(np.clip(rng.lognormal(mean=3.1, sigma=0.6), 1.0, 5000.0)),
                        "basket_size": int(rng.integers(1, 7)),
                        "is_first_time_user": bool(rng.random() < 0.18),
                        "is_premium_user": bool(rng.random() < 0.25),
                        "credit_card_hash": None if rng.random() < 0.15 else f"cc_{abs(hash((uid, 'cc'))) % 200000:06d}",
                        "checkout_result": str(checkout_result),
                        "decline_reason": decline_reason,
                    }
                )

    checkout_df = pd.DataFrame(checkout_rows)
    if not checkout_df.empty:
        checkout_df["event_ts"] = pd.to_datetime(checkout_df["event_ts"], utc=False)

    meta = {
        "campaigns": [
            {
                "campaign_id": c.campaign_id,
                "start_hour_index": c.start_hour_index,
                "duration_hours": c.duration_hours,
                "campaign_type": c.campaign_type,
                "playbooks": list(c.playbooks),
                "volume_multiplier": c.volume_multiplier,
                "attack_rate_multiplier": c.attack_rate_multiplier,
            }
            for c in campaigns
        ]
    }
    return login_df, checkout_df, meta
