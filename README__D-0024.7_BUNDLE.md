# D-0024.7 — RR Patch: Baselines + Eval + Export crash fixes

## Fixes
- Baselines: ensure `model_path` is always defined before writing metrics.
- Eval: ensure `meta` is initialized early (prevents NameError on partial paths).
- Export: call `write_exec_summary(..., run_dir=...)` (no unexpected `run_id` kwarg).

## How to apply
Unzip over your repo, restart Jupyter kernel, rerun notebook from top.
