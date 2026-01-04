# Evaluation — Stability (login_attempt)

Run: `RUN_SAMPLE_SMOKE_0001`  
Generated: `None`

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
- Missing baselines directory: runs\RUN_SAMPLE_SMOKE_0001\models\login_attempt\baselines\baselines
- No loadable baseline model artifacts found under: runs\RUN_SAMPLE_SMOKE_0001\models\login_attempt\baselines
