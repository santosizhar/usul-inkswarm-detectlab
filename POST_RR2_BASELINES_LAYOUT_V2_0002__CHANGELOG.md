# POST-RR2 Baselines Layout v2 — Fixpack 0002 (Changelog)

This fixpack addresses baseline artifact layout discoverability and standardizes how baseline models are persisted.

## What changed

### 1) Baseline artifacts now saved in an organized folder layout (v2)
Baseline model artifacts are now written in **both** formats:

- **Layout v2 (preferred):** `.../baselines/<model>/<label>.joblib`
- **Layout v1 (legacy):** `.../baselines/<label>__<model>.joblib`

Writing both ensures:
- the folder is human-browsable (grouped by model), and
- existing tooling and older runs remain compatible.

**Code:** `src/inkswarm_detectlab/models/runner.py`

### 2) Evaluator discovery supports both layouts (v1 + v2)
`_discover_baseline_artifacts(...)` was rewritten to reliably discover artifacts under either layout and to emit useful notes for:
- missing baselines directory
- missing artifacts per expected model
- duplicates
- unrecognized filenames

**Code:** `src/inkswarm_detectlab/eval/runner.py`

### 3) Optional normalizer script for older runs
For older runs that only have legacy flat filenames, you can create the v2 folders by copying artifacts:

```bash
python tools/normalize_baselines_layout.py --baselines-dir runs/<run_id>/models/login_attempt/baselines
```

Add `--dry-run` to preview, `--remove-legacy` to delete legacy artifacts after copying.

**Code:** `tools/normalize_baselines_layout.py`

### 4) Documentation updates
`docs/baselines.md` now documents the layouts, the normalizer, and Windows search alternatives to `rg`.

## Validations executed (in this environment)

- `python -m compileall -q src`
- `pytest -q` (all tests passed, including a new test that checks discovery for both layouts)

## What you should do locally

1) Pull/apply this fixpack to your repo.
2) Re-run the relevant baseline training/eval for `login_attempt`:
   - confirm that `.../baselines/logreg/<label>.joblib` and `.../baselines/rf/<label>.joblib` are created
   - confirm reports generate without "Missing model artifact" warnings
3) (Optional) Normalize older run folders with the script if you want consistent browsing.
