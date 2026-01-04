# D-0024 — Manifest-first reuse policy

Builds on D-0023 by centralizing reuse decisions for step execution.

## Why
We want minimal wasted time in notebooks:
- avoid retraining/recomputing when artifacts already exist
- reuse should be consistent and explainable

## Key changes
- New: `src/inkswarm_detectlab/ui/reuse_policy.py`
  - `decide_reuse(...)` uses the run manifest first (step fingerprint + outputs present)
  - falls back to disk existence checks if the manifest is missing/incomplete

- Updated: `src/inkswarm_detectlab/ui/step_runner.py`
  - step wrappers now defer reuse logic to `decide_reuse(...)`
  - step-specific checks remain (e.g., baselines still require at least one `.joblib`)

- Updated: `notebooks/00_step_runner.ipynb`
  - prints reuse decision metadata (used_manifest, forced)

## Validation
- `python -m compileall -q src`
- `python -c "from inkswarm_detectlab.ui.reuse_policy import decide_reuse; from inkswarm_detectlab.ui.step_runner import step_features; print('IMPORT_OK')"`
