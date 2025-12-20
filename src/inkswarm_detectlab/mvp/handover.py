from __future__ import annotations

from pathlib import Path
from typing import Any

from ..io.paths import run_dir as run_dir_for, reports_dir


def write_mvp_handover(
    *,
    runs_dir: Path,
    run_id: str,
    ui_bundle_dir: Path | None,
    summary: dict[str, Any],
) -> Path:
    """Write a stakeholder-facing handover markdown for a run.

    This document is meant for non-technical readers. It points to the shareable UI
    bundle and provides a short interpretation guide.
    """
    rdir = run_dir_for(runs_dir, run_id)
    r_reports = reports_dir(rdir)
    r_reports.mkdir(parents=True, exist_ok=True)

    rel_ui = None
    if ui_bundle_dir is not None:
        try:
            rel_ui = ui_bundle_dir.relative_to(rdir)
        except Exception:
            rel_ui = ui_bundle_dir

    # Step status digest
    rows = summary.get("steps", []) or []
    ok = [s for s in rows if s.get("status") == "ok"]
    fail = [s for s in rows if s.get("status") == "fail"]
    skip = [s for s in rows if s.get("status") == "skipped"]

    lines: list[str] = []
    lines.append("# Inkswarm DetectLab — MVP Handover")
    lines.append("")
    lines.append("## What this is")
    lines.append(
        "This folder contains one end-to-end run of Inkswarm DetectLab: synthetic activity, "
        "feature generation, baseline models, and a stakeholder-friendly report. "
        "You can review results without running any code."
    )
    lines.append("")
    lines.append("## How to view the results")
    if rel_ui is not None:
        lines.append(f"1) Open the shareable viewer: `{rel_ui / 'index.html'}`")
    else:
        lines.append("1) Open the shareable viewer: (not generated)")
    lines.append("2) If you prefer reading: open `reports/summary.md` and `reports/baselines_login_attempt.md`")
    lines.append("")

    lines.append("## How to interpret (quick)")
    lines.append("- **PR-AUC** (higher is better) is a strong headline metric when positives are rare.")
    lines.append("- **Recall @ 1% FPR** answers: ‘How many true fraud cases do we catch while keeping false alarms low?’")
    lines.append("- **Time Eval** checks stability over time; **User Holdout** checks generalization to new users.")
    lines.append("")

    lines.append("## What succeeded in this run")
    if ok:
        for s in ok:
            msg = s.get("message")
            lines.append(f"- ✅ {s.get('name')}{f' — {msg}' if msg else ''}")
    else:
        lines.append("- (none)")
    lines.append("")

    if fail:
        lines.append("## What failed (and where to look)")
        for s in fail:
            msg = s.get("message") or ""
            lines.append(f"- ❌ {s.get('name')}{f' — {msg}' if msg else ''}")
        lines.append("")
        lines.append("If something failed, the most useful artifact is usually the log file:")
        lines.append("- `logs/` (pipeline logs)")
        lines.append("- `logs/baselines.log` (baseline models)")
        lines.append("")

    if skip:
        lines.append("## What was skipped")
        for s in skip:
            msg = s.get("message")
            lines.append(f"- ⏭️ {s.get('name')}{f' — {msg}' if msg else ''}")
        lines.append("")

    lines.append("## How to re-run (for operators)")
    lines.append("If you are running this locally, the recommended single command is:")
    lines.append("```bash")
    lines.append("detectlab run mvp -c configs/skynet_mvp.yaml")
    lines.append("```")
    lines.append("For a full release readiness run (two-run determinism), use `scripts/rr_mvp.ps1`.")
    lines.append("")

    lines.append("## Where to learn more")
    lines.append("- `docs/mvp_user_guide.md` (non-technical walkthrough)")
    lines.append("- `docs/pipeline_overview.md` (what the pipeline does at a high level)")
    lines.append("")

    out = r_reports / "mvp_handover.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out
