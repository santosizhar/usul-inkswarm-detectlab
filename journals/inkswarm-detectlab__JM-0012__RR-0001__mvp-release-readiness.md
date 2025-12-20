# JM-0012 — RR-0001 — MVP Release Readiness (Meta)

**Closed?** <YES/NO>

## Inputs
- Config: `configs/skynet_mvp.yaml`
- Helper script: `scripts/rr_mvp.ps1` (preferred)

## Outputs
- Evidence directory: `rr_evidence/RR-0001/<base_run_id>/`
- Evidence summary: `journals/inkswarm-detectlab__RR_EVIDENCE__RR-0001__<base_run_id>.md`
- Run A folder: `runs/<base_run_id>_A/`
- Run B folder: `runs/<base_run_id>_B/`

## Exit criteria
- Two-run determinism signature is identical.
- Required artifacts exist for both runs (see `docs/release_readiness_mvp.md`).

## Notes
- If RR fails, the scripts clean up run folders and keep only the evidence bundle (log + signatures + error message).