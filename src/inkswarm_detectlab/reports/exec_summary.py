from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from inkswarm_detectlab.utils.md_to_html import md_to_html_document

EXEC_START = "<!-- EXEC_SUMMARY:START -->"
EXEC_END = "<!-- EXEC_SUMMARY:END -->"


@dataclass(frozen=True)
class ExecSummaryArtifacts:
    exec_md: Path
    exec_html: Path
    summary_md: Path
    summary_html: Path


def _safe_read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _safe_write_text(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _load_json_if_exists(p: Path) -> Optional[Any]:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except Exception:
        return None


def _fmt(v: Any) -> str:
    try:
        if isinstance(v, float):
            return f"{v:.4f}"
        return str(v)
    except Exception:
        return "—"


def _best_baseline_from_reports(reports_dir: Path) -> tuple[str, dict[str, Any]]:
    """Best-effort baseline selection.

    AQ1: Current behavior = max user_holdout PR-AUC.
    We attempt to find a baseline summary JSON if present. If not, we return placeholders.
    """
    # Common candidates (best-effort). If none exist, placeholder.
    candidates = [
        reports_dir / "baselines.json",
        reports_dir / "baselines_summary.json",
        reports_dir / "baseline_summary.json",
        reports_dir / "baseline_report.json",
    ]
    data = None
    for c in candidates:
        data = _load_json_if_exists(c)
        if data:
            break

    if not data:
        return ("—", {})

    # Try to normalize possible shapes.
    # Expect something like: {"baselines":[{"name":..,"splits":{"user_holdout":{"pr_auc":..}}}, ...]}
    baselines = None
    if isinstance(data, dict):
        for k in ["baselines", "models", "items"]:
            if k in data and isinstance(data[k], list):
                baselines = data[k]
                break
        if baselines is None and isinstance(data.get("baseline"), dict):
            baselines = [data["baseline"]]
    if not isinstance(baselines, list):
        return ("—", {})

    best_name = "—"
    best_row: dict[str, Any] = {}
    best_score = None

    for b in baselines:
        if not isinstance(b, dict):
            continue
        name = str(b.get("name") or b.get("id") or b.get("model") or "—")
        # Drill into splits.user_holdout.pr_auc
        pr_auc = None
        splits = b.get("splits")
        if isinstance(splits, dict):
            uh = splits.get("user_holdout") or splits.get("userHoldout") or splits.get("holdout")
            if isinstance(uh, dict):
                pr_auc = uh.get("pr_auc") or uh.get("prauc") or uh.get("prAuc")
        if pr_auc is None:
            # fallback: look for user_holdout_pr_auc at top-level
            pr_auc = b.get("user_holdout_pr_auc") or b.get("uh_pr_auc")
        try:
            score = float(pr_auc) if pr_auc is not None else None
        except Exception:
            score = None

        if score is None:
            continue
        if best_score is None or score > best_score:
            best_score = score
            best_name = name
            best_row = b

    return (best_name, best_row)


def _recommended_actions_template(*, rr_provisional: bool, d0004_deferred: bool) -> str:
    lines = []
    lines.append("## Recommended actions")
    lines.append("")
    lines.append("- If **time_eval** is materially worse than **user_holdout**, treat it as **drift risk** → consider retraining with newer data, recalibrating thresholds, or deploying drift monitors.")
    lines.append("- If a slice shows materially worse performance or instability → consider slice-specific mitigations (rules, extra features, targeted data collection).")
    lines.append("- If model quality is acceptable but ops cost is high → consider tightening thresholds, adding guardrails, or using a simpler baseline in low-risk paths.")
    if rr_provisional:
        lines.append("- **Reproducibility is PROVISIONAL** (RR evidence pending) → run RR-0001/0002 on Windows/Py3.12 and record evidence before any high-stakes deployment.")
    if d0004_deferred:
        lines.append("- **D-0004 validation is deferred** → run the deferred validation and record outcomes before relying on that baseline claim.")
    lines.append("")
    return "\n".join(lines)


def _heuristic_flags(reports_dir: Path) -> list[str]:
    """Best-effort heuristic flags derived from known report files.

    This is intentionally conservative: if we can't find trustworthy fields, we emit nothing.
    """
    flags: list[str] = []
    # Candidate: a combined metrics json, if present
    candidates = [
        reports_dir / "headline_metrics.json",
        reports_dir / "metrics.json",
        reports_dir / "summary_metrics.json",
    ]
    data = None
    for c in candidates:
        data = _load_json_if_exists(c)
        if data:
            break
    if not isinstance(data, dict):
        return flags

    # Look for nested splits
    splits = data.get("splits") if isinstance(data.get("splits"), dict) else None
    if not splits:
        return flags

    uh = splits.get("user_holdout") if isinstance(splits.get("user_holdout"), dict) else None
    te = splits.get("time_eval") if isinstance(splits.get("time_eval"), dict) else None
    if not (uh and te):
        return flags

    # Try compare PR-AUC if present
    def get_pr_auc(d: dict[str, Any]) -> Optional[float]:
        v = d.get("pr_auc") or d.get("prauc") or d.get("prAuc")
        try:
            return float(v) if v is not None else None
        except Exception:
            return None

    uh_pr = get_pr_auc(uh)
    te_pr = get_pr_auc(te)

    if uh_pr is not None and te_pr is not None:
        if te_pr < uh_pr * 0.9:
            flags.append(f"Drift warning: time_eval PR-AUC {_fmt(te_pr)} is >10% below user_holdout {_fmt(uh_pr)}.")
    return flags


def write_exec_summary(
    *,
    run_dir: Path,
    rr_provisional: bool = True,
    d0004_deferred: bool = True,
) -> ExecSummaryArtifacts:
    """Generate executive summary MD+HTML, and HTML render of summary.md.

    - Creates `reports/EXEC_SUMMARY.md` and `.html`.
    - Ensures `reports/summary.md` contains an injected exec section between markers.
    - Creates `reports/summary.html` from `summary.md`.
    """
    reports_dir = run_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    summary_md = reports_dir / "summary.md"
    summary_text = _safe_read_text(summary_md)

    # Best-effort baseline selection (AQ1 current: max user_holdout PR-AUC)
    best_name, _best_row = _best_baseline_from_reports(reports_dir)

    flags = _heuristic_flags(reports_dir)

    exec_md_path = reports_dir / "EXEC_SUMMARY.md"
    exec_html_path = reports_dir / "EXEC_SUMMARY.html"
    summary_html_path = reports_dir / "summary.html"

    exec_lines: list[str] = []
    exec_lines.append("# Executive Summary")
    exec_lines.append("")
    exec_lines.append("## How to open")
    exec_lines.append("- Open the bundle UI: `share/ui_bundle/index.html`")
    exec_lines.append("- Or read this report: `reports/EXEC_SUMMARY.html`")
    exec_lines.append("")
    exec_lines.append("## What to trust (truth split)")
    exec_lines.append("- **user_holdout** = primary truth (generalization to new users)")
    exec_lines.append("- **time_eval** = drift check (time stability)")
    exec_lines.append("")
    exec_lines.append("## Best baseline (best-effort)")
    exec_lines.append(f"- Selected by max **user_holdout PR-AUC** (if available): **{best_name}**")
    exec_lines.append("")
    if flags:
        exec_lines.append("## Flags (best-effort)")
        for f in flags:
            exec_lines.append(f"- {f}")
        exec_lines.append("")

    exec_lines.append(_recommended_actions_template(rr_provisional=rr_provisional, d0004_deferred=d0004_deferred))

    exec_md_text = "\n".join(exec_lines).rstrip() + "\n"
    _safe_write_text(exec_md_path, exec_md_text)

    # Inject exec section into summary.md between markers (or prepend if missing)
    injected_block = "\n".join([
        EXEC_START,
        "",
        "## Executive summary",
        "",
        "- Open `reports/EXEC_SUMMARY.html` for a stakeholder-friendly view.",
        "- Truth split: **user_holdout = primary**, **time_eval = drift check**.",
        f"- Best baseline (max user_holdout PR-AUC, if available): **{best_name}**.",
        "",
        EXEC_END,
        "",
    ])

    if EXEC_START in summary_text and EXEC_END in summary_text:
        pre = summary_text.split(EXEC_START)[0]
        post = summary_text.split(EXEC_END, 1)[1]
        summary_text = pre + injected_block + post.lstrip("\n")
    else:
        # Prepend with markers
        summary_text = injected_block + summary_text

    _safe_write_text(summary_md, summary_text)

    # Render HTML versions
    _safe_write_text(exec_html_path, md_to_html_document(exec_md_text, title="Executive Summary"))
    _safe_write_text(summary_html_path, md_to_html_document(summary_text, title="Summary"))

    return ExecSummaryArtifacts(
        exec_md=exec_md_path,
        exec_html=exec_html_path,
        summary_md=summary_md,
        summary_html=summary_html_path,
    )


__all__ = ["write_exec_summary", "ExecSummaryArtifacts", "EXEC_START", "EXEC_END"]
