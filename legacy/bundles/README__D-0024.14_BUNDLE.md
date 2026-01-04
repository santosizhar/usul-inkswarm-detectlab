# D-0024.14 — RR Patch: Eval meta initialization

Fixes UnboundLocalError in `run_login_eval_for_run` when the code hits partial paths before `meta` is assigned.

Change:
- Initialize `meta` immediately after function signature.

Apply: unzip over repo, restart kernel.
