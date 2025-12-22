# Baselines & Metrics (MVP)

The MVP baseline set is intentionally small and stable:

- **logreg** (Logistic Regression): fast, interpretable, reliable anchor
- **rf** (Random Forest): non-linear baseline that usually improves over logreg

> Note: `hgb` (HistGradientBoosting) is excluded for MVP until a platform-specific native crash is resolved.

## Primary headline metric
- **PR-AUC** (area under the Precision–Recall curve)

This is useful when positives are rare.

## Secondary operating-point metric
- **Recall @ 1% FPR**

Interpretation:
- Fix a false positive rate of ~1% (how often we wrongly flag)
- Measure recall (how many true positives we catch)

## What “good” looks like
- Similar or improving metrics from `train` → `time_eval`
- Stable metrics on `user_holdout` (generalizes to new users)
- Clear model comparisons in `report.md`

## Where to read results
For a run_id:
- `runs/<run_id>/models/login_attempt/baselines/report.md`
- `runs/<run_id>/models/login_attempt/baselines/metrics.json`

Additional stakeholder-friendly outputs:
- `runs/<run_id>/reports/baselines_login_attempt.md` (copy of the report)
- `runs/<run_id>/logs/baselines.log` (fit/debug log; includes failures)

## Failure behavior
Baseline training is **fail-soft** for MVP usability:
- If at least one baseline succeeds, artifacts are still written and a warning is emitted.
- If all requested baselines fail, the command returns an error.

## Artifact layout
Baseline model artifacts are written in **two layouts** for compatibility:

- **Layout v2 (preferred):** `runs/<run_id>/models/<task>/baselines/<model>/<label>.joblib`
- **Layout v1 (legacy):** `runs/<run_id>/models/<task>/baselines/<label>__<model>.joblib`

The evaluator and report generator will discover **either** layout.

### Normalizing older runs (optional)
If you have older runs that only contain the legacy flat files, you can create the v2 folder layout by copying artifacts:

```bash
python tools/normalize_baselines_layout.py --baselines-dir runs/<run_id>/models/login_attempt/baselines
```

Add `--dry-run` to preview actions, and `--remove-legacy` to delete legacy files after copying.

### Searching the repo on Windows (no ripgrep)
If you don't have `rg` (ripgrep) installed, you can use PowerShell's built-in `Select-String`:

```powershell
Select-String -Path "src\**\*.py" -Pattern "baselines" -List
Select-String -Path "src\**\*.py" -Pattern "Missing model artifact" -List
```
