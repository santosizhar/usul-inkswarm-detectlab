from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Any

import json

import numpy as np
import pandas as pd
from sklearn.metrics import (
    silhouette_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    adjusted_rand_score,
    normalized_mutual_info_score,
)


@dataclass
class ClusterQualityResult:
    n_rows: int
    n_features: int
    n_clusters: int
    metrics: dict[str, float]
    notes: list[str]

    def to_json(self) -> dict[str, Any]:
        return {
            "n_rows": self.n_rows,
            "n_features": self.n_features,
            "n_clusters": self.n_clusters,
            "metrics": self.metrics,
            "notes": self.notes,
        }


def _as_numeric_matrix(df: pd.DataFrame, feature_cols: Optional[list[str]]) -> tuple[np.ndarray, list[str], list[str]]:
    """Return X as float matrix + used cols + dropped cols."""
    if feature_cols is None:
        feature_cols = [c for c in df.columns if c not in ("cluster", "label", "y", "y_true", "target")]
    used = []
    dropped = []
    for c in feature_cols:
        if c not in df.columns:
            dropped.append(c)
            continue
        used.append(c)
    if not used:
        raise ValueError("No usable feature columns found. Provide --feature-col multiple times.")
    X = df[used].to_numpy()
    # Coerce to float; errors become nan and will be handled
    X = X.astype("float64", copy=False)
    return X, used, dropped


def compute_cluster_quality(
    df: pd.DataFrame,
    cluster_col: str = "cluster",
    label_col: Optional[str] = None,
    feature_cols: Optional[list[str]] = None,
    sample_n: Optional[int] = None,
    random_state: int = 42,
) -> ClusterQualityResult:
    """Compute lightweight cluster-quality metrics.

    This is intentionally generic so it can be used for:
    - any clustering stage (topic clusters, embedding clusters, behavior clusters)
    - any dataset where you have features + a cluster assignment

    Metrics:
    - Silhouette (requires >=2 clusters and numeric features)
    - Calinski-Harabasz
    - Davies-Bouldin
    - If label_col provided: ARI + NMI between clusters and labels
    """
    notes: list[str] = []

    if cluster_col not in df.columns:
        raise ValueError(f"Missing cluster column: {cluster_col!r}")

    # Drop rows without cluster assignment
    base = df.dropna(subset=[cluster_col]).copy()
    n0 = len(df)
    if len(base) != n0:
        notes.append(f"dropped_rows_missing_cluster={n0 - len(base)}")

    # Optionally sample for speed
    if sample_n is not None and len(base) > sample_n:
        base = base.sample(n=sample_n, random_state=random_state)
        notes.append(f"sampled_rows={sample_n}")

    clusters = base[cluster_col].to_numpy()
    # Normalize clusters to ints for sklearn metrics that expect labels
    # (works fine for strings too)
    _, clusters = np.unique(clusters, return_inverse=True)
    n_clusters = int(np.unique(clusters).shape[0])

    X, used_cols, dropped_cols = _as_numeric_matrix(base, feature_cols)
    if dropped_cols:
        notes.append("missing_feature_cols=" + ",".join(dropped_cols))

    # Basic cleaning: drop rows with any nan/inf in features
    mask = np.isfinite(X).all(axis=1)
    if not mask.all():
        notes.append(f"dropped_rows_nonfinite_features={int((~mask).sum())}")
        X = X[mask]
        clusters = clusters[mask]
    n_rows = int(X.shape[0])
    n_features = int(X.shape[1])

    metrics: dict[str, float] = {}

    if n_rows == 0 or n_clusters < 2:
        notes.append("insufficient_data_for_internal_metrics")
    else:
        # silhouette can be expensive; guard a bit
        metrics["silhouette"] = float(silhouette_score(X, clusters, metric="euclidean"))
        metrics["calinski_harabasz"] = float(calinski_harabasz_score(X, clusters))
        metrics["davies_bouldin"] = float(davies_bouldin_score(X, clusters))

    if label_col is not None:
        if label_col not in base.columns:
            notes.append(f"label_col_missing={label_col}")
        else:
            y = base[label_col].to_numpy()
            # align with mask if we dropped nonfinite rows
            if "dropped_rows_nonfinite_features" in " ".join(notes):
                y = y[mask]
            _, y = np.unique(y, return_inverse=True)
            metrics["ari"] = float(adjusted_rand_score(y, clusters))
            metrics["nmi"] = float(normalized_mutual_info_score(y, clusters))

    return ClusterQualityResult(
        n_rows=n_rows,
        n_features=n_features,
        n_clusters=n_clusters,
        metrics=metrics,
        notes=notes,
    )


def write_cluster_quality_artifacts(
    out_dir: Path,
    result: ClusterQualityResult,
    *,
    title: str = "Cluster Quality Report",
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    p_json = out_dir / "cluster_quality.json"
    p_md = out_dir / "cluster_quality.md"

    p_json.write_text(json.dumps(result.to_json(), indent=2, sort_keys=True), encoding="utf-8")

    lines = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"- rows: **{result.n_rows}**")
    lines.append(f"- features: **{result.n_features}**")
    lines.append(f"- clusters: **{result.n_clusters}**")
    lines.append("")
    if result.metrics:
        lines.append("## Metrics")
        for k, v in sorted(result.metrics.items()):
            lines.append(f"- **{k}**: `{v:.6f}`")
        lines.append("")
    if result.notes:
        lines.append("## Notes")
        for n in result.notes:
            lines.append(f"- {n}")
        lines.append("")
    lines.append("## Interpretation (quick)")
    lines.append("- **Silhouette**: closer to 1 is cleaner separation; near 0 means overlap; negative indicates possible misassignment.")
    lines.append("- **Davies-Bouldin**: lower is better (tighter / better separated).")
    lines.append("- **Calinski-Harabasz**: higher is better (but scale depends on dataset).")
    lines.append("- **ARI/NMI**: only meaningful if you provided a ground-truth `label_col`.")
    lines.append("")

    p_md.write_text("
".join(lines), encoding="utf-8")
    return p_json, p_md
