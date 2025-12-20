# MVP Usage Guide

This document explains how to **install**, **run**, and **interpret** the current MVP of **Inkswarm DetectLab**.

## Install (Python 3.12)

From repo root.

### Windows (PowerShell)
```powershell
python -m venv .venv
.
\.venv\Scripts\Activate.ps1

pip install -U pip
pip install -e ".[dev]"
```

### macOS / Linux
```bash
python -m venv .venv
source .venv/bin/activate

pip install -U pip
pip install -e ".[dev]"
```

Quick diagnostic:
```bash
python -m inkswarm_detectlab doctor
```

## Run the MVP

Pick a `run_id`, for example:
- `MVP_YYYYMMDD_001` for exploratory runs
- `RR_MVP_YYYYMMDD_001_A` / `_B` for Release Readiness (RR)

### End-to-end pipeline (raw + dataset)
```bash
detectlab run skynet -c configs/skynet_mvp.yaml --run-id MVP_YYYYMMDD_001
```

### Features (login_attempt)
```bash
detectlab features build -c configs/skynet_mvp.yaml --run-id MVP_YYYYMMDD_001 --force
```

### Baselines (MVP locked set: logreg + rf)
```bash
detectlab baselines run -c configs/skynet_mvp.yaml --run-id MVP_YYYYMMDD_001 --force
```

## Where outputs live

Everything lands under:
- `runs/<run_id>/`

Key files:
- `runs/<run_id>/manifest.json` — inventory of artifacts + formats
- `runs/<run_id>/reports/summary.md` — high-level run summary
- `runs/<run_id>/features/login_attempt/features.parquet` — feature table
- `runs/<run_id>/models/login_attempt/baselines/metrics.json` — machine-readable metrics
- `runs/<run_id>/models/login_attempt/baselines/report.md` — human report (includes a summary table)

## How to analyze progress/results

### 1) Sanity-check data volume
Confirm split sizes are stable and look reasonable:
- `train` vs `time_eval` vs `user_holdout`

If split sizes change unexpectedly between identical configs, treat it as a determinism regression.

### 2) Read the baseline report
Open:
- `runs/<run_id>/models/login_attempt/baselines/report.md`

At the top, you’ll see a summary table with (model × split) metrics:
- `pr_auc` (headline)
- `roc_auc` (supporting)
- `recall@1%FPR` (secondary)

### 3) Track changes over time
For iterative development, keep a tiny “evidence bundle” instead of committing full run data:
- The report paths above
- Optional: a copy of `metrics.json`

For RR, the helper scripts will generate:
- `journals/inkswarm-detectlab__RR_EVIDENCE__RR-0001__<base_run_id>.md`
- `rr_evidence/RR-0001/<base_run_id>/` (logs + determinism signatures)

## Troubleshooting

### Parquet engine missing
Parquet is mandatory. If you see a message about missing `pyarrow`, install dev deps:
```bash
pip install -e ".[dev]"
```

### CLI issues
If the CLI errors immediately, run:
```bash
python -m inkswarm_detectlab doctor
```
and confirm Python 3.12 + pinned dependency versions are installed.
