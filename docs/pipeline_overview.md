# Pipeline Overview

Runs live under `runs/<run_id>/...`.

## Current run layout
- `runs/<run_id>/raw/` — raw event tables (`login_attempt`, `checkout_attempt`)
- `runs/<run_id>/dataset/` — leakage-aware dataset splits per event table
- `runs/<run_id>/features/` — FeatureLab outputs (login_attempt features table + spec)
- `runs/<run_id>/models/` — BaselineLab outputs (models + metrics + report; uncommitted by default)
- `runs/<run_id>/manifest.json` — run metadata, artifact rows + hashes, and formats written
- `runs/<run_id>/reports/summary.md` — human-readable run summary (labels, splits, outputs)

## Locked leakage-aware split (implemented in D-0002)
- **85% time-based** split (`train` + `time_eval`)
- **15% by-user holdout** split (`user_holdout`)
- Splits are computed per event table (shared holdout across tables can be introduced later via CC).

## Locked timezone
All timestamps are standardized to `America/Argentina/Buenos_Aires`.

## Determinism contract
DetectLab aims for reproducibility:
- Tables are canonicalized (stable sort + stable column order) **before write and hash**.
- Manifest stores `content_hash` per artifact.
- Parquet is **mandatory** as of **D-0005** (fail-closed; no CSV fallback).

## Legacy Parquet conversion
Use the explicit command to upgrade **older runs** that still contain CSV artifacts:

```bash
detectlab dataset parquetify -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001
```
