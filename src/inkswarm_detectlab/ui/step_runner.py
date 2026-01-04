
from __future__ import annotations
def _repo_root() -> Path:
    # step_runner.py lives at <repo>/src/inkswarm_detectlab/ui/step_runner.py
    return Path(__file__).resolve().parents[3]


def _resolve_cfg_path(p: Path) -> Path:
    """Resolve config path robustly for notebooks.

    - If p exists, return it.
    - Else try resolving relative to repo root.
    - Else search under <repo>/configs for a matching filename.
    """
    if p.exists():
        return p

    root = _repo_root()

    cand = root / p
    if cand.exists():
        return cand

    # common: user passes "configs/foo.yaml" but CWD is notebooks/
    if "configs" in p.parts:
        cand2 = root / "configs" / p.name
        if cand2.exists():
            return cand2

    matches = list((root / "configs").rglob(p.name))
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        # pick the shortest path (closest) deterministically
        matches = sorted(matches, key=lambda x: len(x.parts))
        return matches[0]

    return p
"""Notebook-oriented step runners.

Design goals (D-0022):
- keep core pipeline modules intact
- provide thin, explicit "step" wrappers for notebooks
- prefer reusing existing artifacts + shared cache when possible
- surface step visibility: inputs, outputs, quick summaries, and "what next"

These helpers intentionally avoid any notebook-only dependencies.
"""

from pathlib import Path
from typing import Union,  Any, Dict, Optional, Tuple

import json


