# Pipeline Overview

Runs live under `runs/<run_id>/...`.

## Current run layout
- `runs/<run_id>/raw/` — raw event tables (`login_attempt`, `checkout_attempt`)
- `runs/<run_id>/dataset/` — leakage-aware dataset splits per event table
- `runs/<run_id>/manifest.json` — run metadata

## Locked leakage-aware split (implemented in D-0002)
- 85% time-based
- 15% by-user holdout

## Locked timezone
All timestamps are standardized to `America/Argentina/Buenos_Aires`.
