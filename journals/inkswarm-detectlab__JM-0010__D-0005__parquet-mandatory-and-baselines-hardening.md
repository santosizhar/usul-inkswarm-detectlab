# JM-0010 — D-0005 — Summary

## What changed
- Parquet is mandatory (fail-closed). CSV fallback removed from normal read/write paths.
- BaselineLab defaults: **logreg + rf**. HGB kept experimental and isolated via subprocess.
- Added `detectlab doctor` + env diagnostics in baseline metrics.
- Configs + docs updated accordingly.

## Key files
- `src/inkswarm_detectlab/io/tables.py`
- `src/inkswarm_detectlab/utils/parquetify.py`
- `src/inkswarm_detectlab/models/runner.py`
- `src/inkswarm_detectlab/models/hgb_worker.py`
- `src/inkswarm_detectlab/cli.py`
- `configs/skynet_*.yaml`
- `docs/baselines.md`
- `DEFERRED_VALIDATION__D-0004.md`

## Validation note
- Local tests require a parquet engine (`pyarrow`). On the target machine (Python 3.12) run:
  - `detectlab doctor`
  - `pytest -q`
  - `detectlab run skynet -c configs/skynet_smoke.yaml`
  - `detectlab features build -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force`
  - `detectlab baselines run -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force`
