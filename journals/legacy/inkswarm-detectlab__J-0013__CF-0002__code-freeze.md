# J-0013 — CF-0002 — Code Freeze

**Project:** Inkswarm DetectLab (inkswarm-detectlab)  
**Date:** 2025-12-18  
**Timezone:** America/Argentina/Buenos_Aires  
**Ceremony:** Code Freeze (CF-0002)

## Why this freeze
We reached a stable, reproducible MVP-prep state:
- Parquet-only pipeline is enforced.
- Baselines are locked to MVP-supported `logreg + random_forest`.
- HGB is explicitly excluded until crash is resolved.
- RR-0001 is prepared with two-run determinism + evidence bundles + cleanup-on-failure.

This freeze creates a restartable snapshot and a restart masterprompt so work can resume in a fresh chat without context loss.

## What was included
- All deliverables through D-0005 and CR-0002.
- RR-0001 preparation scripts and docs (not executed here on target Windows).
- Updated docs with placeholders removed and runnable commands.
- Code Freeze restart masterprompt: `inkswarm-detectlab__MASTERPROMPT_CF-0002__Code-Freeze-Restart.md`

## What remains open
- RR-0001 must be executed locally on Windows 3.12 to close validation.
- D-0004 validation remains deferred until RR is run on target.
- HGB crash investigation remains deferred.

## Next recommended step
Run RR-0001 locally using `scripts/rr_mvp.ps1`, then write J + JM with results and proceed to MVP release steps.

