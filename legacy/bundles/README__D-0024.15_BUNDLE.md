# D-0024.15 — RR Patch: Eval meta unconditional

Fixes `UnboundLocalError: meta` in `run_login_eval_for_run`.

Root cause:
- `meta` was initialized only inside the early-return cache hit branch. On normal runs (no cached reports yet),
  the code later referenced `meta` on partial paths (e.g., missing models) before initialization.

Fix:
- Initialize `meta` unconditionally near the top of the function.
