# D-0017 — RR-0002 Final Queue + Evidence Pack

This bundle adds a **single, fail-closed RR procedure** (RR-0002) that includes the **final manual confirmation** steps and interpretation guidance.

## Contents
- `docs/release_readiness/RR-0002__Final-Queue_and_Operator-Guide.md`  
  The end-to-end RR queue (git + unpacked zip modes, MVP + smoke configs), plus the **final manual confirmation** checklist.
- `docs/release_readiness/RR-0002__recording_template.md`  
  Copy/paste template for your **J** entry when you execute RR.
- `docs/rr_evidence/RR-0001/SANDBOX_RR_FAST_001/`  
  **Example-only** evidence bundle from sandbox RR work (format reference, not Windows certification).
- `journals/_drafts/...`  
  D-0017 journal drafts (**J + JM**) to paste/renumber in your repo.

## Where to place files
Copy into repo root, preserving paths.

## Evidence integrity note
Files under `docs/rr_evidence/**` are treated as **immutable evidence** once recorded.  
Do not “polish” or edit them after capture; instead, add clarifying notes in a journal entry.

## Fail-closed reminder
This bundle includes a sandbox evidence example. It is **not** proof of Windows/Python 3.12 reproducibility.
