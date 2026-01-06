from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class FeatureSpec(BaseModel):
    """Spec describing how a feature table was produced."""

    spec_version: str = Field(default="1")
    event_type: str = Field(default="login_attempt")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().replace(microsecond=0).isoformat() + "Z")

    windows: list[str]
    entities: list[str]
    strict_past_only: bool = True

    include_support: bool = True
    include_labels: bool = True
    include_is_fraud: bool = True

    keys: list[str] = Field(default_factory=lambda: ["event_id", "event_ts", "user_id", "session_id"])
    label_columns: list[str] = Field(default_factory=lambda: ["label_replicators", "label_the_mule", "label_the_chameleon", "label_benign"])
    derived_columns: list[str] = Field(default_factory=lambda: ["is_fraud"])
    split_column: str | None = None
    partition_columns: list[str] = Field(default_factory=list)

    feature_columns: list[str] = Field(default_factory=list)

    def to_json(self) -> dict[str, Any]:
        return self.model_dump()


class FeatureManifest(BaseModel):
    """Run-local manifest for features artifacts."""

    run_id: str
    event_type: str
    features_rows: int
    features_cols: int

    artifact_path: str
    artifact_format: str
    artifact_note: str | None = None
    content_hash: str
    split_column: str | None = None
    partition_columns: list[str] = Field(default_factory=list)

    spec: FeatureSpec
