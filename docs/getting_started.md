# Getting Started

## Install (uv)
```bash
uv venv
uv pip install -e ".[dev]"
```

## Verify (D-0001 contract)
```bash
uv run detectlab --help
uv run pytest -q
```

## Validate / inspect a config
```bash
uv run detectlab config validate configs/skynet_smoke.yaml
uv run detectlab config show configs/skynet_smoke.yaml
```

## Generate a sample run (D-0002)
End-to-end synthetic generation + leakage-aware splits:

```bash
uv run detectlab run skynet configs/skynet_smoke.yaml
# or:
uv run detectlab run skynet --config configs/skynet_smoke.yaml
```

This writes under:
- `runs/RUN_SAMPLE_SMOKE_0001/...` (raw tables, dataset splits, `manifest.json`, and `reports/summary.md`)

### Output layout (current)
- `runs/<run_id>/raw/` — raw event tables
- `runs/<run_id>/dataset/` — leakage-aware splits per event table
- `runs/<run_id>/manifest.json` — metadata + artifact hashes
- `runs/<run_id>/reports/summary.md` — human-readable summary (includes formats written)

## Troubleshooting
### Parquet engine missing (hard fail as of D-0005)
DetectLab requires Parquet. If the Parquet engine is missing, commands will fail closed with instructions.

Fix:
```bash
uv pip install pyarrow
```

If you are validating an older run that still has CSV artifacts, migrate it first:
```bash
detectlab dataset parquetify -c <config.yaml> --run-id <RUN_ID> --force
```

## FeatureLab + BaselineLab

```bash
# after you have a run_id
detectlab features build -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001
detectlab baselines run -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001
```

## Parquet mandatory (D-0005)

All pipeline artifacts are written/read as **Parquet**.

### Migrate a legacy CSV run

If you have an older run (or fixture) that still has `.csv` artifacts, migrate it first:

```bash
detectlab dataset parquetify -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force
```

This writes `.parquet` files next to the `.csv` files and updates the run manifest to point to Parquet.



## Generate a final report (D-0006)

```bash
uv run detectlab report generate -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001
```

This writes `runs/<run_id>/reports/final_report.md` and `insights.json`.
