# inkswarm-detectlab — JM-0009 — D-0005 — Parquet mandatory

- Parquet is mandatory across all artifacts (raw/dataset/features/models).
- `read_auto`/`write_auto` no longer support CSV fallback; legacy CSV triggers fail-closed guidance.
- Kept explicit migration tool: `detectlab dataset parquetify` (writes parquet next to csv; updates manifest; keeps csv).
- Updated docs + deferred validation scripts to run parquetify first when validating legacy fixture.
- Fixture remains legacy CSV; migration is required before running FeatureLab/BaselineLab on it.
