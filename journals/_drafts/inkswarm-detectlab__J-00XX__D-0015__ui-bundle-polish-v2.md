# inkswarm-detectlab__J-00XX__D-0015__ui-bundle-polish-v2.md

# J-00XX — D-0015 — UI Bundle Polish v2

**Date:** 2025-12-19  
**Scope:** Stakeholder-grade UI improvements in the shareable HTML bundle.

## Changes delivered
- Truth split messaging made explicit:
  - **user_holdout = generalization to new users (primary)**
  - **time_eval = time drift check (secondary)**
- Added **“Go to run”** dropdown navigation (scrolls to selected run).
- Run signature pills made fail-soft:
  - Missing code hash ⇒ **`Code: (no git)`**
  - Missing config hash ⇒ **`Config: —`**
- Added per-run anchor IDs so navigation can scroll reliably.
- Added an interpretability bullet: “Run signature shows config hash and (if available) code hash”.

## Files changed
- `src/inkswarm_detectlab/ui/bundle.py`

## Acceptance check (intended)
- Landing page clearly communicates the truth split without hunting.
- Users can navigate multiple runs via dropdown.
- Missing git metadata no longer looks like an error in the UI.

## Fail-closed notes
- RR-0001 may remain **ADMIN CLOSED / PROVISIONAL** unless Windows/Py3.12 evidence is recorded.
- D-0004 validation remains deferred unless explicitly validated and journaled.

## Outcome
**D-0015 COMPLETE.**
