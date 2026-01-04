# J-0025 — D-0022 — Step Notebook Solution (pipeline step-by-step)

## Goal (locked)
Provide a notebook UX that allows a user to execute the pipeline **step-by-step** while:
- keeping the code structure intact (thin wrappers, no rewrite)
- providing clear step visibility (what ran, what was produced, what's next)
- minimizing wasted time (reuse artifacts and shared cache when available)

## What shipped
### 1) New orchestrator notebook
- `notebooks/00_step_runner.ipynb`
  - Top-of-notebook step list + toggles (run/skip/force)
  - Runs the 5 major steps:
    1) raw + dataset
    2) features (with shared cache restore/write)
    3) baselines
    4) eval (slice + stability)
    5) export (summary + UI bundle + handover + evidence)
  - Surfaces label logic + sanity checks (label definitions + prevalence)
  - Prints a step table at the end via `StepRecorder`

### 2) Thin step wrappers (notebook API)
- `src/inkswarm_detectlab/ui/step_runner.py`
  - `resolve_run_id(...)` and `wire_check(...)` (dry-run wiring check)
  - `step_dataset(...)`, `step_features(...)`, `step_baselines(...)`, `step_eval(...)`, `step_export(...)`
  - Reuse-first logic is **explicitly controlled** by notebook toggles (BQ2=C)
  - Shared feature cache is used (restore/write) without changing the underlying pipeline modules

### 3) Docs updates
- `docs/notebooks.md` updated with a section describing the new step runner notebook.

## Design notes
- The notebook intentionally calls existing modules (`pipeline`, `features.runner`, `models.runner`, `eval.runner`, `ui.bundle`, `share.evidence`).
- Step wrappers return a small, typed outcome (`StepOutcome`) so notebook cells can print consistent “inputs/outputs/next”.
- Recompute avoidance is achieved via:
  - artifact existence checks
  - shared feature cache restore for features
  - reuse toggles to allow manual control without hidden state

## Follow-ups (optional)
- Add an equivalent step runner for `checkout_attempt` once the `checkout` pipeline is upgraded to feature/baseline parity.
- Consider adding a config-fingerprint stamp per step for stricter mismatch detection (kept out of D-0022 to avoid redesign).
