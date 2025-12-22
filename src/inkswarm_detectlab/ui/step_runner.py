from __future__ import annotations

"""Notebook-oriented step runners.

Design goals (D-0022):
- keep core pipeline modules intact
- provide thin, explicit "step" wrappers for notebooks
- prefer reusing existing artifacts + shared cache when possible
- surface step visibility: inputs, outputs, quick summaries, and "what next"

These helpers intentionally avoid any notebook-only dependencies.
"""

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
from .step_contract import (
    StepResult,
    StepInputs,
    ReuseDecision,
    ArtifactRef,
    record_step_result,
)





def _mk_inputs(cfg_path: Path, cfg: Any, run_id: str, params: Dict[str, Any] | None = None, toggles: Dict[str, Any] | None = None) -> StepInputs:
    cfg_hash, _ = _config_fingerprint(cfg)
    return StepInputs(
        cfg_path=str(cfg_path),
        run_id=run_id,
        config_hash=cfg_hash,
        params=params or {},
        toggles=toggles or {},
    )


def _artifact_map(outputs: Dict[str, Path]) -> Dict[str, ArtifactRef]:
    return {k: ArtifactRef(kind=k, path=str(p), exists=Path(p).exists()) for k, p in outputs.items()}


def _finalize_step(run_dir: Path, step: StepResult) -> StepResult:
    # Persist for visibility; does not overwrite core artifact records (it writes under manifest["steps"])
    record_step_result(run_dir, step)
    return step

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
    cfg_path: Optional[Path] = None,
    run_id: str,
    rec: Optional[StepRecorder] = None,
    reuse_if_exists: bool = True,
    force: bool = False,
) -> StepResult:
    """Step 1: raw + dataset for login_attempt (and required cross-event raw)."""
    rdir = run_dir_for(Path(cfg.paths.runs_dir), run_id)
    rdir.mkdir(parents=True, exist_ok=True)
    _ensure_manifest(cfg, rdir)

    cfg_path = cfg_path or Path("<cfg_path_unknown>")
    inputs = _mk_inputs(
        cfg_path,
        cfg,
        run_id,
        params={"event": "login_attempt"},
        toggles={"reuse_if_exists": reuse_if_exists, "force": force},
    )

    raw_login = raw_table_basepath(rdir, "login_attempt").with_suffix(".parquet")
    raw_checkout = raw_table_basepath(rdir, "checkout_attempt").with_suffix(".parquet")
    ds_train = dataset_split_basepath(rdir, "login_attempt", "train").with_suffix(".parquet")
    ds_time = dataset_split_basepath(rdir, "login_attempt", "time_eval").with_suffix(".parquet")
    ds_hold = dataset_split_basepath(rdir, "login_attempt", "user_holdout").with_suffix(".parquet")

    expected = {
        "run_dir": rdir,
        "raw_login_attempt": raw_login,
        "raw_checkout_attempt": raw_checkout,
        "dataset_train": ds_train,
        "dataset_time_eval": ds_time,
        "dataset_user_holdout": ds_hold,
    }

    have_all = all(Path(p).exists() for k, p in expected.items() if k != "run_dir")
    if reuse_if_exists and have_all and not force:
        step = StepResult(
            name="dataset",
            status="skipped",
            decision=ReuseDecision(mode="reuse", reason="All expected raw+dataset artifacts already exist on disk.", used_manifest=False, forced=False),
            inputs=inputs,
            outputs=_artifact_map({k: Path(v) for k, v in expected.items()}),
            notes=["Skipped compute (reuse_if_exists=True, force=False)."],
        )
        return _finalize_step(rdir, step)

    if rec:
        with rec.step("raw+dataset", details={"run_id": run_id, "force": force}):
            run_all(cfg, run_id=run_id)
    else:
        run_all(cfg, run_id=run_id)

    step = StepResult(
        name="dataset",
        status="ok",
        decision=ReuseDecision(mode="compute", reason="Generated raw+dataset artifacts via pipeline.run_all(...).", used_manifest=False, forced=force),
        inputs=inputs,
        outputs=_artifact_map({k: Path(v) for k, v in expected.items()}),
    )
    return _finalize_step(rdir, step)

