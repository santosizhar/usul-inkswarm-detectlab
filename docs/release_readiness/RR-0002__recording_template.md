# RR-0002 Recording Template (paste into J)

Use this template when you execute RR-0002 on Windows/Python 3.12.

## Context
- Date:
- Machine:
- OS:
- Python (`py -3.12 --version`):
- Repo mode:
  - [ ] Git checkout mode (code SHA expected)
  - [ ] Unpacked zip mode (no git; UI shows "(no git)")
- Config used:
  - [ ] MVP (`configs/skynet_mvp.yaml`)
  - [ ] Smoke (`configs/skynet_smoke.yaml`)

## Preconditions (paste outputs)
- `py -3.12 --version`
- `python -m inkswarm_detectlab doctor` (key lines)

## Runs executed (run ids)
- RR2_MVP_GIT_A:
- RR2_MVP_GIT_B:
- RR2_SMOKE_GIT:
- RR2_MVP_ZIP_A:
- RR2_MVP_ZIP_B:
- RR2_SMOKE_ZIP:
- MVP_SEND:

## Determinism outcome (MVP A/B)
- Git mode: HARD / QUALIFIED / FAIL  
  Evidence pointer(s):  
  Notes:
- Zip mode: HARD / QUALIFIED / FAIL  
  Evidence pointer(s):  
  Notes:

## Share artifact
- Share zip name:
- Location:
- Contents verified:
  - [ ] `share/ui_bundle/index.html`
  - [ ] `share/reports/EXEC_SUMMARY.html`
  - [ ] `share/reports/summary.html`

## Final manual confirmation (screenshots)
Save screenshots under:
- `docs/rr_evidence/RR-0002/YYYYMMDD/screenshots/`

Checklist:
- UI landing screenshot:
- `EXEC_SUMMARY.html` screenshot:
- `summary.html` screenshot:

## Interpretation notes (stakeholder-ready)
- user_holdout:
- time_eval:
- drift risk assessment:
- recommended next actions:

## Final RR statement
RR-0002: PASS / QUALIFIED / FAIL
