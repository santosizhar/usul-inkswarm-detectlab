# inkswarm-detectlab — J-0011 — CR-0002 — Review after D-0006

## Scope reviewed
- D-0005: Parquet mandatory (repo-wide) + migration tool `dataset parquetify`
- D-0006: Reporting (final report generator) + docs + test

## What was verified (no-manual-runs policy)
This CR is performed without executing the pipeline. Verification is based on:
- static inspection of code paths and CLI wiring
- presence of tests and docs updates
- clear fail-closed behavior (overwrite flags, missing artifacts messaging)

### D-0005 checks
- Parquet is enforced as the default artifact format; CSV legacy runs require migration.
- Migration tool remains available and is documented.

### D-0006 checks
- New CLI `detectlab report generate` exists and requires `--run-id`.
- Report generation:
  - reads run manifest (identity + artifacts)
  - reads FeatureLab feature_manifest if present
  - reads BaselineLab metrics/report if present
  - fails safe when baselines are absent (explicit validation note)
  - writes `final_report.md` and `insights.json`
  - updates the run manifest to reference report artifacts

## Code review notes
- The report generator intentionally avoids new heavy deps; uses stdlib + existing config/manifest.
- Baseline metrics parsing is tolerant of missing keys and missing splits; it produces a compact highlight summary.
- Appendix is truncated to prevent huge markdown growth.

## Risks / known gaps
- No runtime execution was performed in this environment; correctness depends on local validation later.
- Parquet engine availability (pyarrow) must be ensured in the user’s environment and CI.

## Actions
- Keep validation scripts as the single “source of truth” for later closure of runtime health.
- Next deliverable could tighten CI by pinning pyarrow and adding a small end-to-end smoke run.

## Deferred validation instructions
Recommended local validation after CR:
- `uv run pytest -q`
- `uv run detectlab dataset parquetify -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force`
- `uv run detectlab features build -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force`
- `uv run detectlab baselines run -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force`
- `uv run detectlab report generate -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force`