def step_features(
    cfg: Any,
    *,
    cfg_path: Optional[Path] = None,
    run_id: str,
    rec: Optional[StepRecorder] = None,
    reuse_if_exists: bool = True,
    force: bool = False,
    use_cache: bool = True,
    write_cache: bool = True,
) -> StepResult:
    """Step 2: build login features (or reuse cache/artifacts)."""
    rdir = run_dir_for(Path(cfg.paths.runs_dir), run_id)
    rdir.mkdir(parents=True, exist_ok=True)
    _ensure_manifest(cfg, rdir)

    cfg_path = cfg_path or Path("<cfg_path_unknown>")
    inputs = _mk_inputs(
        cfg_path,
        cfg,
        run_id,
        params={"event": "login_attempt"},
        toggles={
            "reuse_if_exists": reuse_if_exists,
            "force": force,
            "use_cache": use_cache,
            "write_cache": write_cache,
        },
    )

    feat_path = (rdir / "features" / "login_attempt" / "features").with_suffix(".parquet")
    expected = {"features_login": feat_path}

    if reuse_if_exists and feat_path.exists() and not force:
        step = StepResult(
            name="features",
            status="skipped",
            decision=ReuseDecision(mode="reuse", reason="Feature table already exists on disk.", used_manifest=False, forced=False),
            inputs=inputs,
            outputs=_artifact_map(expected),
            notes=["Skipped build (reuse_if_exists=True, force=False)."],
        )
        return _finalize_step(rdir, step)

    # Attempt shared-cache restore before compute
    cache_hit = False
    cache_key = None
    if use_cache and not force:
        cache_info = try_restore_feature_artifacts(cfg, rdir, force_rebuild=False)
        cache_hit = bool(getattr(cache_info, "is_hit", False))
        cache_key = getattr(cache_info, "cache_key", None)
        if cache_hit and feat_path.exists():
            step = StepResult(
                name="features",
                status="ok",
                decision=ReuseDecision(mode="reuse", reason="Restored feature artifacts from shared cache.", used_manifest=False, forced=False),
                inputs=inputs,
                outputs=_artifact_map(expected),
                summary={"cache_hit": True, "cache_key": cache_key},
                notes=[f"Shared feature cache HIT: key={cache_key}"],
            )
            return _finalize_step(rdir, step)

    # Compute features
    if rec:
        with rec.step("build_features", details={"run_id": run_id, "force": force, "use_cache": use_cache}):
            build_login_features_for_run(cfg, run_id=run_id, force=force)
    else:
        build_login_features_for_run(cfg, run_id=run_id, force=force)

    # Optionally write to cache after compute
    if write_cache and use_cache:
        save_feature_artifacts_to_cache(cfg, rdir)

    notes = []
    if cache_hit:
        notes.append("Cache was consulted but did not produce a usable hit; computed features.")
    step = StepResult(
        name="features",
        status="ok",
        decision=ReuseDecision(mode="compute", reason="Built features via features.runner.build_login_features_for_run(...).", used_manifest=False, forced=force),
        inputs=inputs,
        outputs=_artifact_map(expected),
        summary={"cache_hit": cache_hit, "cache_key": cache_key},
        notes=notes,
    )
    return _finalize_step(rdir, step)

def _baselines_present(rdir: Path) -> Tuple[bool, Optional[Path]]:
    out_dir = rdir / "models" / "login_attempt" / "baselines"
    metrics = out_dir / "metrics.json"
    any_model = any(out_dir.glob("**/*.joblib"))
    return bool(metrics.exists() and any_model), metrics if metrics.exists() else None