def _read_json(path: Path) -> Dict[str, Any]:
    """Read a JSON file as UTF-8 (stdlib-only)."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


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
from .reuse_policy import decide_reuse

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
    cfg_or_path: Union[Path, Any],
    run_id: Optional[str] = None,
) -> Tuple[Any, str]:
    """Resolve config + run_id for notebook step helpers.

    Accepts either:
    - cfg_or_path: Path to a YAML config, or
    - cfg_or_path: an already-loaded AppConfig-like object.
    """
    if isinstance(cfg_or_path, Path):
        cfg_path = _resolve_cfg_path(cfg_or_path)
        cfg = load_config(cfg_path)
    else:
        cfg = cfg_or_path

    # explicit override wins
    if run_id is not None:
        return cfg, run_id

    # config may pin run_id
    pinned = getattr(getattr(cfg, "run", None), "run_id", None)
    if pinned:
        return cfg, pinned

    # otherwise generate sequential id using fingerprint + configured prefix/width (no strategy field)
    _, cfg_hash8 = _config_fingerprint(cfg)
    prefix = getattr(getattr(cfg, "run", None), "run_id_prefix", "RUN")
    width = int(getattr(getattr(cfg, "run", None), "run_id_width", 4) or 4)
    rid = make_run_id(
        config_hash8=cfg_hash8,
        runs_dir=Path(cfg.paths.runs_dir),
        prefix=prefix,
        width=width,
    )
    return cfg, rid


def wire_check(cfg_or_path: Union[Path, Any], run_id: Optional[str] = None) -> Dict[str, Any]:
    """Lightweight wiring check (no heavy compute).

    - resolves cfg + run_id
    - creates run dir if missing
    - ensures manifest exists
    - returns the key paths the step notebook will use
    """
    cfg, rid = resolve_run_id(cfg_or_path, run_id=run_id)
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

    dec = decide_reuse(
        run_dir=rdir,
        step_name="dataset",
        current_config_hash=inputs.config_hash,
        expected_outputs={k: Path(v) for k, v in expected.items()},
        reuse_if_exists=reuse_if_exists,
        force=force,
    )
    if dec.mode == "reuse":
        step = StepResult(
            name="dataset",
            status="skipped",
            decision=dec,
            inputs=inputs,
            outputs=_artifact_map({k: Path(v) for k, v in expected.items()}),
            notes=["Skipped compute based on reuse policy."],
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
        decision=ReuseDecision(mode="compute", reason="Generated raw+dataset artifacts via pipeline.run_all(...).", used_manifest=dec.used_manifest, forced=force),
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
    # Canonical notebook-facing toggles (D-0025)
    use_shared_feature_cache: bool = True,
    write_shared_feature_cache: bool = True,
    # Compatibility shims (pre-RR / internal naming). If provided, overrides canonical.
    use_cache: Optional[bool] = None,
    write_cache: Optional[bool] = None,
    use_shared_cache: Optional[bool] = None,
    write_shared_cache: Optional[bool] = None,
) -> StepResult:
    """Step 2: build login features (or reuse cache/artifacts)."""
    # Resolve compatibility toggles
    if use_shared_cache is not None:
        use_shared_feature_cache = use_shared_cache
    if write_shared_cache is not None:
        write_shared_feature_cache = write_shared_cache
    if use_cache is not None:
        use_shared_feature_cache = use_cache
    if write_cache is not None:
        write_shared_feature_cache = write_cache

    use_cache_final = bool(use_shared_feature_cache)
    write_cache_final = bool(write_shared_feature_cache)
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
            "use_cache": use_cache_final,
            "write_cache": write_cache_final,
        },
    )

    feat_path = (rdir / "features" / "login_attempt" / "features").with_suffix(".parquet")
    expected = {"features_login": feat_path}

    dec = decide_reuse(
        run_dir=rdir,
        step_name="features",
        current_config_hash=inputs.config_hash,
        expected_outputs={k: Path(v) for k, v in expected.items()},
        reuse_if_exists=reuse_if_exists,
        force=force,
    )
    if dec.mode == "reuse":
        step = StepResult(
            name="features",
            status="skipped",
            decision=dec,
            inputs=inputs,
            outputs=_artifact_map(expected),
            notes=["Skipped build based on reuse policy."],
        )
        return _finalize_step(rdir, step)

    # Attempt shared-cache restore before compute (only makes sense when outputs are missing)
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
                decision=ReuseDecision(mode="reuse", reason="Restored feature artifacts from shared cache.", used_manifest=dec.used_manifest, forced=False),
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

    if write_cache and use_cache:
        save_feature_artifacts_to_cache(cfg, rdir)

    step = StepResult(
        name="features",
        status="ok",
        decision=ReuseDecision(mode="compute", reason="Built features via features.runner.build_login_features_for_run(...).", used_manifest=dec.used_manifest, forced=force),
        inputs=inputs,
        outputs=_artifact_map(expected),
        summary={"cache_hit": cache_hit, "cache_key": cache_key},
        notes=["Cache was consulted but did not produce a usable hit; computed features."] if cache_hit else [],
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

    dec = decide_reuse(
        run_dir=rdir,
        step_name="baselines",
        current_config_hash=inputs.config_hash,
        expected_outputs={k: Path(v) for k, v in expected.items()},
        reuse_if_exists=reuse_if_exists,
        force=force,
    )

    present, metrics_path0 = _baselines_present(rdir)
    if dec.mode == "reuse" and present:
        summary = {}
        if metrics_path0 and metrics_path0.exists():
            try:
                summary = _read_json(metrics_path0).get("meta", {})
            except Exception:  # noqa: BLE001
                summary = {}
        step = StepResult(
            name="baselines",
            status="skipped",
            decision=dec,
            inputs=inputs,
            outputs=_artifact_map(expected),
            notes=["Skipped training based on reuse policy."],
            summary=summary,
        )
        return _finalize_step(rdir, step)

    # If manifest/disk suggest reuse but baseline presence check failed, compute instead.
    if dec.mode == "reuse" and not present:
        dec = ReuseDecision(mode="compute", reason="Baseline presence check failed (metrics and at least one .joblib required).", used_manifest=dec.used_manifest, forced=force)

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
            summary2 = _read_json(metrics_path2).get("meta", {})
        except Exception:  # noqa: BLE001
            summary2 = {}

    step = StepResult(
        name="baselines",
        status=status,
        decision=ReuseDecision(mode="compute", reason="Trained baselines via models.runner.run_login_baselines_for_run(...).", used_manifest=dec.used_manifest, forced=force),
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

    dec = decide_reuse(
        run_dir=rdir,
        step_name="eval",
        current_config_hash=inputs.config_hash,
        expected_outputs={k: Path(v) for k, v in expected.items()},
        reuse_if_exists=reuse_if_exists,
        force=force,
    )
    if dec.mode == "reuse" and _eval_present(rdir):
        step = StepResult(
            name="eval",
            status="skipped",
            decision=dec,
            inputs=inputs,
            outputs=_artifact_map(expected),
            notes=["Skipped eval based on reuse policy."],
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
        decision=ReuseDecision(mode="compute", reason="Ran eval via eval.runner.run_login_eval_for_run(...).", used_manifest=dec.used_manifest, forced=force),
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

    dec = decide_reuse(
        run_dir=rdir,
        step_name="export",
        current_config_hash=inputs.config_hash,
        expected_outputs={k: Path(v) for k, v in expected.items()},
        reuse_if_exists=reuse_if_exists,
        force=force,
    )
    if dec.mode == "reuse" and _share_present(rdir):
        step = StepResult(
            name="export",
            status="skipped",
            decision=dec,
            inputs=inputs,
            outputs=_artifact_map(expected),
            notes=["Skipped export based on reuse policy."],
        )
        return _finalize_step(rdir, step)

    def _do() -> None:
        # 5A) UI summary (used as input to handover)
        ui_summary_path = write_ui_summary(cfg, run_id=run_id, force=force)
        try:
            summary: dict[str, Any] = _read_json(ui_summary_path)
        except Exception as e:  # noqa: BLE001
            summary = {
                "run_id": run_id,
                "note": f"Failed to read ui_summary.json for handover ({e})",
                "ui_summary_json": str(ui_summary_path),
            }

        # 5B) Exec summary (writes into runs/<run_id>/reports/...)
        exec_art = write_exec_summary(run_dir=rdir)
        summary.setdefault("artifacts", {})
        for k in ("exec_md", "exec_html", "summary_md", "summary_html"):
            p = getattr(exec_art, k, None)
            if p is not None:
                summary["artifacts"][k] = str(p)

        # 5C) UI bundle (writes into runs/<run_id>/share/reports/...)
        ui_out_dir = (rdir / "share" / "reports")
        ui_out_dir.mkdir(parents=True, exist_ok=True)
        ui_bundle_dir = export_ui_bundle(cfg, run_ids=[run_id], out_dir=ui_out_dir, force=force)
        summary["artifacts"]["ui_bundle_dir"] = str(ui_bundle_dir)

        # 5D) Handover markdown (runs/<run_id>/reports/mvp_handover.md)
        write_mvp_handover(
            runs_dir=Path(cfg.paths.runs_dir),
            run_id=run_id,
            ui_bundle_dir=Path(ui_bundle_dir) if ui_bundle_dir else None,
            summary=summary,
        )

        # 5E) Evidence bundle (optional) — best-effort, never fails the step
        try:
            export_evidence_bundle(run_dir=rdir, force=force)
        except TypeError:
            export_evidence_bundle(run_dir=rdir)
        except Exception:  # noqa: BLE001
            pass


    if rec:
        with rec.step("export_share_bundle", details={"run_id": run_id, "force": force}):
            _do()
    else:
        _do()

    step = StepResult(
        name="export",
        status="ok",
        decision=ReuseDecision(mode="compute", reason="Exported share bundle via ui.* + share.evidence.* helpers.", used_manifest=dec.used_manifest, forced=force),
        inputs=inputs,
        outputs=_artifact_map(expected),
    )
    return _finalize_step(rdir, step)
