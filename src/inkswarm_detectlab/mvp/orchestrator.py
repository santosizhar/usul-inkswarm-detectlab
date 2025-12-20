from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from ..config import load_config
from ..pipeline import run_all
from ..features import build_login_features_for_run
from ..models import run_login_baselines_for_run
from ..eval import run_login_eval_for_run
from ..ui.summarize import write_ui_summary
from ..ui.bundle import export_ui_bundle
from ..share.evidence import export_evidence_bundle
from ..io.paths import run_dir as run_dir_for

from .handover import write_mvp_handover
from inkswarm_detectlab.reports.exec_summary import write_exec_summary


def run_mvp(
    *,
    cfg_path: Path,
    run_id: Optional[str] = None,
    force: bool = False,
) -> tuple[Path, dict[str, Any]]:
    """Run the MVP pipeline in a best-effort, shareable way.

    D-0009 design:
    - fastest default: build features for login only
    - stakeholder output: always export a static HTML bundle and a handover md
    - best effort: continue when possible and report failures clearly
    """
    cfg = load_config(cfg_path)

    summary: dict[str, Any] = {
        "run_id": run_id,
        "config": str(cfg_path),
        "status": "unknown",
        "steps": [],
    }

    def _step(name: str, fn):
        try:
            out = fn()
            summary["steps"].append({"name": name, "status": "ok"})
            return out
        except Exception as e:
            summary["steps"].append({"name": name, "status": "fail", "message": str(e)})
            return None

    # 1) Raw + dataset (required; if this fails we can't proceed).
    out = _step("skynet+dataset", lambda: run_all(cfg, run_id=run_id))
    if out is None:
        summary["status"] = "fail"
        # best guess: run_dir can't be known if generation failed.
        rdir = run_dir_for(cfg.paths.runs_dir, run_id or "RUN_UNKNOWN")
        return rdir, summary

    rdir, _ = out
    rid = rdir.name
    summary["run_id"] = rid

    # 2) Features (login only; fastest)
    _step("features(login)", lambda: build_login_features_for_run(cfg, run_id=rid, force=force))

    # 3) Baselines (logreg + rf)
    try:
        _, results = run_login_baselines_for_run(cfg, run_id=rid, force=force, cfg_path=cfg_path)
        if results.get("status") == "partial":
            summary["steps"].append(
                {"name": "baselines(login)", "status": "ok", "message": "partial (see logs/baselines.log)"}
            )
        else:
            summary["steps"].append({"name": "baselines(login)", "status": "ok"})
    except Exception as e:
        summary["steps"].append({"name": "baselines(login)", "status": "fail", "message": str(e)})


    # 4) Evaluation diagnostics (slices + stability; stakeholder-first)
    try:
        ev = run_login_eval_for_run(cfg, run_id=rid, force=force)
        if ev.status == "partial":
            summary["steps"].append({"name": "eval(login)", "status": "ok", "message": "partial (see reports/eval_*.md)"})
        else:
            summary["steps"].append({"name": "eval(login)", "status": "ok"})
    except Exception as e:
        summary["steps"].append({"name": "eval(login)", "status": "fail", "message": str(e)})

    # 4) ui_summary.json (even if baselines failed, summary can still be produced)
    _step("ui_summarize", lambda: write_ui_summary(cfg, run_id=rid, force=True))

    # 5) Export HTML bundle (single run, but supports up to 5)
    share_dir = rdir / "share" / "ui_bundle"
    _step("ui_export", lambda: export_ui_bundle(cfg, run_ids=[rid], out_dir=share_dir, force=True))

    # 6) Stakeholder handover
    _step(
        "handover",
        lambda: write_mvp_handover(
            runs_dir=cfg.paths.runs_dir,
            run_id=rid,
            ui_bundle_dir=share_dir,
            summary=summary,
        ),
    )

    

    # 7) Tidy share package (evidence bundle layout)
    _step("evidence_bundle", lambda: export_evidence_bundle(run_dir=rdir))

# Overall status
    fails = [s for s in summary["steps"] if s.get("status") == "fail"]
    summary["status"] = "ok" if not fails else "partial"

    # D-0016: generate stakeholder-friendly executive summary (MD + HTML) and HTML render of summary.md
    try:
        write_exec_summary(run_dir=rdir, rr_provisional=True, d0004_deferred=True)
    except Exception as e:
        # Fail-soft for reporting extras; core pipeline should remain usable
        logger.warning(f"Exec summary generation failed: {e}")

    return rdir, summary
