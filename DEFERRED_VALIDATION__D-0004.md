# Deferred Validation — D-0004 (BaselineLab)

This delivery was **closed without running validation** (per request at the time).
Use the steps below to validate on your machine later.

> Note: As of **D-0005**, Parquet is mandatory. If you are validating using the committed fixture
> `RUN_SAMPLE_SMOKE_0001` (which may contain legacy `.csv` artifacts), migrate it first.

## Prereqs
- Python 3.12+ (repo target)
- Install dependencies (includes `scikit-learn` and `pyarrow`)

## 1) Install
```bash
uv venv
uv pip install -e ".[dev]"
```

## 2) If validating a legacy run, migrate it to Parquet (D-0005 rule)
```bash
detectlab dataset parquetify -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force
```

Notes:
- This writes `.parquet` files next to `.csv` files.
- It updates `runs/<run_id>/manifest.json` to point to Parquet.
- It does **not** delete the CSV files (migration keeps originals).

## 3) Run tests
```bash
pytest -q
```

## 4) FeatureLab + BaselineLab (D-0003 + D-0004)
```bash
detectlab features build -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force
detectlab baselines run -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force
```

Expected outputs:
- `runs/RUN_SAMPLE_SMOKE_0001/features/login_attempt/features.parquet`
- `runs/RUN_SAMPLE_SMOKE_0001/models/login_attempt/reports/baseline_report.md`
- `runs/RUN_SAMPLE_SMOKE_0001/models/login_attempt/metrics/metrics.json`
- `runs/RUN_SAMPLE_SMOKE_0001/models/login_attempt/metrics/thresholds.json`

## 5) Optional: fresh smoke run
```bash
detectlab run skynet -c configs/skynet_smoke.yaml
# then migrate (if needed) and repeat steps 3–4 with the printed run_id
```
