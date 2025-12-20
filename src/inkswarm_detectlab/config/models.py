from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

DEFAULT_SCHEMA_VERSION = "v1"


class PathsConfig(BaseModel):
    runs_dir: Path = Field(default=Path("runs"), description="Base directory for all runs (repo-relative by default).")


class RunConfig(BaseModel):
    schema_version: str = Field(default=DEFAULT_SCHEMA_VERSION)
    timezone: str = Field(default="America/Argentina/Buenos_Aires")
    seed: int = Field(default=1337, ge=0)

    # Optional: allow pinning a run_id in config (useful for committed fixtures like RUN_SAMPLE_SMOKE_0001).
    run_id: str | None = Field(default=None)


class SkynetSeasonalityConfig(BaseModel):
    # Hour-of-day multipliers (length 24). If not provided, defaults are used.
    hourly_factors: list[float] | None = Field(default=None)
    # Day-of-week multipliers (Mon=0..Sun=6). If not provided, defaults are used.
    weekday_factors: list[float] | None = Field(default=None)


class SkynetSpikeConfig(BaseModel):
    enabled: bool = Field(default=True)
    n_campaigns: int = Field(default=4, ge=0)
    duration_hours_min: int = Field(default=1, ge=1)
    duration_hours_max: int = Field(default=4, ge=1)

    # The generator uses campaign "types" that may modify volume, attack share, or both.
    campaign_types: list[Literal["VOLUME_SPIKE", "SHARE_SPIKE", "MIXED_SPIKE", "PERSISTENT_LOW"]] = Field(
        default_factory=lambda: ["VOLUME_SPIKE", "SHARE_SPIKE", "MIXED_SPIKE", "PERSISTENT_LOW"]
    )

    # How likely each playbook is to be involved in a campaign.
    playbook_weights: dict[str, float] = Field(
        default_factory=lambda: {"REPLICATORS": 0.45, "THE_MULE": 0.20, "THE_CHAMELEON": 0.35}
    )

    # Overlap behavior (triples allowed but typically rare)
    p_pair_overlap: float = Field(default=0.20, ge=0.0, le=1.0)
    p_triple_overlap: float = Field(default=0.04, ge=0.0, le=1.0)


class SkynetSyntheticConfig(BaseModel):
    # Time window
    start_date: date = Field(default=date(2025, 12, 1), description="Local start date in BA timezone.")
    days: int = Field(default=30, ge=1)

    # Population / volumes
    n_users: int = Field(default=5000, ge=1)
    login_events_per_day: int = Field(default=20000, ge=1)
    checkout_events_per_day: int = Field(default=2000, ge=0)

    # Prevalence
    attack_prevalence: float = Field(default=0.06, ge=0.0, le=1.0)

    # Checkout: adverse outcomes until SPACING GUILD (fraud labels effectively disabled here)
    checkout_adverse_rate: float = Field(default=0.005, ge=0.0, le=1.0)

    # Realism knobs
    seasonality: SkynetSeasonalityConfig = Field(default_factory=SkynetSeasonalityConfig)
    spikes: SkynetSpikeConfig = Field(default_factory=SkynetSpikeConfig)


class SyntheticConfig(BaseModel):
    skynet: SkynetSyntheticConfig = Field(default_factory=SkynetSyntheticConfig)


class DatasetBuildConfig(BaseModel):
    time_split: float = Field(default=0.85, gt=0.0, lt=1.0)
    user_holdout: float = Field(default=0.15, gt=0.0, lt=1.0)
    canonical_sort_keys: list[str] = Field(default_factory=lambda: ["event_ts", "user_id", "event_id"])


class DatasetConfig(BaseModel):
    build: DatasetBuildConfig = Field(default_factory=DatasetBuildConfig)


# -----------------------------
# D-0003: FeatureLab (login_attempt)
# -----------------------------

class LoginFeatureConfig(BaseModel):
    enabled: bool = Field(default=True)

    # Time windows for rolling aggregates.
    windows: list[str] = Field(default_factory=lambda: ["1h", "6h", "24h", "7d"])

    # Entities to aggregate by (safe aggregates only).
    entities: list[Literal["user", "ip", "device"]] = Field(default_factory=lambda: ["user", "ip", "device"])

    # Strict past-only leakage control.
    strict_past_only: bool = Field(default=True)

    # Include support aggregates (support is embedded inside login_attempt).
    include_support: bool = Field(default=True)

    # Include label columns in feature table (multi-label heads).
    include_labels: bool = Field(default=True)

    # Include derived is_fraud boolean.
    include_is_fraud: bool = Field(default=True)


class FeaturesConfig(BaseModel):
    login_attempt: LoginFeatureConfig = Field(default_factory=LoginFeatureConfig)


# -----------------------------
# D-0004: BaselineLab (login_attempt)
# -----------------------------

class LogRegBaselineConfig(BaseModel):
    C: float = Field(default=1.0, gt=0.0)
    max_iter: int = Field(default=1000, ge=1)
    class_weight: Literal["balanced", "none"] = Field(default="balanced")


class HGBBaselineConfig(BaseModel):
    # Quality-first defaults (locked): max_iter=300, early_stopping disabled unless explicitly enabled.
    max_iter: int = Field(default=300, ge=1)
    learning_rate: float = Field(default=0.1, gt=0.0)
    max_depth: int | None = Field(default=None)
    l2_regularization: float = Field(default=0.0, ge=0.0)

    early_stopping: bool = Field(default=False)
    validation_fraction: float = Field(default=0.1, gt=0.0, lt=1.0)
    n_iter_no_change: int = Field(default=10, ge=1)


class LoginBaselinesConfig(BaseModel):
    enabled: bool = Field(default=True)
    models: list[Literal["logreg", "hgb"]] = Field(default_factory=lambda: ["logreg", "hgb"])
    target_fpr: float = Field(default=0.01, gt=0.0, lt=1.0)
    report_top_features: bool = Field(default=True)

    logreg: LogRegBaselineConfig = Field(default_factory=LogRegBaselineConfig)
    hgb: HGBBaselineConfig = Field(default_factory=HGBBaselineConfig)


class BaselinesConfig(BaseModel):
    login_attempt: LoginBaselinesConfig = Field(default_factory=LoginBaselinesConfig)


class AppConfig(BaseModel):
    run: RunConfig = Field(default_factory=RunConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)
    synthetic: SyntheticConfig = Field(default_factory=SyntheticConfig)
    dataset: DatasetConfig = Field(default_factory=DatasetConfig)
    features: FeaturesConfig = Field(default_factory=FeaturesConfig)
    baselines: BaselinesConfig = Field(default_factory=BaselinesConfig)
