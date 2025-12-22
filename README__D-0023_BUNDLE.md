# D-0023 — Step Contract Hardening

This bundle introduces a typed **StepResult** contract for notebook/CLI step execution.

## Why
The D-0022 step notebook needed clearer, structured visibility:
- what inputs were used
- what artifacts were produced
- whether the step reused existing outputs or recomputed them

## Key changes
- New: `src/inkswarm_detectlab/ui/step_contract.py`
  - `StepResult`, `StepInputs`, `ReuseDecision`, `ArtifactRef`
  - `record_step_result(...)` writes the latest step result per step into `runs/<run_id>/manifest.json` under `steps`

- Updated: `src/inkswarm_detectlab/ui/step_runner.py`
  - step wrappers now return `StepResult`
  - each wrapper persists its result to the manifest for later inspection
  - outputs now include existence flags for quick sanity checks

- Updated: `notebooks/00_step_runner.ipynb`
  - prints decision and output existence per step
  - passes `CFG_PATH` into step wrappers

## Validation
- `python -m compileall -q src`
- `python -c "from inkswarm_detectlab.ui.step_contract import StepResult; from inkswarm_detectlab.ui.step_runner import step_dataset; print('IMPORT_OK')"`
