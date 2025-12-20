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

## Models (MVP)
- Logistic Regression (with standardization)
- HistGradientBoostingClassifier

## Thresholding (FPR target)
We select a threshold per label/model to achieve:
- **FPR ≤ target_fpr** (default: 0.01)

We pick the closest FPR under the target (max FPR that still satisfies the constraint).

## CLI
```bash
detectlab baselines run -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001
# overwrite:
detectlab baselines run -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001 --force
```
