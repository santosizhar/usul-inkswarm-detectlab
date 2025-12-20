# CODE FREEZE — CF-0002 — Inkswarm DetectLab (inkswarm-detectlab)

**Freeze date:** 2025-12-18  
**Timezone:** America/Argentina/Buenos_Aires

This Code Freeze is a deliberate, fail-closed snapshot intended to be restarted from a new chat using the companion restart masterprompt:
- `inkswarm-detectlab__MASTERPROMPT_CF-0002__Code-Freeze-Restart.md`

---

## What is DONE (frozen in this snapshot)

### Core deliverables
- **D-0001**: Repo skeleton + docs structure + CLI scaffold.
- **D-0002**: **SKYNET** synthetic data generator + leakage-aware splits (**train / time_eval / user_holdout**) + manifests/reports.
- **CR-0001**: Determinism tightening, canonicalization, CLI UX, CI smoke improvements.
- **D-0003**: FeatureLab v0 (safe aggregates; windows **1h/6h/24h/7d**; `login_attempt` only).
- **D-0004**: BaselineLab v0 (LogReg + initial baseline set) — **validation deferred**.
- **CC-0001 / CC-0002**: D-0004 deferred validation explicitly extended to **post-MVP**.
- **D-0005**: **Parquet mandatory** (fail-closed), legacy parquetify for old runs, Feature/Baseline reporting upgrades, docs placeholder completion.
- **CR-0002**: Baseline robustness review + RR requirements hardened.
- **RR-0001 (prepared)**: Release Readiness scripts, evidence bundling, two-run determinism check, cleanup-on-failure behavior.

### Repo-wide invariants
- **Parquet-only I/O** on active paths (`pyarrow` required). CSV fallback removed.
- **Primary ID:** `user_id` (splits + joins).
- **Targets:** `login_attempt` (support included), `checkout_attempt` (placeholder for expansion).
- **Metric headline:** PR-AUC; **secondary:** Recall@1%FPR (threshold chosen on TRAIN, applied to eval splits).

---

## What is NOT DONE / Explicitly deferred

### Deferred validation (still pending)
- **D-0004 deferred validation remains OPEN** until you run RR locally on Windows 3.12.
  - See: `DEFERRED_VALIDATION__D-0004.md` (now fully filled with runnable commands).

### HGB crash investigation
- `HistGradientBoostingClassifier` is **excluded from MVP** due to native crash behavior observed in some environments.
  - MVP baselines are **logreg + random_forest**.
  - HGB is reserved for a later investigation track once the crash is reproducible + diagnosable on the target Windows setup.

---

## How to (unfreeze) run MVP Release Readiness (RR-0001)

**Target environment:** Windows + Python **3.12** (PowerShell at repo root).

1) Create venv and install:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e ".[dev]"
```

2) Run RR:
```powershell
.\scripts\rr_mvp.ps1
```

Expected outputs:
- Evidence bundle under `rr_evidence/RR-0001/<base_run_id>/`
- A markdown evidence summary in `journals/`:
  - `inkswarm-detectlab__RR_EVIDENCE__RR-0001__<base_run_id>.md`

**RR policy:**
- Two runs are executed (`_A` and `_B`).
- If determinism signatures differ → RR fails.
- If PR-AUC is low → **warning**, not an MVP blocker (unless you decide otherwise).

---

## Next steps after RR-0001 passes
1) Write journals immediately: J + JM for RR outcomes (actual numbers per MP5 rules).
2) Proceed to **MVP release** (tag/versioning + docs final pass).
3) Optionally schedule a new Code Freeze after MVP (`CF-0003`) for a clean restart point.

---

## Files added/updated in this freeze
- `CODE_FREEZE__CF-0002.md` (this file)
- `inkswarm-detectlab__MASTERPROMPT_CF-0002__Code-Freeze-Restart.md`
- Journals: `inkswarm-detectlab__J-0013__CF-0002__code-freeze.md`, `inkswarm-detectlab__JM-0013__CF-0002__code-freeze.md`

