# FeatureLab (D-0003, D-0007)

FeatureLab produces **leakage-aware** feature tables for:

- `login_attempt` (D-0003, extended in D-0007 with cross-event context)
- `checkout_attempt` (D-0007)

## Output locations
For a run `<run_id>`:

### login_attempt
- Feature table: `runs/<run_id>/features/login_attempt/features.{parquet|csv}`
- Spec: `runs/<run_id>/features/login_attempt/feature_spec.json`
- Feature manifest: `runs/<run_id>/features/login_attempt/feature_manifest.json`

### checkout_attempt
- Feature table: `runs/<run_id>/features/checkout_attempt/features.{parquet|csv}`
- Spec: `runs/<run_id>/features/checkout_attempt/feature_spec.json`
- Feature manifest: `runs/<run_id>/features/checkout_attempt/feature_manifest.json`

All are also registered under `runs/<run_id>/manifest.json` → `artifacts`.

## Leakage controls
- **Strict past-only** rolling windows (`[t-window, t)`) so the current event does not see itself.
- Same-timestamp events are treated as not visible to each other.

## Safe aggregates
Aggregations are computed over:
- entities: `user`, `ip`, `device`
- windows: configurable (default: `1h, 6h, 24h, 7d`)

### login_attempt (high level)
- attempt counts and outcome counts/rates (success/failure/challenge/lockout)
- unique companion counts (e.g., unique `ip_hash` per user window)
- optional support aggregates (counts + costs + wait/handle seconds)
- **cross-event context (D-0007):** checkout history aggregates as additional context

### checkout_attempt (high level)
- attempt counts and outcome counts/rates (success/failure/review, plus adverse=failure|review)
- basic numeric aggregates (e.g., payment value / basket size sums + means)
- unique companion counts (e.g., unique `credit_card_hash` per user window)
- **cross-event context (D-0007):** login history aggregates as additional context
- derived label for MVP: `is_adverse = (checkout_result != "success")`

## CLI
```bash
# Default: login_attempt
detectlab features build -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001

# checkout_attempt only
detectlab features build -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --event checkout

# both (login + checkout)
detectlab features build -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --event all

# overwrite:
detectlab features build -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --event all --force
```
