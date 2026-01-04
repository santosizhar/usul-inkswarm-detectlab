# D-0024.5 — RR patch: find_run_dir robustness

## Why
During RR, the step notebook crashed at label sanity-check step:

`FileNotFoundError: Run dir not found: runs\runs\<RUN_ID>`

This happened because `find_run_dir(root, run_id)` assumed `root` is the project root and always appended `"runs"`,
but in practice notebooks pass `cfg.paths.runs_dir` (which is already `"runs"`).

## What changed
- `src/inkswarm_detectlab/ui/notebook_tools.py`
  - `find_run_dir(...)` now accepts either:
    - project root -> `<root>/runs/<run_id>`
    - runs dir itself -> `<root>/<run_id>`
  - tries both candidates and raises a more informative error.

## Validation
- Import-time safe (stdlib only).
- This patch is exercised by the step notebook label sanity-check cell.

