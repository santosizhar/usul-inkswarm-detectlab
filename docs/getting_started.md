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
### Parquet engine missing (CSV fallback)
DetectLab **prefers Parquet**. If a Parquet engine (e.g., `pyarrow`) is not available, it will fall back to CSV.

You will see:
- `format: csv` and a note like `parquet_failed:ImportError` in the manifest and summary.

Fix:
```bash
uv pip install pyarrow
```

## FeatureLab + BaselineLab

```bash
# after you have a run_id
detectlab features build -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001
detectlab baselines run -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001
```

## Explicit Parquet conversion

```bash
# convert any CSV artifacts to Parquet for a run
detectlab dataset parquetify -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001
```
