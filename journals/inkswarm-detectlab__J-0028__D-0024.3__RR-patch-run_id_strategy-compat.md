# J-0028 — D-0024.3 RR patch (wire_check compatibility)

## Symptom
`wire_check(Path('configs/skynet_smoke.yaml'))` raised:
`AttributeError: 'RunConfig' object has no attribute 'run_id_strategy'`.

## Root cause
The notebook helper `resolve_run_id(...)` assumed a `run_id_strategy` field that is not present in the current `RunConfig` schema.

## Fix
Update `resolve_run_id(...)` to:
- respect an explicit run_id override
- respect pinned `cfg.run.run_id`
- otherwise call `make_run_id(config_hash8, runs_dir=..., prefix=..., width=...)` using existing config fields.

## Notes
This is intentionally minimal and RR-focused; it does not change pipeline behavior, only notebook helper wiring.
