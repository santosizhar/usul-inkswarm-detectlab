# Inkswarm DetectLab

Repo / NS: `inkswarm-detectlab`

DetectLab is a **reproducible detection lab**: it generates synthetic event telemetry, builds leakage-aware datasets, engineers safe aggregate features, and trains/evaluates simple baselines.

If you only read one doc:
- `docs/runbook.md` (canonical “what to run”)

---

## Quickstart (git + run)

```bash
git clone https://github.com/santosizhar/usul-inkswarm-detectlab.git
cd usul-inkswarm-detectlab
git checkout main
git pull
```

Create a virtualenv and install:

```bash
python -m venv .venv
# Windows PowerShell:
#   .\.venv\Scripts\Activate.ps1
# macOS/Linux:
#   source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Run a smoke pipeline (example run id: `RUN_XXX_0005`):

```bash
detectlab run skynet -c configs/skynet_smoke.yaml --run-id RUN_XXX_0005 --force
detectlab features build -c configs/skynet_smoke.yaml --run-id RUN_XXX_0005 --event all --force
detectlab baselines run -c configs/skynet_smoke.yaml --run-id RUN_XXX_0005 --force
```

Expected output:
- `runs/RUN_XXX_0005/reports/summary.md`

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


---

## RR sanity (quick validation)

Use this when you want a fast fail-closed check that the code compiles, imports, and (optionally) can execute a tiny end-to-end run.

```bash
# compile + import checks only (no artifacts)
detectlab sanity --no-tiny-run

# tiny end-to-end (writes under runs/)
detectlab sanity -c configs/skynet_smoke.yaml --run-id SANITY_SMOKE_0001 --force
```

## Code Freeze

- Latest: `CODE_FREEZE__CF-0004.md`  
- Restart prompt: `inkswarm-detectlab__MASTERPROMPT_CF-0004__Code-Freeze-Restart.md`
