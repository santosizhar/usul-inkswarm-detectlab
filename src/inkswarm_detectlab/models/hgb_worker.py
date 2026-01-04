from __future__ import annotations

"""Experimental HGB worker.

Why this exists
---------------
Some platforms / wheels have been observed to hard-abort the Python interpreter
during HistGradientBoostingClassifier.fit(). When that happens, there is no
Python traceback to catch.

To keep BaselineLab fail-closed *and* diagnosable, we fit HGB in a subprocess.
If the worker aborts, the parent process can surface a clear "model failed"
entry in metrics.json and exit non-zero.
"""

import argparse
import json
from pathlib import Path

import pandas as pd

from ..config import load_config
from ..io.paths import run_dir as run_dir_for, dataset_split_basepath
from ..io.tables import read_auto


def _select_X_y(df: pd.DataFrame, label: str) -> tuple[pd.DataFrame, pd.Series]:
    exclude = {
        "event_id",
        "event_ts",
        "user_id",
        "session_id",
        "is_fraud",
        "label_benign",
        "label_replicators",
        "label_the_mule",
        "label_the_chameleon",
    }
    feat_cols = [c for c in df.columns if c not in exclude and pd.api.types.is_numeric_dtype(df[c])]
    if label not in df.columns:
        raise ValueError(f"Label column not found: {label}")
    X = df[feat_cols].copy()
    y = df[label].astype(int)
    return X, y


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, type=str, help="Path to YAML config")
    ap.add_argument("--run-id", required=True, type=str)
    ap.add_argument("--label", required=True, type=str)
    ap.add_argument("--out-dir", required=True, type=str)
    args = ap.parse_args(argv)

    cfg_path = Path(args.config)
    cfg = load_config(cfg_path)
    run_id = str(args.run_id)
    label = str(args.label)
    out_dir = Path(args.out_dir)

    rdir = run_dir_for(cfg.paths.runs_dir, run_id)

    # Load FeatureLab output
    feat_base = rdir / "features" / "login_attempt" / "features"
    df = read_auto(feat_base)

    # Restrict to TRAIN split
    train_split = read_auto(dataset_split_basepath(rdir, "login_attempt", "train"))
    train_ids = set(train_split["event_id"].astype(str).tolist())
    df_train = df[df["event_id"].astype(str).isin(train_ids)].copy()

    X_train, y_train = _select_X_y(df_train, label)

    # Local sklearn imports (kept inside worker)
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.ensemble import HistGradientBoostingClassifier
    import joblib

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
    pipe.fit(X_train, y_train.to_numpy())

    out_dir.mkdir(parents=True, exist_ok=True)
    model_path = (out_dir / f"{label}__hgb.joblib").resolve()
    joblib.dump(pipe, model_path)

    payload = {
        "model_path": str(model_path),
        "meta": {
            "feature_count": int(X_train.shape[1]),
            "train_rows": int(X_train.shape[0]),
        },
    }
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
