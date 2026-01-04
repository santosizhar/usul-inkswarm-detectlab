# J-0012 — RR-0001 — MVP Release Readiness

**Date:** YYYY-MM-DD  
**Operator:** <name>  
**Env:** Windows / PowerShell / Python 3.12  

## Goal
Close **RR-0001** by running the full MVP pipeline **twice** (Run A and Run B) and confirming determinism via identical RR signatures.

For step-by-step usage and interpretation guidance (non-technical), see:
- `docs/mvp_user_guide.md`

## Run identifiers
- Base run_id: `RR_MVP_YYYYMMDD_001`
- Run A: `RR_MVP_YYYYMMDD_001_A`
- Run B: `RR_MVP_YYYYMMDD_001_B`

## Commands executed

### Option A: helper script (recommended)
```powershell
.\scripts\rr_mvp.ps1
```

### Option B: manual (advanced)
```powershell
# Run A
detectlab run skynet -c configs\skynet_mvp.yaml --run-id RR_MVP_YYYYMMDD_001_A --force
detectlab features build -c configs\skynet_mvp.yaml --run-id RR_MVP_YYYYMMDD_001_A --force
detectlab baselines run -c configs\skynet_mvp.yaml --run-id RR_MVP_YYYYMMDD_001_A --force

# Run B
detectlab run skynet -c configs\skynet_mvp.yaml --run-id RR_MVP_YYYYMMDD_001_B --force
detectlab features build -c configs\skynet_mvp.yaml --run-id RR_MVP_YYYYMMDD_001_B --force
detectlab baselines run -c configs\skynet_mvp.yaml --run-id RR_MVP_YYYYMMDD_001_B --force
```

## Evidence collected
- Evidence directory: `rr_evidence/RR-0001/RR_MVP_YYYYMMDD_001/`
- Evidence summary note: `journals/inkswarm-detectlab__RR_EVIDENCE__RR-0001__RR_MVP_YYYYMMDD_001.md`

Expected evidence files:
- `rr_mvp.log`
- `signature_A.json`
- `signature_B.json`
- `rr_error.txt` (only present on failure)

## Results
- RR status: <PASS/FAIL>
- Determinism signatures identical? <YES/NO>
- Notes on metrics (headline PR-AUC): <value/notes>
- Notes on Recall@1%FPR: <value/notes>

If PR-AUC is unexpectedly low, treat it as a **warning** for MVP (not an RR failure) unless artifacts are missing or determinism fails.

## Follow-ups
- <follow-up items / issues to open / next steps>
