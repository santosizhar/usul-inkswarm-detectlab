# inkswarm-detectlab — J-0009 — D-0005 — Parquet mandatory

## Goal
Make Parquet **mandatory** across all run artifacts (raw, dataset, features, models) and remove CSV fallback from the pipeline.

Keep an explicit migration tool for legacy runs: `detectlab dataset parquetify`.

## Changes implemented
### Parquet mandatory IO contract
- `io.tables.read_auto()` now reads **Parquet only**.
  - If a legacy `.csv` is found, it fails closed with instructions to run `dataset parquetify`.
- `io.tables.write_auto()` now writes **Parquet only** and raises a clear error if the parquet engine is missing.
- Placeholder data generation writes Parquet only.

### Legacy migration tool kept (explicit)
- `detectlab dataset parquetify -c <cfg> --run-id <RUN_ID> --force`
  - Reads legacy CSV artifacts, writes `.parquet` next to them
  - Updates `manifest.json` to point to Parquet
  - Does **not** delete CSV files (migration keeps originals)

### Docs + scripts updated
- Docs now treat Parquet as mandatory (D-0005).
- Deferred validation instructions and scripts run `dataset parquetify` first when validating the committed fixture.

## Known constraint (repo consistency)
The committed fixture `RUN_SAMPLE_SMOKE_0001` includes legacy `.csv` artifacts.
This is now intentional legacy state; validate by running `dataset parquetify` first.

## Next
- D-0006+: remove legacy CSV fixture from repo (or replace with Parquet artifact set) once a Parquet engine is guaranteed in the build environment.
- Consider a `--delete-csv` option for parquetify if repo cleanliness becomes a goal.
