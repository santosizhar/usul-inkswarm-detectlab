# Deferred Validation — D-0004 (BaselineLab)

This delivery was **closed without running validation** (per request).  
Use the steps below to validate on your machine later.

## Prereqs
- Python 3.12+ recommended (repo target); 3.11 usually works.
- Install dependencies (includes `scikit-learn` for BaselineLab and `pyarrow` for Parquet).

### Windows (PowerShell)
```powershell
cd <repo_root>
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e .
```

### macOS/Linux
```bash
cd <repo_root>
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -e .
```

## Validation steps (recommended order)

### 1) Run tests (fast sanity)
```bash
pytest -q
```

### 2) FeatureLab on committed fixture run
This repo includes a fixture run: `RUN_SAMPLE_SMOKE_0001`.

```bash
detectlab features build -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force
```

Check:
- `runs/RUN_SAMPLE_SMOKE_0001/features/login_attempt/features.*`
- `runs/RUN_SAMPLE_SMOKE_0001/features/login_attempt/feature_spec.json`
- `runs/RUN_SAMPLE_SMOKE_0001/manifest.json` includes `features/login_attempt/*`

### 3) BaselineLab
```bash
detectlab baselines run -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force
```

Check:
- `runs/RUN_SAMPLE_SMOKE_0001/models/login_attempt/baselines/report.md`
- `runs/RUN_SAMPLE_SMOKE_0001/models/login_attempt/baselines/metrics.json`

### 4) Parquet ramp (explicit conversion)
If any artifacts were written as CSV fallback (e.g., missing `pyarrow`), convert them explicitly:

```bash
detectlab dataset parquetify -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force
```

## Optional: rerun a fresh smoke run
```bash
detectlab run skynet -c configs/skynet_smoke.yaml
# then repeat FeatureLab + BaselineLab using the printed run_id
```
