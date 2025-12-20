# D-0016 — Reporting Pack v2 (bundle)

This deliverable adds stakeholder-friendly HTML exports for reports and an Executive Summary.

## What you get
Generated at runtime under `runs/<run_id>/reports/`:
- `EXEC_SUMMARY.md`
- `EXEC_SUMMARY.html`
- `summary.html` (HTML render of `summary.md`)

And copied into the share bundle under `runs/<run_id>/share/reports/`:
- `EXEC_SUMMARY.html`
- `summary.html`

## Files included in this zip
- New code:
  - `src/inkswarm_detectlab/utils/md_to_html.py`
  - `src/inkswarm_detectlab/reports/exec_summary.py`
  - `src/inkswarm_detectlab/reports/__init__.py`
- Updated code:
  - `src/inkswarm_detectlab/pipeline.py` (ensures exec markers are available)
  - `src/inkswarm_detectlab/mvp/orchestrator.py` (calls exec summary generation)
  - `src/inkswarm_detectlab/share/evidence.py` (ensures `.html` reports get copied)

## How to apply
- Copy the files into your repo, preserving paths.
- Or apply the patch in `patches/` if you're using git.

## Notes (fail-closed)
- This deliverable does not claim end-to-end MVP execution in this environment.
- RR determinism may remain provisional unless Windows/Py3.12 evidence is recorded.
