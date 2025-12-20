# Manual Runs & Checks (Outside the Repo)

This file is meant to be used **by a human** during review / release readiness.

It intentionally avoids “engineering ceremony” language and focuses on **observable checks**.

---

## A) MVP run (single-run sanity)

### 1) Run
```bash
detectlab run mvp -c configs/skynet_mvp.yaml --run-id MVP_CHECK_001 --force
```

### 2) Check artifacts exist
- `runs/MVP_CHECK_001/manifest.json`
- `runs/MVP_CHECK_001/reports/summary.md`
- `runs/MVP_CHECK_001/reports/mvp_handover.md`
- `runs/MVP_CHECK_001/share/ui_bundle/index.html`
- `runs/MVP_CHECK_001/share/evidence_manifest.json`

### 3) Open the UI
Open:
- `runs/MVP_CHECK_001/share/ui_bundle/index.html`

Sanity checks:
- You can switch between **User Holdout** and **Time Eval**
- You can select the available run id
- The page loads without console errors

---

## B) RR determinism check (two-run)

Goal: confirm the share evidence is **comparable** (fingerprinted).

### Windows
```powershell
.\scripts\rr_mvp.ps1 configs\skynet_mvp.yaml RR_MVP_YYYYMMDD_001
```

### macOS/Linux
```bash
bash scripts/rr_mvp.sh configs/skynet_mvp.yaml RR_MVP_YYYYMMDD_001
```

### Check outputs
- `rr_evidence/RR-0001/<BASE_RUN_ID>/...`

Open:
- `rr_evidence/RR-0001/<BASE_RUN_ID>/runs/<RUN_A>/share/evidence_manifest.json`
- `rr_evidence/RR-0001/<BASE_RUN_ID>/runs/<RUN_B>/share/evidence_manifest.json`

Manual check:
- confirm the same paths exist across both manifests
- compare sha256 values for the “core” artifacts:
  - `ui_bundle/index.html`
  - `reports/summary.md`
  - `meta/manifest.json`

If hashes differ:
- check `logs/` for randomness / timestamp noise
- verify that config and run id were identical
- check if any report includes a timestamp that should be deterministic

---

## C) Packaging check (send-to-stakeholder zip)

After an MVP run:

### Windows
```powershell
.\scripts\make_share_zip.ps1 -RunId MVP_CHECK_001
```

### macOS/Linux
```bash
bash scripts/make_share_zip.sh MVP_CHECK_001
```

Unzip it somewhere else (or on another machine), then open:
- `share/ui_bundle/index.html`

The UI should render, with no dependency on the original repo.
