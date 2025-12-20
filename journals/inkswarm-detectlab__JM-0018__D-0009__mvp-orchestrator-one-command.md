# JM-0018 — D-0009 — MVP Orchestrator (one-command)

## Deliverable
- **D-0009**: Add a best-effort orchestrator command: `detectlab run mvp`.

## Inputs / answers captured
- Baselines: **logreg + rf** (HGB excluded until crash is resolved)
- Output format: **HTML** (static bundle)
- Orchestration goal: **fastest** happy path; keep running and report failures

## Acceptance criteria
- A single command runs the MVP pipeline and generates a shareable artifact.
- On failure, prints a clear per-step status log and exits non-zero.
- Produces a stakeholder-facing `mvp_handover.md`.

## Changes made
- New module: `src/inkswarm_detectlab/mvp/` with:
  - `orchestrator.py` (best-effort pipeline runner)
  - `handover.py` (non-technical handover writer)
- CLI: new `detectlab run mvp` command.
- Docs: updated `docs/mvp_user_guide.md`, `docs/pipeline_overview.md`, `README.md`.
- Tests: added `tests/test_mvp_handover.py`.

## Operator note
Run locally:
```bash
detectlab run mvp -c configs/skynet_mvp.yaml
```
Then open:
- `runs/<run_id>/reports/mvp_handover.md`
- `runs/<run_id>/share/ui_bundle/index.html`
