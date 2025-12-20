from __future__ import annotations

from pathlib import Path
import json
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd

from ..config import AppConfig
from ..io.paths import run_dir as run_dir_for, dataset_split_basepath, manifest_path
from ..io.tables import read_auto
from ..io.manifest import read_manifest, write_manifest
from ..utils.canonical import canonicalize_df
from ..utils.hashing import stable_hash_dict
from ..features.runner import build_login_features_for_run
from .metrics import choose_threshold_for_fpr

# sklearn is an MVP dependency (D-0004)
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score, roc_auc_score
import joblib


LABEL_COLS = ["label_replicators", "label_the_mule", "label_the_chameleon"]


def _split_event_ids(cfg: AppConfig, rdir: Path) -> dict[str, set[str]]:
    ids: dict[str, set[str]] = {}
    for split in ["train", "time_eval", "user_holdout"]:
        sdf = read_auto(dataset_split_basepath(rdir, "login_attempt", split))
        ids[split] = set(sdf["event_id"].astype(str).tolist())
    return ids


def _load_features(cfg: AppConfig, rdir: Path) -> pd.DataFrame:
    # Always use FeatureLab output path
    base = rdir / "features" / "login_attempt" / "features"
    return read_auto(base)


def _select_X_y(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    # Feature columns: numeric only, exclude keys + labels
    exclude = {"event_id", "event_ts", "user_id", "session_id", "is_fraud", "label_benign"} | set(LABEL_COLS)
    feat_cols = [c for c in df.columns if c not in exclude and pd.api.types.is_numeric_dtype(df[c])]
    X = df[feat_cols].copy()
    ys = {lab: df[lab].astype(int).to_numpy() for lab in LABEL_COLS if lab in df.columns}
    return X, ys


def _fit_logreg(cfg: AppConfig, X: pd.DataFrame, y: np.ndarray) -> Pipeline:
    c = cfg.baselines.login_attempt.logreg
    class_weight = "balanced" if c.class_weight == "balanced" else None
    pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value=0.0)),
            ("scaler", StandardScaler(with_mean=True, with_std=True)),
            ("model", LogisticRegression(C=c.C, max_iter=c.max_iter, class_weight=class_weight, solver="lbfgs")),
        ]
    )
    pipe.fit(X, y)
    return pipe


def _fit_hgb(cfg: AppConfig, X: pd.DataFrame, y: np.ndarray) -> Pipeline:
    c = cfg.baselines.login_attempt.hgb
    model = HistGradientBoostingClassifier(
        max_iter=c.max_iter,
        learning_rate=c.learning_rate,
        max_depth=c.max_depth,
        l2_regularization=c.l2_regularization,
        early_stopping=c.early_stopping,
        validation_fraction=c.validation_fraction,
        n_iter_no_change=c.n_iter_no_change,
        random_state=cfg.run.seed,
    )
    pipe = Pipeline(steps=[("imputer", SimpleImputer(strategy="constant", fill_value=0.0)), ("model", model)])
    pipe.fit(X, y)
    return pipe


def _score_model(model: Pipeline, X: pd.DataFrame) -> np.ndarray:
    # Prefer predict_proba if available; otherwise decision_function
    if hasattr(model, "predict_proba"):
        p = model.predict_proba(X)
        return p[:, 1]
    if hasattr(model, "decision_function"):
        return model.decision_function(X)
    return model.predict(X).astype(float)


