# D-0002 — SKYNET synthetic pipeline + leakage-aware splits — Implementation Journal (J-0002)

Date: 2025-12-16
NS: inkswarm-detectlab

## Goal
Deliver the first end-to-end executable pipeline stage for the MVP:

1) Generate raw SKYNET synthetic event tables (`login_attempt`, `checkout_attempt`).
2) Produce leakage-aware dataset splits per event table:
   - 15% by-user holdout (entire user histories)
   - 85% time split for the remaining users
3) Record artifacts + content hashes in a `manifest.json` and write a short run summary.
4) Commit a reproducible sample smoke run inside the repo.

## What was implemented

### 1) SKYNET synthetic generator
Implemented in `src/inkswarm_detectlab/synthetic/skynet.py`.

Key properties:
- Timezone aware timestamps (Buenos Aires).
- Hourly + weekday seasonality.
- “Short, intense spikes” via campaign windows (volume and/or share spikes).
- Mostly benign baseline; attacks are injected via **SKYNET playbooks**:
  - REPLICATORS, THE_MULE, THE_CHAMELEON
- Multi-label support (a row can carry multiple playbook labels).
- Overlap patterns are enabled (pair + triple overlap probabilities), while keeping the combinations coherent.

The generator also emits campaign metadata that is stored in the manifest.

### 2) Leakage-aware dataset split
Implemented in `src/inkswarm_detectlab/dataset/build.py`.

Split behavior:
- A holdout user set is sampled (fraction = `dataset.build.user_holdout`).
- All rows for those users become `user_holdout`.
- Remaining rows are split on a **time boundary computed in BA local time** (fraction = `dataset.build.time_split`).

Each event table is split independently for now (shared holdout across tables is left as a later CC decision).

### 3) Pipeline orchestration (raw → dataset)
Implemented in `src/inkswarm_detectlab/pipeline.py`.

Key entrypoints:
- `generate_raw(cfg, run_id=None)`
- `build_dataset(cfg, run_id)`
- `run_all(cfg, run_id=None)`

Outputs:
- Raw tables written under `runs/<run_id>/raw/`.
- Dataset splits written under `runs/<run_id>/dataset/<event>/<split>.<fmt>`.
- `runs/<run_id>/manifest.json` records:
  - config hash (fingerprint)
  - artifact paths, row counts, and deterministic content hashes
  - dataset parameters + boundary timestamps
- `runs/<run_id>/reports/summary.md` provides a compact human-readable summary.

### 4) Configs for synthetic runs
Added repo-root YAML configs:
- `configs/skynet_mvp.yaml` — MVP-sized synthetic
- `configs/skynet_smoke.yaml` — small-ish “smoke” example pinned to `RUN_SAMPLE_SMOKE_0001`

### 5) CLI commands
Extended Typer CLI in `src/inkswarm_detectlab/cli.py`:
- `detectlab synthetic skynet <config> [--run-id]`
- `detectlab dataset build <config> --run-id <id>`
- `detectlab run skynet <config> [--run-id]` (end-to-end)

### 6) Deterministic config hashing
Fixed `stable_hash_dict()` to support config dictionaries containing `Path` and `date` objects by using `default=str`.
This prevents pipeline crashes and keeps config hashing deterministic.

### 7) Tests (fast + deterministic)
Added `tests/test_d0002_skynet.py` covering:
- determinism: same seed ⇒ same artifact hashes
- sanity: label columns exist + rough prevalence guardrails
- seasonality/spike presence checks
- leakage checks: holdout users do not appear in train/time_eval splits

All tests (including notebook execution) pass in this environment.

### 8) Sample smoke run committed
Generated and committed:
- `runs/RUN_SAMPLE_SMOKE_0001/raw/` (event tables)
- `runs/RUN_SAMPLE_SMOKE_0001/dataset/` (splits)
- `runs/RUN_SAMPLE_SMOKE_0001/reports/summary.md`
- `runs/RUN_SAMPLE_SMOKE_0001/manifest.json`

Note: In this build environment, Parquet engines were not available, so the run is stored as CSV.
When `pyarrow` is installed (declared in `pyproject.toml`), the pipeline prefers Parquet.

Historical note: As of D-0005, Parquet became mandatory (fail-closed). Legacy conversion remains available via `detectlab dataset parquetify`.

### 9) Docs updates
Updated:
- `docs/getting_started.md` to include the sample run command
- `docs/pipeline_overview.md` to reflect that dataset splits are now present

## Verification performed (in this environment)
- `python -m pytest -q` (passes)
- `PYTHONPATH=src python -m inkswarm_detectlab.cli run skynet configs/skynet_smoke.yaml` (produces `runs/RUN_SAMPLE_SMOKE_0001`)

## Notes / trade-offs
- Parquet is the preferred format, but CSV fallback is used automatically when Parquet engines are missing.
- Split boundaries are computed and reported in BA local time for interpretability.
- Shared holdout across multiple event tables is deferred (can be introduced via CC later).

## Next
Proceed to D-0003 (first modeling baseline / sklearn MVP scaffolding) once CP ceremony triggers.
