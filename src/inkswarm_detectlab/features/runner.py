from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from ..config import AppConfig
from ..io.paths import (
    run_dir as run_dir_for,
    raw_table_basepath,
    dataset_split_basepath,
    manifest_path,
    summary_path,
    reports_dir,
)
from ..io.tables import read_auto, write_auto
from ..io.manifest import read_manifest, write_manifest
from ..utils.hashing import stable_hash_df, stable_hash_dict
from ..utils.canonical import canonicalize_df
from ..schemas import get_schema
from ..pipeline import _write_summary  # internal helper (used to keep summary consistent)
from .spec import FeatureSpec, FeatureManifest
from .builder import build_login_features, build_checkout_features


def _artifact_entry(
    *,
    cfg: AppConfig,
    df: pd.DataFrame,
    rel_path: Path,
    fmt: str,
    note: str | None,
    sort_keys: list[str],
) -> dict[str, Any]:
    canonical = canonicalize_df(df, sort_keys=sort_keys, schema=None)
    return {
        "path": str(rel_path),
        "format": fmt,
        "note": note,
        "rows": int(len(canonical)),
        "content_hash": stable_hash_df(canonical, sort_keys=sort_keys, column_order=list(canonical.columns)),
    }


def build_login_features_for_run(cfg: AppConfig, *, run_id: str, force: bool = False) -> Path:
    """Build login_attempt feature table for an existing run_id and update run manifest + summary."""
    rdir = run_dir_for(cfg.paths.runs_dir, run_id)
    mpath = manifest_path(rdir)
    manifest = read_manifest(mpath) if mpath.exists() else {
        "run_id": run_id,
        "schema_version": cfg.run.schema_version,
        "timezone": cfg.run.timezone,
        "seed": cfg.run.seed,
        "artifacts": {},
    }

    fcfg = cfg.features.login_attempt
    if not fcfg.enabled:
        raise ValueError("features.login_attempt.enabled is false; nothing to do")

    # Inputs
    login_df = read_auto(raw_table_basepath(rdir, "login_attempt"))
    checkout_df = read_auto(raw_table_basepath(rdir, "checkout_attempt"))

    # Build features
    df, feature_cols = build_login_features(
        login_df,
        windows=fcfg.windows,
        entities=fcfg.entities,
        strict_past_only=fcfg.strict_past_only,
        include_support=fcfg.include_support,
        include_cross_event=getattr(fcfg, 'include_cross_event', True),
        checkout_df=checkout_df,
    )

    # Select output columns (minimal keys + labels + derived + features)
    keys = ["event_id", "event_ts", "user_id"]
    if "session_id" in df.columns:
        keys.append("session_id")

    labels = []
    if fcfg.include_labels:
        for c in ["label_replicators", "label_the_mule", "label_the_chameleon", "label_benign"]:
            if c in df.columns:
                labels.append(c)

    if fcfg.include_is_fraud:
        if "is_fraud" not in df.columns:
            if all(c in df.columns for c in ["label_replicators", "label_the_mule", "label_the_chameleon"]):
                df["is_fraud"] = (
                    df["label_replicators"].astype(bool)
                    | df["label_the_mule"].astype(bool)
                    | df["label_the_chameleon"].astype(bool)
                )
            elif "is_fraud" in login_df.columns:
                df["is_fraud"] = df["is_fraud"].astype(bool)
            else:
                df["is_fraud"] = False
        derived = ["is_fraud"]
    else:
        derived = []

    out_cols = keys + labels + derived + sorted([c for c in feature_cols if c in df.columns])

    out_df = df[out_cols].copy()

    # Attach split membership for downstream filtering/pushdown.
    split_markers: list[pd.DataFrame] = []
    for split_name in ["train", "time_eval", "user_holdout"]:
        sdf = read_auto(dataset_split_basepath(rdir, "login_attempt", split_name))
        split_markers.append(
            pd.DataFrame(
                {
                    "event_id": sdf["event_id"],
                    "split": split_name,
                }
            )
        )
    split_df = pd.concat(split_markers, ignore_index=True)
    out_df = out_df.merge(split_df, on="event_id", how="left")

    # Canonical sort for determinism.
    sort_keys = cfg.dataset.build.canonical_sort_keys
    out_df = canonicalize_df(out_df, sort_keys=sort_keys, schema=None)

    # Output paths
    base_no_ext = rdir / "features" / "login_attempt" / "features"
    # fail-closed overwrite policy
    if base_no_ext.with_suffix(".parquet").exists() and not force:
        raise FileExistsError("Feature table already exists. Re-run with --force to overwrite.")

    p, fmt, note = write_auto(out_df, base_no_ext, partition_cols=["split"])

    # Write spec + run-local manifest
    spec = FeatureSpec(
        windows=fcfg.windows,
        entities=list(fcfg.entities),
        strict_past_only=fcfg.strict_past_only,
        include_support=fcfg.include_support,
        include_labels=fcfg.include_labels,
        include_is_fraud=fcfg.include_is_fraud,
        keys=["event_id", "event_ts", "user_id"] + (["session_id"] if "session_id" in out_df.columns else []),
        split_column="split",
        partition_columns=["split"],
        feature_columns=sorted([c for c in feature_cols if c in out_df.columns]),
    )

    feat_manifest = FeatureManifest(
        run_id=run_id,
        event_type="login_attempt",
        features_rows=int(len(out_df)),
        features_cols=int(len(out_df.columns)),
        artifact_path=str(p.relative_to(cfg.paths.runs_dir)),
        artifact_format=fmt,
        artifact_note=note,
        content_hash=stable_hash_df(out_df, sort_keys=sort_keys, column_order=list(out_df.columns)),
        split_column="split",
        partition_columns=["split"],
        spec=spec,
    )

    spec_path = rdir / "features" / "login_attempt" / "feature_spec.json"
    man_path = rdir / "features" / "login_attempt" / "feature_manifest.json"
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    spec_path.write_text(spec.model_dump_json(indent=2) + "\n", encoding="utf-8")
    man_path.write_text(feat_manifest.model_dump_json(indent=2) + "\n", encoding="utf-8")

    # Update run manifest artifacts
    artifacts = manifest.get("artifacts", {}) or {}
    artifacts["features/login_attempt/features"] = _artifact_entry(
        cfg=cfg,
        df=out_df,
        rel_path=p.relative_to(cfg.paths.runs_dir),
        fmt=fmt,
        note=note,
        sort_keys=list(sort_keys),
    )
    artifacts["features/login_attempt/spec"] = {
        "path": str(spec_path.relative_to(cfg.paths.runs_dir)),
        "format": "json",
        "rows": None,
        "note": None,
        "content_hash": stable_hash_dict(spec.model_dump()),
    }
    artifacts["features/login_attempt/manifest"] = {
        "path": str(man_path.relative_to(cfg.paths.runs_dir)),
        "format": "json",
        "rows": None,
        "note": None,
        "content_hash": stable_hash_dict(feat_manifest.model_dump()),
    }
    manifest["artifacts"] = artifacts

    write_manifest(mpath, manifest)

    # Refresh run summary to include new outputs list
    # boundary + holdout users derived from dataset split files
    boundary_ts = None
    holdout_users: set[str] = set()
    try:
        boundary_ts = pd.Timestamp(manifest.get("dataset", {}).get("login_attempt", {}).get("boundary_ts_ba"))
    except Exception:
        boundary_ts = pd.Timestamp.utcnow().tz_localize("UTC")

    try:
        user_holdout = read_auto(dataset_split_basepath(rdir, "login_attempt", "user_holdout"))
        if "user_id" in user_holdout.columns:
            holdout_users = set(user_holdout["user_id"].astype(str).unique().tolist())
    except Exception:
        holdout_users = set()

    _write_summary(rdir, manifest, login_df, checkout_df, boundary_ts, holdout_users)

    return rdir




