# J-0005 — CP-0001 — Planning + High-level roadmap

## CP-0001 outcomes
- Confirmed the MVP scope for FeatureLab and BaselineLab:
  - **FeatureLab:** safe aggregates only for now; map richer ideas later (session_id features, longer windows, etc.)
  - **BaselineLab:** quality-first defaults; feature standardization enabled where beneficial
- Confirmed `login_attempt` is the only event type in scope for now.
- Confirmed notebook expectation: 2 notebooks total (kept in `notebooks/`).

## High-level roadmap (preview)
- D-0005: Make Parquet **mandatory** (remove CSV fallback) after confirming Windows installation path.
- D-0006+: Add richer feature families (session_id aggregates, longer windows, selected categorical handling).
- D-0007+: Extend baselines into calibrated models + threshold selection variants + reporting.
- Later: introduce new event tables and cross-table joins (still leakage-safe).
