# Code Freeze (CF)

A Code Freeze is a deliberate snapshot point for safe handoff/restart.

## What you get at CF-0001
- A full repository snapshot through **D-0004**
- Journals summarizing decisions and deliverables
- A restart masterprompt for a new chat:
  - `inkswarm-detectlab__MASTERPROMPT_CF-0001__Code-Freeze-Restart.md`

## Deferred validation (D-0004)
This freeze includes D-0004 “closed with deferred validation”.
Run validation later using:

- `DEFERRED_VALIDATION__D-0004.md`
- `scripts/validate_d0004.ps1` (Windows)
- `scripts/validate_d0004.sh` (macOS/Linux)

## Typical CF checklist
- Ensure docs explain how to run: synthetic → features → baselines
- Ensure config examples exist (`configs/skynet_smoke.yaml`, `configs/skynet_ci.yaml`)
- Ensure journals are up to date
- Ensure restart prompt exists and points to canonical docs

## How to resume work
1) Start a new chat with `inkswarm-detectlab__MASTERPROMPT_CF-0001__Code-Freeze-Restart.md` and attach this repository zip.
2) Choose Start-coding vs No-code mode when asked.
3) Run deferred validation and record results.
4) Continue with the next deliverable (D-0005).


## Latest freeze
- **CF-0002**: See `CODE_FREEZE__CF-0002.md` and restart prompt `inkswarm-detectlab__MASTERPROMPT_CF-0002__Code-Freeze-Restart.md`.
