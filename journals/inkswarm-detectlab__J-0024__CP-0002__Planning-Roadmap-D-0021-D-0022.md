# Inkswarm DetectLab — CP-0002 Planning

Deliverables planned: **D-0021** and **D-0022**

Date: 2025-12-22 (America/Argentina/Buenos_Aires)

## Why this planning session

We observed that the MVP pipeline works end-to-end, but:

- Notebook iteration feels opaque (hard to see what step is running / where artifacts are).
- Baseline training can be slower than needed for quick exploration.
- Readers need clearer context on how the **synthetic dataset** and **labels** are generated so they can interpret reports.

This CP scopes D-0021/D-0022 and re-checks the remaining roadmap against the end goals.

---

## D-0021 — Scope (locked)

**Theme:** Make iteration transparent + faster while improving interpretation of results.

### 1) Notebook step visibility
- Add lightweight step logging helpers usable from notebooks.
- Provide notebook cells to locate a run folder, print key artifact paths, and tail logs.
- Update baseline notebook instructions so the documented model set matches the code.

### 2) Faster baseline training (config-only)
- Add a `preset: fast` option for `baselines.login_attempt`.
- In `fast` mode, clamp expensive hyperparameters (e.g., RF trees/depth) while preserving:
  - dataset generation
  - splits
  - metrics and thresholding logic
- Ensure reports record the chosen preset and the effective hyperparameters.

### 3) Dataset + label semantics surfaced in reporting
- Add a single source of truth for label definitions.
- Add a short “synthetic dataset and labels” doc.
- Update baseline report(s) to include:
  - label definitions
  - the fact that labels are deterministic given a seed
  - the fact that labels represent *synthetic scenarios*, not real attacker ground truth

### Acceptance criteria
- `python -m compileall -q src` passes.
- Import smoke: `from inkswarm_detectlab.models.runner import run_login_baselines_for_run`.
- Shipped notebooks include an easy way to find artifacts and tail logs.
- Baseline report contains the new sections.

---

## D-0022 — Proposed scope (planning)

**Theme:** Increase product realism + usefulness of analysis outputs.

### A) Data realism + reproducibility
- Add a “scenario manifest” exported with each run (seed, scenario knobs, sampling rates).
- Add a small “data drift / stability sanity” section that compares run-to-run feature distributions.

### B) Reporting & sharing
- Standardize a “share bundle” structure (reports + configs + key metrics JSON + logs pointers).
- Add a notebook that loads a run and generates a compact executive summary.

### C) Performance & caching polish
- Validate that the feature cache covers the long pole steps.
- Add a “cache hit rate” section to logs and/or report.

---

## Remaining roadmap check (high level)

### Near-term goals
1) **Repeatable runs** that generate a shareable evidence bundle.
2) **Interpretability**: reports that clearly explain what was measured and why it matters.
3) **Iteration velocity**: quick notebook loop for feature ideas and baseline experiments.

### Longer-term goals
1) Swap synthetic data for real ingest (or a dual mode: synthetic + real).
2) Add richer model families / calibration.
3) Productize: CLI, configs, and report outputs stable enough to hand to someone else.

---

## Notes / decisions captured from Q&A

- Prefer to fix and organize the **current layout** rather than supporting multiple layouts.
- Add a **fast training preset** for faster iteration.
- Emphasize label + dataset generation logic in analysis and reporting.
