# BaselineLab (D-0004)

BaselineLab trains and evaluates quick baseline detectors for `login_attempt`.

## Outputs (uncommitted by default)
- `runs/<run_id>/models/login_attempt/baselines/metrics.json`
- `runs/<run_id>/models/login_attempt/baselines/report.md`
- `runs/<run_id>/models/login_attempt/baselines/*.joblib`

These are referenced in `runs/<run_id>/manifest.json` with `note: UNCOMMITTED`.

## Targets
- Multi-label heads:
  - `label_replicators`
  - `label_the_mule`
  - `label_the_chameleon`

## Models (MVP defaults)
- Logistic Regression (with standardization)
- RandomForestClassifier (robust tree baseline)

## HGB status
`HistGradientBoostingClassifier` is **excluded for MVP** as of **CR-0002**.

Reason: on some platforms (notably Windows wheels / certain BLAS/OpenMP backends), HGB
may hard-abort the Python interpreter during `.fit()` (native crash). We will reintroduce
it only after the crash is reproduced + resolved.

## Thresholding (FPR target)
We select a threshold per label/model to achieve:
- **FPR ≤ target_fpr** (default: 0.01)

We pick the closest FPR under the target (max FPR that still satisfies the constraint).

## CLI
```bash
detectlab doctor

detectlab baselines run -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001
# overwrite:
detectlab baselines run -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force
```
