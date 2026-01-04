# D-0024.2 — RR Patch: wire_check accepts cfg or path

## Why
During RR, `wire_check` was called with an already-loaded `cfg` object, which raised:

`AttributeError: 'AppConfig' object has no attribute 'read_text'`

because `wire_check` expected a config **path** and attempted to load it again.

## Changes
- `src/inkswarm_detectlab/ui/step_runner.py`
  - `wire_check(...)` now accepts either:
    - a `Path` to a YAML config, **or**
    - an already-loaded config object (AppConfig-like)
  - `resolve_run_id(...)` updated accordingly (same dual-input support)

## RR impact
- You can now run either of these safely:
  - `wire_check(Path("configs/skynet_smoke.yaml"))`
  - `cfg = load_config(...); wire_check(cfg)`

## Validation notes
- This patch is intentionally minimal and does **not** change any core pipeline logic.
