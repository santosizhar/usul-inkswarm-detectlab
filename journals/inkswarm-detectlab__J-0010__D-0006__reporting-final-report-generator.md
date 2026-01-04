# inkswarm-detectlab — J-0010 — D-0006 — Reporting (Final Report generator)

## What changed
D-0006 adds an operator-friendly stitched report generator that summarizes:
- run identity and artifact inventory from `manifest.json`
- FeatureLab v0 summary (windows/groups/strict past-only) from `feature_manifest.json`
- BaselineLab performance (if present) from `runs/<run_id>/models/login_attempt/baselines/metrics.json`
- narrative interpretation aligned with SKYNET / SPACING GUILD playbooks
- explicit validation status (including deferred validation instructions)

## New CLI
- `uv run detectlab report generate -c <CFG.yaml> --run-id <RUN_ID> [--force]`

## Outputs
Written under:
- `runs/<run_id>/reports/final_report.md`
- `runs/<run_id>/reports/insights.json`

And the run manifest is updated to reference both artifacts.

## Design notes
- Report generation is fail-safe: it can run even if baselines are missing, but it will clearly state that performance is unknown.
- No new heavy dependencies were introduced; uses stdlib + existing project modules.

## Deferred validation
Runtime validation can be performed later using the repo’s validation scripts and/or:
- `uv run pytest -q`
- `uv run detectlab report generate ... --force`
