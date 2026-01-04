# Playground Guide

This page is the **fastest path** from “fresh checkout” to “I see useful outputs” — optimized for a *final user playground* experience.

## The 2 playground surfaces

### 1) CLI (recommended)
The canonical entrypoint is the Typer CLI:

- `detectlab --help`
- `detectlab run --help`
- **Fastest first run:** `detectlab run quick` (defaults to `configs/skynet_smoke.yaml`)

The MVP run is the main “demo pipeline” surface.

### 2) Notebooks (optional)
If you prefer notebooks, start with:
- `notebooks/00_step_runner.ipynb` (one-click top-to-bottom)

## Quick workflows

### A) Fast smoke run (small + visible)
Use the smoke config:
- `configs/skynet_smoke.yaml`

Expect:
- a run directory under `runs/<run_id>/...`
- raw tables (`raw/...`), dataset splits (`dataset/...`), features (`features/...`)
- a `manifest.json` describing artifacts
- a human-readable report under `reports/` (if enabled by the config)

> Note: Parquet is mandatory (install a parquet engine, e.g. `pyarrow`).

### B) MVP run (default experience)
Use:
- `configs/skynet_mvp.yaml` (balanced)
- `configs/skynet_mvp_heavy.yaml` (heavier / slower)

### C) CI-shaped run (minimal, deterministic)
The CI config uses:
- `configs/skynet_ci.yaml`

This writes into `runs_ci/` by default (ignored by git). A tiny historical fixture lives under `examples/fixtures/runs_ci/` for reference.

## Incrementalism + caching
DetectLab is designed for staged, incremental workflows:

- Run steps individually (select → hydrate → normalize → score/eval)
- Reuse prior artifacts safely when the config has not materially changed
- Use the feature cache (`_cache/`) to avoid re-computing expensive feature builds

See also:
- `docs/runbook.md` (commands + expected outputs)
- `docs/pipeline_overview.md` (artifact layout)

## “Quality” as a first-class output
Beyond “it runs”, the best playground experience includes a **single quality scorecard**:

- Dataset quality (label prevalence, sanity checks, leakage checks)
- Feature quality (missingness, stability)
- Model/baseline quality (headline metrics + stability)

RC-0001 recommends adding a compact “quality report” entrypoint (CLI + docs) so users can judge outputs at a glance.
