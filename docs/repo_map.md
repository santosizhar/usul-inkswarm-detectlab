# Repo Map (High Signal)

This is a curated map of the repo for portfolio/code-review readers.

---

## Top-level

- `src/inkswarm_detectlab/` — application code
- `configs/` — YAML configs (smoke/MVP/CI)
- `docs/` — MkDocs documentation
- `scripts/` — helper scripts (RR, make_share_zip, etc.)
- `tests/` — pytest unit tests
- `notebooks/` — Jupyter notebooks (optional exploration)
- `runs/` / `runs_ci/` — **local outputs** (ignored; not source-controlled)
- `examples/fixtures/runs_ci/` — small committed fixture used for documentation/examples

---

## Core runtime surface

### CLI
- `src/inkswarm_detectlab/cli.py`
  - Typer command tree: `detectlab ...`

### Config
- `src/inkswarm_detectlab/config/`
  - Pydantic models + YAML loader

### Synthetic data (Skynet)
- `src/inkswarm_detectlab/synthetic/skynet.py`
  - Generates `login_attempt` and `checkout_attempt` event tables

### Dataset builder
- `src/inkswarm_detectlab/dataset/`
  - Leakage-aware splits:
    - `user_holdout` (primary truth)
    - `time_eval` (drift check)

### FeatureLab
- `src/inkswarm_detectlab/features/`
  - Safe aggregate features over time windows

### BaselineLab
- `src/inkswarm_detectlab/models/`
  - Baseline models (logreg + RF) + metrics + report
  - HGB worker (subprocess) for crash isolation

### EvalLab
- `src/inkswarm_detectlab/eval/`
  - Slice metrics + threshold stability diagnostics

### Reporting
- `src/inkswarm_detectlab/reports/`
  - `summary.md` generator
  - optional HTML renders + EXEC_SUMMARY

### UI bundle + Share package
- `src/inkswarm_detectlab/ui/`
  - Static HTML viewer (index.html + app.js + style.css)
- `src/inkswarm_detectlab/share/evidence.py`
  - Packages `share/` folder and writes `evidence_manifest.json`

---

## End-to-end flow (conceptual)

```text
configs/*.yaml + run_id
    |
    v
Skynet -> runs/<run_id>/raw/*.parquet
    |
    v
Dataset -> runs/<run_id>/dataset/<event>/{train,user_holdout,time_eval}.parquet
    |
    v
Features -> runs/<run_id>/features/<event>/*.parquet
    |
    v
Baselines -> runs/<run_id>/models/<event>/baselines/{metrics.json,report.md}
    |
    v
Eval/Reports -> runs/<run_id>/reports/*
    |
    v
UI bundle -> runs/<run_id>/share/ui_bundle/index.html
Evidence bundle -> runs/<run_id>/share/{reports,logs,meta,evidence_manifest.json}
```
