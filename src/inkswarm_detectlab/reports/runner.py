from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
import json
import datetime as _dt

from ..config import AppConfig
from ..io.paths import run_dir as run_dir_for, reports_dir as reports_dir_for
from ..io.manifest import read_manifest, write_manifest


@dataclass(frozen=True)
class ReportPaths:
    reports_dir: Path
    final_report_md: Path
    insights_json: Path


def _now_ba_iso() -> str:
    # Keep it explicit (BA timezone) without extra deps.
    # We store offset -03:00 as per project convention.
    now = _dt.datetime.utcnow() - _dt.timedelta(hours=3)
    return now.replace(microsecond=0).isoformat() + "-03:00"


def _safe_read_text(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def _safe_read_json(path: Path) -> Optional[dict]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _extract_baseline_highlights(metrics: dict) -> dict:
    """
    Normalize metrics.json into a compact highlights object:
    - headline: PR-AUC (average_precision) on time_eval + user_holdout
    - operating: recall@target_fpr on time_eval + user_holdout
    Expected structure is produced by models.runner (D-0004).
    """
    highlights: Dict[str, Any] = {"heads": {}}
    if not isinstance(metrics, dict):
        return highlights

    results = metrics.get("results") if isinstance(metrics.get("results"), dict) else metrics
    # models.runner writes keys: results[model_name][label][split]...
    for model_name, model_block in (results.items() if isinstance(results, dict) else []):
        if not isinstance(model_block, dict):
            continue
        for label, label_block in model_block.items():
            if not isinstance(label_block, dict):
                continue
            h = highlights["heads"].setdefault(label, {})
            # Pull for each split
            for split in ("time_eval", "user_holdout", "train"):
                sb = label_block.get(split)
                if not isinstance(sb, dict):
                    continue
                # tolerate different key spellings
                pr_auc = sb.get("average_precision", sb.get("pr_auc"))
                rec = sb.get("recall_at_target_fpr", sb.get("recall_at_fpr", sb.get("recall")))
                fpr = sb.get("achieved_fpr", sb.get("fpr"))
                h.setdefault("models", {}).setdefault(model_name, {})[split] = {
                    "pr_auc": pr_auc,
                    "recall_at_target_fpr": rec,
                    "achieved_fpr": fpr,
                }
    return highlights


def _render_final_report(
    cfg: AppConfig,
    run_id: str,
    manifest: dict,
    feature_manifest: Optional[dict],
    baseline_metrics: Optional[dict],
    baseline_report_md: Optional[str],
    validation_note: str,
) -> str:
    lines: list[str] = []
    lines.append("# Inkswarm DetectLab — Final Report (D-0006)")
    lines.append("")
    lines.append("## Identity")
    lines.append(f"- run_id: `{run_id}`")
    lines.append(f"- timezone: `America/Argentina/Buenos_Aires`")
    lines.append(f"- generated_at: `{_now_ba_iso()}`")
    lines.append(f"- schema_version: `{manifest.get('schema_version', 'unknown')}`")
    lines.append("")

    lines.append("## What this report is")
    lines.append(
        "This is a stitched, operator-friendly report that summarizes the run artifacts (raw → dataset → features → baselines) "
        "and provides a narrative interpretation aligned with the SKYNET / SPACING GUILD fiction layer. "
        "It is intended to be readable first, and reproducible second."
    )
    lines.append("")

    # Artifact presence
    lines.append("## Artifacts present")
    art = manifest.get("artifacts", {})
    if isinstance(art, dict) and art:
        for k, v in art.items():
            if isinstance(v, dict) and "path" in v:
                lines.append(f"- {k}: `{v.get('path')}`")
    else:
        lines.append("- (manifest does not list artifacts — run may be legacy)")
    lines.append("")

    # Feature summary
    lines.append("## FeatureLab v0 summary (login_attempt)")
    if feature_manifest:
        lines.append(f"- rows: {feature_manifest.get('rows', feature_manifest.get('n_rows', 'unknown'))}")
        lines.append(f"- columns: {feature_manifest.get('cols', feature_manifest.get('n_cols', 'unknown'))}")
        params = feature_manifest.get("params", {})
        if isinstance(params, dict) and params:
            lines.append(f"- windows: {params.get('windows')}")
            lines.append(f"- groups: {params.get('groups')}")
            lines.append(f"- strict_past_only: {params.get('strict_past_only')}")
    else:
        lines.append("- Feature manifest not found for this run.")
    lines.append("")

    # Baselines
    lines.append("## BaselineLab summary (login_attempt)")
    if baseline_metrics:
        highlights = _extract_baseline_highlights(baseline_metrics)
        # Headline tables
        lines.append("")
        lines.append("### Headline: PR-AUC (time_eval, user_holdout)")
        for head, head_block in highlights.get("heads", {}).items():
            lines.append(f"- **{head}**")
            models = head_block.get("models", {})
            for mname, mblock in models.items():
                te = mblock.get("time_eval", {})
                uh = mblock.get("user_holdout", {})
                lines.append(
                    f"  - {mname}: PR-AUC time_eval={te.get('pr_auc')}, user_holdout={uh.get('pr_auc')}"
                )
        lines.append("")
        lines.append("### Operating point: Recall @ target FPR=1% (threshold set on train)")
        for head, head_block in highlights.get("heads", {}).items():
            lines.append(f"- **{head}**")
            models = head_block.get("models", {})
            for mname, mblock in models.items():
                te = mblock.get("time_eval", {})
                uh = mblock.get("user_holdout", {})
                lines.append(
                    f"  - {mname}: Recall@1%FPR time_eval={te.get('recall_at_target_fpr')} (FPR={te.get('achieved_fpr')}), "
                    f"user_holdout={uh.get('recall_at_target_fpr')} (FPR={uh.get('achieved_fpr')})"
                )
    else:
        lines.append("- Baseline metrics not found for this run (baselines may not have been executed).")
    lines.append("")

    # Narrative / interpretation
    lines.append("## Narrative interpretation (SKYNET / SPACING GUILD)")
    lines.append(
        "The synthetic world defines three adversary playbooks for login_attempt: "
        "**REPLICATORS** (repeatable automation), **THE_MULE** (credential ferry / compromised account handoff), "
        "and **THE_CHAMELEON** (shape-shifting behavior to evade heuristics)."
    )
    lines.append("")
    lines.append("### What to look for")
    lines.append("- REPLICATORS: high-frequency bursts; repeated patterns; shared IP/device density.")
    lines.append("- THE_MULE: cross-identity reuse (device or IP seen across users) with intermittent success.")
    lines.append("- THE_CHAMELEON: low-and-slow drift; subtle rate changes; higher variance in session cadence.")
    lines.append("")
    lines.append("### Practical operator guidance (MVP)")
    lines.append("- Start with thresholds tuned to your tolerance (Recall@1%FPR is the first operating anchor).")
    lines.append("- Use the feature windows (1h/6h/24h/7d) to debug false positives by horizon.")
    lines.append("- Prefer user-holdout performance for generalization judgement.")
    lines.append("")

    # Limitations / validation status
    lines.append("## Validation status")
    lines.append(validation_note)
    lines.append("")
    lines.append("## Known limitations")
    lines.append("- Synthetic data will never perfectly match production fraud; treat results as a sandbox baseline.")
    lines.append("- Multi-label overlaps are plausible but model calibration may be unstable without more data diversity.")
    lines.append("- Parquet is mandatory (D-0005+); legacy CSV runs require migration.")
    lines.append("")
    lines.append("## Next steps (roadmap)")
    lines.append("- CR ceremony: review usability of report + error messages + config ergonomics.")
    lines.append("- D-0007 (proposed): SPACING GUILD checkout fraud generator + checkout features.")
    lines.append("- D-0008 (proposed): calibration, cost curves, and narrative report enrichment.")
    lines.append("")

    # Append baseline_report_md verbatim if present but avoid huge output
    if baseline_report_md:
        lines.append("## Appendix: Baseline report excerpt")
        excerpt = "\n".join(baseline_report_md.splitlines()[:120])
        lines.append(excerpt)
        if len(baseline_report_md.splitlines()) > 120:
            lines.append("...(truncated)...")
        lines.append("")

    return "\n".join(lines) + "\n"


def generate_final_report_for_run(cfg: AppConfig, run_id: str, *, force: bool = False) -> Path:
    """
    D-0006: Generate a stitched, operator-friendly report for a run.
    Writes:
      runs/<run_id>/reports/final_report.md
      runs/<run_id>/reports/insights.json
    Updates run manifest with report artifact references.
    """
    rdir = run_dir_for(cfg.paths.runs_dir, run_id)
    rpts = reports_dir_for(rdir)
    rpts.mkdir(parents=True, exist_ok=True)

    final_md = rpts / "final_report.md"
    insights_json = rpts / "insights.json"

    if not force and final_md.exists():
        raise RuntimeError(f"final_report.md already exists for run_id={run_id}. Re-run with --force to overwrite.")

    manifest = read_manifest(rdir)
    # Feature manifest
    fman_path = rdir / "features" / "login_attempt" / "feature_manifest.json"
    feature_manifest = _safe_read_json(fman_path)

    # Baselines
    bdir = rdir / "models" / "login_attempt" / "baselines"
    metrics_path = bdir / "metrics.json"
    report_path = bdir / "report.md"
    baseline_metrics = _safe_read_json(metrics_path)
    baseline_report_md = _safe_read_text(report_path)

    # Validation status section: be explicit about deferred validation
    validation_lines = []
    if baseline_metrics is None:
        validation_lines.append(
            "- Baselines were not found for this run. This report can be generated without them, but detection performance is unknown."
        )
        validation_lines.append(
            "- To validate later: run `detectlab baselines run -c <cfg> --run-id <RUN_ID> --force` and regenerate this report."
        )
    else:
        validation_lines.append("- Baseline metrics are present for this run.")
        validation_lines.append("- Thresholds are selected on train to target FPR=1% (per head/model).")

    # If parquet mandatory, note migration
    validation_lines.append("- Parquet is mandatory (D-0005+). If you have legacy CSV artifacts, run `detectlab dataset parquetify ...` first.")

    validation_note = "\n".join(validation_lines)

    text = _render_final_report(
        cfg=cfg,
        run_id=run_id,
        manifest=manifest,
        feature_manifest=feature_manifest,
        baseline_metrics=baseline_metrics,
        baseline_report_md=baseline_report_md,
        validation_note=validation_note,
    )
    final_md.write_text(text, encoding="utf-8")

    insights = {
        "run_id": run_id,
        "generated_at": _now_ba_iso(),
        "has_feature_manifest": feature_manifest is not None,
        "has_baselines": baseline_metrics is not None,
        "baseline_highlights": _extract_baseline_highlights(baseline_metrics or {}),
    }
    insights_json.write_text(json.dumps(insights, indent=2, sort_keys=True), encoding="utf-8")

    # Update run manifest
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        artifacts = {}
        manifest["artifacts"] = artifacts
    artifacts["final_report_md"] = {"path": str(final_md.relative_to(rdir))}
    artifacts["insights_json"] = {"path": str(insights_json.relative_to(rdir))}
    write_manifest(rdir, manifest)

    return final_md
