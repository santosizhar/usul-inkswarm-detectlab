# Inkswarm DetectLab

Repo / NS: `inkswarm-detectlab`

DetectLab is a reproducible lab to generate **event-level telemetry**, build **leakage-aware datasets**, and train/evaluate **event-level detectors**.

## Locked MVP constraints (summary)
- Targets: `login_attempt`, `checkout_attempt` (event-level)
- `support` is embedded inside `login_attempt` (not a separate event)
- Primary entity id: `user_id` (no `account_id`)
- Canonical timezone: `America/Argentina/Buenos_Aires`
- Default artifact format: Parquet (fallbacks may exist for placeholders)

## Quick verification (D-0001 contract)
```bash
uv run python -m inkswarm_detectlab.cli --help && uv run pytest -q
```
