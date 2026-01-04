# D-0024.4 — RR patch: config path fallback for wire_check

## Why
During RR, `wire_check(Path("configs/skynet_smoke.yaml"))` failed with `FileNotFoundError` because the config file
was not found at that exact relative path in the user's working directory (some snapshots place configs under
`configs/configs/`).

## What changed
- `src/inkswarm_detectlab/ui/step_runner.py`
  - `resolve_run_id()` now accepts a `Path` and will:
    1) Use it directly if it exists
    2) If missing and it looks like `configs/<name>.yaml`, try `configs/configs/<name>.yaml`
    3) If still missing, search under `configs/` for a single matching filename and use that

## RR usage
You can keep using:

```python
from pathlib import Path
from inkswarm_detectlab.ui.step_runner import wire_check
print(wire_check(Path("configs/skynet_smoke.yaml")))
```

Even if the actual file lives in `configs/configs/`.
