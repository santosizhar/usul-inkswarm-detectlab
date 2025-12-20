# J-0006 — D-0004 — BaselineLab (login_attempt)

## What changed
- Added **BaselineLab** runner to train quick models on FeatureLab output:
  - Logistic Regression (with standardization)
  - HistGradientBoostingClassifier
- Multi-label heads supported:
  - `label_replicators`, `label_the_mule`, `label_the_chameleon`
- Threshold selection:
  - choose threshold per label/model such that **FPR ≤ target_fpr** (default 0.01), closest under target.

## CLI
- Feature build:
  - `detectlab features build -c <cfg> --run-id <RUN_ID> [--force]`
- Baselines:
  - `detectlab baselines run -c <cfg> --run-id <RUN_ID> [--force]`

## Parquet ramp (explicit command)
- Parquet becomes mandatory at **D-0005** (pushed forward one delivery).
- Added explicit conversion command:
  - `detectlab dataset parquetify -c <cfg> --run-id <RUN_ID> [--force]`

## Outputs
- Baseline outputs are written under:
  - `runs/<run_id>/models/login_attempt/baselines/`
- These are marked **UNCOMMITTED** in the run manifest by design.

## Validation status
- Closed without executing validations (per request).
- See `DEFERRED_VALIDATION__D-0004.md` and `scripts/validate_d0004.*`.
