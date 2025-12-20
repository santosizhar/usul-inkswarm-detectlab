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
