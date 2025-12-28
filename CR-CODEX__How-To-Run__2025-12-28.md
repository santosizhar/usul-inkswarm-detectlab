# CR-CODEX — How to Run DetectLab (tunable parameters)

This guide distills the minimum commands and knobs to run DetectLab end-to-end. Keep it alongside the change log and review doc for auditability.

## Environment setup
- Python 3.12 virtualenv (recommended):
  ```bash
  python -m venv .venv
  source .venv/bin/activate  # Windows: .\.venv\Scripts\activate
  python -m pip install --upgrade pip
  pip install -e ."[dev]"
  ```
- Quick guardrails (fail fast):
  ```bash
  python -m compileall src
  pytest -q
  detectlab doctor
  ```

## Core commands and tunable parameters

### 1) Data generation + pipeline
- **Generate synthetic events**
  ```bash
  detectlab run skynet -c configs/skynet_smoke.yaml --run-id RUN_SMOKE_001 --force
  ```
  - `-c/--config` — choose a YAML config (e.g., `configs/skynet_smoke.yaml`, `configs/skynet_mvp.yaml`).
  - `--run-id` — logical run key; controls output folder under `runs/<RUN_ID>/`.
  - `--force` — overwrite existing run artifacts for the same `run-id`.

- **Feature engineering**
  ```bash
  detectlab features build -c configs/skynet_smoke.yaml --run-id RUN_SMOKE_001 --event all --force
  ```
  - `--event` — restrict to a specific event stream (e.g., `login_attempt`) or use `all`.

- **Baselines + evaluation**
  ```bash
  detectlab baselines run -c configs/skynet_smoke.yaml --run-id RUN_SMOKE_001 --force
  detectlab eval run -c configs/skynet_smoke.yaml --run-id RUN_SMOKE_001 --force
  ```
  - `--reuse-if-exists` (if present in configs) allows step runner reuse across runs.

- **Reports and UI bundle**
  ```bash
  detectlab reports build -c configs/skynet_smoke.yaml --run-id RUN_SMOKE_001 --force
  detectlab ui export -c configs/skynet_smoke.yaml --run-ids RUN_SMOKE_001 --out-dir runs/RUN_SMOKE_001/share/ui_bundle --force
  ```
  - `--run-ids` — comma-separated list to bundle multiple runs into one UI export.
  - `--out-dir` — where the HTML bundle is written.

### 2) Health + readiness
- **Doctor (environment diagnostics)**
  ```bash
  detectlab doctor
  ```
  Outputs Python version, platform, pandas/sklearn/pyarrow versions, threadpool counts; exits non-zero if a critical dependency (e.g., `pyarrow`) is missing.

- **Sanity (compile/import + optional tiny run)**
  ```bash
  detectlab sanity --no-tiny-run               # default CI-safe mode
  detectlab sanity -c configs/skynet_smoke.yaml --run-id SANITY_SMOKE_0001 --force  # enables tiny run
  ```
  - `--tiny-run/--no-tiny-run` — toggle artifact-producing tiny pipeline.

- **Parquet requirement gate**
  ```bash
  detectlab config check-parquet
  ```
  Fails if `pyarrow` is unavailable.

## Artifacts and observability
- All outputs live under `runs/<RUN_ID>/`:
  - `raw/`, `dataset/`, `features/`, `models/`, `reports/`
  - `manifest.json` — step metadata + outputs
  - `logs/` — per-step logs
  - `share/ui_bundle/` — exported UI HTML bundle
- Cache cleanup (optional): `tools/cache_prune.sh` wraps `detectlab cache prune`.

## Common parameter tweaks (per run)
- `--force` — overwrite existing artifacts for a run id.
- `--run-id` — namespace outputs; pick meaningful IDs (e.g., `RUN_SMOKE_001`).
- `--config/-c` — swap config files to change data volumes and feature sets.
- `--event` (features) — scope feature generation to a specific event type.
- `--run-ids` (ui export) — export multiple runs together.

## Quick reference (copy/paste)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ."[dev]"
detectlab doctor
detectlab sanity --no-tiny-run
RUN_ID=RUN_SMOKE_001
CFG=configs/skynet_smoke.yaml
detectlab run skynet -c $CFG --run-id $RUN_ID --force
detectlab features build -c $CFG --run-id $RUN_ID --event all --force
detectlab baselines run -c $CFG --run-id $RUN_ID --force
detectlab eval run -c $CFG --run-id $RUN_ID --force
detectlab reports build -c $CFG --run-id $RUN_ID --force
detectlab ui export -c $CFG --run-ids $RUN_ID --out-dir runs/$RUN_ID/share/ui_bundle --force
```
