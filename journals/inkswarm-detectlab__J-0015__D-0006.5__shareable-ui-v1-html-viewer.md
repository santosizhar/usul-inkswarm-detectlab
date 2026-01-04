# J-0015 — D-0006.5 — Shareable UI v1 (Static HTML Viewer)

**Date:** 2025-12-18  
**NS:** inkswarm-detectlab

## What was delivered
A lightweight, stakeholder-friendly **static HTML** viewer that compares up to **5** runs side-by-side.

Key design decisions:
- **No server required**: open `index.html` directly.
- Reads from stable `ui_summary.json` generated per run.
- Focused on non-technical readability (headline tables, minimal jargon).

## New/updated commands
- Generate per-run summary:
  - `python -m inkswarm_detectlab ui summarize -c configs/skynet_mvp.yaml --run-id <RUN_ID>`
  - writes: `runs/<RUN_ID>/ui/ui_summary.json`

- Export viewer bundle for up to 5 runs:
  - `python -m inkswarm_detectlab ui export -c configs/skynet_mvp.yaml --run-ids RUN1,RUN2 --out-dir ui_bundle`
  - outputs: `ui_bundle/index.html`, `ui_bundle/app.js`, `ui_bundle/style.css`

## RR integration
RR scripts now export a UI bundle into the RR evidence folder:
- `rr_evidence/RR-0001/<base_run_id>/ui_bundle/`

## Validation performed (in-repo)
- Added unit tests for bundle export and `nmax=5` enforcement.
- CI includes the new tests under `pytest`.

## Notes / risks
- If baseline artifacts (`models/login_attempt/baselines/metrics.json`) are missing, the UI renders a clear “No baselines found” message.
- Viewer currently assumes MVP baselines are `logreg` and `rf` (consistent with CR-0002 decision).
