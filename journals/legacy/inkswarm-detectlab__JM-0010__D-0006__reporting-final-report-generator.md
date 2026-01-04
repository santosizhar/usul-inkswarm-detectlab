# inkswarm-detectlab — JM-0010 — D-0006 — Reporting

- Added `detectlab report generate` CLI.
- Generates `final_report.md` + `insights.json` under `runs/<run_id>/reports/`.
- Summarizes manifest + FeatureLab + BaselineLab (if present) and adds operator narrative.
- Updates run manifest to reference the report artifacts.
- Added minimal unit test for report generation without baselines.
- Added docs page `Reporting` and MkDocs nav entry.
