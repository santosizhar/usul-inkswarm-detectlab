# Inkswarm DetectLab — Run Summary

## Identity
- run_id: `RR_FAST_001_A`
- timezone: `America/Argentina/Buenos_Aires`
- schema_version: `v1`

## Raw tables
- login_attempt rows: 202
- checkout_attempt rows: 34

## Labels (login_attempt)
- overall attack prevalence (any label): 0.0545
- label_replicators: 0.0347
- label_the_mule: 0.0099
- label_the_chameleon: 0.0099

### Overlaps
- REPLICATORS & THE_MULE: 0
- REPLICATORS & THE_CHAMELEON: 0
- THE_MULE & THE_CHAMELEON: 0
- triple overlap: 0

## Checkout (checkout_attempt)
- adverse rate (failure or review): 0.0000

## Dataset splits
- time boundary (America/Argentina/Buenos_Aires): 2025-12-01T20:22:38.200000-03:00
- holdout users: 7 (15.2% of 46 unique users)

## Outputs written
- dataset/checkout_attempt/time_eval: `RR_FAST_001_A/dataset/checkout_attempt/time_eval.parquet` (parquet) — 5 rows
- dataset/checkout_attempt/train: `RR_FAST_001_A/dataset/checkout_attempt/train.parquet` (parquet) — 26 rows
- dataset/checkout_attempt/user_holdout: `RR_FAST_001_A/dataset/checkout_attempt/user_holdout.parquet` (parquet) — 3 rows
- dataset/login_attempt/time_eval: `RR_FAST_001_A/dataset/login_attempt/time_eval.parquet` (parquet) — 22 rows
- dataset/login_attempt/train: `RR_FAST_001_A/dataset/login_attempt/train.parquet` (parquet) — 156 rows
- dataset/login_attempt/user_holdout: `RR_FAST_001_A/dataset/login_attempt/user_holdout.parquet` (parquet) — 24 rows
- features/login_attempt/features: `RR_FAST_001_A/features/login_attempt/features.parquet` (parquet) — 202 rows
- features/login_attempt/manifest: `RR_FAST_001_A/features/login_attempt/feature_manifest.json` (json)
- features/login_attempt/spec: `RR_FAST_001_A/features/login_attempt/feature_spec.json` (json)
- raw/checkout_attempt: `RR_FAST_001_A/raw/checkout_attempt.parquet` (parquet) — 34 rows
- raw/login_attempt: `RR_FAST_001_A/raw/login_attempt.parquet` (parquet) — 202 rows

<!-- BASELINES_LOGIN_ATTEMPT_START -->

## Baselines (login_attempt)

This section summarizes baseline performance for the current run.
- detailed baseline report: `runs/RR_FAST_001_A/reports/baselines_login_attempt.md`
- baselines log: `runs/RR_FAST_001_A/logs/baselines.log`

| label | model | train PR-AUC | train thr | train FPR | train recall | time_eval PR-AUC | time_eval FPR | time_eval recall | user_holdout PR-AUC | user_holdout FPR | user_holdout recall |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| label_replicators | logreg | 0.7125 | 0.972054 | 0.0066 | 0.4000 | 0.0588 | 0.0476 | 0.0000 | 0.1250 | 0.0435 | 0.0000 |
| label_replicators | rf | 0.8769 | 0.211416 | 0.0066 | 0.8000 | 0.0455 | 0.0476 | 0.0000 | 0.0833 | 0.0000 | 0.0000 |
| label_the_mule | logreg | 0.2679 | 0.997289 | 0.0065 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| label_the_mule | rf | 0.7500 | 0.613333 | 0.0000 | 0.5000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| label_the_chameleon | logreg | 1.0000 | 0.17463 | 0.0065 | 1.0000 | 0.0526 | 0.0000 | 0.0000 | 0.0000 | 0.0833 | 0.0000 |
| label_the_chameleon | rf | 1.0000 | 0.0833333 | 0.0065 | 1.0000 | 0.0455 | 0.0952 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

<!-- BASELINES_LOGIN_ATTEMPT_END -->
