# inkswarm-detectlab__J-00XX__D-0016__reporting-pack-v2-exec-summary-html.md

# J-00XX — D-0016 — Reporting Pack v2 (Exec Summary + HTML)

**Date:** 2025-12-19  
**Scope:** Add stakeholder-friendly HTML exports of reports and an Executive Summary to the run artifacts and share bundle.

## Delivered
- Executive Summary generation:
  - `runs/<run_id>/reports/EXEC_SUMMARY.md`
  - `runs/<run_id>/reports/EXEC_SUMMARY.html`
- HTML render of summary:
  - `runs/<run_id>/reports/summary.html` (from `summary.md`)
- Evidence bundle includes HTML reports:
  - `runs/<run_id>/share/reports/EXEC_SUMMARY.html`
  - `runs/<run_id>/share/reports/summary.html`

## Behavioral notes
- “Best baseline” selection: **max user_holdout PR-AUC** (best-effort if baseline metrics JSON exists).
- “Recommended actions” includes template + conservative heuristic flags (best-effort).

## Files changed / added
- NEW: `src/inkswarm_detectlab/utils/md_to_html.py`
- NEW: `src/inkswarm_detectlab/reports/exec_summary.py`
- NEW: `src/inkswarm_detectlab/reports/__init__.py`
- UPDATED: `src/inkswarm_detectlab/pipeline.py`
- UPDATED: `src/inkswarm_detectlab/mvp/orchestrator.py`
- UPDATED: `src/inkswarm_detectlab/share/evidence.py`

## Fail-closed notes
- No claim of end-to-end MVP execution here.
- Manual tests are scheduled after D-0016 (MT-0001 gate).
- RR reproducibility may remain provisional unless Windows/Py3.12 evidence is recorded.

## Outcome
**D-0016 COMPLETE.**
