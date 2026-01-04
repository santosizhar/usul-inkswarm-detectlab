# Journal — J-0017 — D-0008 — BaselineLab v1: headline metrics + stakeholder reporting
Date: 2025-12-18

## Goal
Improve BaselineLab MVP usability and stakeholder readability:
- Make baseline outputs easier to consume (single summary table and stable stakeholder-friendly paths)
- Add a compact “threshold candidates” view (top-3 thresholds under target FPR)
- Ensure baseline runs are debuggable (persistent log file)
- Keep behavior MVP-friendly: partial failures should still produce artifacts and a clear warning

## Inputs / constraints
- **Label:** current label (`is_fraud` for login_attempt)
- **Models (MVP preset):** `logreg` + `rf`
- **Defer:** checkout baselines (not in scope)
- **Target operating point:** Recall @ 1% FPR as a secondary metric (threshold chosen on train)

## What changed
### 1) Baseline artifacts and stakeholder-friendly outputs
Baseline training now writes:
- `runs/<run_id>/models/login_attempt/baselines/metrics.json`
- `runs/<run_id>/models/login_attempt/baselines/report.md`
- `runs/<run_id>/logs/baselines.log`

And additionally copies the report to:
- `runs/<run_id>/reports/baselines_login_attempt.md`

The run summary is updated (or created) with a new embedded section:
- `runs/<run_id>/reports/summary.md` now includes “Baselines (login_attempt)” with the same compact summary table and links to the detailed report + log.

### 2) Compact threshold candidates table
For each label/model, BaselineLab now stores and renders a “top-3” threshold candidates table:
- Candidates are thresholds from train with FPR <= target_fpr
- Ranked deterministically by recall, then FPR, then precision

This is included in `metrics.json` under:
- `train.threshold_table_top3`

And rendered in `report.md` under each model.

### 3) Fail-soft behavior for MVP usability
- If **at least one** baseline succeeds, artifacts are still written and the CLI prints a warning when status is `partial`.
- If **all** requested baselines fail, the baselines command returns an error.

### 4) UI summary enrichment
`ui_summary.json` now includes:
- Baselines status (`ok` / `partial` / `failed`)
- Paths to the stakeholder-friendly report and the baselines log (if present)
- A note when status is `partial`

### 5) Documentation
Updated `docs/baselines.md` to reflect:
- Additional output paths (`reports/` copy + `logs/`)
- Failure behavior expectations

## Validations (in this environment)
- `pytest -q` passed.

## Known limitations
- Checkout baselines remain deferred.
- HGB remains excluded per CR-0002 crash triage until resolved.

## Next
Proceed to the next deliverable per roadmap, keeping login-first focus while maintaining feature parity and stakeholder usability.
