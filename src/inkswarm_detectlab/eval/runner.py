from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import json
import datetime

import numpy as np
import pandas as pd

from ..config import AppConfig
from ..io.paths import run_dir as run_dir_for, manifest_path
from ..io.manifest import read_manifest, write_manifest
from ..io.tables import read_auto
from ..utils.hashing import stable_hash_dict
from ..models.metrics import choose_threshold_for_fpr
from ..models.runner import LABEL_COLS, _select_X_y  # reuse exact feature selection logic

import joblib


PRIMARY_SPLIT = "user_holdout"  # stakeholder-first: generalization to new users


@dataclass(frozen=True)
class EvalOutputs:
    status: str  # ok | partial | failed
    slices_json: Path | None
    slices_md: Path | None
    stability_json: Path | None
    stability_md: Path | None
    notes: list[str]


def _safe_read_auto(path: Path) -> tuple[pd.DataFrame | None, str | None]:
    try:
        return read_auto(path), None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def _safe_load_model(path: Path) -> tuple[Any | None, str | None]:
    try:
        return joblib.load(path), None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"



def _discover_baseline_artifacts(
    model_dir: Path, expected_models: tuple[str, ...] = ("logreg", "rf")
) -> tuple[dict[str, dict[str, Path]], list[str]]:
    """Discover baseline artifacts under `model_dir`.

    Supported layouts (under `<model_dir>/baselines/`):
      - v2 (preferred): `<model>/<label>.joblib`
      - v1 (legacy):   `<label>__<model>.joblib`

    Returns:
      (artifacts, notes)

      artifacts:
        dict[model_name][label_name] -> joblib path

      notes:
        list of warnings and missing-artifact messages.
    """
    baselines_dir = model_dir / "baselines"
    notes: list[str] = []

    # Always return keys for expected_models to make downstream logic simpler.
    artifacts: dict[str, dict[str, Path]] = {m: {} for m in expected_models}

    if not baselines_dir.exists():
        notes.append(f"Missing baselines directory: {baselines_dir}")
        return artifacts, notes

    for p in sorted(baselines_dir.glob("**/*.joblib")):
        stem = p.stem

        # Layout v2: <model>/<label>.joblib (model is parent directory name)
        if p.parent.name in expected_models and p.parent != baselines_dir:
            model_name = p.parent.name
            label_name = stem
            if label_name in artifacts[model_name]:
                notes.append(
                    f"Duplicate artifact for model='{model_name}', label='{label_name}'. "
                    f"Keeping {artifacts[model_name][label_name]}, ignoring {p}"
                )
            else:
                artifacts[model_name][label_name] = p
            continue

        # Layout v1 legacy: <label>__<model>.joblib (usually directly under baselines_dir)
        if "__" in stem:
            label_name, model_name = stem.rsplit("__", 1)
            if model_name in expected_models and label_name:
                if label_name in artifacts[model_name]:
                    notes.append(
                        f"Duplicate artifact for model='{model_name}', label='{label_name}'. "
                        f"Keeping {artifacts[model_name][label_name]}, ignoring {p}"
                    )
                else:
                    artifacts[model_name][label_name] = p
                continue

        notes.append(f"Unrecognized baseline artifact filename: {p}")

    for m in expected_models:
        if not artifacts[m]:
            notes.append(f"Missing model artifacts for model='{m}' under {baselines_dir}")

    return artifacts, notes


def _predict_scores(model: Any, X: pd.DataFrame) -> np.ndarray:
    # Works for sklearn pipelines + estimators
    if hasattr(model, "predict_proba"):
        p = model.predict_proba(X)
        if isinstance(p, list):
            p = p[0]
        return np.asarray(p)[:, 1]
    if hasattr(model, "decision_function"):
        s = np.asarray(model.decision_function(X))
        # map to (0,1) with sigmoid-ish; not calibrated but monotonic
        return 1.0 / (1.0 + np.exp(-s))
    raise ValueError("Model has neither predict_proba nor decision_function")


