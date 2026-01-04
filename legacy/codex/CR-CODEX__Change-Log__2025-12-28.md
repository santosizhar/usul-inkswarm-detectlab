# CR-CODEX change log — actionable follow-ups

## Summary of changes
- Implemented shared diagnostics helper and wired into `doctor`/`sanity` with fail-closed pyarrow check.
- Added CLI tests for doctor output and failure modes.
- Updated onboarding docs with repo map, entry points, artifact paths, and first-success path.
- Added hygiene scripts/docs (dependency check, artifact retention) and CI sanity wrapper.

## Files touched
- `src/inkswarm_detectlab/diagnostics.py`
- `src/inkswarm_detectlab/cli.py`
- `tests/test_diagnostics_cli.py`
- `README.md`
- `docs/getting_started.md`
- `docs/artifact_retention.md`
- `tools/dependency_check.sh`
- `tools/ci_sanity.sh`

---

## Follow-up changes (CI + hygiene + regression coverage)
- Added Parquet gate command `detectlab config check-parquet` and tests.
- Added step-runner reuse regression test to cover dataset → features → baselines → eval reuse flows.
- Added dependency lock snapshot (`requirements.lock`) and CI workflow running compileall, pytest, and doctor.
- Documented bundle index, secrets scanning, cache cleanup helper, and manifest observability.
- Added cache prune wrapper script for automation.

### Files touched
- `README.md`
- `README__D-0024_INDEX.md`
- `docs/getting_started.md`
- `docs/runbook.md`
- `docs/secrets_scanning.md`
- `src/inkswarm_detectlab/cli.py`
- `tests/test_pyarrow_requirement_cli.py`
- `tests/test_step_runner_reuse.py`
- `tests/test_notebooks.py`
- `requirements.lock`
- `.github/workflows/ci.yml`
- `tools/cache_prune.sh`

## Notes
- `detectlab sanity` now defaults to `--no-tiny-run` to keep CI runs side-effect free; enable `--tiny-run` explicitly when artifacts are acceptable.

---

## Additional actionable items addressed (release readiness + run guidance)
- Added a dedicated how-to-run CR-CODEX guide with tunable parameters and copy/paste commands.
- Documented release readiness acceptance criteria in the runbook (doctor, sanity, manifest, UI bundle, cache hygiene).
- Enhanced README expected outputs with log and UI bundle paths to improve artifact discoverability.

### Files touched
- `CR-CODEX__How-To-Run__2025-12-28.md`
- `docs/runbook.md`
- `README.md`
