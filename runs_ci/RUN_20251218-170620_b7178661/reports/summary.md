# Inkswarm DetectLab — Run Summary

## Identity
- run_id: `RUN_20251218-170620_b7178661`
- timezone: `America/Argentina/Buenos_Aires`
- schema_version: `v1`

## Raw tables
- login_attempt rows: 266
- checkout_attempt rows: 48

## Labels (login_attempt)
- overall attack prevalence (any label): 0.0526
- label_replicators: 0.0226
- label_the_mule: 0.0150
- label_the_chameleon: 0.0150

### Overlaps
- REPLICATORS & THE_MULE: 0
- REPLICATORS & THE_CHAMELEON: 0
- THE_MULE & THE_CHAMELEON: 0
- triple overlap: 0

## Checkout (checkout_attempt)
- adverse rate (failure or review): 0.0000

## Dataset splits
- time boundary (America/Argentina/Buenos_Aires): 2025-12-01T20:19:15.700000-03:00
- holdout users: 6 (15.4% of 39 unique users)

## Outputs written
- dataset/checkout_attempt/time_eval: `RUN_20251218-170620_b7178661/dataset/checkout_attempt/time_eval.parquet` (parquet) — 9 rows
- dataset/checkout_attempt/train: `RUN_20251218-170620_b7178661/dataset/checkout_attempt/train.parquet` (parquet) — 31 rows
- dataset/checkout_attempt/user_holdout: `RUN_20251218-170620_b7178661/dataset/checkout_attempt/user_holdout.parquet` (parquet) — 8 rows
- dataset/login_attempt/time_eval: `RUN_20251218-170620_b7178661/dataset/login_attempt/time_eval.parquet` (parquet) — 37 rows
- dataset/login_attempt/train: `RUN_20251218-170620_b7178661/dataset/login_attempt/train.parquet` (parquet) — 206 rows
- dataset/login_attempt/user_holdout: `RUN_20251218-170620_b7178661/dataset/login_attempt/user_holdout.parquet` (parquet) — 23 rows
- raw/checkout_attempt: `RUN_20251218-170620_b7178661/raw/checkout_attempt.parquet` (parquet) — 48 rows
- raw/login_attempt: `RUN_20251218-170620_b7178661/raw/login_attempt.parquet` (parquet) — 266 rows

