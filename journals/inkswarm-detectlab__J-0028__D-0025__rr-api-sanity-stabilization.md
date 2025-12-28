# J-0028 — D-0025 — RR API Stabilization + Sanity Command

## Context
After RR2 step-notebook hardening (D-0024.x), remaining friction was caused by:
- Notebook calling `step_features(..., use_shared_feature_cache=..., write_shared_feature_cache=...)` while `step_features` expected different arg names.
- Baselines reruns raising `FileExistsError` even when reuse was intended.
- Need for a single, fail-closed “quick validation” command before/after patches.

## What changed (D-0025)
1. **Notebook-facing API stabilization**
   - `ui.step_runner.step_features` now supports the canonical args:
     - `use_shared_feature_cache`
     - `write_shared_feature_cache`
   - Compatibility shims kept for older arg names (`use_cache`, `write_cache`, etc.).

2. **Baselines idempotency guardrail**
   - `models.runner.run_login_baselines_for_run` returns existing `metrics.json` when baselines already exist and `--force` is not used.
   - If the folder exists but is incomplete (no `metrics.json`), it still fails closed.

3. **CLI: `detectlab sanity`**
   - Adds a fast, fail-closed compile + import check.
   - Optional `--tiny-run` executes a small end-to-end run via the step-runner to validate wiring + artifacts.

4. **Notebook refresh**
   - Updated `notebooks/00_step_runner.ipynb` to match the stabilized API and current signatures.

## How to validate
```bash
# compile + imports only
detectlab sanity --no-tiny-run

# tiny end-to-end (writes under runs/)
detectlab sanity -c configs/skynet_smoke.yaml --run-id SANITY_SMOKE_0001 --force
```

## Notes
- No behavioral change intended for the training/eval logic itself—this is primarily stability + ergonomics for RR workflows.
