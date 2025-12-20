# RR-0001 Recording Template (Paste-ready)

Use this to record RR-0001 in a fail-closed manner. Replace XXXX with the next journal number.

---

## J-XXXX — RR-0001 — Windows/Python 3.12 Reproducibility & Readiness

**Date:** <YYYY-MM-DD>  
**Target:** Windows + Python 3.12  
**Status:** PASS / FAIL / ADMIN CLOSE (PROVISIONAL)

### Commands run
- <paste exact commands>
- Example:
  - `./scripts/rr_mvp.ps1 -Config "configs/skynet_mvp.yaml" -RunId "RR-0001_<YYYYMMDD>_01"`

### RR outcome
- PASS: signatures match and script reports success
- FAIL: mismatch or runtime error (include reason)
- ADMIN CLOSE (PROVISIONAL): final user chose to proceed without evidence “for now”

### Evidence (authoritative)
If PASS/FAIL:
- `rr_evidence/RR-0001/<run_id>/rr_mvp.log`
- `rr_evidence/RR-0001/<run_id>/signature_A*.json`
- `rr_evidence/RR-0001/<run_id>/signature_B*.json`
- (if FAIL) `rr_evidence/RR-0001/<run_id>/rr_error.txt`

If ADMIN CLOSE:
- Evidence: none recorded yet (explicitly note this)

### Canonical share artifact (send-to-someone)
- `runs/<send_run_id>/share/` zipped as `<send_run_id>__share.zip`
- Note: RR scripts may clean A/B runs; do a dedicated send run if needed.

### Notes / caveats
- Any warnings, performance notes, environment caveats.
- If running from an unpacked zip: `code_sha` may be null (no `.git`).

---

## JM-XXXX — RR-0001 — Meta

### Files
- (list any files changed; usually none)

### Artifacts produced
- `rr_evidence/RR-0001/<run_id>/...`
- `<send_run_id>__share.zip`

### Caveats
- If ADMIN CLOSE: determinism not proven; upgrade to HARD PASS when evidence is later recorded.
