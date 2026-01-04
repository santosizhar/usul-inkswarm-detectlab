# J-0010 — D-0005 — Parquet mandatory + BaselineLab hardening

Date: 2025-12-18

## Goal (D-0005 contract)
1) Make **Parquet mandatory** (remove CSV fallback where agreed; keep parquetify upgrade path).
2) Expand / harden BaselineLab and reporting for MVP robustness.
3) Add "maximum possible" validations without running Windows-local deferred validation.

## Key changes
### Parquet-only enforcement
- `write_auto()` is Parquet-only and fail-closed with a clear message if a parquet engine is missing.
- `read_auto()` is Parquet-only (no CSV fallback).
- `read_auto_legacy()` remains only for parquetifying older runs.
- Fixed parquetify bug to write to the `.parquet` target path.

### BaselineLab (login_attempt)
- Default models are now:
  - `logreg`
  - `rf` (RandomForestClassifier)
- HGB kept as **experimental**:
  - Fit happens in a subprocess worker (`inkswarm_detectlab.models.hgb_worker`) so that native crashes become diagnosable.
  - If HGB fails, BaselineLab records `status: failed` in metrics, writes a report, and exits non-zero (fail-closed).
- Added environment diagnostics (`meta.env`) into baseline metrics for crash triage.
- Report rendering now handles model failures explicitly (❌ failed + error message).

### CLI / UX
- Added `detectlab doctor` to print environment diagnostics (Python/platform/sklearn/pandas/pyarrow/threadpools).

### Config updates
- Updated sample configs (`skynet_smoke.yaml`, `skynet_ci.yaml`, `skynet_mvp.yaml`) to use `logreg + rf`.

### Docs updates
- Updated `docs/baselines.md` and deferred validation instructions to reflect:
  - Parquet-only behavior
  - `logreg + rf` defaults
  - HGB experimental / crash behavior
  - `detectlab doctor`
- Updated notebook example run id constant to point to the committed fixture run (`RUN_SAMPLE_SMOKE_0001`).

## Validations performed in this chat
- Python bytecode compile for `src/` (syntax check) passed.
- Full pytest / notebook execution could not be completed in this environment due to missing parquet engine (`pyarrow`).
  - This is expected to pass on the target setup (Python 3.12 + dependencies installed) and in GitHub Actions.

## Follow-ups
- Run the deferred validation steps on Windows after MVP (per CC-0002) and journal outcomes.
