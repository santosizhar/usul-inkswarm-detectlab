# Notebooks

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
  Reads the placeholder run id from `inkswarm_detectlab.utils.run_id.PLACEHOLDER_RUN_ID` and displays sample rows.  
  If you want to inspect a real run, replace the `run_dir` assignment to point to your run folder.

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
