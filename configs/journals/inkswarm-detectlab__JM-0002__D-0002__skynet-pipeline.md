# D-0002 — SKYNET pipeline + splits — Mini Journal (JM-0002)

Date: 2025-12-16  
NS: inkswarm-detectlab

## What you got
- End-to-end **SKYNET v1** synthetic pipeline for:
  - `login_attempt` (primary; multi-label subtypes)
  - `checkout_attempt` (present; ~0.5% adverse; fraud disabled until SPACING GUILD)
- Leakage-aware datasets:
  - **15% by-user holdout** (uniform, seeded)
  - **85/15 time split** for remaining users
- Deterministic **content hashes** for artifacts (canonical sort + stable hash)
- Run outputs under `runs/<run_id>/` with `manifest.json` + `reports/summary.md`
- Two configs shipped: `configs/skynet_mvp.yaml`, `configs/skynet_smoke.yaml`
- A committed fixture run: `runs/RUN_SAMPLE_SMOKE_0001/…`

## How to run
Smoke run (creates/overwrites the pinned run id from config):
- `uv run detectlab run skynet configs/skynet_smoke.yaml`

MVP run (auto-generates a run_id unless you pass one):
- `uv run detectlab run skynet configs/skynet_mvp.yaml`

## Key files
- Generator: `src/inkswarm_detectlab/synthetic/skynet.py`
- Dataset split: `src/inkswarm_detectlab/dataset/build.py`
- Orchestration + manifest/summary: `src/inkswarm_detectlab/pipeline.py`
- CLI: `src/inkswarm_detectlab/cli.py`
- Tests: `tests/test_d0002_skynet.py`

## Notes
- Preferred artifact format is **Parquet**; if the environment lacks a Parquet engine, the pipeline falls back to **CSV** automatically (paths + manifest reflect the actual format).
- Split boundary is computed/reporting in **America/Argentina/Buenos_Aires**.
