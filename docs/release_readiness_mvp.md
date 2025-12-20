# Release Readiness — MVP (RR)

The RR gate for the MVP is **full-requirements**:
- run the full pipeline
- produce required artifacts
- run it **twice** and verify determinism

## Preconditions
- Python **3.12**
- Parquet engine available (**pyarrow**)

Quick check:
```bash
python -m inkswarm_detectlab doctor
```

## Run RR (recommended)

### Windows (PowerShell) — repo root
```powershell
.\scripts\rr_mvp.ps1
```

### macOS/Linux — repo root
```bash
./scripts/rr_mvp.sh
```

## Evidence bundle
RR writes evidence under:
- `rr_evidence/RR-0001/<base_run_id>/`

Expected files:
- `rr_mvp.log` — full log output
- `signature_A.json` and `signature_B.json` — determinism signatures
- `rr_error.txt` — present only on failure
- `ui_bundle/` — static stakeholder viewer comparing the two runs (open `index.html`)

RR also writes a short markdown evidence note under:
- `journals/inkswarm-detectlab__RR_EVIDENCE__RR-0001__<base_run_id>.md`

## Failure behavior (fail-closed)
If RR fails:
- it cleans up the run folders (`runs/<run_id>_A`, `runs/<run_id>_B`)
- it leaves `rr_error.txt` under the evidence directory
- it exits non-zero

## MVP baseline set (locked)
- `logreg`
- `rf`

`hgb` is excluded for MVP until the native crash is resolved.

## Required artifacts (per run)
- `runs/<run_id>/manifest.json`
- `runs/<run_id>/reports/summary.md`
- `runs/<run_id>/features/login_attempt/features.parquet`
- `runs/<run_id>/models/login_attempt/baselines/metrics.json`
- `runs/<run_id>/models/login_attempt/baselines/report.md`


### Evidence bundle layout

RR should produce a tidy `runs/<run_id>/share/` folder. This is the preferred artifact to share.
