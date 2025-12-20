# Inkswarm DetectLab — MVP Stakeholder One-Pager (D-0014)

## What this is
This zip is a shareable “evidence bundle” from the DetectLab MVP run. It contains a static web page and summary reports intended for non-technical review.

## How to open it
1) Unzip the file
2) Open: `share/ui_bundle/index.html`

## What you’ll see (3-minute guide)

### 1) Headline results (primary truth)
The headline metrics are reported on **`user_holdout`**:
- This is the “generalization” check (the most important split).

### 2) Drift check (secondary truth)
A second set of metrics is reported on **`time_eval`**:
- This is a “drift monitor” to detect time-based degradation.

### 3) Slice and stability diagnostics
The bundle includes:
- **slice reports** (performance across segments)
- **stability checks** (variance/instability warnings)

## What to trust / what to treat carefully

### Trust
- The bundle is self-contained and reproducible in principle.
- A “run signature” (config hash, and optionally code hash) is included for traceability.

### Treat carefully (if noted)
- If reproducibility (RR) is marked **PROVISIONAL**, determinism has not yet been proven on the target Windows/Python environment.
- D-0004 validation remains deferred; see `DEFERRED_VALIDATION__D-0004.md`.

## What to do with it
- Use `user_holdout` to judge whether the model generalizes.
- Use `time_eval` to understand drift exposure.
- Use slice/stability to decide where it is safe/unsafe and what mitigations are needed.

## Glossary (minimal)
- **user_holdout:** a holdout split at user level; primary “truth”.
- **time_eval:** a time-based split; drift check.
- **baseline:** a standard model used as a reference point (MVP uses simple baselines).
- **run signature:** identifiers (hashes) to uniquely reference the run configuration and code state.


---

## Validated run example

This procedure was validated end-to-end with run id `RUN_XXX_0005` on 2025-12-20.
