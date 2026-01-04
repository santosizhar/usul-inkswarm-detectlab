# Journal — J-0016 — D-0007 — FeatureLab v1: checkout parity + cross-event context
Date: 2025-12-18

## Goal
Extend FeatureLab beyond `login_attempt` to support:
- `checkout_attempt` feature tables (parity with MVP rolling-aggregate style)
- **symmetric cross-event context** (login history ↔ checkout history), while keeping strict leakage controls.

## Key decisions
- **Default focus remains login-first** for stakeholder friendliness; CLI allows `--event checkout` or `--event all`.
- Checkout “label” for MVP is **derived**:
  - `is_adverse = (checkout_result != "success")`
  - This is intentionally not “fraud” (SKYNET currently sets `is_fraud=False` for checkout events).
- Cross-event context uses strict past-only alignment: interval is **[t-window, t)**.

## What changed
### Code
- `features/builder.py`
  - Added `build_checkout_features(...)`
  - Added cross-event context helpers:
    - `add_cross_event_context(...)`
    - `_cross_event_window_sums(...)`
  - Extended `build_login_features(...)` with optional cross-event context (checkout history).
- `features/runner.py`
  - Added `build_checkout_features_for_run(...)`
  - Updated `build_login_features_for_run(...)` to pass cross-event inputs/config.
- `config/models.py`
  - Added `features.checkout_attempt` config block (with sensible defaults).
  - Added `features.login_attempt.include_cross_event`.
- `cli.py`
  - `detectlab features build` now supports `--event login|checkout|all` (default: `login`).

### Docs
- Updated:
  - `docs/features.md` (new outputs, CLI examples, leakage notes)
  - `docs/getting_started.md` (recommend building `--event all`)
  - `docs/pipeline_overview.md` (checkout supported)
  - `docs/mvp_user_guide.md` (build features for both)

### Tests / validations (within this chat)
- `pytest -q` passed locally **with pyarrow-dependent tests skipped** (this environment lacks pyarrow).
  - Runtime still fail-closed: Feature writing requires parquet support and CLI enforces `_require_pyarrow()`.

## Outputs expected in a run directory
After `detectlab features build --event all`:
- `runs/<run_id>/features/login_attempt/...`
- `runs/<run_id>/features/checkout_attempt/...`
- Updated `runs/<run_id>/manifest.json` artifacts + refreshed `runs/<run_id>/run_summary.md`

## Known limitations
- Checkout baselines are **not** added yet (BaselineLab remains login-focused for MVP).
- Cross-event context currently includes stable counts/rates (and checkout payment_value aggregates where available).
  Additional “advanced” cross-event features can be planned for later if needed.

## Next
Proceed to the next deliverable (postponing DV-0001 as agreed), focusing on feature parity + pipeline separation.
