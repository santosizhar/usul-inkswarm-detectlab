# J-0007 — CC-0001 — Deferred validation for D-0004

## Decision
Close D-0004 **without running validation** and ship a repo artifact that contains:
- Implementation
- Documentation
- Explicit validation instructions + scripts

## Rationale
Manual runs are not possible in the current workflow, but we still need a repeatable way to validate later.

## What was added
- `DEFERRED_VALIDATION__D-0004.md`
- `scripts/validate_d0004.ps1`
- `scripts/validate_d0004.sh`

## Acceptance criteria (to be verified later)
- `pytest -q` passes
- `detectlab features build ...` produces feature artifacts and updates run manifest
- `detectlab baselines run ...` produces baseline artifacts and report
- `detectlab dataset parquetify ...` converts CSV fallbacks to Parquet (where applicable)
