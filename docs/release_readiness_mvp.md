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
RR-0001 requires **two consecutive runs** with identical signatures.

Choose a fresh **base** run_id, e.g. `RR_MVP_YYYYMMDD_001`.
You will run:
- `RR_MVP_YYYYMMDD_001_A`
- `RR_MVP_YYYYMMDD_001_B`

1) End-to-end pipeline (run A)
```bash
detectlab run skynet -c configs/skynet_mvp.yaml --run-id RR_MVP_YYYYMMDD_001_A
```

2) Features (run A)
```bash
detectlab features build -c configs/skynet_mvp.yaml --run-id RR_MVP_YYYYMMDD_001_A --force
```

3) Baselines (run A; MVP locked set)
```bash
detectlab baselines run -c configs/skynet_mvp.yaml --run-id RR_MVP_YYYYMMDD_001_A --force
```

4) Repeat steps 1–3 for **run B** (`..._B`).

5) Generate and compare determinism signatures
```bash
python -m inkswarm_detectlab.tools.rr_signature --run-id RR_MVP_YYYYMMDD_001_A --out rr_evidence/RR-0001/RR_MVP_YYYYMMDD_001/signature_A.json
python -m inkswarm_detectlab.tools.rr_signature --run-id RR_MVP_YYYYMMDD_001_B --out rr_evidence/RR-0001/RR_MVP_YYYYMMDD_001/signature_B.json
```

If the signatures differ, RR fails.

## Evidence outputs (small)
The helper scripts also write:
- `journals/inkswarm-detectlab__RR_EVIDENCE__RR-0001__<base_run_id>.md`
- `rr_evidence/RR-0001/<base_run_id>/` (log + signatures)

If RR fails, scripts clean up the run folders and leave an error message under the evidence directory.

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
