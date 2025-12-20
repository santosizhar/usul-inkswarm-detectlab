# CR-0001 — D-0002 Code Review Patch — Implementation Journal (J-0003)

Date: 2025-12-16  
NS: inkswarm-detectlab

## Goal
Apply the CR-0001 patch set requested after D-0002 with a focus on:
- tighter determinism (canonicalization + stable identifiers)
- clearer artifact format reporting (parquet preferred, csv fallback explicit)
- improved developer UX (CLI + config helpers)
- updated CI coverage (adds a smoke pipeline run)
- fixture regeneration (re-run committed smoke run)

## Changes implemented

### 1) Tightened determinism
- **Stable identifiers**: replaced Python `hash()` usage with `stable_mod()` (SHA256-based) to avoid per-process hash randomization.
  - Affects: `session_id`, `ip_hash`, `device_fingerprint_hash`, `credit_card_hash`.
- **Canonicalization before write + hash**:
  - Added `utils/canonical.py` with `canonicalize_df()` (stable sort + schema-based column ordering).
  - Pipeline now canonicalizes all raw and split tables **before** writing and hashing.

### 2) Checkout adverse exact-k assignment (variance reduction)
- Implemented deterministic **exact-k** adverse assignment for `checkout_attempt` based on configured `checkout_adverse_rate`:
  - All rows default to `success`.
  - Exactly `k = round(rate * n)` rows become adverse (`failure` or `review`, deterministic).
- This preserves the “mostly benign until SPACING GUILD” rule while reducing noisy drift in small runs.

### 3) Artifact format reporting (parquet preferred, csv fallback)
- `io.tables.write_auto()` now returns `(path, format, note)`:
  - `format`: `parquet` or `csv`
  - `note`: short reason if parquet write failed (e.g., `parquet_failed:ImportError`)
- Manifest artifacts now store `format` and `note`.
- Run summary now lists **Outputs written** including format + fallback notes.

### 4) CLI developer UX improvements
- Added:
  - `detectlab config validate <config>` → prints `OK`
  - `detectlab config show <config>` → prints resolved config as YAML
- Commands now accept config either as:
  - positional arg (`detectlab run skynet configs/skynet_smoke.yaml`)
  - or option (`--config/-c`)
- After pipeline commands, CLI prints an “Outputs written” list (paths + formats).

### 5) CI enhancement
- Added `configs/skynet_ci.yaml` (tiny run) and updated GitHub Actions to run:
  - `pytest`
  - `detectlab run skynet --config configs/skynet_ci.yaml`

### 6) Notebook test reliability
- Added `ipykernel` to `.[dev]` optional dependencies so notebook execution tests have a kernel available in CI.

### 7) Fixture regeneration
- Regenerated committed fixture run:
  - `runs/RUN_SAMPLE_SMOKE_0001/…`
- New fixture includes updated `manifest.json` and `reports/summary.md` with format reporting.

## Validation performed (no manual runs assumption)
The following validations were executed via automation commands:

### Unit tests
- `pytest -q -k "not notebooks"` (core tests pass in this environment)
- Notebook execution is expected to pass in CI because `ipykernel` was added to `.[dev]`.

### Pipeline smoke
- Executed the end-to-end pipeline for the pinned config `configs/skynet_smoke.yaml` to regenerate the committed fixture.

## Files touched (high signal)
- `src/inkswarm_detectlab/synthetic/skynet.py` (stable ids, exact-k adverse)
- `src/inkswarm_detectlab/utils/hashing.py` (stable_mod)
- `src/inkswarm_detectlab/utils/canonical.py` (new)
- `src/inkswarm_detectlab/io/tables.py` (format+note)
- `src/inkswarm_detectlab/pipeline.py` (canonicalize, format reporting, summary improvements)
- `src/inkswarm_detectlab/cli.py` (config show/validate, --config, output listing)
- `.github/workflows/ci.yml` + `configs/skynet_ci.yaml`
- `pyproject.toml` (dev dep: ipykernel)
- `runs/RUN_SAMPLE_SMOKE_0001/…` (regenerated)
