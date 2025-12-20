# Windows reproducibility notes (CR-0002)

This repo targets **Python 3.12**.

On some Windows setups, native ML libraries can behave differently depending on the BLAS/OpenMP backend (MKL/OpenBLAS) and thread settings. To make runs more reproducible and easier to debug, use the guidance below.

## Quick diagnostics
```powershell
python -m inkswarm_detectlab doctor
```

The output is also captured under `meta.env` in `runs/<run_id>/models/login_attempt/baselines/metrics.json`.

## Recommended thread settings (during validation)
Set these **in the same terminal** before running baselines:

```powershell
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:OPENBLAS_NUM_THREADS = "1"
$env:NUMEXPR_NUM_THREADS = "1"
```

These reduce nondeterminism and avoid a class of backend/threadpool issues.

## Known limitation: HGB temporarily disabled
`HistGradientBoostingClassifier` is **disabled for MVP** as of CR-0002 due to a native crash observed on some platforms during `.fit()`. The MVP baseline set is:

- `logreg`
- `rf`

We will reintroduce HGB only after reproducing and resolving the crash.