def step_baselines(
    cfg: Any,
    *,
    cfg_path: Optional[Path] = None,
    run_id: str,
    rec: Optional[StepRecorder] = None,
    reuse_if_exists: bool = True,
    force: bool = False,
) -> StepResult:
    """Step 3: train baselines (or reuse existing)."""
    rdir = run_dir_for(Path(cfg.paths.runs_dir), run_id)
    rdir.mkdir(parents=True, exist_ok=True)
    _ensure_manifest(cfg, rdir)

    cfg_path = cfg_path or Path("<cfg_path_unknown>")
    inputs = _mk_inputs(
        cfg_path,
        cfg,
        run_id,
        params={"event": "login_attempt"},
        toggles={"reuse_if_exists": reuse_if_exists, "force": force},
    )

    out_dir = rdir / "models" / "login_attempt" / "baselines"
    metrics_path = out_dir / "metrics.json"
    expected = {"baselines_dir": out_dir, "metrics_json": metrics_path}

    present, metrics_path0 = _baselines_present(rdir)
    if reuse_if_exists and present and not force:
        summary = {}
        if metrics_path0 and metrics_path0.exists():
            try:
                summary = read_json(metrics_path0).get("meta", {})
            except Exception:  # noqa: BLE001
                summary = {}
        step = StepResult(
            name="baselines",
            status="skipped",
            decision=ReuseDecision(mode="reuse", reason="Baseline metrics + at least one .joblib already exist on disk.", used_manifest=False, forced=False),
            inputs=inputs,
            outputs=_artifact_map(expected),
            notes=["Skipped training (reuse_if_exists=True, force=False)."],
            summary=summary,
        )
        return _finalize_step(rdir, step)

    if rec:
        with rec.step("train_baselines", details={"run_id": run_id, "force": force}):
            run_login_baselines_for_run(cfg, run_id=run_id, force=force, cfg_path=cfg_path)
    else:
        run_login_baselines_for_run(cfg, run_id=run_id, force=force, cfg_path=cfg_path)

    present2, metrics_path2 = _baselines_present(rdir)
    status = "ok" if present2 else "partial"
    summary2: Dict[str, Any] = {}
    if metrics_path2 and metrics_path2.exists():
        try:
            summary2 = read_json(metrics_path2).get("meta", {})
        except Exception:  # noqa: BLE001
            summary2 = {}

    step = StepResult(
        name="baselines",
        status=status,
        decision=ReuseDecision(mode="compute", reason="Trained baselines via models.runner.run_login_baselines_for_run(...).", used_manifest=False, forced=force),
        inputs=inputs,
        outputs=_artifact_map(expected),
        summary=summary2,
        notes=[] if status == "ok" else ["Expected baseline artifacts were not fully present after training (partial)."],
    )
    return _finalize_step(rdir, step)

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
    cfg_path: Optional[Path] = None,
    run_id: str,
    rec: Optional[StepRecorder] = None,
    reuse_if_exists: bool = True,
    force: bool = False,
) -> StepResult:
    """Step 4: eval diagnostics (slice + stability) for login_attempt."""
    rdir = run_dir_for(Path(cfg.paths.runs_dir), run_id)
    rdir.mkdir(parents=True, exist_ok=True)
    _ensure_manifest(cfg, rdir)

    cfg_path = cfg_path or Path("<cfg_path_unknown>")
    inputs = _mk_inputs(
        cfg_path,
        cfg,
        run_id,
        params={"event": "login_attempt"},
        toggles={"reuse_if_exists": reuse_if_exists, "force": force},
    )

    out_reports = rdir / "reports"
    expected = {
        "reports_dir": out_reports,
        "eval_slices_json": out_reports / "eval_slices_login_attempt.json",
        "eval_stability_json": out_reports / "eval_stability_login_attempt.json",
        "eval_slices_md": out_reports / "eval_slices_login_attempt.md",
        "eval_stability_md": out_reports / "eval_stability_login_attempt.md",
    }

    if reuse_if_exists and _eval_present(rdir) and not force:
        step = StepResult(
            name="eval",
            status="skipped",
            decision=ReuseDecision(mode="reuse", reason="Eval slice/stability outputs already exist on disk.", used_manifest=False, forced=False),
            inputs=inputs,
            outputs=_artifact_map(expected),
            notes=["Skipped eval (reuse_if_exists=True, force=False)."],
        )
        return _finalize_step(rdir, step)

    if rec:
        with rec.step("eval", details={"run_id": run_id, "force": force}):
            out = run_login_eval_for_run(cfg, run_id=run_id, force=force)
    else:
        out = run_login_eval_for_run(cfg, run_id=run_id, force=force)

    status = getattr(out, "status", "ok") if out is not None else "partial"
    notes = list(getattr(out, "notes", []) or []) if out is not None else ["Eval returned no outputs (unexpected)."]

    step = StepResult(
        name="eval",
        status=str(status),
        decision=ReuseDecision(mode="compute", reason="Ran eval via eval.runner.run_login_eval_for_run(...).", used_manifest=False, forced=force),
        inputs=inputs,
        outputs=_artifact_map(expected),
        notes=notes,
    )
    return _finalize_step(rdir, step)

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
    cfg_path: Optional[Path] = None,
    run_id: str,
    rec: Optional[StepRecorder] = None,
    reuse_if_exists: bool = True,
    force: bool = False,
) -> StepResult:
    """Step 5: export share bundle (summary, exec summary, UI bundle, handover, evidence)."""
    rdir = run_dir_for(Path(cfg.paths.runs_dir), run_id)
    rdir.mkdir(parents=True, exist_ok=True)
    _ensure_manifest(cfg, rdir)

    cfg_path = cfg_path or Path("<cfg_path_unknown>")
    inputs = _mk_inputs(
        cfg_path,
        cfg,
        run_id,
        params={},
        toggles={"reuse_if_exists": reuse_if_exists, "force": force},
    )

    share_dir = rdir / "share"
    expected = {
        "share_dir": share_dir,
        "share_summary_md": share_dir / "summary.md",
        "share_handover_md": share_dir / "handover.md",
        "share_ui_bundle_dir": share_dir / "ui_bundle",
        "share_evidence_dir": share_dir / "evidence",
        "share_exec_summary_md": share_dir / "exec_summary.md",
    }

    if reuse_if_exists and _share_present(rdir) and not force:
        step = StepResult(
            name="export",
            status="skipped",
            decision=ReuseDecision(mode="reuse", reason="Share bundle outputs already exist on disk.", used_manifest=False, forced=False),
            inputs=inputs,
            outputs=_artifact_map(expected),
            notes=["Skipped export (reuse_if_exists=True, force=False)."],
        )
        return _finalize_step(rdir, step)

    def _do() -> None:
        # Keep output surfaces stable; these funcs manage their own overwrites/policies.
        write_ui_summary(cfg, run_id=run_id)
        write_exec_summary(cfg, run_id=run_id)
        export_ui_bundle(cfg, run_id=run_id)
        write_mvp_handover(cfg, run_id=run_id)
        export_evidence_bundle(cfg, run_id=run_id)

    if rec:
        with rec.step("export_share_bundle", details={"run_id": run_id, "force": force}):
            _do()
    else:
        _do()

    step = StepResult(
        name="export",
        status="ok",
        decision=ReuseDecision(mode="compute", reason="Exported share bundle via ui.* + share.evidence.* helpers.", used_manifest=False, forced=force),
        inputs=inputs,
        outputs=_artifact_map(expected),
    )
    return _finalize_step(rdir, step)

