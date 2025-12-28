# J-0027 — D-0024.2 — RR patch: wire_check cfg input

## Symptom (RR)
Calling `wire_check(cfg)` raised:

- `AttributeError: 'AppConfig' object has no attribute 'read_text'`

## Root cause
`wire_check` accepted only a config path (`Path`) and passed it to `load_config`.
When given an AppConfig instance, `load_config` treated it as a path and tried to call `read_text`.

## Fix
`wire_check` + `resolve_run_id` now accept either a `Path` or an already-loaded config object.

## Notes
No behavior changes to step execution, reuse policy, or artifact locations.