def _slice_defs(df: pd.DataFrame) -> list[tuple[str, pd.Series]]:
    """Recommended slice set: synthetic archetypes + a few obvious covariates."""
    out: list[tuple[str, pd.Series]] = []

    # Archetypes (mutually exclusive in SKYNET): label flags
    for lab, pretty in [
        ("label_replicators", "Playbook: Replicators"),
        ("label_the_mule", "Playbook: The Mule"),
        ("label_the_chameleon", "Playbook: The Chameleon"),
    ]:
        if lab in df.columns:
            out.append((pretty, df[lab].astype(bool)))

    # Benign bucket (explicit if present, else derived)
    if "label_benign" in df.columns:
        out.append(("Playbook: Benign", df["label_benign"].astype(bool)))
    elif all(c in df.columns for c in ["label_replicators", "label_the_mule", "label_the_chameleon"]):
        benign = (df["label_replicators"].astype(int) + df["label_the_mule"].astype(int) + df["label_the_chameleon"].astype(int)) == 0
        out.append(("Playbook: Benign", benign))

    # Covariates
    for col, pretty in [
        ("mfa_used", "MFA used"),
        ("username_present", "Username present"),
        ("support_contacted", "Support contacted"),
    ]:
        if col in df.columns:
            out.append((f"{pretty}: yes", df[col].astype(bool)))
            out.append((f"{pretty}: no", ~df[col].astype(bool)))

    # Country (top-3)
    if "country" in df.columns:
        vc = df["country"].fillna("unknown").astype(str).value_counts()
        top = list(vc.index[:3])
        for c in top:
            out.append((f"Country: {c}", df["country"].fillna("unknown").astype(str) == c))
        out.append(("Country: other", ~df["country"].fillna("unknown").astype(str).isin(top)))

    # Outcome buckets
    if "login_result" in df.columns:
        for v in ["success", "failure", "review"]:
            out.append((f"Login result: {v}", df["login_result"].astype(str) == v))

    # Always include "All"
    out.insert(0, ("All", pd.Series([True] * len(df), index=df.index)))

    # Drop zero-sized slices at render time
    return out


def _slice_metrics(y: np.ndarray, s: np.ndarray, thr: float) -> dict[str, Any]:
    n = int(len(y))
    pos = int(np.sum(y))
    pos_rate = float(pos / n) if n else 0.0
    # PR-AUC
    try:
        from sklearn.metrics import average_precision_score

        pr_auc = float(average_precision_score(y, s)) if len(np.unique(y)) > 1 else 0.0
    except Exception:
        pr_auc = 0.0

    # At threshold
    pred = s >= float(thr)
    fp = int(np.sum((pred == 1) & (y == 0)))
    tp = int(np.sum((pred == 1) & (y == 1)))
    tn = int(np.sum((pred == 0) & (y == 0)))
    fn = int(np.sum((pred == 0) & (y == 1)))

    fpr = float(fp / (fp + tn)) if (fp + tn) else 0.0
    recall = float(tp / (tp + fn)) if (tp + fn) else 0.0
    precision = float(tp / (tp + fp)) if (tp + fp) else 0.0
    return {
        "rows": n,
        "positives": pos,
        "pos_rate": pos_rate,
        "pr_auc": pr_auc,
        "at_train_threshold": {"threshold": float(thr), "fpr": fpr, "recall": recall, "precision": precision},
    }


