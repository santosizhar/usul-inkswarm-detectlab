# J-0007 — CC-0001 — Deferred validation for D-0004

## Decision
Close D-0004 **without running validation** and ship a repo artifact that contains:
- Implementation
- Documentation
- Explicit validation instructions + scripts

## Rationale
Manual runs were not possible in the original workflow, but we still needed a repeatable way to validate later.

## What was added
- `DEFERRED_VALIDATION__D-0004.md`
- `scripts/validate_d0004.ps1`
- `scripts/validate_d0004.sh`

## Acceptance criteria (to be verified later)
- `pytest -q` passes
- Feature artifacts are produced and the run manifest updates:

```bash
detectlab features build -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force
```

- Baseline artifacts and report are produced:

```bash
detectlab baselines run -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force
```

- If legacy CSV artifacts exist, they can be upgraded to Parquet:

```bash
detectlab dataset parquetify -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force
```
