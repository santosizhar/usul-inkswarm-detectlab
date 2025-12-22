from __future__ import annotations

"""Notebook-oriented step runners.

Design goals (D-0022):
- keep core pipeline modules intact
- provide thin, explicit "step" wrappers for notebooks
- prefer reusing existing artifacts + shared cache when possible
- surface step visibility: inputs, outputs, quick summaries, and "what next"

These helpers intentionally avoid any notebook-only dependencies.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import json

from ..config import load_config
from ..pipeline import run_all, _config_fingerprint
from ..utils.run_id import make_run_id
from ..io.paths import (
    run_dir as run_dir_for,
    raw_table_basepath,
    dataset_split_basepath,
    manifest_path,
    baselines_dir as baselines_dir_for,
)
from ..io.manifest import read_manifest, write_manifest

from ..cache.feature_cache import try_restore_feature_artifacts, save_feature_artifacts_to_cache
from ..features import build_login_features_for_run
from ..models import run_login_baselines_for_run
from ..eval import run_login_eval_for_run
from ..ui.summarize import write_ui_summary
from ..ui.bundle import export_ui_bundle
from ..share.evidence import export_evidence_bundle
from ..mvp.handover import write_mvp_handover
from ..reports.exec_summary import write_exec_summary

from .steps import StepRecorder


@dataclass(frozen=True)
class StepOutcome:
    name: str
    status: str  # ok|skipped|fail|partial
    outputs: Dict[str, str] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)


def _exists_parquet(base_no_ext: Path) -> bool:
    return base_no_ext.with_suffix(".parquet").exists()


def _ensure_manifest(cfg: Any, run_dir: Path) -> Dict[str, Any]:
    """Ensure run manifest exists; return loaded/created manifest dict."""
    mpath = manifest_path(run_dir)
    if mpath.exists():
        return read_manifest(mpath)
    manifest: Dict[str, Any] = {
        "run_id": run_dir.name,
        "schema_version": getattr(cfg.run, "schema_version", "unknown"),
        "timezone": getattr(cfg.run, "timezone", "unknown"),
        "seed": getattr(cfg.run, "seed", None),
        "artifacts": {},
    }
    write_manifest(mpath, manifest)
    return manifest


def resolve_run_id(
    cfg_path: Path,
    run_id: Optional[str] = None,
) -> Tuple[Any, str]:
    """Load config and return (cfg, run_id). If run_id is None, generate one."""
    cfg = load_config(cfg_path)
    if run_id is not None:
        return cfg, run_id
    _, cfg_hash8 = _config_fingerprint(cfg)
    run_id = make_run_id(
        runs_dir=cfg.paths.runs_dir,
        prefix=cfg.run.run_id_prefix,
        config_hash8=cfg_hash8,
        strategy=cfg.run.run_id_strategy,
    )
    return cfg, run_id


def wire_check(cfg_path: Path, run_id: Optional[str] = None) -> Dict[str, Any]:
    """Lightweight wiring check (no heavy compute).

    - resolves cfg + run_id
    - creates run dir if missing
    - ensures manifest exists
    - returns the key paths the step notebook will use
    """
    cfg, rid = resolve_run_id(cfg_path, run_id=run_id)
    rdir = run_dir_for(Path(cfg.paths.runs_dir), rid)
    rdir.mkdir(parents=True, exist_ok=True)
    _ensure_manifest(cfg, rdir)

    paths = {
        "run_dir": str(rdir),
        "raw_login_attempt": str(raw_table_basepath(rdir, "login_attempt").with_suffix(".parquet")),
        "raw_checkout_attempt": str(raw_table_basepath(rdir, "checkout_attempt").with_suffix(".parquet")),
        "dataset_train": str(dataset_split_basepath(rdir, "login_attempt", "train").with_suffix(".parquet")),
        "dataset_time_eval": str(dataset_split_basepath(rdir, "login_attempt", "time_eval").with_suffix(".parquet")),
        "dataset_user_holdout": str(dataset_split_basepath(rdir, "login_attempt", "user_holdout").with_suffix(".parquet")),
        "features_login": str((rdir / "features" / "login_attempt" / "features").with_suffix(".parquet")),
        "baselines_dir": str(baselines_dir_for(rdir, "login_attempt")),
        "eval_reports_dir": str(rdir / "reports"),
        "share_dir": str(rdir / "share"),
        "manifest": str(manifest_path(rdir)),
    }
    return {"run_id": rid, "paths": paths}


def step_dataset(
    cfg: Any,
    *,
    run_id: str,
    rec: Optional[StepRecorder] = None,
    reuse_if_exists: bool = True,
    force: bool = False,
) -> StepOutcome:
    """Step 1: raw + dataset for login_attempt (and required cross-event raw)."""
    rdir = run_dir_for(Path(cfg.paths.runs_dir), run_id)
    rdir.mkdir(parents=True, exist_ok=True)
    _ensure_manifest(cfg, rdir)

    raw_login = raw_table_basepath(rdir, "login_attempt")
    raw_checkout = raw_table_basepath(rdir, "checkout_attempt")
    ds_train = dataset_split_basepath(rdir, "login_attempt", "train")
    ds_time = dataset_split_basepath(rdir, "login_attempt", "time_eval")
    ds_hold = dataset_split_basepath(rdir, "login_attempt", "user_holdout")

    have_all = all(_exists_parquet(p) for p in (raw_login, raw_checkout, ds_train, ds_time, ds_hold))

    if reuse_if_exists and have_all and not force:
        return StepOutcome(
            name="dataset",
            status="skipped",
            outputs={
                "run_dir": str(rdir),
                "raw_login_attempt": str(raw_login.with_suffix(".parquet")),
                "raw_checkout_attempt": str(raw_checkout.with_suffix(".parquet")),
                "dataset_train": str(ds_train.with_suffix(".parquet")),
                "dataset_time_eval": str(ds_time.with_suffix(".parquet")),
                "dataset_user_holdout": str(ds_hold.with_suffix(".parquet")),
            },
            notes=["All raw+dataset artifacts already exist; skipped (reuse_if_exists=True, force=False)."],
        )

    if rec:
        with rec.step("raw+dataset", details={"run_id": run_id, "force": force}):
            run_all(cfg, run_id=run_id)
    else:
        run_all(cfg, run_id=run_id)

    return StepOutcome(
        name="dataset",
        status="ok",
        outputs={
            "run_dir": str(rdir),
            "raw_login_attempt": str(raw_login.with_suffix(".parquet")),
            "raw_checkout_attempt": str(raw_checkout.with_suffix(".parquet")),
            "dataset_train": str(ds_train.with_suffix(".parquet")),
            "dataset_time_eval": str(ds_time.with_suffix(".parquet")),
            "dataset_user_holdout": str(ds_hold.with_suffix(".parquet")),
        },
    )


def step_features(
    cfg: Any,
    *,
    run_id: str,
    rec: Optional[StepRecorder] = None,
    reuse_if_exists: bool = True,
    force: bool = False,
    use_cache: bool = True,
    write_cache: bool = True,
) -> StepOutcome:
    """Step 2: build login features (or reuse cache/artifacts)."""
    rdir = run_dir_for(Path(cfg.paths.runs_dir), run_id)
    rdir.mkdir(parents=True, exist_ok=True)
    _ensure_manifest(cfg, rdir)

    feat_base = rdir / "features" / "login_attempt" / "features"
    feat_path = feat_base.with_suffix(".parquet")

    if reuse_if_exists and feat_path.exists() and not force:
        return StepOutcome(
            name="features",
            status="skipped",
            outputs={"features_login": str(feat_path)},
            notes=["Features table already exists; skipped (reuse_if_exists=True, force=False)."],
        )

    cache_hit = False
    cache_note = None
    if use_cache and not force:
        cache_info = try_restore_feature_artifacts(cfg, rdir, force_rebuild=False)
        cache_hit = bool(getattr(cache_info, "is_hit", False))
        if cache_hit and feat_path.exists():
            cache_note = f"Shared feature cache HIT: key={getattr(cache_info, 'cache_key', 'unknown')}"
            return StepOutcome(
                name="features",
                status="ok",
                outputs={"features_login": str(feat_path)},
                notes=[cache_note],
                summary={"cache_hit": True, "cache_key": getattr(cache_info, "cache_key", None)},
            )

    if rec:
        with rec.step("build_features", details={"run_id": run_id, "force": force, "use_cache": use_cache}):
            build_login_features_for_run(cfg, run_id=run_id, force=force)
    else:
        build_login_features_for_run(cfg, run_id=run_id, force=force)

    if write_cache and use_cache:
        # Best-effort: if cache write fails, do not fail the notebook step.
        try:
            save_feature_artifacts_to_cache(cfg, rdir)
        except Exception as e:
            cache_note = f"Cache write skipped/failed: {e}"

    notes = []
    if cache_note:
        notes.append(cache_note)

    return StepOutcome(
        name="features",
        status="ok",
        outputs={"features_login": str(feat_path)},
        notes=notes,
        summary={"cache_hit": cache_hit},
    )


def _baselines_present(rdir: Path) -> Tuple[bool, Optional[Path]]:
    out_dir = rdir / "models" / "login_attempt" / "baselines"
    metrics = out_dir / "metrics.json"
    any_model = any(out_dir.glob("**/*.joblib"))
    return bool(metrics.exists() and any_model), metrics if metrics.exists() else None


def step_baselines(
    cfg: Any,
    *,
    run_id: str,
    rec: Optional[StepRecorder] = None,
    reuse_if_exists: bool = True,
    force: bool = False,
    cfg_path: Optional[Path] = None,
) -> StepOutcome:
    """Step 3: train baselines (or reuse existing)."""
    rdir = run_dir_for(Path(cfg.paths.runs_dir), run_id)
    rdir.mkdir(parents=True, exist_ok=True)
    _ensure_manifest(cfg, rdir)

    present, metrics_path = _baselines_present(rdir)
    if reuse_if_exists and present and not force:
        summary: Dict[str, Any] = {}
        if metrics_path:
            try:
                summary = json.loads(metrics_path.read_text(encoding="utf-8"))
            except Exception:
                summary = {}
        return StepOutcome(
            name="baselines",
            status="skipped",
            outputs={
                "baselines_dir": str(rdir / "models" / "login_attempt" / "baselines"),
                "metrics_json": str(metrics_path) if metrics_path else "",
            },
            notes=["Baselines already present; skipped (reuse_if_exists=True, force=False)."],
            summary=summary.get("meta", {}) if isinstance(summary, dict) else {},
        )

    if rec:
        with rec.step("train_baselines", details={"run_id": run_id, "force": force}):
            run_login_baselines_for_run(cfg, run_id=run_id, force=force, cfg_path=cfg_path)
    else:
        run_login_baselines_for_run(cfg, run_id=run_id, force=force, cfg_path=cfg_path)

    present2, metrics_path2 = _baselines_present(rdir)
    status = "ok" if present2 else "partial"
    summary: Dict[str, Any] = {}
    if metrics_path2 and metrics_path2.exists():
        try:
            summary = json.loads(metrics_path2.read_text(encoding="utf-8"))
        except Exception:
            summary = {}
    return StepOutcome(
        name="baselines",
        status=status,
        outputs={
            "baselines_dir": str(rdir / "models" / "login_attempt" / "baselines"),
            "metrics_json": str(metrics_path2) if metrics_path2 else "",
        },
        summary=summary.get("meta", {}) if isinstance(summary, dict) else {},
    )


def _eval_present(rdir: Path) -> bool:
    out_reports = rdir / "reports"
    req = [
        out_reports / "eval_slices_login_attempt.json",
        out_reports / "eval_stability_login_attempt.json",
        out_reports / "eval_slices_login_attempt.md",
        out_reports / "eval_stability_login_attempt.md",
    ]
    return all(p.exists() for p in req)


def step_eval(
    cfg: Any,
    *,
    run_id: str,
    rec: Optional[StepRecorder] = None,
    reuse_if_exists: bool = True,
    force: bool = False,
) -> StepOutcome:
    """Step 4: eval diagnostics (slice + stability) for login_attempt."""
    rdir = run_dir_for(Path(cfg.paths.runs_dir), run_id)
    rdir.mkdir(parents=True, exist_ok=True)
    _ensure_manifest(cfg, rdir)

    if reuse_if_exists and _eval_present(rdir) and not force:
        return StepOutcome(
            name="eval",
            status="skipped",
            outputs={"reports_dir": str(rdir / "reports")},
            notes=["Eval reports already present; skipped (reuse_if_exists=True, force=False)."],
        )

    if rec:
        with rec.step("eval_login_attempt", details={"run_id": run_id, "force": force}):
            out = run_login_eval_for_run(cfg, run_id=run_id, force=force)
    else:
        out = run_login_eval_for_run(cfg, run_id=run_id, force=force)

    status = getattr(out, "status", "ok") if out is not None else "partial"
    notes = list(getattr(out, "notes", []) or []) if out is not None else ["Eval returned no outputs (unexpected)."]

    return StepOutcome(
        name="eval",
        status=str(status),
        outputs={"reports_dir": str(rdir / "reports")},
        notes=notes,
    )


def _share_present(rdir: Path) -> bool:
    # Evidence + UI bundle are the most important "share" artifacts.
    ev = rdir / "share" / "evidence"
    ui = rdir / "share" / "ui_bundle"
    handover = rdir / "share" / "handover.md"
    summary = rdir / "share" / "summary.md"
    return (ev.exists() and ui.exists() and handover.exists() and summary.exists())


def step_export(
    cfg: Any,
    *,
    run_id: str,
    rec: Optional[StepRecorder] = None,
    reuse_if_exists: bool = True,
    force: bool = False,
) -> StepOutcome:
    """Step 5: export share bundle (summary, exec summary, UI bundle, handover, evidence)."""
    rdir = run_dir_for(Path(cfg.paths.runs_dir), run_id)
    rdir.mkdir(parents=True, exist_ok=True)
    _ensure_manifest(cfg, rdir)

    if reuse_if_exists and _share_present(rdir) and not force:
        return StepOutcome(
            name="export",
            status="skipped",
            outputs={"share_dir": str(rdir / "share")},
            notes=["Share bundle already present; skipped (reuse_if_exists=True, force=False)."],
        )

    share_dir = rdir / "share"
    share_dir.mkdir(parents=True, exist_ok=True)

    def _do():
        # Ensure core summaries exist (best-effort)
        write_ui_summary(cfg, run_id=run_id)
        write_exec_summary(cfg, run_id=run_id)

        # Export UI bundle for this run
        export_ui_bundle(cfg, run_ids=[run_id], out_dir=share_dir / "ui_bundle", force=force)

        # Handover + evidence
        write_mvp_handover(cfg, run_id=run_id)
        export_evidence_bundle(cfg, run_id=run_id)

    if rec:
        with rec.step("export_share_bundle", details={"run_id": run_id, "force": force}):
            _do()
    else:
        _do()

    return StepOutcome(
        name="export",
        status="ok",
        outputs={"share_dir": str(share_dir)},
    )
