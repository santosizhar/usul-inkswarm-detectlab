# Getting Started

This is the minimal “sanity check” path. For a full end-to-end validation, use the **Release Readiness** scripts:
- `docs/release_readiness_mvp.md`

## Install (Python 3.12)

### Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e ".[dev]"
```

### macOS/Linux
```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
```

## Quick verification
```bash
detectlab --help
pytest -q
python -m inkswarm_detectlab doctor
detectlab config check-parquet
```

Expected doctor output (examples):
```
DetectLab doctor
- python: 3.12.x
- platform: <os> 
- sklearn: <version>
- pandas: <version>
- pyarrow: <version>
- threadpools: <count>
```
If `pyarrow` is missing, the command exits non-zero with an explicit error.
`detectlab config check-parquet` provides a minimal RR-friendly gate you can embed in CI.

## Run the smallest smoke path
```bash
detectlab run skynet -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force
detectlab features build -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --event all --force
detectlab baselines run -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force
```

Artifacts land under `runs/<RUN_ID>/`. Check `runs/<RUN_ID>/manifest.json` to see what was produced.

## First success path (10–15 minutes)
1. `detectlab --help`
2. `python -m inkswarm_detectlab doctor` (ensure pyarrow is available)
3. `detectlab sanity --no-tiny-run` (compile/import only; no artifacts)
4. `detectlab run skynet -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force`
5. Inspect `runs/RUN_SAMPLE_SMOKE_0001/reports/summary.md` and the manifest for produced artifacts.

## Legacy conversion (only if you have old CSV runs)
```bash
detectlab dataset parquetify -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force
```

## Cache maintenance (optional)

DetectLab caches computed feature matrices to speed up repeated baseline training/evaluation.

- Default location: `runs/_cache/features/<feature_key>/`
- Inspect:
  - `detectlab cache list`
- Prune old entries (destructive):
  - `detectlab cache prune --older-than-days 30 --yes`

## Troubleshooting quick hits
- `python -m inkswarm_detectlab doctor` fails with `pyarrow` missing: reinstall deps (`pip install -e .[dev]`) and rerun.
- Unexpected threadpool count or OpenBLAS warnings: verify `threadpoolctl` output from `doctor` and pin BLAS libraries if needed.
- Smoke run writes artifacts under `runs/<RUN_ID>/`; remove with `rm -rf runs/<RUN_ID>` once inspected.
