# MVP User Guide (Non-Technical)

This guide explains how to **run the MVP**, what it **produces**, and how to **interpret the results**.

If you are not comfortable running commands, ask someone to:
- run the MVP, and
- send you the generated **share package** (a zip).

---

## What you need

- Python **3.12+**
- This repo checked out locally

---

## 1) Install (developer help)

From the repo root:

```bash
python -m venv .venv
# Windows: .\.venv\Scripts\activate
source .venv/bin/activate

pip install -U pip
pip install -e ".[dev]"
```

---

## 2) Run the MVP (one command)

```bash
detectlab run mvp -c configs/skynet_mvp.yaml --run-id MVP_SEND_YYYYMMDD_001 --force
```

Expected output folder:
- `runs/MVP_SEND_YYYYMMDD_001/share/`

---

## 3) Open the results viewer (no server required)

Open this file in your browser:

- `runs/MVP_SEND_YYYYMMDD_001/share/ui_bundle/index.html`

You can switch between:
- **User Holdout** (primary “truth”)
- **Time Eval** (drift check)

---

## 4) Zip the share package (send to someone else)

### Windows (PowerShell)
```powershell
.\scripts\make_share_zip.ps1 -RunId MVP_SEND_YYYYMMDD_001
```

### macOS/Linux (bash)
```bash
bash scripts/make_share_zip.sh MVP_SEND_YYYYMMDD_001
```

This produces a zip next to the run folder (see script output).

---

## 5) What to read (in order)

Inside `runs/<run_id>/share/`:

1) `ui_bundle/index.html` — interactive comparison
2) `reports/mvp_handover.md` — plain-language interpretation
3) `reports/summary.md` — technical summary + known limitations
4) `logs/` — if something failed
5) `meta/manifest.json` + `meta/ui_summary.json` — machine-readable evidence
6) `evidence_manifest.json` — hashes used for determinism checks

---

## 6) How to interpret (3-minute guide)

### Primary truth: User Holdout
Use **User Holdout** to decide if the model generalizes to unseen users.

### Secondary truth: Time Eval
Use **Time Eval** to understand drift exposure (performance over time).

### Red flags
- Metrics improve on train but not on holdout
- Strong performance overall but collapses on key slices (e.g., country/device)
- Threshold stability looks unstable (high variance)

---

## 7) Release Readiness (optional but recommended)

RR runs the MVP **twice** and checks that evidence signatures match.

- Windows: `scripts/rr_mvp.ps1`
- macOS/Linux: `scripts/rr_mvp.sh`

See `docs/runbook.md` for the exact commands and where the RR evidence is written.
