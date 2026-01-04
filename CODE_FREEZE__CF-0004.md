# CODE_FREEZE__CF-0004.md

**Project:** Inkswarm DetectLab  
**NS:** inkswarm-detectlab  
**Freeze ID:** CF-0004  
**Date:** 2025-12-19  
**Type:** Docs + Procedure Anchor (fail-closed)

---

## What this freeze is
This freeze is a **restart anchor** for the project state after integrating the RR-0002 operator guide and recording template.

This freeze intentionally **does not claim**:
- Windows/Python 3.12 determinism has been proven (unless you add evidence under `docs/rr_evidence/RR-0002/...`).
- End-to-end MVP execution was performed in this chat.

---

## Included artifacts (in this freeze bundle)
- `docs/release_readiness/RR-0002__Final-Queue_and_Operator-Guide.md`
- `docs/release_readiness/RR-0002__recording_template.md`
- Example evidence format (sandbox only):
  - `docs/rr_evidence/RR-0001/SANDBOX_RR_FAST_001/`
- Journal drafts (placeholders) for D-0017 and CF-0004.

---

## Current status summary (fail-closed)
- RR-0001 may have been **administratively closed** earlier; treat it as **PROVISIONAL** unless Windows/Py3.12 evidence exists.
- RR-0002 is the **current canonical RR queue** and must be executed on Windows/Py3.12 for a hard readiness claim.
- Deferred validations remain deferred unless explicitly recorded (e.g., D-0004 baseline validation).

---

## Default next actions after restart from CF-0004
1) Execute **RR-0002** on Windows/Py3.12 in:
   - Git mode
   - Unpacked zip mode  
   Record evidence and screenshots under `docs/rr_evidence/RR-0002/YYYYMMDD/`.
2) Produce a canonical stakeholder artifact:
   - `MVP_SEND_YYYYMMDD_01__share.zip`
3) If RR-0002 HARD PASS is achieved:
   - proceed to version/tag and optionally create CF-0005 as a clean post-RR anchor.

---

## Integrity rules
- Evidence folders `docs/rr_evidence/**` are immutable once recorded.
- Never claim “green” unless tests were run and outputs were captured.
