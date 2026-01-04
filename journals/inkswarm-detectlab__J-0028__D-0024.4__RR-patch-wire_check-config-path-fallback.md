# J-0028 — D-0024.4 RR patch: wire_check config path fallback

## Trigger
RR attempt failed with `FileNotFoundError` for `configs/skynet_smoke.yaml` on the user's machine.

## Root cause
Repo snapshots can contain configs in either:
- `configs/<name>.yaml` (expected), or
- `configs/configs/<name>.yaml` (nested), depending on how the zip was assembled/unpacked.

## Fix
`resolve_run_id()` now:
- accepts a Path or cfg
- when Path is missing, tries the common nested path (`configs/configs/<name>.yaml`)
- if still missing, attempts a best-effort single-match lookup under `configs/`.

## RR impact
Wire-check and the step notebook can be executed without the user needing to hunt for the correct config path.
