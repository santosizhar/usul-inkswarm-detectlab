# MVP User Guide (Non-Technical)

This guide explains how to **run the MVP**, what it **produces**, and how to **tell if progress is real**.

If you are not comfortable running commands, ask someone to run **one script** for you (Release Readiness) and share the produced evidence bundle.

---

## What is DetectLab?

DetectLab is a “lab bench” for detection work:
1) It **generates synthetic event data** (SKYNET).
2) It builds **leakage-aware splits** (train / time_eval / user_holdout).
3) It creates **safe aggregate features** (FeatureLab).
4) It trains and evaluates **simple baselines** (BaselineLab).
5) It writes all outputs into a run folder: `runs/<run_id>/`.

The MVP focuses on one event table: **`login_attempt`**.

---

## What you need

- A computer with **Python 3.12** installed.
- Windows is supported (PowerShell scripts are provided).
- Parquet is mandatory, so you need `pyarrow` (the install step below includes it).

---

## The simplest way to validate everything (recommended)

Run **Release Readiness** (RR). It runs the full pipeline **twice** and checks determinism.

### Windows (PowerShell) — repo root
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e ".[dev]"

.\scripts\rr_mvp.ps1
```

### What “success” looks like
RR prints a PASS message and produces an evidence bundle under:
- `rr_evidence/RR-0001/<base_run_id>/`

The key items are:
- `rr_mvp.log` — full log output
- `signature_A.json` and `signature_B.json` — determinism signatures (should match)
- `rr_error.txt` — **only present on failure**

It also writes a markdown evidence note under:
- `journals/inkswarm-detectlab__RR_EVIDENCE__RR-0001__<base_run_id>.md`

---

## If you want to run steps one by one (optional)

### 1) Generate synthetic data (SKYNET)
```bash
detectlab run skynet -c configs/skynet_mvp.yaml --run-id MVP_YYYYMMDD_001 --force
```

### 2) Build features (FeatureLab)
```bash
detectlab features build -c configs/skynet_mvp.yaml --run-id MVP_YYYYMMDD_001 --force
```

### 3) Train and evaluate baselines (BaselineLab)
MVP baseline set is locked to:
- `logreg` (Logistic Regression)
- `rf` (Random Forest)

```bash
detectlab baselines run -c configs/skynet_mvp.yaml --run-id MVP_YYYYMMDD_001 --force
```

---

## Where to find results

Everything lands under:
- `runs/<run_id>/`

Important outputs:
- `runs/<run_id>/reports/summary.md` — quick run summary (counts, splits, labels)
- `runs/<run_id>/models/login_attempt/baselines/report.md` — readable evaluation report
- `runs/<run_id>/models/login_attempt/baselines/metrics.json` — machine-readable metrics
- `runs/<run_id>/manifest.json` — content hashes (integrity + determinism support)

---

## How to interpret “progress”

### 1) Don’t overfit to one number
PR-AUC can move for many reasons. Use it as a headline, but also check:
- Recall at a fixed false positive rate (e.g. 1% FPR)
- Stability across splits (time_eval vs user_holdout)
- Slice stability (planned for post-MVP)

### 2) The most important question
**Does it generalize?**  
A model that looks good on train but collapses on `user_holdout` is not usable.

### 3) Track progress like a lab notebook
Every meaningful change should produce:
- a new `run_id`
- a `report.md` / `metrics.json`
- a journal entry under `journals/` summarizing what changed and what improved (or broke)

---

## Sharing results (for stakeholders)
To share a run:
1) Share the `runs/<run_id>/reports/summary.md`
2) Share `runs/<run_id>/models/login_attempt/baselines/report.md`
3) If needed for reproducibility, share `manifest.json` and the RR evidence bundle

---

## Lore (optional)
Lore exists to make the project memorable and cohesive. It is separate from the technical docs:
- `docs/lore/world_bible.md`
