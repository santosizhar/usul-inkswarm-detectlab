# Notebooks

## Important: run from the repo root

The notebooks use relative paths like `configs/...` and `runs/...`.

To avoid `FileNotFoundError`, **start Jupyter from the repo root** (the folder that contains `pyproject.toml`), or rely on the first notebook cell that auto-detects the repo root and `chdir`s there.

The notebooks are **optional**. They are meant for:
- quick inspection of outputs (`runs/<run_id>/...`),
- interactive exploration for portfolio reviewers,
- sanity checks when iterating on features / baselines.

They do **not** replace the canonical CLI pipeline.

---

## Prerequisites

1) Run the CLI pipeline first (see `docs/runbook.md`). You should have a run folder like:
- `runs/RUN_XXX_0005/raw/...`
- `runs/RUN_XXX_0005/features/...`
- `runs/RUN_XXX_0005/models/...`
- `runs/RUN_XXX_0005/reports/summary.md`

2) Install notebook dependencies (recommended):

```bash
pip install jupyter
```

---

## How to run

From the repo root:

```bash
jupyter notebook
```

Open the notebook you want from `notebooks/`.

### Notebook conventions

Most notebooks either:
- read `cfg.run.run_id` from the YAML config, or
- fall back to a default string.

If you used a different run id than `RUN_XXX_0005`, set the `run_id` variable in the notebook cells to match your folder under `runs/`.

---

## What each notebook does

- `notebooks/00_schema_preview.ipynb`  
  Lists schemas and column contracts (quick tour of tables).

- `notebooks/01_placeholder_data_inspection.ipynb`  
  Reads a chosen `run_id` (set in the first cells) and displays sample rows.

Tip: generate a tiny run with `detectlab run quick` first, then point the notebook at that run folder.

- `notebooks/02_featurelab_login_attempt.ipynb`  
  Re-runs the FeatureLab builder for `login_attempt` (idempotent if outputs exist) and displays the resulting feature table.

- `notebooks/03_baselinelab_login_attempt.ipynb`  
  Runs login baselines for the selected run and prints the start of the markdown report.

---

## Expected outputs (when things work)

- Feature notebook: prints a dataframe `head()` and the feature table exists at:
  - `runs/<run_id>/features/login_attempt/features.parquet`

- Baseline notebook: prints a path and a snippet of:
  - `runs/<run_id>/models/login_attempt/baselines/report.md`
## Step Runner notebook (D-0022)

**Notebook:** `notebooks/00_step_runner.ipynb`

Purpose: run the pipeline **step-by-step** for `login_attempt` while keeping the core code structure intact.
It is intentionally a thin wrapper over existing modules (pipeline/features/models/eval/ui/share).

What you get:
- a top-of-notebook step list / TOC
- per-step toggles (run / skip / force)
- per-step prints: inputs, output paths, quick summaries, and what to run next
- shared feature-cache reuse where available
- an end-of-notebook step table via `StepRecorder`

Recommended workflow:
1. Start with `configs/skynet_smoke.yaml` for a tiny end-to-end run.
2. Switch to `configs/skynet_mvp.yaml` when ready.
3. For deep dives, open:
   - `notebooks/02_featurelab_login_attempt.ipynb`
   - `notebooks/03_baselinelab_login_attempt.ipynb`


## D-0023: StepResult contract

`notebooks/00_step_runner.ipynb` uses `inkswarm_detectlab.ui.step_runner` step wrappers which return a typed `StepResult` and persist the latest per-step result to `runs/<run_id>/manifest.json` under `steps`.


## D-0024: Manifest-first reuse policy

The step notebook uses `inkswarm_detectlab.ui.reuse_policy.decide_reuse` to decide reuse vs compute, preferring a matching `config_hash` in `manifest.json` step records when available.
