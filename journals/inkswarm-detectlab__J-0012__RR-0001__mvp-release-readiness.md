# J-0012 — RR-0001 — MVP Release Readiness

**Date:** YYYY-MM-DD
**Operator:** <name>
**Env:** Windows / PowerShell / Python 3.12

## Goal
Close **RR-0001** by running the full MVP pipeline **twice** (`_A` and `_B`) and confirming determinism via identical RR signatures.

## Run identifiers
- Base run_id: `RR_MVP_YYYYMMDD_001`
- Run A: `RR_MVP_YYYYMMDD_001_A`
- Run B: `RR_MVP_YYYYMMDD_001_B`

## Commands executed
### Option A: helper script (recommended)
```powershell
.\scripts\rr_mvp.ps1
```

### Option B: manual
```powershell
detectlab run skynet -c configs\skynet_mvp.yaml --run-id RR_MVP_YYYYMMDD_001_A
detectlab features build -c configs\skynet_mvp.yaml --run-id RR_MVP_YYYYMMDD_001_A --force
detectlab baselines run -c configs\skynet_mvp.yaml --run-id RR_MVP_YYYYMMDD_001_A --force

detectlab run skynet -c configs\skynet_mvp.yaml --run-id RR_MVP_YYYYMMDD_001_B
detectlab features build -c configs\skynet_mvp.yaml --run-id RR_MVP_YYYYMMDD_001_B --force
detectlab baselines run -c configs\skynet_mvp.yaml --run-id RR_MVP_YYYYMMDD_001_B --force

python -m inkswarm_detectlab.tools.rr_signature --run-id RR_MVP_YYYYMMDD_001_A --out rr_evidence\RR-0001\RR_MVP_YYYYMMDD_001\signature_A.json
python -m inkswarm_detectlab.tools.rr_signature --run-id RR_MVP_YYYYMMDD_001_B --out rr_evidence\RR-0001\RR_MVP_YYYYMMDD_001\signature_B.json
```

## Validation checklist
- [ ] `python -m inkswarm_detectlab doctor` output saved (in RR evidence log)
- [ ] Run A produced required artifacts
- [ ] Run B produced required artifacts
- [ ] Signatures identical (`signature_A.json == signature_B.json`)
- [ ] Evidence summary written to `journals/inkswarm-detectlab__RR_EVIDENCE__RR-0001__<base_run_id>.md`

## Outcomes
### Determinism
- Status: <PASS/FAIL>
- Notes: <if failed, reference rr_error.txt and rr_mvp.log>

### Baseline results (MVP)
Note: unusually low PR-AUC is **warning-only** for MVP RR, but still record it here.

- LogReg:
  - train PR-AUC: <value>
  - time_eval PR-AUC: <value>
  - user_holdout PR-AUC: <value>
- RandomForest:
  - train PR-AUC: <value>
  - time_eval PR-AUC: <value>
  - user_holdout PR-AUC: <value>

## Evidence pointers
- Evidence bundle: `rr_evidence/RR-0001/<base_run_id>/`
- RR log: `rr_evidence/RR-0001/<base_run_id>/rr_mvp.log`
- RR error (if any): `rr_evidence/RR-0001/<base_run_id>/rr_error.txt`

## How to use the MVP (required reference)
After RR completes, use these docs to run and interpret the MVP:
- `docs/mvp_usage.md` — install, run commands, output locations, and how to interpret results.
- `docs/getting_started.md` — project overview and first commands.
- `docs/baselines.md` — what the baselines do and how to read the report.
- `docs/release_readiness_mvp.md` — the RR gate definition.
