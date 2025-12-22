# J-0027 — D-0024 — Manifest-first reuse policy

Date: 2025-12-22

## Goal
Centralize step-level reuse logic so the step notebook can avoid recompute with minimal wasted time.

Key intent:
- prefer **manifest-driven** reuse decisions (fingerprint + expected outputs present)
- fall back to disk existence when manifest is missing/incomplete
- keep per-step toggles (BQ2=C) as the user-facing override

## What changed
- Added `src/inkswarm_detectlab/ui/reuse_policy.py`
  - `decide_reuse(...)` implements a manifest-first policy using:
    - `manifest["steps"][step_name].inputs.config_hash`
    - expected output presence

- Updated `src/inkswarm_detectlab/ui/step_runner.py`
  - all notebook step wrappers call `decide_reuse(...)`
  - wrappers still preserve step-specific safety checks where needed
    (e.g., baselines require metrics.json AND at least one .joblib)

- Updated `notebooks/00_step_runner.ipynb`
  - prints decision metadata (used_manifest / forced)

## Notes
- This is intentionally conservative: we do not attempt content-hash validation of artifacts.
- If artifacts exist but fingerprints differ, reuse still occurs when `REUSE_IF_EXISTS=True` (manual override) but the decision reason warns about the mismatch.
