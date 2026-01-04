# Getting Started

## Install (uv)
```bash
uv venv
uv pip install -e ".[dev]"
```

## Verify (D-0001 contract)
```bash
uv run python -m inkswarm_detectlab.cli --help && uv run pytest -q
```

## Generate a sample run (D-0002)
End-to-end synthetic generation + leakage-aware splits:

```bash
uv run detectlab run skynet configs/skynet_smoke.yaml
```

This writes under:
- `runs/RUN_SAMPLE_SMOKE_0001/...` (raw tables, dataset splits, manifest, and a short summary report)
