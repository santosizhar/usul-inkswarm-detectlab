# CODE REVIEW — CR-0004
**Project:** Inkswarm DetectLab (`inkswarm-detectlab`)  
**Scope:** portfolio repo audit + runtime hardening + doc curation + “share package” reliability  
**Mode:** Start-coding (fixes implemented in this repo snapshot)

---

## 1) Executive summary

DetectLab is a **reproducible detection lab** for event-level telemetry:
- generates synthetic events (`login_attempt`, `checkout_attempt`),
- creates leakage-aware splits (`user_holdout`, `time_eval`),
- builds safe aggregate features,
- trains and evaluates baseline models,
- produces a shareable static HTML viewer + evidence bundle for stakeholders.

### Biggest gaps pre-fix (claims vs reality)
- The MVP pipeline could fail at the end due to a **corrupted evidence exporter** (syntax errors).
- RR / evidence packaging existed in docs and scripts, but the underlying exporter was not reliable.

### Top risks (current)
1) **Determinism drift**: timestamps/non-deterministic ordering can still make RR flaky if not carefully controlled in reports.
2) **CLI surface completeness**: reports are partly generated inside the MVP orchestrator; the CLI does not expose a first-class `reports` command group.
3) **Dependency hygiene**: scikit-learn + pyarrow ecosystem changes can break reproducibility without pinned versions.
4) **Docs drift**: multiple docs can diverge unless there’s a single canonical runbook (added in this CR).
5) **Artifact bloat**: sample runs/fixtures can grow and slow clones/CI if not pruned.

---

## 2) Repo map (high signal)

Canonical docs:
- `docs/runbook.md` — **what to run**
- `docs/repo_map.md` — **where things live**
- `docs/mvp_user_guide.md` — stakeholder-friendly execution + interpretation

Core code packages:
- `src/inkswarm_detectlab/cli.py` — `detectlab` CLI (Typer)
- `src/inkswarm_detectlab/synthetic/` — Skynet synthetic data
- `src/inkswarm_detectlab/dataset/` — leakage-aware splits
- `src/inkswarm_detectlab/features/` — FeatureLab
- `src/inkswarm_detectlab/models/` — BaselineLab
- `src/inkswarm_detectlab/eval/` — EvalLab diagnostics
- `src/inkswarm_detectlab/ui/` — UI summary + static bundle exporter
- `src/inkswarm_detectlab/share/` — evidence packaging + fingerprinting
- `scripts/` — RR and packaging helpers

---

## 3) Blockers & critical issues found (and fixed)

### Blocker B-001 — Corrupted evidence exporter
**Symptom:** Syntax errors in `src/inkswarm_detectlab/share/evidence.py` prevented import/execution for flows that reach evidence bundling.  
**Fix:** Rewrote the module with a deterministic, fail-soft implementation that:
- keeps `share/ui_bundle/` intact (does not delete it),
- packages `reports/`, `logs/`, and `meta/` into `share/`,
- writes `evidence_manifest.json` with sha256 for all files **excluding itself**.

### Critical C-001 — Manifest read/write semantics mismatch
**Symptom:** `read_manifest()` / `write_manifest()` expected an explicit file path, but callers passed the run directory (e.g., reports runner).  
**Fix:** `io/manifest.py` now accepts either:
- a run directory (writes/reads `manifest.json` inside it), or
- an explicit `manifest.json` path.

### Major M-001 — Missing dependency declared
**Symptom:** `src/inkswarm_detectlab/models/runner.py` imports `numpy`, but `pyproject.toml` did not declare it.  
**Fix:** Added `numpy>=1.26` to dependencies.

### Major M-002 — CI didn’t catch syntax corruption early
**Fix:** Added `python -m compileall src` to `.github/workflows/ci.yml`.

### Major M-003 — Broken public API for reports package
**Symptom:** tests import `generate_final_report_for_run` from `inkswarm_detectlab.reports` but the symbol wasn’t exported.  
**Fix:** added export in `src/inkswarm_detectlab/reports/__init__.py`.

### Major M-004 — Accidental duplicate repo copy under `configs/`
**Symptom:** `configs/` contained a full nested repo copy (noise + confusion).  
**Fix:** pruned `configs/` to keep only YAML configs + its README.

---

## 4) Changes applied (file-by-file)

### Code
- `src/inkswarm_detectlab/share/evidence.py`
  - full rewrite: share packaging + evidence fingerprinting (sha256)
- `src/inkswarm_detectlab/io/manifest.py`
  - accept directory or file path
- `src/inkswarm_detectlab/reports/__init__.py`
  - export `generate_final_report_for_run`
- `src/inkswarm_detectlab/mvp/orchestrator.py`
  - fixed a wrong variable reference (`run_dir` → `rdir`) in exec summary write path
  - indented “Overall status” comment for readability
- `tests/test_share_evidence.py`
  - new unit test for evidence bundle export + manifest behavior
- `pyproject.toml`
  - added missing dependency `numpy`
- `.github/workflows/ci.yml`
  - added compile step

### Docs
- `docs/runbook.md` — canonical commands + expected outputs
- `docs/repo_map.md` — curated code map + end-to-end flow
- `docs/index.md` — simplified “start here”
- `docs/mvp_user_guide.md` — rewritten for faithful MVP instructions
- `docs/ceremonies/CR-0004.md` — compact ceremony summary
- `mkdocs.yml` — nav updated to include runbook + repo map
- `README.md` — rewritten to match current runtime surface

### Release/review helper
- `MANUAL_RUNS_AND_CHECKS.md` — human checklist for MVP / RR / packaging

---

## 5) Verification (performed in this environment)

### Syntax
- `python -m compileall src` ✅

### Tests
- `pytest -q` ✅

---

## 6) Remaining recommendations (not implemented in this CR)

### R-001 (Major) Add MkDocs build to CI
Add a CI job that runs `mkdocs build --strict` to catch:
- broken links,
- missing pages referenced in nav,
- markdown rendering regressions.

### R-002 (Major) Add a CLI “doctor” command
A `detectlab doctor` command that checks:
- python version,
- presence of required deps,
- write permissions,
- pyarrow import,
- config readability.

### R-003 (Major) First-class reports command group
Expose a `detectlab reports ...` group so non-MVP flows can:
- generate final report,
- generate exec summary,
- generate share package (UI export + evidence export).

### R-004 (Minor) Determinism audit
Review all report generators to ensure:
- ordering is stable,
- timestamps are either deterministic or clearly labeled as non-deterministic,
- RR signature comparison is meaningful.

---

## 7) What to run (canonical)

See:
- `docs/runbook.md`

---

## 8) Manual runs & checks

See:
- `MANUAL_RUNS_AND_CHECKS.md`
