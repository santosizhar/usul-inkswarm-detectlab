# Executive Summary

## How to open
- Open the bundle UI: `share/ui_bundle/index.html`
- Or read this report: `reports/EXEC_SUMMARY.html`

## What to trust (truth split)
- **user_holdout** = primary truth (generalization to new users)
- **time_eval** = drift check (time stability)

## Best baseline (best-effort)
- Selected by max **user_holdout PR-AUC** (if available): **—**

## Recommended actions

- If **time_eval** is materially worse than **user_holdout**, treat it as **drift risk** → consider retraining with newer data, recalibrating thresholds, or deploying drift monitors.
- If a slice shows materially worse performance or instability → consider slice-specific mitigations (rules, extra features, targeted data collection).
- If model quality is acceptable but ops cost is high → consider tightening thresholds, adding guardrails, or using a simpler baseline in low-risk paths.
- **Reproducibility is PROVISIONAL** (RR evidence pending) → run RR-0001/0002 on Windows/Py3.12 and record evidence before any high-stakes deployment.
- **D-0004 validation is deferred** → run the deferred validation and record outcomes before relying on that baseline claim.
