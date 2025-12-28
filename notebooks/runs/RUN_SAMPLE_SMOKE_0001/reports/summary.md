<!-- EXEC_SUMMARY:START -->

## Executive summary

- Open `reports/EXEC_SUMMARY.html` for a stakeholder-friendly view.
- Truth split: **user_holdout = primary**, **time_eval = drift check**.
- Best baseline (max user_holdout PR-AUC, if available): **—**.

<!-- EXEC_SUMMARY:END -->
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
- dataset/checkout_attempt/time_eval: `RUN_SAMPLE_SMOKE_0001\dataset\checkout_attempt\time_eval.parquet` (parquet) — 138 rows
- dataset/checkout_attempt/train: `RUN_SAMPLE_SMOKE_0001\dataset\checkout_attempt\train.parquet` (parquet) — 799 rows
- dataset/checkout_attempt/user_holdout: `RUN_SAMPLE_SMOKE_0001\dataset\checkout_attempt\user_holdout.parquet` (parquet) — 169 rows
- dataset/login_attempt/time_eval: `RUN_SAMPLE_SMOKE_0001\dataset\login_attempt\time_eval.parquet` (parquet) — 1,184 rows
- dataset/login_attempt/train: `RUN_SAMPLE_SMOKE_0001\dataset\login_attempt\train.parquet` (parquet) — 8,142 rows
- dataset/login_attempt/user_holdout: `RUN_SAMPLE_SMOKE_0001\dataset\login_attempt\user_holdout.parquet` (parquet) — 1,476 rows
- features/login_attempt/features: `RUN_SAMPLE_SMOKE_0001\features\login_attempt\features.parquet` (parquet) — 10,802 rows
- features/login_attempt/manifest: `RUN_SAMPLE_SMOKE_0001\features\login_attempt\feature_manifest.json` (json)
- features/login_attempt/spec: `RUN_SAMPLE_SMOKE_0001\features\login_attempt\feature_spec.json` (json)
- raw/checkout_attempt: `RUN_SAMPLE_SMOKE_0001\raw\checkout_attempt.parquet` (parquet) — 1,106 rows
- raw/login_attempt: `RUN_SAMPLE_SMOKE_0001\raw\login_attempt.parquet` (parquet) — 10,802 rows

<!-- BASELINES_LOGIN_ATTEMPT_START -->

## Baselines (login_attempt)

This section summarizes baseline performance for the current run.
- detailed baseline report: `runs\RUN_SAMPLE_SMOKE_0001\reports\baselines_login_attempt.md`
- baselines log: `runs\RUN_SAMPLE_SMOKE_0001\logs\baselines.log`

| label | model | train PR-AUC | train thr | train FPR | train recall | time_eval PR-AUC | time_eval FPR | time_eval recall | user_holdout PR-AUC | user_holdout FPR | user_holdout recall |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| label_replicators | logreg | 0.0556 | 0.857037 | 0.0100 | 0.0287 | 0.0214 | 0.0181 | 0.0000 | 0.0256 | 0.0069 | 0.0000 |
| label_replicators | rf | 1.0000 | 0.0766667 | 0.0097 | 1.0000 | 0.0224 | 0.1002 | 0.0385 | 0.0257 | 0.0763 | 0.0571 |
| label_the_mule | logreg | 0.0441 | 0.942848 | 0.0099 | 0.0206 | 0.0146 | 0.0137 | 0.0000 | 0.0148 | 0.0130 | 0.0000 |
| label_the_mule | rf | 1.0000 | 0.0533333 | 0.0089 | 1.0000 | 0.0195 | 0.0883 | 0.0556 | 0.0164 | 0.0446 | 0.1053 |
| label_the_chameleon | logreg | 0.0478 | 0.931153 | 0.0099 | 0.0201 | 0.0457 | 0.0165 | 0.0323 | 0.0196 | 0.0049 | 0.0000 |
| label_the_chameleon | rf | 0.9999 | 0.0633333 | 0.0093 | 1.0000 | 0.0315 | 0.0755 | 0.0968 | 0.0233 | 0.0583 | 0.0294 |

<!-- BASELINES_LOGIN_ATTEMPT_END -->

