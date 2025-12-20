"""RR determinism signature.

This module is intentionally dependency-light and uses only project outputs.
It produces a stable JSON signature for a run_id to sanity-check determinism
across two consecutive RR runs.
"""

from __future__ import annotations

import argparse
import json
import hashlib
from pathlib import Path
from typing import Any, Dict

import pandas as pd


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _numeric_summary(df: pd.DataFrame) -> Dict[str, Any]:
    num = df.select_dtypes(include=["number"])
    if num.empty:
        return {"n_num_cols": 0}
    # Stable summaries (rounded) for determinism sanity.
    means = num.mean(numeric_only=True).round(6).to_dict()
    stds = num.std(numeric_only=True).fillna(0).round(6).to_dict()
    # Sort keys for determinism.
    means = {k: float(means[k]) for k in sorted(means.keys())}
    stds = {k: float(stds[k]) for k in sorted(stds.keys())}
    return {
        "n_num_cols": int(num.shape[1]),
        "means": means,
        "stds": stds,
    }


def build_signature(repo_root: Path, run_id: str) -> Dict[str, Any]:
    rdir = repo_root / "runs" / run_id
    if not rdir.exists():
        raise SystemExit(f"Run folder not found: {rdir}")

    manifest_path = rdir / "manifest.json"
    metrics_path = rdir / "models" / "login_attempt" / "baselines" / "metrics.json"
    features_path = rdir / "features" / "login_attempt" / "features.parquet"
    feature_spec_path = rdir / "features" / "login_attempt" / "feature_spec.json"

    # Dataset splits (login_attempt is MVP focus)
    ds = {
        "train": rdir / "dataset" / "login_attempt" / "train.parquet",
        "time_eval": rdir / "dataset" / "login_attempt" / "time_eval.parquet",
        "user_holdout": rdir / "dataset" / "login_attempt" / "user_holdout.parquet",
    }

    m = json.loads(manifest_path.read_text(encoding="utf-8"))

    # Row counts for splits
    split_rows: Dict[str, int] = {}
    for k, p in ds.items():
        if not p.exists():
            raise SystemExit(f"Missing dataset split: {p}")
        # read minimal columns for speed
        dfi = pd.read_parquet(p, columns=["user_id"])
        split_rows[k] = int(dfi.shape[0])

    # Features summary
    fdf = pd.read_parquet(features_path)
    feat_summary = {
        "rows": int(fdf.shape[0]),
        "cols": int(fdf.shape[1]),
        "numeric": _numeric_summary(fdf),
        "feature_spec_sha256": _sha256_file(feature_spec_path) if feature_spec_path.exists() else None,
    }

    # Baseline metrics (select the stable “headline” numbers)
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    # Expected structure: metrics["models"][model]["splits"][split][...]
    model_summ: Dict[str, Any] = {}
    for model_name in sorted((metrics.get("models") or {}).keys()):
        mm = metrics["models"][model_name] or {}
        splits = mm.get("splits") or {}
        split_out: Dict[str, Any] = {}
        for split in ["train", "time_eval", "user_holdout"]:
            sm = splits.get(split) or {}
            split_out[split] = {
                "pr_auc": float(sm.get("pr_auc")) if sm.get("pr_auc") is not None else None,
                "roc_auc": float(sm.get("roc_auc")) if sm.get("roc_auc") is not None else None,
                "recall_at_1pct_fpr": float(sm.get("recall_at_1pct_fpr")) if sm.get("recall_at_1pct_fpr") is not None else None,
            }
        model_summ[model_name] = {
            "splits": split_out,
        }

    return {
        "run_id": run_id,
        "manifest_sha256": _sha256_file(manifest_path),
        "login_split_rows": split_rows,
        "features": feat_summary,
        "baseline_models": model_summ,
        # Keep minimal config identity if present
        "config_path": (m.get("config", {}) or {}).get("path"),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[3]
    sig = build_signature(repo_root, args.run_id)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(sig, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
