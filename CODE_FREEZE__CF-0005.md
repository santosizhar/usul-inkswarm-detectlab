# CODE_FREEZE__CF-0005.md

**Project:** Inkswarm DetectLab  
**NS:** inkswarm-detectlab  
**Freeze ID:** CF-0005  
**Date:** 2025-12-20  
**Type:** Verified run + docs stabilization + evidence bundling fix (fail-closed)

---

## What this freeze is

This freeze is a **release-quality anchor** for the state of the repo after:

- a successful end-to-end local run using run id `RUN_XXX_0005`,
- a docs sweep to remove “pending/placeholder” friction,
- a fix to evidence bundle export so MVP share artifacts can be packaged and hashed deterministically,
- CI hardening (`compileall` step), and
- repo structure cleanup (removal of accidental duplicate tree under `configs/`).

This freeze is meant to be used as the **default restart anchor**.

---

## Verified runtime surface

### Canonical CLI run (smoke)

```bash
detectlab run skynet -c configs/skynet_smoke.yaml --run-id RUN_XXX_0005 --force
detectlab features build -c configs/skynet_smoke.yaml --run-id RUN_XXX_0005 --event all --force
detectlab baselines run -c configs/skynet_smoke.yaml --run-id RUN_XXX_0005 --force
```

**Expected output**
- `runs/RUN_XXX_0005/reports/summary.md`
- `runs/RUN_XXX_0005/share/` (after share export / zip step)

### Share bundle (stakeholder artifact)

Use the scripts in `scripts/`:

- Windows:
  - `./scripts/make_share_zip.ps1 -RunId "RUN_XXX_0005"`

- macOS/Linux:
  - `./scripts/make_share_zip.sh "RUN_XXX_0005"`

Expected output:
- `MVP_SEND_20251220_01__share.zip` (or similar) in the repo root (or configured output dir)
- includes `runs/RUN_XXX_0005/share/` and a generated `evidence_manifest.json`

---

## Read-first “truth sources” for restart

1) `README.md`
2) `docs/runbook.md`
3) `docs/repo_map.md`
4) `docs/notebooks.md`
5) `docs/release_readiness_mvp.md`
6) `CODE_REVIEW__CR-0004.md` (historical)
7) This file: `CODE_FREEZE__CF-0005.md`

---

## Known constraints (still true)

- Parquet is mandatory for the pipeline write path (install `pyarrow`).
- The pipeline is designed for local reproducibility, not distributed training.
- D-0004 deferred validation remains documented in `DEFERRED_VALIDATION__D-0004.md` (explicitly out of scope here).

---

## Exit criteria (what “frozen” means)

- `python -m compileall src` passes
- `pytest -q` passes
- Smoke CLI run produces expected outputs
- Evidence bundle export produces a zip with a manifest and stable hashes
- Runbook + notebooks docs match the current runtime surface
