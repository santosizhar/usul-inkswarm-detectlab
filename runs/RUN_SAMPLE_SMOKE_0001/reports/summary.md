# Inkswarm DetectLab — Run Summary

## Identity
- run_id: `RUN_SAMPLE_SMOKE_0001`
- timezone: `America/Argentina/Buenos_Aires`
- schema_version: `v1`

## Raw tables
- login_attempt rows: 10,802
- checkout_attempt rows: 1,106

## Labels (login_attempt)
- overall attack prevalence (any label): 0.0568
- label_replicators: 0.0250
- label_the_mule: 0.0124
- label_the_chameleon: 0.0198

### Overlaps
- REPLICATORS & THE_MULE: 0
- REPLICATORS & THE_CHAMELEON: 2
- THE_MULE & THE_CHAMELEON: 2
- triple overlap: 0

## Checkout (checkout_attempt)
- adverse rate (failure or review): 0.0054

## Dataset splits
- time boundary (America/Argentina/Buenos_Aires): 2025-12-06T22:45:28.350000-03:00
- holdout users: 27 (14.9% of 181 unique users)

## Outputs written
- dataset/checkout_attempt/time_eval: `RUN_SAMPLE_SMOKE_0001/dataset/checkout_attempt/time_eval.parquet` (parquet) — 138 rows
- dataset/checkout_attempt/train: `RUN_SAMPLE_SMOKE_0001/dataset/checkout_attempt/train.parquet` (parquet) — 799 rows
- dataset/checkout_attempt/user_holdout: `RUN_SAMPLE_SMOKE_0001/dataset/checkout_attempt/user_holdout.parquet` (parquet) — 169 rows
- dataset/login_attempt/time_eval: `RUN_SAMPLE_SMOKE_0001/dataset/login_attempt/time_eval.parquet` (parquet) — 1,184 rows
- dataset/login_attempt/train: `RUN_SAMPLE_SMOKE_0001/dataset/login_attempt/train.parquet` (parquet) — 8,142 rows
- dataset/login_attempt/user_holdout: `RUN_SAMPLE_SMOKE_0001/dataset/login_attempt/user_holdout.parquet` (parquet) — 1,476 rows
- features/login_attempt/features: `RUN_SAMPLE_SMOKE_0001/features/login_attempt/features.parquet` (parquet) — 10,802 rows
- features/login_attempt/manifest: `RUN_SAMPLE_SMOKE_0001/features/login_attempt/feature_manifest.json` (json)
- features/login_attempt/spec: `RUN_SAMPLE_SMOKE_0001/features/login_attempt/feature_spec.json` (json)
- raw/checkout_attempt: `RUN_SAMPLE_SMOKE_0001/raw/checkout_attempt.parquet` (parquet) — 1,106 rows
- raw/login_attempt: `RUN_SAMPLE_SMOKE_0001/raw/login_attempt.parquet` (parquet) — 10,802 rows

