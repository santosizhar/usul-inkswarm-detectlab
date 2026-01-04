# J-0004 — D-0003 — FeatureLab (login_attempt)

## What changed
- Added **FeatureLab** pipeline to build a leakage-aware feature table for `login_attempt`.
- Implemented safe rolling aggregates across entities (`user`, `ip`, `device`) and windows (default: `1h, 6h, 24h, 7d`).
- Strict past-only leakage control:
  - rolling windows exclude the current event
  - unique-count features treat same-timestamp events as not visible to each other
- Added two notebooks:
  - `notebooks/02_featurelab_login_attempt.ipynb`
  - `notebooks/03_baselinelab_login_attempt.ipynb` (Baseline preview)

## Outputs
For run `<run_id>`:
- `runs/<run_id>/features/login_attempt/features.{parquet|csv}`
- `runs/<run_id>/features/login_attempt/feature_spec.json`
- `runs/<run_id>/features/login_attempt/feature_manifest.json`
- Manifest updated: `runs/<run_id>/manifest.json` → `artifacts.features/login_attempt/*`

## Notes
- An earlier D-0003 export was missing `src/` content (packaging mistake). This repository contains the complete implementation.
