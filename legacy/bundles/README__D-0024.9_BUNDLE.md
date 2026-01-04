# D-0024.9 — RR Patch: Notebook cell imports + restart-safe Step 0

Fixes NameError in notebook when running after kernel restart.

Changes:
- Adds a dedicated imports cell after the bootstrap cell.
- Makes Step 0 (wire_check) self-contained: imports + cfg/run_id guards.

How to apply:
1) Unzip over repo
2) Restart kernel
3) Run cells top-down
