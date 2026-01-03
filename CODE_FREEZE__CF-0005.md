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

---

## Status addendum (Maintainer audit 2026-01-02)

### Current status
- CLI surface and smoke configs remain consistent with the CF-0005 anchor; deterministic run ids and manifest-first policies are intact.
- Evidence/share packaging and report stitching continue to rely on the canonical `runs/<run_id>/` layout and pass existing smoke expectations.
- Documentation points to the CF-0005 freeze, with runbook/repo map still aligned to the runtime surface.

### Strengths
- Deterministic data flow with manifest preservation and cache pruning safeguards to avoid stale artifacts.
- Rich ceremony and runbook docs make entrypoints discoverable for both operators and reviewers.
- Tests cover critical surfaces (CLI flags, schema validation, cache operations, share packaging) enabling safe refactors.

### Weaknesses / risks
- Test suite is still unit-heavy; no automated end-to-end execution of the full MVP path in CI.
- Share/report rendering relies on custom Markdown/HTML glue with minimal fuzz tests, making regressions possible if formats drift.
- Multiple README bundles and ceremony files risk drifting without a single authoritative index.

### Next 5 high-leverage actions
1. Add a lightweight automated smoke run (Skynet config) in CI to exercise the full CLI pipeline on every freeze branch.
2. Backfill small tests for the Markdown → HTML/report glue (safe I/O helpers, exec summary stitching) to catch malformed artifacts early.
3. Consolidate README bundles into a concise “latest” pointer with dated changelog to reduce ceremony drift.
4. Document cache eviction/size expectations in the runbook and enforce defaults via config validation.
5. Expand release readiness evidence to include Windows/Python 3.12 runs for the deferred D-0004 validation gap.

## Status addendum (Maintainer audit 2026-01-03)

### Current status
- Safe I/O helpers now have direct callsites in reporting and cache modules plus focused unit tests, reducing drift risk.
- Audit coverage clarified in REVIEW_REPORT to capture remaining weak spots (end-to-end CI gap, HTML glue coverage).

### Strengths
- Shared helpers and tests lower the chance of silent failure when report artifacts are missing or malformed.
- Existing ceremony docs continue to point at CF-0005 with aligned runbook guidance.

### Weaknesses / risks
- Notebook/UI helpers and tool scripts still carry bespoke JSON readers; they should be consolidated with `safe_io` once behavior expectations are documented.
- Full pipeline smoke coverage in CI remains absent; current unit tests won’t catch integration regressions.

### Next 3 high-leverage actions
1. Replace bespoke JSON reads in UI and tooling modules with `safe_io` (or documented strict variants) to keep behavior uniform.
2. Add a CI smoke job that executes the default config end-to-end to exercise report generation and share packaging.
3. Backfill tests around HTML/Markdown stitching to detect malformed report sections early.

## Status addendum (Maintainer audit 2026-01-04)

### Current status
- Notebook/UI helpers now rely on the shared `safe_io` reader to avoid silent divergence from the reporting/cache behaviors.
- Targeted unit coverage exercises the UI JSON reader shim to ensure missing/invalid files do not crash notebook flows.

### Strengths
- Consolidated JSON reads reduce drift and make it easier to harden additional UI/tooling surfaces.
- New unit cases for the UI reader helpers guard the expected best-effort behavior.

### Weaknesses / risks
- Tools that assert fail-closed behavior (e.g., RR evidence scripts) still use strict JSON loads; they may need explicit error messaging or best-effort variants depending on future requirements.
- End-to-end smoke coverage and HTML glue tests are still missing, keeping integration risk elevated.

### Next 3 high-leverage actions
1. Decide which RR/tooling surfaces should adopt `safe_io` vs. fail-closed JSON loading and document the policy.
2. Add a minimal CI smoke to exercise the UI summary generation path alongside core pipeline steps.
3. Extend coverage to the Markdown/HTML stitching functions before expanding report formats.

## Status addendum (Maintainer audit 2026-01-05)

### Current status
- RR evidence + signature tools now read JSON via a shared strict helper to surface actionable errors when required artifacts are missing or malformed.
- JSON I/O policy is documented in the runbook, clarifying when to use best-effort vs. fail-closed helpers across the repo.

### Strengths
- Centralized strict reader reduces drift and provides consistent failure messages for determinism tooling.
- Operators have clearer guidance on which helper to use when extending pipelines or UI surfaces.

### Weaknesses / risks
- End-to-end smoke coverage in CI is still absent; strict helper adoption does not validate cross-step integration.
- HTML/Markdown stitching remains lightly tested; malformed artifacts could still slip through report generation.

### Next 3 high-leverage actions
1. Add a CI smoke job that exercises the MVP run and RR tooling to validate strict JSON handling in context.
2. Backfill tests for report/HTML stitching to catch malformed content before release packaging.
3. Extend the strict reader to additional tooling surfaces (if/when they prove to be fail-closed) to keep diagnostics uniform.
