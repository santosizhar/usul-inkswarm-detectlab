# J-0018 — D-0009 — MVP Orchestrator (one-command)

Date: 2025-12-18

## Context
We want a *single*, stakeholder-friendly command that:
- runs the MVP pipeline in a best-effort mode
- produces a shareable static HTML viewer by default
- writes a non-technical handover file telling people what to open / what to look at

Constraints captured in this chat:
- Windows-first operators; validation postponed until after MVP (DV-0001 postponed)
- Python 3.12
- HGB excluded until its crash is resolved; MVP baselines are **logreg + rf**
- On failure, keep running where possible and always print a clear message about what failed

## What was done
### CLI
- Added `detectlab run mvp -c <config.yaml>`.
- Default behavior: **fastest** path focusing on `login_attempt`.
- Best-effort execution; prints per-step OK/FAIL and returns non-zero exit code if any step fails.

### Artifacts produced by `detectlab run mvp`
Inside `runs/<run_id>/`:
- `share/ui_bundle/index.html` — self-contained viewer (open in browser, no server)
- `reports/mvp_handover.md` — non-technical guide to viewing + interpreting results
- `reports/summary.md` and `reports/baselines_login_attempt.md` — readable markdown reports

### Docs updates
- Updated `docs/mvp_user_guide.md` and `docs/pipeline_overview.md` to include the one-command workflow.
- Updated `README.md` with the new command and artifact locations.

## Validation performed (in-repo)
- Added a small unit test for writing the handover markdown.

## Known limitations / defers
- No attempt to run Deferred Validation (DV-0001) in this deliverable (explicitly postponed).
- `checkout_attempt` orchestration is not included in the MVP command yet (planned post-MVP).

## Next
- Proceed to the next deliverable (post-MVP roadmap): evaluation robustness (slices), multi-label calibration, and (later) UI revamp in React.
