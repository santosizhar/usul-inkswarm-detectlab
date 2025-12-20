# JM-0021 — CR-0004 — Repo Hardening + Evidence Bundle Fix + Docs Curation

This journal is the **change record** for CR-0004.

Canonical detailed write-up:
- `CODE_REVIEW__CR-0004.md`

## Why this CR exists
The repo is a portfolio artifact and must be runnable end-to-end.
A corrupted evidence exporter (syntax errors) made the MVP pipeline brittle and could break RR.

## Summary of fixes applied
### Blockers / Critical
- Rewrote `src/inkswarm_detectlab/share/evidence.py` (share packaging + sha256 evidence manifest)
- Fixed manifest IO semantics (`src/inkswarm_detectlab/io/manifest.py`) so callers can pass run directories
- Exported report symbol used by tests (`src/inkswarm_detectlab/reports/__init__.py`)

### Major hygiene
- Added missing declared dependency: `numpy` in `pyproject.toml`
- Added compile/syntax check to CI (`python -m compileall src`)
- Removed accidental duplicate repo copy under `configs/`

### Docs + portfolio polish
- Added `docs/runbook.md` and `docs/repo_map.md`
- Simplified `docs/index.md`
- Rewrote `docs/mvp_user_guide.md` and root `README.md` to match actual CLI surface
- Added `MANUAL_RUNS_AND_CHECKS.md`

## Verification
- `python -m compileall src` ✅
- `pytest -q` ✅

## Follow-ups (recommended)
- CI: add `mkdocs build --strict`
- Add `detectlab doctor` command for quick environment validation
- Expose a `detectlab reports ...` command group (non-MVP flows)
