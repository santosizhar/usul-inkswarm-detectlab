# CODE FREEZE — CF-0001 — Inkswarm DetectLab (inkswarm-detectlab)

Date: 2025-12-17
Status: **Frozen snapshot for handoff / restart**

## What this Code Freeze is
This repository snapshot is intended to be a stable handoff point.
It includes deliverables through **D-0004** and the documentation/journals needed to restart work in a new chat.

## What is DONE
- **D-0001**: repo skeleton + docs structure + CI scaffold
- **D-0002**: SKYNET synthetic generator + dataset build (train/time_eval/user_holdout), manifests, summaries
- **CR-0001**: determinism tightening, canonicalization, improved CLI help + config show/validate, CI smoke run
- **D-0003**: FeatureLab v0 for `login_attempt` only
  - safe aggregate features for `user_id`, `ip_hash`, `device_fingerprint_hash`
  - windows: 1h / 6h / 24h / 7d
  - labels included, `metadata_json` excluded
  - CLI: `detectlab features build ... --run-id ...`
- **D-0004**: BaselineLab v0 for `login_attempt`
  - sklearn LogReg + HistGradientBoosting
  - headline metric: PR-AUC
  - operating point: Recall @ 1% FPR (threshold chosen on Train)
  - CLI: `detectlab baselines run ... --run-id ...`

## What is DEFERRED / NOT VERIFIED here
- D-0004 was **closed with deferred validation** (tests and end-to-end run were not verified in-chat).
- Validation must be run locally later using instructions in:
  - `DEFERRED_VALIDATION__D-0004.md`
  - `scripts/validate_d0004.ps1` (Windows)
  - `scripts/validate_d0004.sh` (macOS/Linux)

## Known defaults / conventions (locked)
- Timezone standard: **America/Argentina/Buenos_Aires**
- ID standard: unified `user_id`
- Raw formats: parquet preferred; CSV fallback exists until the Parquet-mandatory flip
- Features: strict past-only, safe aggregates only in v0
- Modelling: OVR multi-head (replicators/mule/chameleon); benign is implied

## Next recommended steps after unfreezing
1) **Run deferred validation** and record results (new J + JM).
2) **D-0005**: make Parquet mandatory and tighten pipeline guarantees.
3) **CR-0002**: review baselines robustness, reporting clarity, and packaging.
4) **RR**: release readiness for MVP (reproducible demo run + docs).
5) **CF**: after MVP release (if you choose to refreeze later).

## Restart prompt
Use: `inkswarm-detectlab__MASTERPROMPT_CF-0001__Code-Freeze-Restart.md`
