# D-0024.10 — RR Patch: Notebook default toggles

Fixes NameError when running step cells without having executed the user-input/toggles cell.

Adds a restart-safe defaults cell (after Imports OK) that defines:
- RUN_ID, REUSE_IF_EXISTS
- DO_STEP_*/FORCE_STEP_* toggles
- shared feature cache toggles

Apply: unzip over repo, restart kernel, run notebook top-down.
