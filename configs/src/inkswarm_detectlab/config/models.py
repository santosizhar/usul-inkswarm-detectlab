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


class AppConfig(BaseModel):
    run: RunConfig = Field(default_factory=RunConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)
    synthetic: SyntheticConfig = Field(default_factory=SyntheticConfig)
    dataset: DatasetConfig = Field(default_factory=DatasetConfig)
