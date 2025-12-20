# Getting Started

This is the minimal “sanity check” path. For a full end-to-end validation, use the **Release Readiness** scripts:
- `docs/release_readiness_mvp.md`

## Install (Python 3.12)

### Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e ".[dev]"
```

### macOS/Linux
```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
```

## Quick verification
```bash
detectlab --help
pytest -q
python -m inkswarm_detectlab doctor
```

## Run the smallest smoke path
```bash
detectlab run skynet -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force
detectlab features build -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --event all --force
detectlab baselines run -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force
```

## Legacy conversion (only if you have old CSV runs)
```bash
detectlab dataset parquetify -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force
```


## What to open after a run
- `runs/<RUN_ID>/share/OPEN_ME_FIRST.md`
- `runs/<RUN_ID>/share/ui_bundle/index.html`
- `runs/<RUN_ID>/share/EXEC_SUMMARY.html`
- `runs/<RUN_ID>/share/summary.html`
