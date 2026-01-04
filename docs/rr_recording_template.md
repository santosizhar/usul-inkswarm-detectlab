# RR Recording — Example (RR-0001)

This page is an **example RR record** you can copy/paste into a journal entry.

- Target: Windows + Python 3.12 (recommended)
- Goal: run the pipeline **twice** and compare determinism signatures

---

## Example record (validated)

**Date:** 2025-12-20  
**Status:** PASS (local)

### Commands run (A)
```bash
detectlab run skynet -c configs/skynet_smoke.yaml --run-id RUN_XXX_0005_A --force
detectlab features build -c configs/skynet_smoke.yaml --run-id RUN_XXX_0005_A --event all --force
detectlab baselines run -c configs/skynet_smoke.yaml --run-id RUN_XXX_0005_A --force
```

### Commands run (B)
```bash
detectlab run skynet -c configs/skynet_smoke.yaml --run-id RUN_XXX_0005_B --force
detectlab features build -c configs/skynet_smoke.yaml --run-id RUN_XXX_0005_B --event all --force
detectlab baselines run -c configs/skynet_smoke.yaml --run-id RUN_XXX_0005_B --force
```

### Evidence captured
- `runs/RUN_XXX_0005_A/manifest.json`
- `runs/RUN_XXX_0005_B/manifest.json`

Optional: run RR helper scripts:
- Windows: `./scripts/rr_mvp.ps1 -Config "configs/skynet_smoke.yaml" -RunId "RUN_XXX_0005"`
- macOS/Linux: `./scripts/rr_mvp.sh`

### Determinism check
Compare the run signatures (normalized) produced by the RR scripts, or compare the per-stage hashes in the run manifests.
