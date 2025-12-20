# Inkswarm DetectLab

Repo / NS: `inkswarm-detectlab`

DetectLab is a reproducible lab to generate **event-level telemetry**, build **leakage-aware datasets**, and train/evaluate **event-level detectors**.

## Locked MVP constraints (summary)
- Targets: `login_attempt`, `checkout_attempt` (event-level)
- `support` is embedded inside `login_attempt` (not a separate event)
- Primary entity id: `user_id` (no `account_id`)
- Canonical timezone: `America/Argentina/Buenos_Aires`
- Default artifact format: Parquet (Parquet is mandatory as of D-0005; no CSV fallback)

## Quick verification (D-0001 contract)
```bash
uv run python -m inkswarm_detectlab.cli --help && uv run pytest -q
```

## FeatureLab + BaselineLab (MVP)
```bash
# after you have a run_id (example fixture):
detectlab features build -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001
detectlab baselines run -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001
```


## Code Freeze
- Latest: `CODE_FREEZE__CF-0002.md` (restart with `inkswarm-detectlab__MASTERPROMPT_CF-0002__Code-Freeze-Restart.md`).
