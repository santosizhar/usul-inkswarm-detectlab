# Inkswarm DetectLab

Repo / NS: `inkswarm-detectlab`

DetectLab is a **reproducible detection lab**: it generates synthetic event telemetry, builds leakage-aware datasets, engineers safe aggregate features, and trains/evaluates simple baselines.

If you only read one doc:
- `docs/runbook.md` (canonical “what to run”)

## Repo map (first look)
- `src/` — application code and CLI (`detectlab`)
- `configs/` — runnable configs (smoke + MVP)
- `docs/` — runbook, readiness, and troubleshooting
- `tests/` — unit/regression tests
- `runs/` — run artifacts (reports, manifests, caches)
- Ceremony: see `CODE_FREEZE__CF-0005.md` (latest) and `inkswarm-detectlab__MASTERPROMPT_CF-0005__Code-Freeze-Restart.md`
- History bundles: latest bundle `README__D-0024.15_BUNDLE.md`; index of older bundles at `README__D-0024_INDEX.md`.

### Entry points
- CLI: `detectlab` (`python -m inkswarm_detectlab`), see `detectlab --help`
- Runbook: `docs/runbook.md`
- Quickstart + verification: `docs/getting_started.md`
- Bundle index + ceremony anchors: `README__D-0024_INDEX.md`, `CODE_FREEZE__CF-0005.md`

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
- Artifacts for most commands live under `runs/<RUN_ID>/`; manifests are written to `runs/<RUN_ID>/manifest.json`.
- Logs for each step: `runs/<RUN_ID>/logs/`
- UI bundle (when exported): `runs/<RUN_ID>/share/ui_bundle/index.html`

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
detectlab doctor
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

- Latest: `CODE_FREEZE__CF-0005.md`
- Restart prompt: `inkswarm-detectlab__MASTERPROMPT_CF-0005__Code-Freeze-Restart.md`

## Hygiene & ops notes
- Dependency drift: run `tools/dependency_check.sh` (prints `pip check` + outdated list) and review `requirements.lock` when bumping deps.
- Secret hygiene: run your preferred scanner (e.g., `gitleaks detect --no-git`) before committing.
- Cache cleanup: `tools/cache_prune.sh` wraps `detectlab cache prune` for automated cleanup.
- Artifact retention: see `docs/artifact_retention.md` for cleanup and cache guidance.
- Secrets scanning guidance: `docs/secrets_scanning.md`.
