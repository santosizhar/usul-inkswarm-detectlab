# Inkswarm DetectLab

Repo / NS: `inkswarm-detectlab`

DetectLab is a **reproducible detection lab**: it generates synthetic event telemetry, builds leakage-aware datasets, engineers safe aggregate features, and trains/evaluates simple baselines.

If you only read one doc:
- `docs/runbook.md` (canonical “what to run”)

---

## Locked MVP constraints (summary)

- Targets: `login_attempt`, `checkout_attempt` (event-level)
- `support` is embedded inside `login_attempt` (not a separate event)
- Primary entity id: `user_id` (no `account_id`)
- Canonical timezone: `America/Argentina/Buenos_Aires`
- Default artifact format: Parquet (**mandatory** as of D-0005; no CSV fallback)

---

## Quickstart (developer)

```bash
python -m venv .venv
# Windows: .\.venv\Scripts\activate
source .venv/bin/activate

pip install -U pip
pip install -e ".[dev]"

python -m compileall src
pytest -q
detectlab --help
```

---

## Fast smoke run

```bash
detectlab run skynet -c configs/skynet_smoke.yaml --run-id RUN_SMOKE_001 --force
detectlab features build -c configs/skynet_smoke.yaml --run-id RUN_SMOKE_001 --event all --force
detectlab baselines run -c configs/skynet_smoke.yaml --run-id RUN_SMOKE_001 --force
detectlab eval run -c configs/skynet_smoke.yaml --run-id RUN_SMOKE_001 --force
detectlab reports build -c configs/skynet_smoke.yaml --run-id RUN_SMOKE_001 --force
```

---

## MVP one-command run (portfolio demo)

```bash
detectlab run mvp -c configs/skynet_mvp.yaml --run-id MVP_001 --force
```

Open:
- `runs/MVP_001/share/ui_bundle/index.html`

Zip the share package:
- Windows: `scripts/make_share_zip.ps1 -RunId MVP_001`
- macOS/Linux: `bash scripts/make_share_zip.sh MVP_001`

---

## Code Freeze

- Latest: `CODE_FREEZE__CF-0004.md`  
- Restart prompt: `inkswarm-detectlab__MASTERPROMPT_CF-0004__Code-Freeze-Restart.md`
