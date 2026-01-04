# J-0028 — D-0024.5 — RR patch: find_run_dir double-runs issue

## Symptom
Notebook label sanity-check crashed with:
- `Run dir not found: runs\runs\RR2_MVP_GIT_B_0002`

## Root cause
`ui/notebook_tools.find_run_dir(root, run_id)` hard-coded `<root>/runs/<run_id>`.
But notebook passes `cfg.paths.runs_dir` which is already `runs`, producing `runs/runs/<run_id>`.

## Fix
`find_run_dir` now tries both:
- `<root>/<run_id>` (root is runs_dir)
- `<root>/runs/<run_id>` (root is project root)

and raises a clearer error listing candidates if neither exists.

## RR impact
Unblocks step notebook execution beyond Step 1 for existing run_ids.
