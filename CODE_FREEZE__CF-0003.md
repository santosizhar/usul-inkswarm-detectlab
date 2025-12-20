# CODE FREEZE — CF-0003 — Inkswarm DetectLab (inkswarm-detectlab)

**Date:** 2025-12-19  
**Purpose:** Post-MVP freeze anchor (recommended after RR-0001 hard PASS and a sendable share zip exists).

> Fail-closed: do not claim RR or validations passed unless evidence is present (logs/signatures).

## Freeze snapshot summary
- Target environment: **Windows + Python 3.12**
- MVP command: `detectlab run mvp -c configs/skynet_mvp.yaml`
- Canonical stakeholder artifact: `runs/<run_id>/share/` zipped as `<run_id>__share.zip`
- RR evidence path: `rr_evidence/RR-0001/<base_run_id>/`

## Preconditions checklist (must be true at freeze time)
- [ ] RR-0001 executed locally on Windows + Python 3.12
- [ ] RR evidence folder exists with `rr_mvp.log` + `signature_A.json` + `signature_B.json`
- [ ] `journals/inkswarm-detectlab__RR_EVIDENCE__RR-0001__<base_run_id>.md` exists
- [ ] A *single-run* send bundle exists: `runs/<send_run_id>/share/`
- [ ] Share bundle zipped: `<send_run_id>__share.zip`
- [ ] Deferred validations are explicitly tracked (e.g., D-0004)

## Notes
- Running from an unpacked zip may result in `code_sha = null`. In that case rely on:
  - `config_hash` in the run manifest
  - `signature_digest` (RR v2)
- Keep this file updated with the actual `<base_run_id>` and `<send_run_id>` when known.
