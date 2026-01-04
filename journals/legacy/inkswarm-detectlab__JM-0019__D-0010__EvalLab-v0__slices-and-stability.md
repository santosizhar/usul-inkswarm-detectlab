# JM-0019 — D-0010 — EvalLab v0 (slices + stability)

Date: 2025-12-19

## One-liner
Added best-effort **slices + threshold stability** diagnostics for login baselines, integrated into the MVP orchestrator and stakeholder UI.

## Decisions captured
- Primary truth split: **user_holdout** (stakeholder-first), time_eval is drift check.
- Slice set: **recommended** (playbooks + MFA/country/etc.).
- Include **threshold stability**: “what threshold shift is needed to keep 1% FPR?”.
- Reporting format: **Markdown + JSON**, with explicit “partial” notes when inputs are missing.

## Artifacts
- `runs/<run_id>/reports/eval_stability_login_attempt.md`
- `runs/<run_id>/reports/eval_slices_login_attempt.md`
- JSON payloads: `eval_*_login_attempt.json`

## CLI
- `python -m inkswarm_detectlab eval run --config <cfg.yaml> --run-id <RUN_ID>`

## Follow-ups
- If we want clickable links in the shareable UI folder, we should **copy reports into the bundle** (or export a single “evidence pack” folder).
