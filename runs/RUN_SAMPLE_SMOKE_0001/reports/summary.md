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

<!-- BASELINES_LOGIN_ATTEMPT_START -->

## Baselines (login_attempt)

This section summarizes baseline performance for the current run.
- detailed baseline report: `runs\RUN_SAMPLE_SMOKE_0001\reports\baselines_login_attempt.md`
- baselines log: `runs\RUN_SAMPLE_SMOKE_0001\logs\baselines.log`

| label | model | train PR-AUC | train thr | train FPR | train recall | time_eval PR-AUC | time_eval FPR | time_eval recall | user_holdout PR-AUC | user_holdout FPR | user_holdout recall |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| label_replicators | logreg | 0.0508 | 0.854924 | 0.0100 | 0.0191 | 0.0212 | 0.0155 | 0.0000 | 0.0274 | 0.0069 | 0.0000 |
| label_replicators | rf | 0.9999 | 0.11 | 0.0097 | 1.0000 | 0.0246 | 0.0415 | 0.0385 | 0.0273 | 0.0472 | 0.0000 |
| label_the_mule | logreg | 0.0410 | 0.930137 | 0.0099 | 0.0206 | 0.0153 | 0.0129 | 0.0000 | 0.0149 | 0.0165 | 0.0000 |
| label_the_mule | rf | 1.0000 | 0.07 | 0.0096 | 1.0000 | 0.0158 | 0.0214 | 0.0000 | 0.0145 | 0.0316 | 0.0526 |
| label_the_chameleon | logreg | 0.0390 | 0.881367 | 0.0099 | 0.0201 | 0.0323 | 0.0243 | 0.0000 | 0.0204 | 0.0125 | 0.0000 |
| label_the_chameleon | rf | 0.9927 | 0.0853276 | 0.0093 | 0.9866 | 0.0356 | 0.0330 | 0.0323 | 0.0225 | 0.0381 | 0.0000 |

<!-- BASELINES_LOGIN_ATTEMPT_END -->
