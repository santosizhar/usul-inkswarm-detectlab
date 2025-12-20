# Evaluation — Stability (login_attempt)

Run: `RR_FAST_001_B`  
Generated: `2025-12-19T20:43:40Z`

Primary split for stakeholder truth is **user_holdout** (generalization to new users).
Time Eval is shown as a drift/stability check.

> **Status:** partial — some inputs were missing. See Notes at the bottom.

## Headline stability table (train threshold)

| Label | Model | Train thr | Time PR-AUC | Time Recall@thr | Holdout PR-AUC | Holdout Recall@thr | ΔRecall (Hold - Time) |
|---|---|---:|---:|---:|---:|---:|---:|

## Threshold stability (what threshold would be needed to hit 1% FPR?)

| Label | Model | Train thr | Time thr@1%FPR | Holdout thr@1%FPR | Δthr (Hold - Train) |
|---|---|---:|---:|---:|---:|

## Notes
- Missing model artifact for 'logreg' under runs/RR_FAST_001_B/models/login_attempt/baselines
- Missing model artifact for 'rf' under runs/RR_FAST_001_B/models/login_attempt/baselines