def _render_md_slices(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    meta = payload.get("meta", {})
    lines.append(f"# Evaluation — Slices (login_attempt)")
    lines.append("")
    lines.append(f"Run: `{meta.get('run_id')}`  \nGenerated: `{meta.get('generated_at_utc')}`")
    lines.append("")
    lines.append("This report breaks performance down by **synthetic archetypes** (playbooks) and a few **obvious covariates** (MFA, country, etc.).")
    lines.append("Metrics are computed using the **train-chosen threshold** (target FPR = 1%) and then applied to each split.")
    lines.append("")
    if payload.get("status") != "ok":
        lines.append(f"> **Status:** {payload.get('status')} — some inputs were missing. See Notes at the bottom.")
        lines.append("")

    for model_name, mobj in payload.get("models", {}).items():
        lines.append(f"## Model: `{model_name}`")
        for label, lobj in mobj.get("labels", {}).items():
            lines.append(f"### Label: `{label}`")
            thr = lobj.get("train_threshold")
            if thr is None:
                lines.append("> Missing train threshold (baselines may have failed).")
                lines.append("")
                continue
            for split_name, sobj in lobj.get("splits", {}).items():
                lines.append(f"#### Split: `{split_name}`")
                lines.append("")
                lines.append("| Slice | Rows | Pos% | PR-AUC | Recall@thr | FPR@thr |")
                lines.append("|---|---:|---:|---:|---:|---:|")
                rows = []
                for sname, sm in sobj.get("slices", {}).items():
                    rows.append((sname, sm))
                # sort by size desc
                rows.sort(key=lambda x: int(x[1].get("rows", 0)), reverse=True)
                for sname, sm in rows:
                    r = int(sm.get("rows", 0))
                    if r <= 0:
                        continue
                    pos_rate = float(sm.get("pos_rate", 0.0)) * 100.0
                    pr = float(sm.get("pr_auc", 0.0))
                    at = sm.get("at_train_threshold", {}) or {}
                    recall = float(at.get("recall", 0.0))
                    fpr = float(at.get("fpr", 0.0))
                    lines.append(f"| {sname} | {r} | {pos_rate:.2f}% | {pr:.4f} | {recall:.4f} | {fpr:.4f} |")
                lines.append("")
    notes = payload.get("notes", []) or []
    if notes:
        lines.append("## Notes")
        for n in notes:
            lines.append(f"- {n}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_md_stability(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    meta = payload.get("meta", {})
    lines.append("# Evaluation — Stability (login_attempt)")
    lines.append("")
    lines.append(f"Run: `{meta.get('run_id')}`  \nGenerated: `{meta.get('generated_at_utc')}`")
    lines.append("")
    lines.append(f"Primary split for stakeholder truth is **{PRIMARY_SPLIT}** (generalization to new users).")
    lines.append("Time Eval is shown as a drift/stability check.")
    lines.append("")
    if payload.get("status") != "ok":
        lines.append(f"> **Status:** {payload.get('status')} — some inputs were missing. See Notes at the bottom.")
        lines.append("")
    lines.append("## Headline stability table (train threshold)")
    lines.append("")
    lines.append("| Label | Model | Train thr | Time PR-AUC | Time Recall@thr | Holdout PR-AUC | Holdout Recall@thr | ΔRecall (Hold - Time) |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for model_name, mobj in payload.get("models", {}).items():
        for label, lobj in mobj.get("labels", {}).items():
            thr = lobj.get("train_threshold")
            time = lobj.get("time_eval", {}) or {}
            hold = lobj.get("user_holdout", {}) or {}
            drec = float(hold.get("recall_at_train_thr", 0.0)) - float(time.get("recall_at_train_thr", 0.0))
            lines.append(
                f"| `{label}` | `{model_name}` | {float(thr or 0.0):.4f} | {float(time.get('pr_auc', 0.0)):.4f} | {float(time.get('recall_at_train_thr', 0.0)):.4f} | {float(hold.get('pr_auc', 0.0)):.4f} | {float(hold.get('recall_at_train_thr', 0.0)):.4f} | {drec:.4f} |"
            )
    lines.append("")
    lines.append("## Threshold stability (what threshold would be needed to hit 1% FPR?)")
    lines.append("")
    lines.append("| Label | Model | Train thr | Time thr@1%FPR | Holdout thr@1%FPR | Δthr (Hold - Train) |")
    lines.append("|---|---|---:|---:|---:|---:|")
    for model_name, mobj in payload.get("models", {}).items():
        for label, lobj in mobj.get("labels", {}).items():
            thr = float(lobj.get("train_threshold") or 0.0)
            tthr = float((lobj.get("time_eval", {}) or {}).get("threshold_for_fpr", 0.0))
            hthr = float((lobj.get("user_holdout", {}) or {}).get("threshold_for_fpr", 0.0))
            lines.append(f"| `{label}` | `{model_name}` | {thr:.4f} | {tthr:.4f} | {hthr:.4f} | {(hthr-thr):.4f} |")
    lines.append("")
    notes = payload.get("notes", []) or []
    if notes:
        lines.append("## Notes")
        for n in notes:
            lines.append(f"- {n}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def run_login_eval_for_run(cfg: AppConfig, *, run_id: str, force: bool = False) -> EvalOutputs:
    """Compute slice + stability diagnostics for login_attempt.

    Best-effort, but explicit about gaps:
    - If required parquet artifacts or models are missing, we still write reports with Notes and status=partial.
    """
    rdir = run_dir_for(cfg.paths.runs_dir, run_id)
    mpath = manifest_path(rdir)
    manifest = read_manifest(mpath) if mpath.exists() else {"run_id": run_id, "artifacts": {}}

    out_reports = rdir / "reports"
    out_reports.mkdir(parents=True, exist_ok=True)

    slices_json = out_reports / "eval_slices_login_attempt.json"
    slices_md = out_reports / "eval_slices_login_attempt.md"
    stability_json = out_reports / "eval_stability_login_attempt.json"
    stability_md = out_reports / "eval_stability_login_attempt.md"


    # Always initialize meta early so partial / missing-artifact paths never crash.
    meta: dict[str, Any] = {"run_id": run_id, "event": "login_attempt"}

    if not force and slices_json.exists() and stability_json.exists():

        return EvalOutputs("ok", slices_json, slices_md if slices_md.exists() else None, stability_json, stability_md if stability_md.exists() else None, [])

    notes: list[str] = []
    status = "ok"

    # Load splits (dataset) to get slice columns + labels
    split_paths = {
        "train": rdir / "dataset" / "login_attempt" / "train.parquet",
        "time_eval": rdir / "dataset" / "login_attempt" / "time_eval.parquet",
        "user_holdout": rdir / "dataset" / "login_attempt" / "user_holdout.parquet",
    }
    splits: dict[str, pd.DataFrame] = {}
    for k, p in split_paths.items():
        df, err = _safe_read_auto(p)
        if df is None:
            status = "partial"
            notes.append(f"Missing dataset split: {k} at {p} ({err})")
        else:
            splits[k] = df

    # Load feature table for scoring (must contain numeric features)
    feat_path = rdir / "features" / "login_attempt" / "features.parquet"
    feat_df, err = _safe_read_auto(feat_path)
    if feat_df is None:
        status = "partial"
        notes.append(f"Missing features table for scoring: {feat_path} ({err})")

    # Load trained models (logreg + rf)
    model_dir = rdir / "models" / "login_attempt" / "baselines"
    expected_models = list(cfg.baselines.login_attempt.models)

    model_artifacts, disc_notes = _discover_baseline_artifacts(model_dir, expected_models)
    notes.extend(disc_notes)

    # Load models into a nested mapping: model_name -> label -> model_object
    models: dict[str, dict[str, Any]] = {}
    for model_name, label_map in model_artifacts.items():
        loaded_labels: dict[str, Any] = {}
        for label, p in label_map.items():
            mobj, err = _safe_load_model(p)
            if mobj is None:
                status = "partial"
                notes.append(f"Failed to load model artifact '{label}__{model_name}' at {p}: {err}")
                continue
            loaded_labels[label] = mobj

        if loaded_labels:
            models[model_name] = loaded_labels

    if not models:
        status = "partial"
        notes.append(f"No loadable baseline model artifacts found under: {model_dir}")
    else:
        missing_models = [m for m in expected_models if m not in models]
        if missing_models:
            status = "partial"
            notes.append(f"Missing expected baseline model(s) under {model_dir}: {missing_models}")

    slices_payload: dict[str, Any] = {"status": status, "meta": meta, "models": {}, "notes": notes[:]}

    stability_payload: dict[str, Any] = {"status": status, "meta": meta, "models": {}, "notes": notes[:]}

    if feat_df is not None and splits and models:
        # Prepare lookup for slice columns: use dataset split df (has covariates)
        # Scoring will be done using features df filtered by event_id in each split.
        # This avoids any accidental look-ahead: features are already rolled past-only.
        feat_df = feat_df.copy()
        if "event_id" not in feat_df.columns:
            status = "partial"
            notes.append("features table missing event_id; cannot join to splits")
        else:
            feat_df.set_index("event_id", inplace=True, drop=False)

        # Compute per split scored matrices
        for model_name, label_models in models.items():
            slices_payload["models"].setdefault(model_name, {"labels": {}})
            stability_payload["models"].setdefault(model_name, {"labels": {}})
            for label in LABEL_COLS:
                # require label column in dataset splits (train) for y
                if "train" not in splits or label not in splits["train"].columns:
                    status = "partial"
                    notes.append(f"Label column missing in dataset for {label}; skipping")
                    continue

                model = label_models.get(label)
                if model is None:
                    status = "partial"
                    notes.append(f"Missing baseline artifact for model='{model_name}', label='{label}' in {model_dir}")
                    continue

                # Get train threshold for target fpr
                # Build X/y from FEATURES joined with train split event_ids
                def _prep(split_name: str) -> tuple[np.ndarray, np.ndarray, pd.DataFrame] | None:
                    sdf = splits.get(split_name)
                    if sdf is None or sdf.empty:
                        return None
                    ids = sdf["event_id"].astype(str).tolist() if "event_id" in sdf.columns else []
                    fsub = feat_df.loc[feat_df.index.intersection(ids)].copy() if feat_df is not None else None
                    if fsub is None or fsub.empty:
                        return None
                    # Align y with fsub rows via merge on event_id
                    y = sdf.set_index("event_id")[label].reindex(fsub["event_id"]).fillna(0).astype(int).to_numpy()
                    X, _ys = _select_X_y(fsub)  # exact numeric selection logic
                    s = _predict_scores(model, X)
                    return y, s, sdf.set_index("event_id").reindex(fsub["event_id"]).reset_index(drop=False)

                train_p = _prep("train")
                time_p = _prep("time_eval")
                hold_p = _prep("user_holdout")

                if train_p is None:
                    status = "partial"
                    notes.append(f"Could not score train split for {model_name}/{label} (missing features?)")
                    continue
                y_tr, s_tr, df_tr = train_p
                thr_tr = choose_threshold_for_fpr(y_tr, s_tr, target_fpr=float(cfg.baselines.login_attempt.target_fpr))
                train_thr = float(thr_tr.threshold)

                # Stability core metrics
                def _core(y: np.ndarray, s: np.ndarray) -> dict[str, Any]:
                    try:
                        from sklearn.metrics import average_precision_score

                        pr_auc = float(average_precision_score(y, s)) if len(np.unique(y)) > 1 else 0.0
                    except Exception:
                        pr_auc = 0.0
                    at = _slice_metrics(y, s, train_thr)["at_train_threshold"]
                    # threshold needed at same target fpr on this split
                    thr = choose_threshold_for_fpr(y, s, target_fpr=float(cfg.baselines.login_attempt.target_fpr))
                    return {
                        "pr_auc": pr_auc,
                        "recall_at_train_thr": float(at["recall"]),
                        "fpr_at_train_thr": float(at["fpr"]),
                        "precision_at_train_thr": float(at["precision"]),
                        "threshold_for_fpr": float(thr.threshold),
                    }

                l_stab = {
                    "train_threshold": train_thr,
                    "time_eval": _core(*time_p[:2]) if time_p is not None else {},
                    "user_holdout": _core(*hold_p[:2]) if hold_p is not None else {},
                }
                stability_payload["models"][model_name]["labels"][label] = l_stab

                # Slices per split
                l_slices: dict[str, Any] = {"train_threshold": train_thr, "splits": {}}
                for split_name, prep in [("train", train_p), ("time_eval", time_p), ("user_holdout", hold_p)]:
                    if prep is None:
                        continue
                    y, s, sdf_aligned = prep
                    # compute slice masks on sdf_aligned (dataset rows aligned to scored events)
                    slice_rows = {}
                    for sname, mask in _slice_defs(sdf_aligned):
                        mask = mask.fillna(False)
                        if int(mask.sum()) == 0:
                            continue
                        sm = _slice_metrics(y[mask.to_numpy()], s[mask.to_numpy()], train_thr)
                        slice_rows[sname] = sm
                    l_slices["splits"][split_name] = {"slices": slice_rows}
                slices_payload["models"][model_name]["labels"][label] = l_slices

    # Write outputs
    slices_json.write_text(json.dumps(slices_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    stability_json.write_text(json.dumps(stability_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    slices_md.write_text(_render_md_slices(slices_payload), encoding="utf-8")
    stability_md.write_text(_render_md_stability(stability_payload), encoding="utf-8")

    # Update manifest
    artifacts = manifest.get("artifacts", {}) or {}
    artifacts["reports/eval_slices_login_attempt"] = {"path": str(slices_md), "content_hash": stable_hash_dict({"md": slices_md.read_text(encoding="utf-8")})}
    artifacts["reports/eval_stability_login_attempt"] = {"path": str(stability_md), "content_hash": stable_hash_dict({"md": stability_md.read_text(encoding="utf-8")})}
    artifacts["reports/eval_slices_login_attempt_json"] = {"path": str(slices_json), "content_hash": stable_hash_dict(slices_payload)}
    artifacts["reports/eval_stability_login_attempt_json"] = {"path": str(stability_json), "content_hash": stable_hash_dict(stability_payload)}
    manifest["artifacts"] = artifacts
    write_manifest(mpath, manifest)

    return EvalOutputs(status, slices_json, slices_md, stability_json, stability_md, notes)
