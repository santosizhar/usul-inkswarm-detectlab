# inkswarm-detectlab__J-00XX__CF-0003__mvp-release-anchor-freeze.md

# J-00XX — CF-0003 — MVP Release Anchor Freeze (Provisional RR)

**Date:** 2025-12-19  
**Scope:** Create a clean restart anchor for the MVP release-candidate state, with explicit fail-closed notes and reproduction steps.

## Inputs
- `CODE_FREEZE__CF-0003.md`
- `inkswarm-detectlab__MASTERPROMPT_CF-0003__Code-Freeze-Restart.md`
- Release candidate docs:
  - `docs/release_candidate_mvp.md`
  - `docs/rr_recording_template.md`
  - `docs/cf_0003_recording_template.md`
- Prior freeze context:
  - `CODE_FREEZE__CF-0002.md`

## Freeze contents (what this anchor represents)
- A documented MVP release candidate path:
  - how to run MVP and create `runs/<run_id>/share/`
  - how to zip and send the canonical artifact
  - how to validate/record RR and how to record CF
- Explicit status declarations (fail-closed) for:
  - RR-0001 (Windows/Py3.12) = provisional if evidence absent
  - deferred validation items (e.g., D-0004) unless evidence exists

## Known caveats (explicit)
- RR-0001 may be **ADMIN CLOSED / PROVISIONAL** (determinism not proven) unless evidence is recorded under `rr_evidence/RR-0001/...`.
- Running from an unpacked zip may result in `code_sha = null` (no `.git`), while `config_hash` remains valid.

## Restart instruction (default next action)
On restart from CF-0003:
1) Confirm whether RR evidence exists; if yes, upgrade to HARD PASS via journaling.
2) Produce a stakeholder share bundle (`runs/<run_id>/share/`), zip it, and send it.
3) Optional: version/tag if working from a git checkout.

## Outcome
**CF-0003 COMPLETE** (restart anchor established).
