# Release Readiness — MVP (RR)

As of **CR-0002**, the RR gate for the MVP is **full-requirements**.

## Preconditions
- Python **3.12**
- `pyarrow` available (Parquet is mandatory)

Quick check:
```bash
python -m inkswarm_detectlab doctor
```

## Helper scripts
- macOS/Linux: `scripts/rr_mvp.sh`
- Windows PowerShell: `scripts/rr_mvp.ps1`

## Manual RR procedure (required)
Choose a fresh run_id, e.g. `RR_MVP_YYYYMMDD_001`.

1) End-to-end pipeline
```bash
detectlab run skynet -c configs/skynet_mvp.yaml --run-id RR_MVP_YYYYMMDD_001
```

2) Features
```bash
detectlab features build -c configs/skynet_mvp.yaml --run-id RR_MVP_YYYYMMDD_001 --force
```

3) Baselines (MVP locked set)
```bash
detectlab baselines run -c configs/skynet_mvp.yaml --run-id RR_MVP_YYYYMMDD_001 --force
```

## MVP baseline set (locked)
- `logreg`
- `rf`

`hgb` is disabled for MVP (CR-0002) due to a platform-specific native crash during `.fit()`.

## Required artifacts
- `runs/<run_id>/manifest.json`
- `runs/<run_id>/reports/summary.md`
- `runs/<run_id>/features/login_attempt/features.parquet`
- `runs/<run_id>/models/login_attempt/baselines/metrics.json`
- `runs/<run_id>/models/login_attempt/baselines/report.md`
