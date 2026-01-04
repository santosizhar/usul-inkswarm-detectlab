# Evaluation — Slices (login_attempt)

Run: `RR_FAST_001_B`  
Generated: `2025-12-19T20:43:40Z`

This report breaks performance down by **synthetic archetypes** (playbooks) and a few **obvious covariates** (MFA, country, etc.).
Metrics are computed using the **train-chosen threshold** (target FPR = 1%) and then applied to each split.

> **Status:** partial — some inputs were missing. See Notes at the bottom.

## Notes
- Missing model artifact for 'logreg' under runs/RR_FAST_001_B/models/login_attempt/baselines
- Missing model artifact for 'rf' under runs/RR_FAST_001_B/models/login_attempt/baselines
