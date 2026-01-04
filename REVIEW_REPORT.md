# REVIEW REPORT

## Repo map (quick)
- `src/inkswarm_detectlab/`: core CLI and pipeline modules (`detectlab` entrypoint via `python -m inkswarm_detectlab`).
- `configs/`: runnable configs for smoke/MVP runs.
- `docs/`: runbook, repo map, ceremonies, readiness docs.
- `tests/`: pytest suite covering CLI flags, schemas, cache ops, sharing, UI pieces.
- `runs/`, `runs_ci/`: sample artifacts and CI fixtures.
- `scripts/`: helper scripts for packaging and evidence handling.

## Code track
### Findings
- Duplicate best-effort JSON/text readers lived in `reports.runner`, `reports.exec_summary`, and `cache.ops`, risking drift between behaviors. **Risk:** Low.
- Wrapper helpers inside `reports.runner` simply forwarded to `safe_io`, adding indirection without benefit. **Risk:** Low.
- `safe_io` lacked targeted tests, so regressions around defaults or malformed input would go unnoticed. **Risk:** Low.
- Notebook/UI helpers (`ui.step_runner`, `ui.summarize`) duplicated JSON reading logic and did not use the shared `safe_io` helpers, risking silent divergence. **Risk:** Low.
- RR tooling (signature/evidence) used bespoke strict JSON reads without shared diagnostics, making failures harder to triage and drifting from documented policy. **Risk:** Low.

### Implemented changes
- Added shared `utils.safe_io` helpers for safe text/JSON reads and routed reporting/cache modules through them to keep behavior consistent and easier to test. **Why:** removes redundancy and centralizes error handling. 【F:src/inkswarm_detectlab/utils/safe_io.py†L1-L23】【F:src/inkswarm_detectlab/reports/exec_summary.py†L8-L16】【F:src/inkswarm_detectlab/cache/ops.py†L9-L13】
- Simplified `reports.runner` to call `safe_io` directly, removing redundant wrappers for clearer behavior tracing. **Why:** reduce unnecessary indirection. 【F:src/inkswarm_detectlab/reports/runner.py†L13-L17】【F:src/inkswarm_detectlab/reports/runner.py†L221-L249】
- Added unit coverage for `safe_io` defaults and malformed inputs to guard the shared helpers. **Why:** ensure future refactors keep the same error-tolerant semantics. 【F:tests/test_safe_io.py†L1-L32】
- UI helpers now call the shared best-effort JSON reader and include focused tests to confirm missing/invalid files no longer crash notebook flows. **Why:** reduce drift from reporting/cache behavior and harden UI surfaces. 【F:src/inkswarm_detectlab/ui/step_runner.py†L53-L59】【F:src/inkswarm_detectlab/ui/summarize.py†L13-L24】【F:tests/test_ui_safe_io.py†L1-L26】
- Introduced a strict JSON reader for RR tooling, adopted by `tools/rr_signature.py` and `tools/rr_evidence_md.py`, and documented the policy split between best-effort and fail-closed surfaces. **Why:** unify diagnostics for determinism/evidence tools while keeping operator flows resilient. 【F:src/inkswarm_detectlab/utils/safe_io.py†L25-L47】【F:src/inkswarm_detectlab/tools/rr_signature.py†L18-L21】【F:src/inkswarm_detectlab/tools/rr_evidence_md.py†L16-L21】【F:docs/runbook.md†L37-L48】

## Docs/journals track
### Findings
- Root README and bundle index still pointed at CF-0004 even though CF-0005 exists, risking stale ceremony pointers. **Risk:** Low.

### Implemented changes
- Updated README and bundle index to reference the latest CF-0005 freeze and restart prompt. **Why:** reduce confusion on the current anchor. 【F:README.md†L13-L24】【F:README__D-0024_INDEX.md†L23-L24】
- Appended maintainer status addenda (current status, strengths, weaknesses, next actions) to the latest code-freeze journal for visibility. **Why:** capture audit snapshot per instructions. 【F:CODE_FREEZE__CF-0005.md†L85-L126】
- Added a 2026-01-04 status addendum capturing the UI JSON consolidation and remaining risks. **Why:** keep the freeze journal aligned with the latest audit. 【F:CODE_FREEZE__CF-0005.md†L127-L147】
- Added a 2026-01-05 addendum plus a runbook JSON I/O policy to document strict vs. best-effort expectations across tooling and UI surfaces. **Why:** make future extensions follow consistent failure semantics. 【F:CODE_FREEZE__CF-0005.md†L148-L169】【F:docs/runbook.md†L37-L48】

### Docs Changelog
- README ceremony pointers now target CF-0005.
- README__D-0024_INDEX updated with CF-0005 links.
- CODE_FREEZE__CF-0005 includes 2026-01-02, 2026-01-03, 2026-01-04, and 2026-01-05 status addenda.
- Runbook now documents JSON I/O policy for best-effort vs. strict tooling.

## Verification
- `python -m compileall src` (pass). 【d94525†L1-L74】
- `pytest -q` (pass). 【d25426†L1-L1】

## Notes / high-risk items left untouched
- No automated end-to-end smoke run in CI; current tests are unit-heavy and may miss full-pipeline regressions.
- Report/share rendering still relies on custom Markdown→HTML glue with limited dedicated tests; future refactors should add coverage before larger changes.
- Strict JSON helper is only applied to RR evidence/signature; broader tooling surfaces may need adoption once their failure expectations are clarified.
