from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
import json
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import importlib.util
import json

import numpy as np
import pandas as pd

from ..config.models import AppConfig, SkynetSyntheticConfig
from ..utils.time import BA_TZ, ensure_ba
from ..utils.hashing import stable_mod


PLAYBOOKS = ["REPLICATORS", "THE_MULE", "THE_CHAMELEON"]


@dataclass(frozen=True)
class AttackPatternSetup:
    pack_size_mean: float
    pack_size_std: float
    max_pack_spacing_seconds: int
    label_pack_weights: dict[str, float]


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


def _setup_attack_pattern(cfg: SkynetSyntheticConfig, rng: np.random.Generator) -> AttackPatternSetup:
    """One-time setup for pack-style attack injection (user-visible knob staging)."""
    weights = cfg.attack_pattern.label_pack_weights or {}
    cleaned = {k: float(v) for k, v in weights.items() if float(v) > 0.0}
    if not cleaned:
        cleaned = {k: 1.0 for k in PLAYBOOKS}
    total = sum(cleaned.values())
    normed = {k: v / total for k, v in cleaned.items()}

    return AttackPatternSetup(
        pack_size_mean=float(cfg.attack_pattern.pack_size_mean),
        pack_size_std=float(cfg.attack_pattern.pack_size_std),
        max_pack_spacing_seconds=int(cfg.attack_pattern.max_pack_spacing_seconds),
        label_pack_weights=normed,
    )


def _choose_pack_label(
    rng: np.random.Generator, setup: AttackPatternSetup, playbooks: tuple[str, ...] | None
) -> str:
    """Pick a lead playbook for a pack, preferring those allowed by the campaign."""

    keys = PLAYBOOKS if not playbooks else [p for p in PLAYBOOKS if p in playbooks]
    w = np.array([setup.label_pack_weights.get(k, 0.0) for k in keys], dtype=float)
    if w.sum() <= 0:
        w = np.ones_like(w)
    w = w / w.sum()
    return str(rng.choice(keys, p=w))


