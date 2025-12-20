# J-0011 — CR-0002 — Baseline robustness + RR requirements

Date: 2025-12-18

## Ceremony
**CR-0002** (Code Review)

Scope: review BaselineLab robustness + packaging/UX after D-0005, and lock MVP RR requirements.

## Decisions locked in CR-0002
1) **Models for MVP:** `logreg + rf` only.
   - `hgb` is **excluded** until its platform-specific native crash during `.fit()` is reproduced + resolved.
2) **Parquet engine preflight:** added a CLI-level fail-closed check for `pyarrow` (low cost, clearer errors).
3) **RR gate for MVP:** **full requirements**. RR must include a complete end-to-end run + features + baselines, and validate expected artifacts.

## Changes made
### BaselineLab report improvements
- Added a **baseline summary table** at the top of `report.md` to make side-by-side model comparison easier.

### Configuration validation
- Config loading now fails early if `baselines.login_attempt.models` includes `hgb` (CR-0002 lock).

### Docs
- Updated BaselineLab docs to reflect `logreg + rf` MVP lock and HGB exclusion.
- Added:
  - `docs/windows_repro.md` (thread settings + crash triage)
  - `docs/release_readiness_mvp.md` (full-requirements RR checklist)

### RR helper scripts
- Added:
  - `scripts/rr_mvp.sh`
  - `scripts/rr_mvp.ps1`

## Validations performed in this chat
- Static review + basic syntax sanity (no runtime execution in this environment).
- Note: D-0004 deferred validation remains deferred until the user runs it locally on Windows after MVP.

## Follow-ups
- Reproduce and isolate the HGB crash on Windows, then reintroduce HGB behind an explicit flag.
