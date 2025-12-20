# Runbook — What to Run (Canonical)

This is the **single canonical “what to run” page** for DetectLab.

It is written for:
- **developers** (who will run locally), and
- **portfolio reviewers / stakeholders** (who want a reproducible demo).

---

## 0) Prerequisites

- Python **3.12+**
- Disk space: a few hundred MB for multiple runs.

DetectLab writes artifacts under:
- `runs/<run_id>/...`

---

## 1) Install (developer)

From the repo root:

```bash
python -m venv .venv
# Windows: .\.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -U pip
pip install -e ".[dev]"
```

Sanity check:

```bash
python -m compileall src
pytest -q
detectlab --help
```

---

## 2) Fast smoke run (recommended first)

This generates a tiny synthetic dataset and trains baselines.

```bash
# 1) Generate raw + dataset (also writes reports/summary.md)
detectlab run skynet -c configs/skynet_smoke.yaml --run-id RUN_SMOKE_001

# 2) Feature build
detectlab features build -c configs/skynet_smoke.yaml --run-id RUN_SMOKE_001 --event all --force

# 3) Baselines (login_attempt)
detectlab baselines run -c configs/skynet_smoke.yaml --run-id RUN_SMOKE_001 --force

# 4) Eval diagnostics (slices + stability)
detectlab eval run --config configs/skynet_smoke.yaml --run-id RUN_SMOKE_001 --force
```

Expected outputs (high level):

- `runs/RUN_SMOKE_001/raw/*.parquet`
- `runs/RUN_SMOKE_001/dataset/.../*.parquet`
- `runs/RUN_SMOKE_001/features/.../*.parquet`
- `runs/RUN_SMOKE_001/models/.../metrics.json`
- `runs/RUN_SMOKE_001/reports/summary.md`
- `runs/RUN_SMOKE_001/reports/eval_*_login_attempt.md`

Optional: export a UI bundle for this run into the run folder:

```bash
detectlab ui export -c configs/skynet_smoke.yaml --run-ids RUN_SMOKE_001 --out-dir runs/RUN_SMOKE_001/share/ui_bundle --force
```

---

## 3) MVP “one command” run (shareable artifacts)

This is the **portfolio demo flow** (end-to-end + UI bundle + share package):

```bash
detectlab run mvp -c configs/skynet_mvp.yaml --run-id MVP_001 --force
```

Then open:

- `runs/MVP_001/share/ui_bundle/index.html`

This should exist:

- `runs/MVP_001/share/evidence_manifest.json`
- `runs/MVP_001/share/reports/summary.md`
- `runs/MVP_001/share/reports/mvp_handover.md`

---

## 4) Zip the share package (send to someone else)

### Windows (PowerShell)

```powershell
.\scripts\make_share_zip.ps1 -RunId MVP_001
```

### macOS/Linux (bash)

```bash
bash scripts/make_share_zip.sh MVP_001
```

---

## 5) Release Readiness (RR) — determinism (two-run)

This runs the MVP **twice** and checks that evidence signatures match.

### Windows (PowerShell)
```powershell
.\scripts\rr_mvp.ps1 configs\skynet_mvp.yaml RR_MVP_YYYYMMDD_001
```

### macOS/Linux (bash)
```bash
bash scripts/rr_mvp.sh configs/skynet_mvp.yaml RR_MVP_YYYYMMDD_001
```

Outputs:
- `rr_evidence/RR-0001/<BASE_RUN_ID>/...` (signatures + logs)
- `journals/inkswarm-detectlab__RR_EVIDENCE__RR-0001__<BASE_RUN_ID>.md`

---

## 6) If something fails (where to look)

- Run logs: `runs/<run_id>/logs/`
- Reports: `runs/<run_id>/reports/summary.md`
- Evidence bundle: `runs/<run_id>/share/evidence_manifest.json`
- CI: `.github/workflows/ci.yml`
