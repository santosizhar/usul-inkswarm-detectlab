# D-0024.1 — Pre-RR Patch: Step Runner Reliability + Clean Packaging

This patch is a **targeted fix** on top of **D-0024** to remove pre-RR footguns.

## What changed

### 1) Fix runtime NameError in notebook step runner
- `src/inkswarm_detectlab/ui/step_runner.py`
  - Added a small stdlib-only JSON reader helper: `_read_json(...)`
  - Replaced the previous (undefined) `read_json(...)` calls

Impact: re-run/reuse paths for baseline/eval steps will no longer crash when parsing existing metrics.

### 2) Preserve recorded step history when regenerating raw tables
- `src/inkswarm_detectlab/pipeline.py`
  - `generate_raw(...)` now **preserves** `manifest["steps"]` if an existing manifest is present for the same `run_id`.

Impact: if step 1 is forced/re-run for an existing run directory, later step records are not wiped.

### 3) Stop shipping generated Python bytecode in deliverable zips
- Removed `__pycache__/` and `*.pyc` from the repo snapshot before packaging
- Added helper: `tools/clean_generated_files.py` to clean these artifacts before future zips.

## Validation (performed here)
- `python -m compileall -q src`
- Import check: `from inkswarm_detectlab.ui import step_runner`

## Notes
- No architecture changes; only minimal reliability fixes + packaging hygiene.
