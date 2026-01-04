# CODE_FREEZE__CF-0003 — MVP Release Anchor (Provisional RR)

**Date:** 2025-12-19  
**Project:** Inkswarm DetectLab (`inkswarm-detectlab`)  
**Intent:** Freeze anchor for MVP release candidate state + restart safety.

---

## 1) What this freeze includes
- MVP pipeline artifacts and documentation sufficient to:
  - run MVP (`detectlab run mvp`)
  - produce a stakeholder share bundle (`runs/<run_id>/share/`)
  - package and send `runs/<run_id>/share/` as a zip
- Release-candidate procedure and recording templates:
  - `docs/release_candidate_mvp.md`
  - `docs/rr_recording_template.md`
  - `docs/cf_0003_recording_template.md`

---

## 2) Current authoritative status (fail-closed)

### RR-0001 (Windows + Python 3.12)
- **Status:** CLOSED (ADMIN OVERRIDE / PROVISIONAL) — evidence pending
- **Meaning:** determinism and Windows reproducibility are **not proven** in-repo.
- **Upgrade path:** run RR locally and record evidence under `rr_evidence/RR-0001/...`, then journal HARD PASS.

### D-0004 validation
- Remains deferred unless/until explicit validation outputs are recorded.

---

## 3) Repro instructions (Windows / Python 3.12 target)

### Setup
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e ".[dev]"
python -m inkswarm_detectlab doctor
```

### Produce the canonical stakeholder artifact
```powershell
python -m inkswarm_detectlab run mvp -c configs\skynet_mvp.yaml --run-id MVP_SEND_<YYYYMMDD>_01
```

Zip the share bundle:
```powershell
Compress-Archive -Path runs\MVP_SEND_<YYYYMMDD>_01\share\* -DestinationPath MVP_SEND_<YYYYMMDD>_01__share.zip -Force
```

Open the UI:
- `runs\MVP_SEND_<YYYYMMDD>_01\share\ui_bundle\index.html`

---

## 4) Known caveats
- Running from an unpacked zip may result in `code_sha = null` (no `.git`).
- RR determinism is provisional until evidence is captured.
- Any performance numbers are scenario-dependent; treat as illustrative unless measured and recorded.

---

## 5) Restart instruction
Use:
- `inkswarm-detectlab__MASTERPROMPT_CF-0003__Code-Freeze-Restart.md`

Default next action after restart:
- confirm RR evidence status (if still provisional, proceed with release as provisional)
- then: produce/send share bundle as needed
