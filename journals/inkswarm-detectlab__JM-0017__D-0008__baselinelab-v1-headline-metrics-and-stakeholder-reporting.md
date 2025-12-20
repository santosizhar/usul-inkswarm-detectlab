# Journal Meta — JM-0017 — D-0008 — BaselineLab v1: headline metrics + stakeholder reporting
Date: 2025-12-18

## Delivered
BaselineLab was upgraded for MVP usability and stakeholder consumption.

### Artifacts written (per run)
- `runs/<run_id>/models/login_attempt/baselines/metrics.json`
  - Includes `status` (`ok` / `partial` / `failed`) and a compact `train.threshold_table_top3`.
- `runs/<run_id>/models/login_attempt/baselines/report.md`
  - Contains a full baseline report plus a compact summary table.
- `runs/<run_id>/logs/baselines.log`
  - Persistent debug log; captures failures without losing artifacts.
- `runs/<run_id>/reports/baselines_login_attempt.md`
  - Stakeholder-friendly copy of the report.
- `runs/<run_id>/reports/summary.md`
  - Now includes an upserted “Baselines (login_attempt)” section with the summary table and links.

### CLI / UX
- `detectlab baselines run` now emits a warning (stderr) when the run status is `partial`, while still returning successfully if at least one baseline succeeded.
- If all requested baselines fail, the command returns an error.

### UI summary
- `ui_summary.json` now includes baselines `status` and stable pointers to the stakeholder-friendly report and baselines log.

## Out of scope / deferred
- Checkout baselines remain deferred.
- HGB remains excluded per CR-0002 crash triage.
