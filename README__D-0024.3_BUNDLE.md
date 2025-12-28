# D-0024.3 — RR patch: wire_check run_id generation compatibility

This is a minimal RR unblock patch on top of D-0024.2.

## Fixes
- `wire_check(...)` / `resolve_run_id(...)` no longer assume `cfg.run.run_id_strategy` exists.
- Run id generation now matches current config schema:
  - supports pinned `cfg.run.run_id`
  - otherwise generates `PREFIX_0001` style ids using `cfg.run.run_id_prefix` + `cfg.run.run_id_width`
  - uses `utils.run_id.make_run_id(config_hash8, runs_dir=..., prefix=..., width=...)`

## Why
Some environments/config schemas (e.g., `skynet_smoke.yaml`) do not define `run_id_strategy`. The previous RR helper attempted to read it and failed before notebook execution.

## Validation
- `python -m compileall -q src`
- `python -c "from inkswarm_detectlab.ui.step_runner import wire_check; from pathlib import Path; print(wire_check(Path('configs/skynet_smoke.yaml'))['run_dir'])"`
