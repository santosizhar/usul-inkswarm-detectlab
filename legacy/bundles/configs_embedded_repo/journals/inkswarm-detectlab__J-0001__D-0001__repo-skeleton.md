# D-0001 — Repo skeleton + schemas + placeholders + CI — Implementation Journal (J-0001)

Date: 2025-12-15
NS: inkswarm-detectlab

## Goal
Deliver a minimal but coherent project skeleton that:
- locks core decisions (targets, timezone, ids, docs structure)
- provides schemas and config plumbing
- includes placeholder run data in the final run layout
- includes notebooks and executes them via pytest
- includes GitHub Actions CI running the single-line verification contract

## What was implemented
### 1) Repo scaffolding
- `pyproject.toml` with Python 3.12.x target, uv-oriented deps, Typer script entrypoint (`detectlab`)
- `src/` layout package `inkswarm_detectlab`
- basic `.gitignore` and `README.md`

### 2) Locked constraints wired
- Canonical timezone constant: `America/Argentina/Buenos_Aires`
- Entity id unified as `user_id` (no `account_id`)
- Targets: `login_attempt`, `checkout_attempt`
- Support embedded in `login_attempt` schema

### 3) Schema v1
- `schemas/base.py` provides a lightweight schema contract (`EventSchema`, `ColumnSpec`)
- `schemas/login_attempt.py` and `schemas/checkout_attempt.py`
- Schema registry (`schemas/__init__.py`)

### 4) Config system (Pydantic + YAML)
- `config/models.py` and `config/loaders.py`
- example YAML: `src/inkswarm_detectlab/config/examples/minimal.yaml`

### 5) IO and run layout
Canonical run layout chosen:
- `runs/<run_id>/raw/<event>.<fmt>`
- `runs/<run_id>/manifest.json`

Helpers live in:
- `io/paths.py`, `io/tables.py`, `io/manifest.py`

### 6) CLI (Typer)
`src/inkswarm_detectlab/cli.py` includes:
- `schemas list`
- `schemas show <name>`
- `config validate <path>`

### 7) Docs skeleton (MkDocs)
- `mkdocs.yml` at repo root
- docs pages in `docs/`:
  - `index.md`, `getting_started.md`, `pipeline_overview.md`, `schemas.md`
- lore bible in `docs/lore/world_bible.md` (lore-only rule)

### 8) Placeholder run + manifest
Committed placeholder run:
- `runs/PLACEHOLDER_RUN_0001/raw/login_attempt.*`
- `runs/PLACEHOLDER_RUN_0001/raw/checkout_attempt.*`
- `runs/PLACEHOLDER_RUN_0001/manifest.json`

Note: In this build environment, Parquet engines were unavailable, so the committed placeholders are CSV.
The code prefers Parquet and will write Parquet when `pyarrow` is installed (as declared in `pyproject.toml`).

Generator:
- `src/inkswarm_detectlab/tools/generate_placeholders.py`

### 9) Notebooks (executed)
- `notebooks/00_schema_preview.ipynb`
- `notebooks/01_placeholder_data_inspection.ipynb`

Notebooks include a small bootstrap cell to add `src/` to `sys.path` so they execute even without editable install.

### 10) Tests + notebook execution
- `tests/` includes schema/config/timezone tests
- notebook execution via `nbclient` inside `pytest` (`tests/test_notebooks.py`)
- `tests/conftest.py` adds `src/` to `sys.path` for local runs

### 11) GitHub Actions CI
- `.github/workflows/ci.yml` runs:
  - install uv
  - install editable deps
  - `uv run python -m inkswarm_detectlab.cli --help && uv run pytest -q`

## Verification performed (in this environment)
- `python -m pytest -q` passes (including notebook execution)

## Notes / trade-offs
- Placeholder files are CSV here due to missing Parquet engine in the build environment.
  In normal use (with `pyarrow`), the generator will write `.parquet` as intended.
- MkDocs build verification is intentionally deferred beyond D-0001 (by agreement).

## Next
Proceed to D-0002 (initial pipeline run orchestration + dataset split scaffolding), following CP/CR cadence.
