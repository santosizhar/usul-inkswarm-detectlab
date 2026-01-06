from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
import platform
import subprocess
import sys
from typing import Any

import numpy as np
import pandas as pd

from ..config import AppConfig
from ..config.models import (
    LogRegBaselineConfig,
    RFBaselineConfig,
    HGBBaselineConfig,
)
from ..io.paths import run_dir as run_dir_for, manifest_path
from ..io.manifest import read_manifest, write_manifest
from ..utils.canonical import canonicalize_df
from ..utils.hashing import stable_hash_dict
from ..features.runner import build_login_features_for_run
from .metrics import choose_threshold_for_fpr, top_thresholds_for_fpr
from ..synthetic.label_defs import as_markdown_table as _labels_markdown_table

# sklearn is an MVP dependency (D-0004)
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, roc_auc_score
import joblib


def _env_diagnostics() -> dict[str, Any]:
    """Best-effort environment diagnostics for crash triage.

    Stored in metrics.json under meta.env.
    """
    env: dict[str, Any] = {
        "python": sys.version.replace("\n", " "),
        "platform": platform.platform(),
    }
    try:
        import sklearn  # type: ignore

        env["sklearn"] = getattr(sklearn, "__version__", None)
    except Exception:
        env["sklearn"] = None
    try:
        import pandas as _pd  # type: ignore

        env["pandas"] = getattr(_pd, "__version__", None)
    except Exception:
        env["pandas"] = None
    try:
        import pyarrow as _pa  # type: ignore

        env["pyarrow"] = getattr(_pa, "__version__", None)
    except Exception:
        env["pyarrow"] = None
    try:
        from threadpoolctl import threadpool_info  # type: ignore

        env["threadpools"] = threadpool_info()
    except Exception:
        env["threadpools"] = None
    return env


LABEL_COLS = ["label_replicators", "label_the_mule", "label_the_chameleon"]


def _load_features(cfg: AppConfig, rdir: Path, *, split: str | None = None) -> pd.DataFrame:
    # Always use FeatureLab output path
    base = rdir / "features" / "login_attempt" / "features"
    pq_path = base.with_suffix(".parquet")
    if split is None:
        return pd.read_parquet(pq_path)
    return pd.read_parquet(pq_path, filters=[("split", "=", split)])


