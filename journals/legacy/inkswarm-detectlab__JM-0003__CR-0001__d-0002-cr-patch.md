# CR-0001 — D-0002 CR Patch — Mini Journal (JM-0003)

Date: 2025-12-16  
NS: inkswarm-detectlab

## What changed
- Replaced Python `hash()` usage with **stable SHA256-based** identifiers for deterministic IDs.
- Added **canonicalize-before-write-and-hash** (stable sort + schema column order).
- Checkout adverse assignment is now **deterministic exact-k** to reduce variance in small runs.
- `write_auto()` now reports actual **format written** (`parquet` or `csv`) + fallback note.
- Manifest + summary now include **Outputs written** with format + fallback note.
- CLI improvements:
  - `detectlab config validate` (prints `OK`)
  - `detectlab config show` (prints resolved YAML)
  - `--config/-c` supported + artifact output listing after runs
- CI now runs a tiny end-to-end smoke pipeline via `configs/skynet_ci.yaml`.
- Added `ipykernel` to `.[dev]` so notebook execution tests have a kernel in CI.
- Regenerated `runs/RUN_SAMPLE_SMOKE_0001` fixture to match the new behavior.

## Result
You get a cleaner developer UX + clearer artifact reporting, and a tighter determinism contract without changing the public pipeline surface.
