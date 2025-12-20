# Pipeline Overview

A run is identified by a `run_id`. All artifacts for that run live under:

- `runs/<run_id>/`

## Run layout (current)

- `runs/<run_id>/raw/` — raw event tables (Parquet)
- `runs/<run_id>/dataset/` — leakage-aware dataset splits per event table (Parquet + manifests)
- `runs/<run_id>/features/` — FeatureLab outputs (features table + spec)
- `runs/<run_id>/models/` — BaselineLab outputs (models + metrics + report)
- `runs/<run_id>/reports/eval_*.md` — EvalLab diagnostics (slices + stability)
- `runs/<run_id>/reports/eval_*.json` — machine-readable diagnostics payloads
- `runs/<run_id>/manifest.json` — inventory + content hashes for each artifact
- `runs/<run_id>/reports/summary.md` — human-readable summary (counts, splits, labels)

## One-command MVP run (D-0009+)

The MVP orchestrator now includes **EvalLab diagnostics** after baselines.

For the shareable MVP workflow (stakeholders), use:

```bash
detectlab run mvp -c configs/skynet_mvp.yaml
```

This produces two stakeholder-facing artifacts:
- `runs/<run_id>/share/ui_bundle/index.html` — static viewer (open in browser, no server)
- `runs/<run_id>/reports/mvp_handover.md` — what to open / what to look at

### BaselineLab artifacts (login-first for MVP)
Within `runs/<run_id>/models/login_attempt/baselines/`:
- `metrics.json` — per-label, per-model metrics including PR-AUC and Recall@1%FPR
- `report.md` — human-readable report with a compact summary table and per-model details

Stakeholder-friendly convenience outputs:
- `runs/<run_id>/reports/baselines_login_attempt.md` — copy of the report
- `runs/<run_id>/logs/baselines.log` — debug log (captures partial failures)

## Leakage-aware split (D-0002)

For each event table (MVP focuses on `login_attempt`, but `checkout_attempt` is supported):

- **15% user holdout**: entire user histories are held out as `user_holdout`
- Remaining 85% users are split by time into:
  - `train`
  - `time_eval`

This structure answers two different “generalization” questions:
- Can we handle **future time**? (`time_eval`)
- Can we handle **new users**? (`user_holdout`)

All timestamps are standardized to `America/Argentina/Buenos_Aires`.

## Determinism contract

DetectLab aims for reproducibility:

- Tables are canonicalized (stable sort + stable column order) **before write and hash**
- The manifest stores `content_hash` per artifact
- Release Readiness runs the MVP pipeline **twice** and compares signatures

## File formats

As of **D-0005**, **Parquet is mandatory** (fail-closed). There is no CSV fallback in the normal pipeline.

### Legacy conversion
If you have old runs that still contain CSV artifacts, you can upgrade them with:

```bash
detectlab dataset parquetify -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force
```
