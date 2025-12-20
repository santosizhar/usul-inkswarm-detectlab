# FeatureLab (D-0003)

FeatureLab produces a **leakage-aware** feature table for `login_attempt`.

## Output locations
For a run `<run_id>`:

- Feature table: `runs/<run_id>/features/login_attempt/features.{parquet|csv}`
- Spec: `runs/<run_id>/features/login_attempt/feature_spec.json`
- Feature manifest: `runs/<run_id>/features/login_attempt/feature_manifest.json`

All are also registered under `runs/<run_id>/manifest.json` → `artifacts`.

## Leakage controls
- **Strict past-only** rolling windows (`closed='left'`) so the current event does not see itself.
- Same-timestamp events are treated as not visible to each other for unique-count features.

## Safe aggregates (MVP)
Aggregations are computed over:
- entities: `user`, `ip`, `device`
- windows: configurable (default: `1h, 6h, 24h, 7d`)

Examples:
- attempt counts and outcome counts/rates
- unique companion counts (e.g., unique `ip_hash` per user window)
- support aggregates (counts + costs + wait/handle seconds)

## CLI
```bash
detectlab features build -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001
# overwrite:
detectlab features build -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force
```
