# D-0022 — Step Notebook Runner (pipeline step-by-step)

This bundle iterates on the **step notebook** solution so a user can execute the pipeline
**step-by-step** via a notebook, while maintaining the existing code structure.

## What changed (changelog-style)

### Added
- `notebooks/00_step_runner.ipynb`
  - End-to-end **step runner** for `login_attempt`
  - Per-step toggles (run/skip/force) and explicit reuse control
  - Step visibility: outputs/paths, log tails, and final StepRecorder table

- `src/inkswarm_detectlab/ui/step_runner.py`
  - Thin notebook wrappers around existing modules:
    - dataset → features → baselines → eval → export
  - Includes a **dry-run wiring check** (`wire_check`) and run_id resolution (`resolve_run_id`)

### Updated
- `docs/notebooks.md`
  - Added usage notes for the new step runner notebook.

## How to use
1. Start from repo root.
2. Open `notebooks/00_step_runner.ipynb`.
3. Default config is `configs/skynet_smoke.yaml` (tiny run).
4. Switch to `configs/skynet_mvp.yaml` for a fuller run.
5. Use the per-step toggles to control reuse vs recompute.

## Validation performed (in this bundle)
- `python -m compileall -q src`
- Import check: `from inkswarm_detectlab.ui.step_runner import wire_check, step_dataset, step_features, step_baselines, step_eval, step_export`