def build_checkout_features_for_run(cfg: AppConfig, *, run_id: str, force: bool = False) -> Path:
    """Build checkout_attempt feature table for an existing run_id and update run manifest + summary."""
    rdir = run_dir_for(cfg.paths.runs_dir, run_id)
    mpath = manifest_path(rdir)
    manifest = read_manifest(mpath) if mpath.exists() else {
        "run_id": run_id,
        "schema_version": cfg.run.schema_version,
        "timezone": cfg.run.timezone,
        "seed": cfg.run.seed,
        "artifacts": {},
    }

    fcfg = cfg.features.checkout_attempt
    if not fcfg.enabled:
        raise ValueError("features.checkout_attempt.enabled is false; nothing to do")

    # Inputs
    login_df = read_auto(raw_table_basepath(rdir, "login_attempt"))
    checkout_df = read_auto(raw_table_basepath(rdir, "checkout_attempt"))

    # Build features
    df, feature_cols = build_checkout_features(
        checkout_df,
        windows=fcfg.windows,
        entities=fcfg.entities,
        strict_past_only=fcfg.strict_past_only,
        include_cross_event=getattr(fcfg, "include_cross_event", True),
        login_df=login_df,
    )

    # Select output columns
    keys = ["event_id", "event_ts", "user_id"]
    if "session_id" in df.columns:
        keys.append("session_id")

    derived: list[str] = []
    if getattr(fcfg, "include_is_adverse", True):
        if "is_adverse" not in df.columns:
            df["is_adverse"] = (df["checkout_result"] != "success")
        derived.append("is_adverse")

    out_cols = keys + derived + sorted([c for c in feature_cols if c in df.columns])
    out_df = df[out_cols].copy()

    sort_keys = cfg.dataset.build.canonical_sort_keys
    out_df = canonicalize_df(out_df, sort_keys=sort_keys, schema=None)

    base_no_ext = rdir / "features" / "checkout_attempt" / "features"
    if base_no_ext.with_suffix(".parquet").exists() and not force:
        raise FileExistsError("Feature table already exists. Re-run with --force to overwrite.")

    p, fmt, note = write_auto(out_df, base_no_ext)

    spec = FeatureSpec(
        windows=fcfg.windows,
        entities=list(fcfg.entities),
        strict_past_only=fcfg.strict_past_only,
        include_support=False,
        include_labels=False,
        include_is_fraud=False,
        keys=["event_id", "event_ts", "user_id"] + (["session_id"] if "session_id" in out_df.columns else []),
        feature_columns=sorted([c for c in feature_cols if c in out_df.columns]),
    )

    feat_manifest = FeatureManifest(
        run_id=run_id,
        event_type="checkout_attempt",
        features_rows=int(len(out_df)),
        features_cols=int(len(out_df.columns)),
        artifact_path=str(p.relative_to(cfg.paths.runs_dir)),
        artifact_format=fmt,
        artifact_note=note,
        content_hash=stable_hash_df(out_df, sort_keys=sort_keys, column_order=list(out_df.columns)),
        spec=spec,
    )

    spec_path = rdir / "features" / "checkout_attempt" / "feature_spec.json"
    man_path = rdir / "features" / "checkout_attempt" / "feature_manifest.json"
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    spec_path.write_text(spec.model_dump_json(indent=2) + "\n", encoding="utf-8")
    man_path.write_text(feat_manifest.model_dump_json(indent=2) + "\n", encoding="utf-8")

    artifacts = manifest.get("artifacts", {}) or {}
    artifacts["features/checkout_attempt/features"] = _artifact_entry(
        cfg=cfg,
        df=out_df,
        rel_path=p.relative_to(cfg.paths.runs_dir),
        fmt=fmt,
        note=note,
        sort_keys=list(sort_keys),
    )
    artifacts["features/checkout_attempt/spec"] = {
        "path": str(spec_path.relative_to(cfg.paths.runs_dir)),
        "format": "json",
        "rows": None,
        "note": None,
        "content_hash": stable_hash_dict(spec.model_dump()),
    }
    artifacts["features/checkout_attempt/manifest"] = {
        "path": str(man_path.relative_to(cfg.paths.runs_dir)),
        "format": "json",
        "rows": None,
        "note": None,
        "content_hash": stable_hash_dict(feat_manifest.model_dump()),
    }
    manifest["artifacts"] = artifacts

    write_manifest(mpath, manifest)

    # Refresh run summary to include new outputs list (reuse existing helper)
    boundary_ts = None
    holdout_users: set[str] = set()
    try:
        boundary_ts = pd.Timestamp(manifest.get("dataset", {}).get("login_attempt", {}).get("boundary_ts_ba"))
    except Exception:
        boundary_ts = pd.Timestamp.utcnow().tz_localize("UTC")

    try:
        user_holdout = read_auto(dataset_split_basepath(rdir, "login_attempt", "user_holdout"))
        if "user_id" in user_holdout.columns:
            holdout_users = set(user_holdout["user_id"].astype(str).unique().tolist())
    except Exception:
        holdout_users = set()

    _write_summary(rdir, manifest, login_df, checkout_df, boundary_ts, holdout_users)

    return rdir
