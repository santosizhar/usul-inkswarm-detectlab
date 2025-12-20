# inkswarm-detectlab__JM-0022__CF-0005__verified-run-and-docs-stabilization.md

**Date:** 2025-12-20  
**Freeze:** CF-0005  
**Verified run:** `RUN_XXX_0005`

## What happened

- Ran the canonical smoke pipeline end-to-end with `RUN_XXX_0005` and confirmed expected artifacts.
- Curated docs to remove “pending / placeholder” friction and aligned instructions with the real runtime surface.
- Added canonical pages:
  - `docs/runbook.md` (includes git commands)
  - `docs/repo_map.md`
  - `docs/notebooks.md`
- Stabilized RR doc language (removed non-existent “doctor” command references).
- Ensured evidence bundle export is syntactically correct and produces a deterministic manifest.
- Cleaned accidental duplicate repo tree under `configs/`.
- Hardened CI by adding `python -m compileall src`.

## Evidence

- Successful outputs under: `runs/RUN_XXX_0005/...`
- Smoke commands: see `docs/runbook.md`
- Manual checklist: `MANUAL_RUNS_AND_CHECKS.md`
- Freeze anchor: `CODE_FREEZE__CF-0005.md`
