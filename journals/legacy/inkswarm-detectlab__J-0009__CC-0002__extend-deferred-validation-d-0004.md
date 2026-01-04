# J-0009 — CC-0002 — Extend deferred validation for D-0004

Date: 2025-12-18

## Trigger
User decision for this restart:
- Running on Windows.
- Will **not** run Deferred Validation for D-0004 now.
- Will validate locally **after MVP**.
- Proceed directly into **D-0005**.

This extends the original CC-0001 deferral window ("validate later") into an explicit **post-MVP** commitment.

## Decision
- Accept deferral extension.
- Proceed with D-0005 while adding **maximum possible validations** without executing the full deferred validation locally.

## Risk
- D-0004 baseline code paths (especially platform-specific ML backends) may still contain issues that would otherwise be caught by running the full validation suite on the target machine.

## Mitigations (implemented in D-0005)
- Make Parquet **mandatory** (fail-closed) with clear error messages.
- Add `detectlab doctor` to print environment diagnostics.
- Record environment diagnostics under `meta.env` in baseline metrics.
- Keep HGB as **experimental** and fit it in a **subprocess worker** so crashes become diagnosable (parent records failure + exits non-zero).
- CI continues to run the smoke pipeline on Linux with Python 3.12.

## Follow-ups
- After MVP: run `DEFERRED_VALIDATION__D-0004.md` end-to-end on the Windows machine and journal results.
