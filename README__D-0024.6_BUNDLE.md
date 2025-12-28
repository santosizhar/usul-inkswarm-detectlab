# D-0024.6 — RR Consolidated Patches + Baselines model_path fix

This bundle consolidates the RR unblock patches found during pre-RR execution:

## Fixes included
1) `ui.step_runner.resolve_run_id` and `wire_check`:
   - Accept either `Path` or already-loaded `cfg`
   - No longer reference non-existent `cfg.run.run_id_strategy`
   - Robust config path fallback relative to repo root

2) `ui.notebook_tools.find_run_dir`:
   - Works whether `root` is project root or `runs_dir`

3) `models.runner.run_login_baselines_for_run`:
   - Fix NameError: define `model_path` (prefers v2 layout `<baselines>/<model>/<label>.joblib`)

4) `notebooks/00_step_runner.ipynb`:
   - Robust `CFG_PATH` resolution regardless of CWD
   - Label sanity check uses `Path(cfg.paths.runs_dir) / run_id`

## Validation
- `python -m compileall -q src` (in this environment)
