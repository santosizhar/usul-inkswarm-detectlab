# J-0019 — D-0010 — EvalLab v0 (slices + stability)

Date: 2025-12-19

## Context
After the MVP orchestrator (D-0009) and stakeholder UI (D-0006.5), we need a **diagnostics layer** that answers:

- *Where does performance hold up vs collapse?* (slices)
- *Is the chosen operating point stable across splits?* (threshold stability)

Constraints:
- Deferred Validation (DV-0001) is postponed until after MVP; this deliverable must be **best-effort** and **explicit about gaps**.
- Baselines for MVP are **logreg + rf**; HGB remains excluded until its crash is resolved.
- Audience includes **non-technical stakeholders**; diagnostics must be readable and aligned to the “primary truth split”.

Captured answers for this step:
- Slice set: **recommended** (synthetic archetypes + obvious covariates)
- Primary split framing: **B)** (stakeholder-first; still show both splits)
- Include: **threshold stability** section
- Split trade-off: evaluated and codified as **user_holdout = primary**, time_eval = drift check
- Reporting: **bit of both** (technical JSON + narrative Markdown), best-effort, fail-closed messaging

## What was done
### EvalLab (new)
- Added `src/inkswarm_detectlab/eval/` with a best-effort runner:
  - `run_login_eval_for_run(...)` produces:
    - `runs/<run_id>/reports/eval_stability_login_attempt.md`
    - `runs/<run_id>/reports/eval_slices_login_attempt.md`
    - JSON payloads for both (`.json`)
- Diagnostics are computed **per label** (`label_replicators`, `label_the_mule`, `label_the_chameleon`) and **per model** (`logreg`, `rf`), using:
  - PR-AUC for headline
  - Recall/FPR/Precision at the **train-chosen threshold** (target FPR = 1%)

### Threshold stability
- For each split, we report:
  - performance at the **train threshold**
  - the threshold that would be required on that split to hit **1% FPR**
- This makes drift visible even when headline PR-AUC stays similar.

### Slices
- Slices include:
  - Playbooks (Replicators / Mule / Chameleon / Benign)
  - MFA used (yes/no), username present (yes/no), support contacted (yes/no)
  - Country (top-3 + other)
  - Login result buckets (success/failure/review) if present
- Metrics are computed slice-by-slice using the **same train threshold**.

### MVP orchestration
- The MVP orchestrator now runs EvalLab after baselines (best-effort):
  - If required artifacts (parquet / models) are missing, it writes reports with **Status: partial** + explicit Notes.

### UI integration (stakeholder-first)
- UI summary now includes an `eval.login_attempt` block:
  - paths to the eval reports
  - a compact stability table (holdout vs time) for quick reading
- The static HTML viewer renders a new “Diagnostics” panel per run showing:
  - primary split (user_holdout)
  - holdout/time recall deltas
  - path hints for deeper reports

## Files added/updated
- `src/inkswarm_detectlab/eval/__init__.py`
- `src/inkswarm_detectlab/eval/runner.py`
- `src/inkswarm_detectlab/mvp/orchestrator.py` (calls EvalLab step)
- `src/inkswarm_detectlab/ui/summarize.py` (adds eval summary fields)
- `src/inkswarm_detectlab/ui/bundle.py` (renders Diagnostics panel)
- `src/inkswarm_detectlab/cli.py` (adds `detectlab eval run`)
- `docs/pipeline_overview.md` (documents new eval artifacts)
- `docs/mvp_user_guide.md` (adds non-technical diagnostics reading guide)
- `docs/getting_started.md` (documents eval command)

## Risks / notes
- Eval scoring requires Parquet support and working feature/model artifacts. If pyarrow is missing or artifacts are missing, reports are still produced but marked **partial**.
- Links inside the HTML viewer are intentionally **path hints** (to keep the UI bundle self-contained). For sharing, include the run folder or RR evidence bundle.

## Next
Proceed to D-0011 (MVP polish & evidence packaging) or D-0012 (checkout baseline re-introduction) depending on roadmap priority.
