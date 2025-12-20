# MVP_SEND Playbook (D-0014)

This playbook describes how to generate the canonical stakeholder artifact:
`MVP_SEND_<YYYYMMDD>_<NN>__share.zip`

It assumes the repository is unpacked locally on Windows with Python 3.12.

---

## What you will produce
A zip containing `runs/<run_id>/share/`:

- `share/ui_bundle/index.html` (open this)
- `share/reports/summary.md` (headline summary)
- supporting reports (baselines, drift, slices, stability)

**Canonical deliverable:** `MVP_SEND_<YYYYMMDD>_<NN>__share.zip`

---

## Preconditions
- Windows machine
- Python 3.12 installed (`py -3.12`)
- repo unpacked (zip) OR git checkout
- venv recommended

---

## 1) Setup (recommended)
From repo root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e ".[dev]"
python -m inkswarm_detectlab doctor
```

---

## 2) Generate the send run
Choose a run id with date + counter:

Example: `MVP_SEND_20251219_01`

```powershell
python -m inkswarm_detectlab run mvp -c configs\skynet_mvp.yaml --run-id MVP_SEND_<YYYYMMDD>_<NN>
```

Expected output folder:
- `runs\MVP_SEND_<YYYYMMDD>_<NN>\share\`

---

## 3) Zip the share bundle

### Preferred helper (if present)
```powershell
.\scripts\make_share_zip.ps1 -RunId MVP_SEND_<YYYYMMDD>_<NN>
```

### Fallback (built-in PowerShell)
```powershell
Compress-Archive -Path runs\MVP_SEND_<YYYYMMDD>_<NN>\share\* `
  -DestinationPath MVP_SEND_<YYYYMMDD>_<NN>__share.zip -Force
```

---

## 4) Quick verification checklist (2 minutes)
Open:
- `runs\MVP_SEND_<YYYYMMDD>_<NN>\share\ui_bundle\index.html`

Verify:
- UI loads (no blank page)
- Headline truth split is understood:
  - `user_holdout` = primary truth
  - `time_eval` = drift check
- “Run signature” shows `config_hash`
  - `code_sha` may be null if unpacked zip (no `.git`)
- Reports exist:
  - `share/reports/summary.md`
  - baseline + eval reports (as configured)

---

## Status disclosures (fail-closed)
Include these in your stakeholder message if true:
- RR determinism may be **ADMIN CLOSED / PROVISIONAL** (evidence pending)
- D-0004 validation may be deferred unless explicitly recorded

---

## What to send
Send only:
- `MVP_SEND_<YYYYMMDD>_<NN>__share.zip`

Do not send:
- full repo zip (unless requested)
- raw `runs/` directories outside `share/`
