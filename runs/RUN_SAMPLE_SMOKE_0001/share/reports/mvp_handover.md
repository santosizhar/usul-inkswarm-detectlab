# Inkswarm DetectLab — MVP Handover

## What this is
This folder contains one end-to-end run of Inkswarm DetectLab: synthetic activity, feature generation, baseline models, and a stakeholder-friendly report. You can review results without running any code.

## How to view the results
1) Open the shareable viewer: `share\reports\index.html`
2) If you prefer reading: open `reports/summary.md` and `reports/baselines_login_attempt.md`

## How to interpret (quick)
- **PR-AUC** (higher is better) is a strong headline metric when positives are rare.
- **Recall @ 1% FPR** answers: ‘How many true fraud cases do we catch while keeping false alarms low?’
- **Time Eval** checks stability over time; **User Holdout** checks generalization to new users.

## What succeeded in this run
- (none)

## How to re-run (for operators)
If you are running this locally, the recommended single command is:
```bash
detectlab run mvp -c configs/skynet_mvp.yaml
```
For a full release readiness run (two-run determinism), use `scripts/rr_mvp.ps1`.

## Where to learn more
- `docs/mvp_user_guide.md` (non-technical walkthrough)
- `docs/pipeline_overview.md` (what the pipeline does at a high level)