def run_login_baselines_for_run(cfg: AppConfig, *, run_id: str, force: bool = False) -> Path:
    """Train baseline models on login_attempt features and write uncommitted artifacts."""
    rdir = run_dir_for(cfg.paths.runs_dir, run_id)
    mpath = manifest_path(rdir)
    manifest = read_manifest(mpath) if mpath.exists() else {"run_id": run_id, "artifacts": {}}

    # Ensure features exist (build if missing)
    feat_base = rdir / "features" / "login_attempt" / "features"
    if not (feat_base.with_suffix(".parquet").exists() or feat_base.with_suffix(".csv").exists()):
        build_login_features_for_run(cfg, run_id=run_id, force=False)

    df = _load_features(cfg, rdir)
    split_ids = _split_event_ids(cfg, rdir)

    # Split frames
    def take(split: str) -> pd.DataFrame:
        ids = split_ids[split]
        return df[df["event_id"].astype(str).isin(ids)].copy()

    df_train = take("train")
    df_time = take("time_eval")
    df_hold = take("user_holdout")

    X_train, ys_train = _select_X_y(df_train)
    X_time, ys_time = _select_X_y(df_time)
    X_hold, ys_hold = _select_X_y(df_hold)

    bcfg = cfg.baselines.login_attempt
    if not bcfg.enabled:
        raise ValueError("baselines.login_attempt.enabled is false; nothing to do")

    out_dir = rdir / "models" / "login_attempt" / "baselines"
    if out_dir.exists() and not force:
        raise FileExistsError("Baselines output already exists. Re-run with --force to overwrite.")
    out_dir.mkdir(parents=True, exist_ok=True)

    results: dict[str, Any] = {
        "run_id": run_id,
        "target_fpr": bcfg.target_fpr,
        "labels": {},
        "models": {},
        "meta": {
            "train_rows": int(len(df_train)),
            "time_eval_rows": int(len(df_time)),
            "user_holdout_rows": int(len(df_hold)),
        },
    }

    # Train per-label per-model
    for label, y_tr in ys_train.items():
        results["labels"][label] = {}
        for model_name in bcfg.models:
            if model_name == "logreg":
                model = _fit_logreg(cfg, X_train, y_tr)
            elif model_name == "hgb":
                model = _fit_hgb(cfg, X_train, y_tr)
            else:
                raise ValueError(f"Unknown model: {model_name}")

            # Scores
            s_time = _score_model(model, X_time)
            s_hold = _score_model(model, X_hold)

            # Metrics
            y_time = ys_time[label]
            y_hold = ys_hold[label]

            ap_time = float(average_precision_score(y_time, s_time)) if len(y_time) else 0.0
            ap_hold = float(average_precision_score(y_hold, s_hold)) if len(y_hold) else 0.0
            try:
                roc_time = float(roc_auc_score(y_time, s_time)) if len(np.unique(y_time)) > 1 else 0.0
            except Exception:
                roc_time = 0.0
            try:
                roc_hold = float(roc_auc_score(y_hold, s_hold)) if len(np.unique(y_hold)) > 1 else 0.0
            except Exception:
                roc_hold = 0.0

            thr_time = choose_threshold_for_fpr(y_time, s_time, bcfg.target_fpr)
            thr_hold = choose_threshold_for_fpr(y_hold, s_hold, bcfg.target_fpr)

            # Persist model
            model_path = out_dir / f"{label}__{model_name}.joblib"
            joblib.dump(model, model_path)

            results["labels"][label][model_name] = {
                "time_eval": {
                    "pr_auc": ap_time,
                    "roc_auc": roc_time,
                    "threshold_for_fpr": thr_time.threshold,
                    "fpr": thr_time.fpr,
                    "recall": thr_time.recall,
                    "precision": thr_time.precision,
                },
                "user_holdout": {
                    "pr_auc": ap_hold,
                    "roc_auc": roc_hold,
                    "threshold_for_fpr": thr_hold.threshold,
                    "fpr": thr_hold.fpr,
                    "recall": thr_hold.recall,
                    "precision": thr_hold.precision,
                },
                "model_path": str(model_path.relative_to(cfg.paths.runs_dir)),
            }

    # Write artifacts
    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path = out_dir / "report.md"
    report_path.write_text(_render_report(results), encoding="utf-8")

    # Update run manifest with pointers (uncommitted by default, but recorded)
    artifacts = manifest.get("artifacts", {}) or {}
    artifacts["models/login_attempt/baselines/metrics"] = {"path": str(metrics_path.relative_to(cfg.paths.runs_dir)), "format": "json", "note": "UNCOMMITTED", "rows": None, "content_hash": stable_hash_dict(results)}
    artifacts["models/login_attempt/baselines/report"] = {"path": str(report_path.relative_to(cfg.paths.runs_dir)), "format": "md", "note": "UNCOMMITTED", "rows": None, "content_hash": stable_hash_dict({"report": report_path.read_text(encoding="utf-8")})}
    manifest["artifacts"] = artifacts
    write_manifest(mpath, manifest)

    return rdir


def _render_report(results: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Baseline Report — login_attempt")
    lines.append("")
    lines.append(f"- run_id: `{results.get('run_id')}`")
    lines.append(f"- target_fpr: {results.get('target_fpr')}")
    meta = results.get("meta", {}) or {}
    lines.append(f"- rows: train={meta.get('train_rows')}, time_eval={meta.get('time_eval_rows')}, user_holdout={meta.get('user_holdout_rows')}")
    lines.append("")
    lines.append("## Per-label metrics")
    lines.append("")
    for label, m in (results.get("labels") or {}).items():
        lines.append(f"### {label}")
        for model_name, mm in (m or {}).items():
            t = mm["time_eval"]
            h = mm["user_holdout"]
            lines.append(f"- **{model_name}**")
            lines.append(f"  - time_eval: PR-AUC={t['pr_auc']:.4f}, ROC-AUC={t['roc_auc']:.4f}, thr={t['threshold_for_fpr']:.6g}, FPR={t['fpr']:.4f}, recall={t['recall']:.4f}")
            lines.append(f"  - user_holdout: PR-AUC={h['pr_auc']:.4f}, ROC-AUC={h['roc_auc']:.4f}, thr={h['threshold_for_fpr']:.6g}, FPR={h['fpr']:.4f}, recall={h['recall']:.4f}")
        lines.append("")
    return "\n".join(lines) + "\n"