def _select_X_y(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    # Feature columns: numeric only, exclude keys + labels
    exclude = {"event_id", "event_ts", "user_id", "session_id", "is_fraud", "label_benign"} | set(LABEL_COLS)
    feat_cols = [c for c in df.columns if c not in exclude and pd.api.types.is_numeric_dtype(df[c])]
    X = df[feat_cols].copy()
    ys = {lab: df[lab].astype(int).to_numpy() for lab in LABEL_COLS if lab in df.columns}
    return X, ys


def _fit_logreg(
    cfg: AppConfig,
    X: np.ndarray,
    y: np.ndarray,
    *,
    logreg_cfg: LogRegBaselineConfig | None = None,
    imputer: SimpleImputer | None = None,
    scaler: StandardScaler | None = None,
    feature_names: list[str] | None = None,
) -> Pipeline:
    c = logreg_cfg or cfg.baselines.login_attempt.logreg
    class_weight = "balanced" if c.class_weight == "balanced" else None
    model = LogisticRegression(
        C=c.C,
        max_iter=c.max_iter,
        class_weight=class_weight,
        solver="lbfgs",
    )
    model.fit(X, y)

    steps = []
    if imputer is not None:
        steps.append(("imputer", deepcopy(imputer)))
    if scaler is not None:
        steps.append(("scaler", deepcopy(scaler)))
    steps.append(("model", model))

    pipe = Pipeline(steps=steps)
    if hasattr(model, "n_features_in_"):
        pipe.n_features_in_ = model.n_features_in_  # type: ignore[attr-defined]
    if feature_names is not None:
        pipe.feature_names_in_ = np.array(feature_names)  # type: ignore[attr-defined]
    return pipe


def _fit_rf(
    cfg: AppConfig,
    X: np.ndarray,
    y: np.ndarray,
    *,
    rf_cfg: RFBaselineConfig | None = None,
    imputer: SimpleImputer | None = None,
    feature_names: list[str] | None = None,
) -> Pipeline:
    c = rf_cfg or cfg.baselines.login_attempt.rf
    model = RandomForestClassifier(
        n_estimators=c.n_estimators,
        max_depth=c.max_depth,
        min_samples_leaf=c.min_samples_leaf,
        max_features=c.max_features,
        max_samples=c.max_samples,
        n_jobs=1,  # deterministic + avoids BLAS/OpenMP surprises
        random_state=cfg.run.seed,
    )
    model.fit(X, y)

    steps = []
    if imputer is not None:
        steps.append(("imputer", deepcopy(imputer)))
    steps.append(("model", model))

    pipe = Pipeline(steps=steps)
    if hasattr(model, "n_features_in_"):
        pipe.n_features_in_ = model.n_features_in_  # type: ignore[attr-defined]
    if feature_names is not None:
        pipe.feature_names_in_ = np.array(feature_names)  # type: ignore[attr-defined]
    return pipe


def _fit_hgb_in_subprocess(
    *,
    cfg_path: Path,
    run_id: str,
    label: str,
    out_dir: Path,
) -> tuple[Path, dict[str, Any]]:
    """Fit HGB in a subprocess to avoid hard-crashing the parent process.

    Some platforms/wheels can abort the interpreter during HGB `.fit()`.
    Running in a subprocess lets us capture a clear failure signal and continue.
    """
    cmd = [
        sys.executable,
        "-m",
        "inkswarm_detectlab.models.hgb_worker",
        "--config",
        str(cfg_path),
        "--run-id",
        run_id,
        "--label",
        label,
        "--out-dir",
        str(out_dir),
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        info = {
            "status": "failed",
            "returncode": int(p.returncode),
            "stdout_tail": (p.stdout or "").strip()[-2000:],
            "stderr_tail": (p.stderr or "").strip()[-2000:],
        }
        raise RuntimeError(
            "HGB worker failed (likely native crash). "
            f"returncode={p.returncode}. stderr_tail={info['stderr_tail'][:400]}"
        )
    try:
        payload = json.loads((p.stdout or "").strip())
    except Exception as e:
        raise RuntimeError(f"HGB worker returned non-JSON output. stdout_tail={(p.stdout or '')[-400:]}") from e
    model_path = Path(payload["model_path"]).resolve()
    meta = payload.get("meta", {}) or {}
    return model_path, meta


def _score_model(model: Pipeline, X: pd.DataFrame | np.ndarray) -> np.ndarray:
    # Prefer predict_proba if available; otherwise decision_function
    if hasattr(model, "predict_proba"):
        p = model.predict_proba(X)
        return p[:, 1]
    if hasattr(model, "decision_function"):
        return model.decision_function(X)
    return model.predict(X).astype(float)


def run_login_baselines_for_run(
    cfg: AppConfig,
    *,
    run_id: str,
    force: bool = False,
    cfg_path: Path | None = None,
) -> tuple[Path, dict[str, Any]]:
    """Train baseline models on login_attempt features and write uncommitted artifacts."""
    rdir = run_dir_for(cfg.paths.runs_dir, run_id)
    mpath = manifest_path(rdir)
    manifest = read_manifest(mpath) if mpath.exists() else {"run_id": run_id, "artifacts": {}}

    # Ensure features exist (build if missing)
    feat_base = rdir / "features" / "login_attempt" / "features"
    if not feat_base.with_suffix(".parquet").exists():
        build_login_features_for_run(cfg, run_id=run_id, force=False)

    df_train = _load_features(cfg, rdir, split="train")
    df_time = _load_features(cfg, rdir, split="time_eval")
    df_hold = _load_features(cfg, rdir, split="user_holdout")

    X_train, ys_train = _select_X_y(df_train)
    X_time, ys_time = _select_X_y(df_time)
    X_hold, ys_hold = _select_X_y(df_hold)

    feature_names = list(X_train.columns)

    # Fit preprocessors once on TRAIN and reuse transforms across models/labels.
    imputer = SimpleImputer(strategy="constant", fill_value=0.0)
    imputer.fit(X_train)
    X_train_imputed = imputer.transform(X_train)
    X_time_imputed = imputer.transform(X_time)
    X_hold_imputed = imputer.transform(X_hold)

    scaler = StandardScaler(with_mean=True, with_std=True)
    scaler.fit(X_train_imputed)
    X_train_scaled = scaler.transform(X_train_imputed)
    X_time_scaled = scaler.transform(X_time_imputed)
    X_hold_scaled = scaler.transform(X_hold_imputed)

    bcfg = cfg.baselines.login_attempt
    if not bcfg.enabled:
        raise ValueError("baselines.login_attempt.enabled is false; nothing to do")

    # Preset support: speed up iteration in notebooks without changing the dataset, splits, or metric definitions.
    # - The "standard" preset now defaults to lighter RF trees (200 estimators, max_depth=20) so large datasets
    #   stay tractable by default; set explicit values in config to restore the previous heavier baseline.
    # - The "fast" preset further clamps expensive knobs for quick iteration.
    preset = getattr(bcfg, "preset", "standard")
    logreg_cfg = bcfg.logreg
    rf_cfg = bcfg.rf
    hgb_cfg = bcfg.hgb
    if preset == "fast":
        # Clamp expensive knobs (but keep user's explicit settings if already smaller).
        logreg_cfg = logreg_cfg.model_copy(update={"max_iter": min(int(logreg_cfg.max_iter), 200)})

        rf_update: dict[str, Any] = {
            "n_estimators": min(int(rf_cfg.n_estimators), 100),
            "min_samples_leaf": max(int(rf_cfg.min_samples_leaf), 2),
        }
        # If max_depth is None, set a reasonable cap in fast mode.
        if rf_cfg.max_depth is None:
            rf_update["max_depth"] = 16
        else:
            rf_update["max_depth"] = min(int(rf_cfg.max_depth), 16)
        rf_cfg = rf_cfg.model_copy(update=rf_update)

        # HGB is powerful but can be expensive; disable by default in fast mode.
        if getattr(hgb_cfg, "enabled", False):
            hgb_cfg = hgb_cfg.model_copy(update={"enabled": False})

    out_dir = rdir / "models" / "login_attempt" / "baselines"
    if out_dir.exists() and not force:
        metrics_path = out_dir / "metrics.json"
        if metrics_path.exists():
            # Idempotent behavior for notebooks / RR replays:
            # if the baselines are already present, just return the existing metrics.
            try:
                existing = json.loads(metrics_path.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                existing = {"status": "ok", "note": "metrics.json unreadable; baselines dir exists"}
            return rdir, existing
        raise FileExistsError(
            "Baselines output already exists but metrics.json is missing. "
            "Re-run with --force to overwrite, or delete runs/<run_id>/models/login_attempt/baselines."
        )
    out_dir.mkdir(parents=True, exist_ok=True)

    logs_dir = rdir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / "baselines.log"

    def _log(msg: str) -> None:
        with log_path.open("a", encoding="utf-8") as f:
            f.write(msg + "\n")

    _log(f"[baselines] start run_id={run_id} out_dir={out_dir}")

    results: dict[str, Any] = {
        "run_id": run_id,
        "target_fpr": bcfg.target_fpr,
        "status": "running",
        "labels": {},
        "models": {},
        "meta": {
            "train_rows": int(len(df_train)),
            "time_eval_rows": int(len(df_time)),
            "user_holdout_rows": int(len(df_hold)),
            "env": _env_diagnostics(),
        },
    }

    results["meta"].update(
        {
            "preset": preset,
            "effective_logreg_max_iter": int(logreg_cfg.max_iter),
            "effective_rf_n_estimators": int(rf_cfg.n_estimators),
            "effective_rf_max_depth": rf_cfg.max_depth,
            "effective_rf_max_samples": rf_cfg.max_samples,
            "effective_hgb_enabled": bool(getattr(hgb_cfg, "enabled", False)),
        }
    )

    def _metrics_at_threshold(y_true: np.ndarray, scores: np.ndarray, thr: float) -> dict[str, float]:
        """Compute fpr/recall/precision for a fixed threshold."""
        y = y_true.astype(int)
        s = scores.astype(float)
        neg = (y == 0)
        pos = (y == 1)
        n_neg = int(neg.sum())
        n_pos = int(pos.sum())
        preds = (s >= float(thr))
        fp = int((preds & neg).sum())
        tp = int((preds & pos).sum())
        fpr = (fp / n_neg) if n_neg else 0.0
        recall = (tp / n_pos) if n_pos else 0.0
        precision = (tp / int(preds.sum())) if int(preds.sum()) else 0.0
        return {"fpr": float(fpr), "recall": float(recall), "precision": float(precision)}

    def _top_features(model: Any, feature_names: list[str], *, k: int = 20) -> list[dict[str, Any]]:
        """Extract top features for reporting (best-effort, model-dependent)."""
        rows: list[dict[str, Any]] = []
        core = model
        if hasattr(model, "named_steps") and "model" in getattr(model, "named_steps", {}):
            core = model.named_steps["model"]

        if hasattr(core, "coef_"):
            coefs = getattr(core, "coef_")
            if coefs is not None:
                w = np.ravel(coefs)
                idx = np.argsort(np.abs(w))[::-1][:k]
                for i in idx:
                    rows.append({"feature": feature_names[int(i)], "weight": float(w[int(i)])})
        elif hasattr(core, "feature_importances_"):
            imp = getattr(core, "feature_importances_")
            if imp is not None:
                w = np.ravel(imp)
                idx = np.argsort(w)[::-1][:k]
                for i in idx:
                    rows.append({"feature": feature_names[int(i)], "importance": float(w[int(i)])})
        return rows

    # Train per-label per-model
    had_failures = False
    n_ok = 0
    n_failed = 0
    for label, y_tr in ys_train.items():
        results["labels"][label] = {}
        _log(f"[baselines] label={label} train_rows={len(y_tr)}")
        for model_name in bcfg.models:
            model: Pipeline | None = None
            model_meta: dict[str, Any] = {}
            X_train_for_model: pd.DataFrame | np.ndarray = X_train
            X_time_for_model: pd.DataFrame | np.ndarray = X_time
            X_hold_for_model: pd.DataFrame | np.ndarray = X_hold
            try:
                if model_name == "logreg":
                    _log(f"[baselines] fit start label={label} model=logreg")
                    X_train_for_model = X_train_scaled
                    X_time_for_model = X_time_scaled
                    X_hold_for_model = X_hold_scaled
                    model = _fit_logreg(
                        cfg,
                        X_train_for_model,
                        y_tr,
                        logreg_cfg=logreg_cfg,
                        imputer=imputer,
                        scaler=scaler,
                        feature_names=feature_names,
                    )
                    _log(f"[baselines] fit ok label={label} model=logreg")
                elif model_name == "rf":
                    _log(f"[baselines] fit start label={label} model=rf")
                    X_train_for_model = X_train_imputed
                    X_time_for_model = X_time_imputed
                    X_hold_for_model = X_hold_imputed
                    model = _fit_rf(
                        cfg,
                        X_train_for_model,
                        y_tr,
                        rf_cfg=rf_cfg,
                        imputer=imputer,
                        feature_names=feature_names,
                    )
                    _log(f"[baselines] fit ok label={label} model=rf")
                elif model_name == "hgb":
                    if not getattr(hgb_cfg, "enabled", False):
                        _log(f"[baselines] skip label={label} model=hgb reason=disabled")
                        results["labels"][label][model_name] = {
                            "status": "skipped",
                            "error": "disabled by preset/config",
                            "meta": {},
                        }
                        continue
                    if cfg_path is None:
                        raise ValueError("HGB requested but cfg_path was not provided (needed for subprocess worker).")
                    # Fit in subprocess; then load back for scoring.
                    abs_model_path, model_meta = _fit_hgb_in_subprocess(
                        cfg_path=cfg_path,
                        run_id=run_id,
                        label=label,
                        out_dir=out_dir,
                    )
                    model = joblib.load(abs_model_path)
                else:
                    raise ValueError(f"Unknown model: {model_name}")
            except Exception as e:
                had_failures = True
                n_failed += 1
                _log(f"[baselines] fit FAILED label={label} model={model_name} err={e}")
                results["labels"][label][model_name] = {
                    "status": "failed",
                    "error": str(e),
                    "meta": model_meta,
                }
                continue

            # Scores
            s_train = _score_model(model, X_train_for_model)
            s_time = _score_model(model, X_time_for_model)
            s_hold = _score_model(model, X_hold_for_model)

            # Metrics
            y_time = ys_time[label]
            y_hold = ys_hold[label]

            ap_train = float(average_precision_score(y_tr, s_train)) if len(y_tr) else 0.0
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

            # D-0004 contract: choose threshold on TRAIN only, then apply to other splits.
            thr_train = choose_threshold_for_fpr(y_tr, s_train, bcfg.target_fpr)
            thr_table = [
                {"threshold": t.threshold, "fpr": t.fpr, "recall": t.recall, "precision": t.precision}
                for t in top_thresholds_for_fpr(y_tr, s_train, bcfg.target_fpr, k=3)
            ]
            time_at_train_thr = _metrics_at_threshold(y_time, s_time, thr_train.threshold)
            hold_at_train_thr = _metrics_at_threshold(y_hold, s_hold, thr_train.threshold)

            # Persist model (for hgb this may already exist; overwrite consistently)
            #
            # Layout v2 (preferred): <out_dir>/<model_name>/<label>.joblib
            # Layout v1 (legacy):   <out_dir>/<label>__<model_name>.joblib
            #
            # We write BOTH so:
            # - new runs are easy to browse and keep model artifacts grouped by model
            # - older tooling remains compatible
            by_model_dir = out_dir / model_name
            by_model_dir.mkdir(parents=True, exist_ok=True)

            by_model_path = by_model_dir / f"{label}.joblib"
            legacy_path = out_dir / f"{label}__{model_name}.joblib"
            # Always define model_path used in metrics entries
            model_path = by_model_path

            # Prefer writing the v2 layout first.
            for _path in (by_model_path, legacy_path):
                try:
                    joblib.dump(model, _path)
                except Exception:
                    # If it was written by a worker and is already there, ignore.
                    pass

            # Path we record for this baseline model (prefer v2 layout)
            model_path = by_model_path
            if not model_path.exists() and legacy_path.exists():
                model_path = legacy_path

            entry: dict[str, Any] = {
                "status": "ok",
                "train": {
                    "pr_auc": ap_train,
                    "threshold_for_fpr": thr_train.threshold,
                    "threshold_table_top3": thr_table,
                    "fpr": thr_train.fpr,
                    "recall": thr_train.recall,
                    "precision": thr_train.precision,
                },
                "time_eval": {
                    "pr_auc": ap_time,
                    "roc_auc": roc_time,
                    "threshold_used": thr_train.threshold,
                    **time_at_train_thr,
                },
                "user_holdout": {
                    "pr_auc": ap_hold,
                    "roc_auc": roc_hold,
                    "threshold_used": thr_train.threshold,
                    **hold_at_train_thr,
                },
                "model_path": str(model_path.relative_to(cfg.paths.runs_dir)),
                "meta": model_meta,
            }

            if bcfg.report_top_features:
                entry["top_features"] = _top_features(model, list(X_train.columns))

            results["labels"][label][model_name] = entry
            n_ok += 1

    # Overall status
    if n_ok == 0:
        results["status"] = "failed"
    elif had_failures:
        results["status"] = "partial"
    else:
        results["status"] = "ok"
    results["meta"]["n_ok"] = int(n_ok)
    results["meta"]["n_failed"] = int(n_failed)

    # Write artifacts
    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path = out_dir / "report.md"
    report_path.write_text(_render_report(results), encoding="utf-8")

    # Also copy a user-friendly report under runs/<run_id>/reports/
    try:
        from ..io.paths import reports_dir as _reports_dir, summary_path as _summary_path

        rep_dir = _reports_dir(rdir)
        rep_dir.mkdir(parents=True, exist_ok=True)
        user_report = rep_dir / "baselines_login_attempt.md"
        user_report.write_text(report_path.read_text(encoding="utf-8"), encoding="utf-8")

        # Upsert a baselines section into the run summary for stakeholders.
        marker_a = "<!-- BASELINES_LOGIN_ATTEMPT_START -->"
        marker_b = "<!-- BASELINES_LOGIN_ATTEMPT_END -->"
        section_lines = [
            marker_a,
            "",
            "## Baselines (login_attempt)",
            "",
            "This section summarizes baseline performance for the current run.",
            f"- detailed baseline report: `{user_report}`",
            f"- baselines log: `{log_path}`",
            "",
        ]
        # Reuse the summary table from the baseline report (rendered by _render_report)
        rep_txt = report_path.read_text(encoding="utf-8").splitlines()
        try:
            i = rep_txt.index("## Summary table")
            # take next 2 header lines + rows until blank
            j = i + 1
            while j < len(rep_txt) and rep_txt[j].strip() == "":
                j += 1
            # from j onward include until first empty line after table
            table_lines: list[str] = []
            while j < len(rep_txt):
                line = rep_txt[j]
                if line.strip() == "":
                    break
                table_lines.append(line)
                j += 1
            section_lines.extend(table_lines)
            section_lines.append("")
        except ValueError:
            section_lines.append("(Baseline summary table unavailable.)")
            section_lines.append("")

        if results.get("status") == "partial":
            section_lines.append("> **WARNING:** One or more baseline fits failed. See the log and metrics for details.")
            section_lines.append("")
        section_lines.append(marker_b)
        section = "\n".join(section_lines) + "\n"

        sp = _summary_path(rdir)
        if sp.exists():
            base = sp.read_text(encoding="utf-8")
        else:
            base = "# Inkswarm DetectLab — Run Summary\n\n"
        if marker_a in base and marker_b in base:
            pre = base.split(marker_a)[0]
            post = base.split(marker_b)[1]
            merged = pre.rstrip() + "\n\n" + section + "\n" + post.lstrip()
        else:
            merged = base.rstrip() + "\n\n" + section
        sp.write_text(merged, encoding="utf-8")
    except Exception as e:
        _log(f"[baselines] failed to write user-facing reports section: {e}")

    # Update run manifest with pointers (uncommitted by default, but recorded)
    artifacts = manifest.get("artifacts", {}) or {}
    artifacts["models/login_attempt/baselines/metrics"] = {"path": str(metrics_path.relative_to(cfg.paths.runs_dir)), "format": "json", "note": "UNCOMMITTED", "rows": None, "content_hash": stable_hash_dict(results)}
    artifacts["models/login_attempt/baselines/report"] = {"path": str(report_path.relative_to(cfg.paths.runs_dir)), "format": "md", "note": "UNCOMMITTED", "rows": None, "content_hash": stable_hash_dict({"report": report_path.read_text(encoding="utf-8")})}
    artifacts["logs/baselines"] = {"path": str(log_path.relative_to(cfg.paths.runs_dir)), "format": "text", "note": "UNCOMMITTED", "rows": None, "content_hash": stable_hash_dict({"log": log_path.read_text(encoding="utf-8") if log_path.exists() else ""})}
    manifest["artifacts"] = artifacts
    write_manifest(mpath, manifest)

    # Fail-soft behavior (MVP-friendly):
    # - If at least one model succeeded, we return normally but the caller may surface warnings.
    # - If everything failed, callers should treat this as an error.
    if n_ok == 0:
        raise RuntimeError("All baseline fits failed. See runs/<run_id>/logs/baselines.log for details.")

    return rdir, results

def _render_report(results: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Baseline Report — login_attempt")
    lines.append("")
    lines.append(f"- run_id: `{results.get('run_id')}`")
    lines.append(f"- target_fpr: {results.get('target_fpr')}")
    meta = results.get("meta", {}) or {}
    lines.append(f"- rows: train={meta.get('train_rows')}, time_eval={meta.get('time_eval_rows')}, user_holdout={meta.get('user_holdout_rows')}")
    lines.append("")
    # --- Summary table (CR-0002 requirement)
    lines.append("## Summary table")
    lines.append("")
    lines.append(
        "| label | model | train PR-AUC | train thr | train FPR | train recall | time_eval PR-AUC | time_eval FPR | time_eval recall | user_holdout PR-AUC | user_holdout FPR | user_holdout recall |"
    )
    lines.append(
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
    )
    for label, m in (results.get("labels") or {}).items():
        for model_name, mm in (m or {}).items():
            if (mm or {}).get("status") != "ok":
                continue
            tr = mm.get("train") or {}
            t = mm.get("time_eval") or {}
            h = mm.get("user_holdout") or {}
            lines.append(
                "| {label} | {model} | {tr_ap:.4f} | {thr:.6g} | {tr_fpr:.4f} | {tr_rec:.4f} | {t_ap:.4f} | {t_fpr:.4f} | {t_rec:.4f} | {h_ap:.4f} | {h_fpr:.4f} | {h_rec:.4f} |".format(
                    label=label,
                    model=model_name,
                    tr_ap=float(tr.get("pr_auc", 0.0)),
                    thr=float(tr.get("threshold_for_fpr", float("nan"))),
                    tr_fpr=float(tr.get("fpr", 0.0)),
                    tr_rec=float(tr.get("recall", 0.0)),
                    t_ap=float(t.get("pr_auc", 0.0)),
                    t_fpr=float(t.get("fpr", 0.0)),
                    t_rec=float(t.get("recall", 0.0)),
                    h_ap=float(h.get("pr_auc", 0.0)),
                    h_fpr=float(h.get("fpr", 0.0)),
                    h_rec=float(h.get("recall", 0.0)),
                )
            )
    lines.append("")

    # --- Preset + effective hyperparams (helps notebook iteration + debugging)
    preset = meta.get("preset", "standard")
    lines.append("## Training preset")
    lines.append("")
    lines.append(f"- preset: `{preset}`")
    if preset == "fast":
        lines.append("- note: 'fast' is intended for iteration; use 'standard' for final baselines.")
    for k in [
        "effective_logreg_max_iter",
        "effective_rf_n_estimators",
        "effective_rf_max_depth",
        "effective_rf_max_samples",
        "effective_hgb_enabled",
    ]:
        if k in meta:
            lines.append(f"- {k}: {meta.get(k)}")
    lines.append("")

    # --- Label definitions (dataset context)
    lines.append("## Label definitions")
    lines.append("")
    lines.append(
        "These labels are generated by the synthetic dataset generator and are **scenario tags**, not real-world ground truth."
    )
    lines.append("")
    lines.append(_labels_markdown_table())
    lines.append("")

    lines.append("## Per-label metrics")
    lines.append("")
    for label, m in (results.get("labels") or {}).items():
        lines.append(f"### {label}")
        for model_name, mm in (m or {}).items():
            status = (mm or {}).get("status")
            if status == "failed":
                lines.append(f"- **{model_name}** — ❌ failed")
                err = (mm or {}).get("error")
                if err:
                    lines.append(f"  - error: {err}")
                lines.append("")
                continue
            tr = mm.get("train") or {}
            t = mm.get("time_eval") or {}
            h = mm.get("user_holdout") or {}

            thr = tr.get("threshold_for_fpr", float("nan"))
            lines.append(f"- **{model_name}**")
            lines.append(
                "  - train (threshold selection): "
                f"PR-AUC={tr.get('pr_auc', 0.0):.4f}, "
                f"thr={thr:.6g}, FPR={tr.get('fpr', 0.0):.4f}, recall={tr.get('recall', 0.0):.4f}"
            )
            # Compact threshold table (top candidates under target FPR)
            ttab = (tr.get("threshold_table_top3") or [])
            if ttab:
                lines.append("  - threshold candidates (train, FPR<=target):")
                lines.append("    | rank | thr | fpr | recall | precision |")
                lines.append("    |---:|---:|---:|---:|---:|")
                for i, row in enumerate(ttab[:3], start=1):
                    lines.append(
                        "    | {i} | {thr:.6g} | {fpr:.4f} | {rec:.4f} | {prec:.4f} |".format(
                            i=i,
                            thr=float(row.get("threshold", float("nan"))),
                            fpr=float(row.get("fpr", 0.0)),
                            rec=float(row.get("recall", 0.0)),
                            prec=float(row.get("precision", 0.0)),
                        )
                    )
            lines.append(
                "  - time_eval (apply train threshold): "
                f"PR-AUC={t.get('pr_auc', 0.0):.4f}, ROC-AUC={t.get('roc_auc', 0.0):.4f}, "
                f"thr={t.get('threshold_used', thr):.6g}, FPR={t.get('fpr', 0.0):.4f}, recall={t.get('recall', 0.0):.4f}"
            )
            lines.append(
                "  - user_holdout (apply train threshold): "
                f"PR-AUC={h.get('pr_auc', 0.0):.4f}, ROC-AUC={h.get('roc_auc', 0.0):.4f}, "
                f"thr={h.get('threshold_used', thr):.6g}, FPR={h.get('fpr', 0.0):.4f}, recall={h.get('recall', 0.0):.4f}"
            )

            if "top_features" in mm:
                lines.append("  - top_features:")
                for row in (mm.get("top_features") or [])[:10]:
                    if "weight" in row:
                        lines.append(f"    - {row['feature']}: {row['weight']:+.6g}")
                    elif "importance" in row:
                        lines.append(f"    - {row['feature']}: {row['importance']:.6g}")

        lines.append("")
    return "\n".join(lines) + "\n"