def _plan_hour_offsets(
    rng: np.random.Generator,
    n_events: int,
    attack_rate: float,
    setup: AttackPatternSetup,
    playbooks: tuple[str, ...] | None,
) -> tuple[np.ndarray, np.ndarray, list[str | None]]:
    """Generate sorted offsets + attack flags with sequential pack behavior."""

    if n_events <= 0:
        return np.array([], dtype=int), np.array([], dtype=bool), []

    expected_attacks = attack_rate * n_events
    n_attacks = int(round(expected_attacks))
    n_attacks = min(max(n_attacks, 0), n_events)

    if n_attacks == 0:
        offsets = np.sort(rng.integers(0, 3600, size=n_events))
        return offsets, np.zeros(n_events, dtype=bool), [None] * n_events

    pack_mean = max(1.0, setup.pack_size_mean)
    n_packs = max(1, int(np.ceil(n_attacks / pack_mean)))

    remaining = n_attacks
    attack_offsets: list[int] = []
    attack_labels: list[str | None] = []
    anchors = np.linspace(0, max(1, 3600 - setup.max_pack_spacing_seconds), num=n_packs, dtype=int)

    for i in range(n_packs):
        pack_size = int(max(1, round(rng.normal(pack_mean, setup.pack_size_std))))
        pack_size = min(pack_size, remaining - (n_packs - i - 1)) if (remaining - (n_packs - i - 1)) > 0 else 1
        remaining -= pack_size

        anchor = int(min(3599, anchors[i] + int(rng.integers(0, max(1, setup.max_pack_spacing_seconds // 2)))))
        increments = np.sort(rng.integers(0, max(1, setup.max_pack_spacing_seconds), size=pack_size))
        attack_offsets.extend([int(min(3599, anchor + int(dx))) for dx in increments])

        label = _choose_pack_label(rng, setup, playbooks)
        attack_labels.extend([label] * pack_size)

    if remaining > 0:
        filler = [int(x) for x in rng.integers(0, 3600, size=remaining)]
        attack_offsets.extend(filler)
        attack_labels.extend([_choose_pack_label(rng, setup, playbooks)] * remaining)

    benign_n = n_events - len(attack_offsets)
    benign_offsets = [] if benign_n <= 0 else [int(x) for x in rng.integers(0, 3600, size=benign_n)]

    offsets = np.array(attack_offsets + benign_offsets, dtype=int)
    attack_flags = np.array([True] * len(attack_offsets) + [False] * len(benign_offsets), dtype=bool)
    preferred_labels: list[str | None] = attack_labels + [None] * len(benign_offsets)

    order = np.argsort(offsets)
    return offsets[order], attack_flags[order], [preferred_labels[i] for i in order]


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
    preferred_label: str | None = None,
) -> tuple[bool, bool, bool]:
    """Return (replicators, mule, chameleon)."""
    if not playbooks:
        # baseline: single-label only
        label = rng.choice(PLAYBOOKS, p=[0.45, 0.20, 0.35])
        rep = label == "REPLICATORS"
        mule = label == "THE_MULE"
        cham = label == "THE_CHAMELEON"
        if preferred_label in PLAYBOOKS:
            rep = rep or preferred_label == "REPLICATORS"
            mule = mule or preferred_label == "THE_MULE"
            cham = cham or preferred_label == "THE_CHAMELEON"
        return rep, mule, cham

    # campaign-driven: allow overlaps that "make sense"
    pb = list(playbooks)
    if len(pb) == 1:
        label = pb[0]
        rep = label == "REPLICATORS"
        mule = label == "THE_MULE"
        cham = label == "THE_CHAMELEON"
        if preferred_label in PLAYBOOKS:
            rep = rep or preferred_label == "REPLICATORS"
            mule = mule or preferred_label == "THE_MULE"
            cham = cham or preferred_label == "THE_CHAMELEON"
        return rep, mule, cham

    u = rng.random()
    if len(pb) == 3 and u < p_triple:
        return True, True, True

    if u < p_triple + p_pair:
        a, b = rng.choice(pb, size=2, replace=False)
        return (a == "REPLICATORS" or b == "REPLICATORS", a == "THE_MULE" or b == "THE_MULE", a == "THE_CHAMELEON" or b == "THE_CHAMELEON")

    # otherwise single label from the campaign set
    label = rng.choice(pb)
    rep = label == "REPLICATORS"
    mule = label == "THE_MULE"
    cham = label == "THE_CHAMELEON"
    if preferred_label in PLAYBOOKS:
        rep = rep or preferred_label == "REPLICATORS"
        mule = mule or preferred_label == "THE_MULE"
        cham = cham or preferred_label == "THE_CHAMELEON"
    return rep, mule, cham


class _ParquetBatchWriter:
    """Minimal parquet row-group writer for streaming batches."""

    def __init__(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.path = Path(self._tmpdir.name) / "buffer.parquet"
        self._writer: pq.ParquetWriter | None = None
        self._row_groups = 0

    def write(self, batch: dict[str, list | np.ndarray]) -> None:
        if not batch:
            return
        df = pd.DataFrame(batch)
        if not df.empty and "event_ts" in df.columns:
            df["event_ts"] = pd.to_datetime(df["event_ts"], utc=False)
        table = pa.Table.from_pandas(df, preserve_index=False)
        if self._writer is None:
            self._writer = pq.ParquetWriter(self.path, table.schema)
        self._writer.write_table(table)
        self._row_groups += 1

    def close(self) -> None:
        if self._writer is not None:
            self._writer.close()
            self._writer = None

    def to_dataframe(self) -> pd.DataFrame:
        self.close()
        if not self.path.exists() or self._row_groups == 0:
            self.cleanup()
            return pd.DataFrame()
        table = pq.read_table(self.path)
        df = table.to_pandas()
        self.cleanup()
        return df

    def cleanup(self) -> None:
        try:
            self.path.unlink(missing_ok=True)
        finally:
            self._tmpdir.cleanup()


def generate_skynet(cfg: AppConfig, run_id: str, seed: int | None = None) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Generate SKYNET login_attempt + checkout_attempt raw tables.

    Deterministic for fixed (seed, config, run_id).
    """
    s = cfg.synthetic.skynet
    rng = np.random.default_rng(cfg.run.seed if seed is None else seed)

    attack_setup = _setup_attack_pattern(s, rng)
    pa = None
    login_schema = None
    checkout_schema = None
    if importlib.util.find_spec("pyarrow") is not None:
        import pyarrow as pa  # type: ignore

        tz = str(BA_TZ)
        login_schema = pa.schema(
            [
                ("run_id", pa.string()),
                ("event_id", pa.string()),
                ("event_ts", pa.timestamp("us", tz=tz)),
                ("user_id", pa.string()),
                ("session_id", pa.string()),
                ("ip_hash", pa.string()),
                ("device_fingerprint_hash", pa.string()),
                ("country", pa.string()),
                ("is_fraud", pa.bool_()),
                ("label_replicators", pa.bool_()),
                ("label_the_mule", pa.bool_()),
                ("label_the_chameleon", pa.bool_()),
                ("label_benign", pa.bool_()),
                ("metadata_json", pa.string()),
                ("login_result", pa.string()),
                ("failure_reason", pa.string()),
                ("username_present", pa.bool_()),
                ("mfa_used", pa.bool_()),
                ("mfa_result", pa.string()),
                ("support_contacted", pa.bool_()),
                ("support_channel", pa.string()),
                ("support_responder_type", pa.string()),
                ("support_wait_seconds", pa.int64()),
                ("support_handle_seconds", pa.int64()),
                ("support_cost_usd", pa.float64()),
                ("support_resolution", pa.string()),
                ("support_offset_seconds", pa.int64()),
            ]
        )

        checkout_schema = pa.schema(
            [
                ("run_id", pa.string()),
                ("event_id", pa.string()),
                ("event_ts", pa.timestamp("us", tz=tz)),
                ("user_id", pa.string()),
                ("session_id", pa.string()),
                ("ip_hash", pa.string()),
                ("device_fingerprint_hash", pa.string()),
                ("country", pa.string()),
                ("is_fraud", pa.bool_()),
                ("metadata_json", pa.string()),
                ("payment_value", pa.float64()),
                ("basket_size", pa.int64()),
                ("is_first_time_user", pa.bool_()),
                ("is_premium_user", pa.bool_()),
                ("credit_card_hash", pa.string()),
                ("checkout_result", pa.string()),
                ("decline_reason", pa.string()),
            ]
        )

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

    batch_size = int(max(1, getattr(s, "batch_size", 50000)))
    login_writer = _ParquetBatchWriter()
    login_batch: dict[str, list] = {}
    event_counter = 0
    meta_cache: dict[tuple[str | None, bool, bool, bool], str] = {}

    for h in range(total_hours):
        ts0 = hour_starts[h]
    # Precompute hour starts
    hour_starts = [start_dt + timedelta(hours=h) for h in range(total_hours)]

    def _append_batch(batches: list, data: dict, schema=None):
        if pa is not None and schema is not None:
            batches.append(pa.Table.from_pydict(data, schema=schema))
        else:
            batches.append(pd.DataFrame(data))

    def _concat_batches(batches: list) -> pd.DataFrame:
        if not batches:
            return pd.DataFrame()
        if pa is not None and batches and isinstance(batches[0], pa.Table):
            return pa.concat_tables(batches).to_pandas()
        return pd.concat(batches, ignore_index=True)

    login_batches: list = []
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

        offsets, attack_flags, preferred_labels = _plan_hour_offsets(
            rng, n, attack_rate, attack_setup, camp_playbooks
        )

        # sample users
        users = rng.choice(user_ids, size=n, replace=True, p=weights)
        # per-event ts within hour (already sorted)
        event_ts = [ts0 + timedelta(seconds=int(o)) for o in offsets]

        for i in range(n):
            event_counter += 1
            eid = f"login_{event_counter:010d}"
        event_ts = np.array([ts0 + timedelta(seconds=int(o)) for o in offsets], dtype=object)
        event_ids = np.array([f"login_{event_counter + i + 1:010d}" for i in range(n)], dtype=object)
        event_counter += n

        batch = {
            "run_id": np.full(n, run_id, dtype=object),
            "event_id": event_ids,
            "event_ts": event_ts,
            "user_id": users.astype(object),
            "session_id": np.empty(n, dtype=object),
            "ip_hash": np.empty(n, dtype=object),
            "device_fingerprint_hash": np.empty(n, dtype=object),
            "country": np.full(n, "AR", dtype=object),
            "is_fraud": np.empty(n, dtype=bool),
            "label_replicators": np.empty(n, dtype=bool),
            "label_the_mule": np.empty(n, dtype=bool),
            "label_the_chameleon": np.empty(n, dtype=bool),
            "label_benign": np.empty(n, dtype=bool),
            "metadata_json": np.empty(n, dtype=object),
            "login_result": np.empty(n, dtype=object),
            "failure_reason": np.empty(n, dtype=object),
            "username_present": np.full(n, True, dtype=bool),
            "mfa_used": np.empty(n, dtype=bool),
            "mfa_result": np.empty(n, dtype=object),
            "support_contacted": np.empty(n, dtype=bool),
            "support_channel": np.empty(n, dtype=object),
            "support_responder_type": np.empty(n, dtype=object),
            "support_wait_seconds": np.empty(n, dtype=object),
            "support_handle_seconds": np.empty(n, dtype=object),
            "support_cost_usd": np.empty(n, dtype=object),
            "support_resolution": np.empty(n, dtype=object),
            "support_offset_seconds": np.empty(n, dtype=object),
        }

        for i in range(n):
            uid = str(users[i])
            is_attack = bool(attack_flags[i])

            if is_attack:
                rep, mule, cham = _sample_attack_labels(
                    rng,
                    camp_playbooks,
                    s.spikes.p_pair_overlap,
                    s.spikes.p_triple_overlap,
                    preferred_labels[i],
                )
            else:
                rep = mule = cham = False

            benign = not (rep or mule or cham)
            is_fraud = not benign

            # Outcome shaping
            if benign:
                login_result = rng.choice(["success", "failure", "challenge", "lockout"], p=[0.80, 0.15, 0.04, 0.01])
            else:
                if rep and not (mule or cham):
                    # spray-style: lots of bulk failures + lockouts
                    login_result = rng.choice(["success", "failure", "challenge", "lockout"], p=[0.10, 0.45, 0.25, 0.20])
                elif mule and not (rep or cham):
                    # targeted takeover attempts
                    login_result = rng.choice(["success", "failure", "challenge", "lockout"], p=[0.40, 0.35, 0.15, 0.10])
                else:
                    # adaptive attackers (chameleon or mixed packs)
                    login_result = rng.choice(["success", "failure", "challenge", "lockout"], p=[0.10, 0.45, 0.25, 0.20])
                elif mule and not rep:
                    login_result = rng.choice(["success", "failure", "challenge", "lockout"], p=[0.40, 0.35, 0.15, 0.10])
                else:
                    login_result = rng.choice(["success", "failure", "challenge", "lockout"], p=[0.22, 0.33, 0.28, 0.17])

            failure_reason = None
            if login_result == "failure":
                failure_reason = rng.choice(["bad_password", "mfa_failed", "rate_limited", "other"], p=[0.55, 0.20, 0.20, 0.05])

            username_present = True
            if benign:
                mfa_used = bool(rng.random() < 0.35)
            elif rep and not mule:
                mfa_used = bool(rng.random() < 0.10)
            elif mule and not rep:
                mfa_used = bool(rng.random() < 0.25)
            else:
                mfa_used = bool(rng.random() < 0.18)
            if not mfa_used:
                mfa_result = "not_applicable"
            else:
                mfa_result = rng.choice(["pass", "fail"], p=[0.92 if benign else 0.40, 0.08 if benign else 0.60])

            support_base = 0.04 if benign else (0.10 if rep else 0.22 if mule else 0.16)
            support_contacted = bool(rng.random() < support_base + (0.06 if login_result in ("challenge", "lockout") else 0.0))
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

            key = (camp_id, rep, mule, cham)
            if key not in meta_cache:
                meta_cache[key] = json.dumps(
                    {
                        "campaign_id": camp_id,
                        "playbooks": [
                            p
                            for p in (
                                "REPLICATORS" if rep else None,
                                "THE_MULE" if mule else None,
                                "THE_CHAMELEON" if cham else None,
                            )
                            if p
                        ],
                    },
                    separators=(",", ":"),
                    ensure_ascii=True,
                )

            row = {
                "run_id": run_id,
                "event_id": eid,
                "event_ts": event_ts[i],
                "user_id": uid,
                "session_id": f"sess_{stable_mod(f'{uid}|{h}|session', 100000):05d}",
                "ip_hash": f"ip_{stable_mod(f'{uid}|ip', 10000):04d}",
                "device_fingerprint_hash": f"dev_{stable_mod(f'{uid}|dev', 10000):04d}",
                "country": "AR",
                "is_fraud": bool(is_fraud),
                "label_replicators": bool(rep),
                "label_the_mule": bool(mule),
                "label_the_chameleon": bool(cham),
                "label_benign": bool(benign),
                "metadata_json": meta_cache[key],
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

            for col, val in row.items():
                login_batch.setdefault(col, []).append(val)

            if login_batch and len(next(iter(login_batch.values()))) >= batch_size:
                login_writer.write(login_batch)
                login_batch = {}

    if login_batch:
        login_writer.write(login_batch)

    login_df = login_writer.to_dataframe()

    # Checkout: mostly benign until SPACING GUILD.
    checkout_writer = _ParquetBatchWriter()
    checkout_batch: dict[str, list] = {}
    checkout_meta_json = json.dumps(
        {"campaign_id": None, "note": "fraud labels disabled until SPACING GUILD"},
        separators=(",", ":"),
        ensure_ascii=True,
    )
            meta = {
                "campaign_id": camp_id,
                "playbooks": [p for p in ("REPLICATORS" if rep else None, "THE_MULE" if mule else None, "THE_CHAMELEON" if cham else None) if p],
            }

            batch["session_id"][i] = f"sess_{stable_mod(f'{uid}|{h}|session', 100000):05d}"
            batch["ip_hash"][i] = f"ip_{stable_mod(f'{uid}|ip', 10000):04d}"
            batch["device_fingerprint_hash"][i] = f"dev_{stable_mod(f'{uid}|dev', 10000):04d}"
            batch["is_fraud"][i] = bool(is_fraud)
            batch["label_replicators"][i] = bool(rep)
            batch["label_the_mule"][i] = bool(mule)
            batch["label_the_chameleon"][i] = bool(cham)
            batch["label_benign"][i] = bool(benign)
            batch["metadata_json"][i] = json.dumps(meta, separators=(",", ":"), ensure_ascii=True)
            batch["login_result"][i] = str(login_result)
            batch["failure_reason"][i] = failure_reason
            batch["mfa_used"][i] = bool(mfa_used)
            batch["mfa_result"][i] = str(mfa_result)
            batch["support_contacted"][i] = bool(support_contacted)
            batch["support_channel"][i] = str(support_channel)
            batch["support_responder_type"][i] = str(support_responder_type)
            batch["support_wait_seconds"][i] = support_wait_seconds
            batch["support_handle_seconds"][i] = support_handle_seconds
            batch["support_cost_usd"][i] = support_cost_usd
            batch["support_resolution"][i] = str(support_resolution)
            batch["support_offset_seconds"][i] = support_offset_seconds

        _append_batch(login_batches, batch, schema=login_schema)

    login_df = _concat_batches(login_batches)
    if not login_df.empty:
        login_df["event_ts"] = pd.to_datetime(login_df["event_ts"], utc=False)

    # Checkout: mostly benign until SPACING GUILD.
    checkout_batches: list = []
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
            n = int(rng.poisson(lam=max(0.0, intensity)))
            if n <= 0:
                continue
            users = rng.choice(user_ids, size=n, replace=True, p=weights)
            offsets = rng.integers(0, 3600, size=n)
            event_ts = np.array([ts0 + timedelta(seconds=int(o)) for o in offsets], dtype=object)
            event_ids = np.array([f"checkout_{checkout_counter + i + 1:010d}" for i in range(n)], dtype=object)
            checkout_counter += n

            batch = {
                "run_id": np.full(n, run_id, dtype=object),
                "event_id": event_ids,
                "event_ts": event_ts,
                "user_id": users.astype(object),
                "session_id": np.empty(n, dtype=object),
                "ip_hash": np.empty(n, dtype=object),
                "device_fingerprint_hash": np.empty(n, dtype=object),
                "country": np.full(n, "AR", dtype=object),
                "is_fraud": np.zeros(n, dtype=bool),
                "metadata_json": np.empty(n, dtype=object),
                "payment_value": np.empty(n, dtype=float),
                "basket_size": np.empty(n, dtype=int),
                "is_first_time_user": np.empty(n, dtype=bool),
                "is_premium_user": np.empty(n, dtype=bool),
                "credit_card_hash": np.empty(n, dtype=object),
                "checkout_result": np.empty(n, dtype=object),
                "decline_reason": np.empty(n, dtype=object),
            }

            meta = {"campaign_id": None, "note": "fraud labels disabled until SPACING GUILD"}

            for i in range(n):
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

                row = {
                    "run_id": run_id,
                    "event_id": eid,
                    "event_ts": event_ts[i],
                    "user_id": uid,
                    "session_id": f"sess_{stable_mod(f'{uid}|{h}|session', 100000):05d}",
                    "ip_hash": f"ip_{stable_mod(f'{uid}|ip', 10000):04d}",
                    "device_fingerprint_hash": f"dev_{stable_mod(f'{uid}|dev', 10000):04d}",
                    "country": "AR",
                    "is_fraud": False,
                    "metadata_json": checkout_meta_json,
                    "payment_value": float(np.clip(rng.lognormal(mean=3.1, sigma=0.6), 1.0, 5000.0)),
                    "basket_size": int(rng.integers(1, 7)),
                    "is_first_time_user": bool(rng.random() < 0.18),
                    "is_premium_user": bool(rng.random() < 0.25),
                    "credit_card_hash": None if rng.random() < 0.15 else f"cc_{stable_mod(f'{uid}|cc', 200000):06d}",
                    "checkout_result": str(checkout_result),
                    "decline_reason": decline_reason,
                }

                for col, val in row.items():
                    checkout_batch.setdefault(col, []).append(val)

                if checkout_batch and len(next(iter(checkout_batch.values()))) >= batch_size:
                    checkout_writer.write(checkout_batch)
                    checkout_batch = {}

    if checkout_batch:
        checkout_writer.write(checkout_batch)

    checkout_df = checkout_writer.to_dataframe()
                batch["session_id"][i] = f"sess_{stable_mod(f'{uid}|{h}|session', 100000):05d}"
                batch["ip_hash"][i] = f"ip_{stable_mod(f'{uid}|ip', 10000):04d}"
                batch["device_fingerprint_hash"][i] = f"dev_{stable_mod(f'{uid}|dev', 10000):04d}"
                batch["metadata_json"][i] = json.dumps(meta, separators=(",", ":"), ensure_ascii=True)
                batch["payment_value"][i] = float(np.clip(rng.lognormal(mean=3.1, sigma=0.6), 1.0, 5000.0))
                batch["basket_size"][i] = int(rng.integers(1, 7))
                batch["is_first_time_user"][i] = bool(rng.random() < 0.18)
                batch["is_premium_user"][i] = bool(rng.random() < 0.25)
                batch["credit_card_hash"][i] = None if rng.random() < 0.15 else f"cc_{stable_mod(f'{uid}|cc', 200000):06d}"
                batch["checkout_result"][i] = str(checkout_result)
                batch["decline_reason"][i] = decline_reason

            _append_batch(checkout_batches, batch, schema=checkout_schema)

    checkout_df = _concat_batches(checkout_batches)
    if not checkout_df.empty:
        checkout_df["event_ts"] = pd.to_datetime(checkout_df["event_ts"], utc=False)
    # Deterministic exact-k adverse assignment to reduce variance in small runs.
    # Note: this keeps checkout mostly benign until SPACING GUILD, while honoring the configured rate.
    try:
        n = len(checkout_df)
        if n > 0:
            k = int(round(float(s.checkout_adverse_rate) * n))
            k = max(0, min(k, n))
            rng_adv = np.random.default_rng(cfg.run.seed + 77777)
            adverse_idx = set(rng_adv.choice(n, size=k, replace=False).tolist()) if k > 0 else set()

            # Default all to success.
            checkout_df["checkout_result"] = "success"
            checkout_df["decline_reason"] = None

            if k > 0:
                idx_list = list(adverse_idx)

                # failure vs review
                fail_or_review = rng_adv.choice(["failure", "review"], size=k, p=[0.80, 0.20])
                checkout_df.loc[checkout_df.index[idx_list], "checkout_result"] = fail_or_review

                # decline_reason only for failures
                failure_mask = (checkout_df["checkout_result"] == "failure")
                fcount = int(failure_mask.sum())
                if fcount > 0:
                    reasons = rng_adv.choice(
                        ["insufficient_funds", "network_error", "other"],
                        size=fcount,
                        p=[0.40, 0.35, 0.25],
                    )
                    checkout_df.loc[failure_mask, "decline_reason"] = reasons
    except Exception:
        # If anything unexpected happens, keep the stochastic assignment.
        pass

    meta = {
        "attack_pattern_setup": {
            "comment": "pack-style attack injection to surface label separation",
            "parameters": asdict(attack_setup),
        },
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
