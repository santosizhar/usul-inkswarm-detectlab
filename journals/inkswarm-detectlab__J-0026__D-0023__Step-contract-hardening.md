# J-0026 — D-0023 — Step contract hardening

Date: 2025-12-22

## Goal
Introduce a typed, reusable **StepResult** contract so notebook/CLI step execution can:
- consistently report **inputs**, **outputs**, and **reuse vs compute** decisions
- persist step outcomes into the run manifest for later inspection
- remain thin wrappers (no architectural rewrite)

## What changed
- Added `src/inkswarm_detectlab/ui/step_contract.py`
  - `StepResult`, `StepInputs`, `ReuseDecision`, `ArtifactRef`
  - `record_step_result(run_dir, step)` persists latest result per step under `manifest["steps"]`

- Updated `src/inkswarm_detectlab/ui/step_runner.py`
  - step functions now return `StepResult` (instead of the previous minimal `StepOutcome`)
  - each step writes its latest result into the manifest
  - notebook calls pass `cfg_path` to improve traceability of inputs

- Updated `notebooks/00_step_runner.ipynb`
  - `_print_outcome` prints decision + artifact existence checks

## Notes
- Reuse decisions are still primarily **disk-existence based** for now.
- D-0024 will centralize reuse policy using the manifest + fingerprints.
