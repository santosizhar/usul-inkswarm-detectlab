# RR-0002 — Final Queue and Operator Guide (D-0017)

This document defines the Release Readiness (RR) procedure **and** the final manual confirmation steps.
It is **fail-closed**: if a step cannot be verified, record **FAIL** or **PROVISIONAL**.

---

## TL;DR (operator quick path)

1) Set up Windows/Python 3.12 + venv + install + `doctor`  
2) Run RR matrix (**git mode** + **unpacked zip mode**) using **two configs** (MVP + smoke)  
3) Run `MVP_SEND_*` and produce `MVP_SEND_*__share.zip`  
4) Do the **final manual confirmation** (UI + HTML reports) and save screenshots  
5) Record everything using `RR-0002__recording_template.md`

---

## 0) Goals (what “RR PASS” means)

RR PASS means:

1) You can run the pipeline on **Windows + Python 3.12** reliably.
2) You can produce a stakeholder artifact: `runs/<run_id>/share/` + `<run_id>__share.zip`
3) The share bundle opens and is interpretable:
   - UI loads
   - `EXEC_SUMMARY.html` and `summary.html` exist and open
4) RR is recorded in a way that’s audit-ready (commands + run ids + evidence pointers).
5) Determinism is recorded as either:
   - **HARD PASS** (strict match; see section 8), or
   - **QUALIFIED** (differences documented + accepted)

---

## 1) Naming conventions (to keep evidence searchable)

Run IDs:

### MVP canonical (A/B determinism)
- Git mode (code SHA available):
  - `RR2_MVP_GIT_A_YYYYMMDD_01`
  - `RR2_MVP_GIT_B_YYYYMMDD_01`
- Unpacked zip mode (no `.git`, code shown as **(no git)**):
  - `RR2_MVP_ZIP_A_YYYYMMDD_01`
  - `RR2_MVP_ZIP_B_YYYYMMDD_01`

### Smoke (single run; fastest loop)
Purpose: quick “does it run end-to-end?” check with minimal time/cost.
- Git mode: `RR2_SMOKE_GIT_YYYYMMDD_01`
- Zip mode: `RR2_SMOKE_ZIP_YYYYMMDD_01`

### Stakeholder send (canonical deliverable)
- `MVP_SEND_YYYYMMDD_01`

Evidence folder (in-repo):
- `docs/rr_evidence/RR-0002/YYYYMMDD/`

---

## 2) RR Matrix (what we run)

We run **2 modes × 2 configs**:

### Mode 1 — Git checkout mode (code SHA available)
- MVP config: **A/B determinism runs**
- Smoke config: **single run**

### Mode 2 — Unpacked zip mode (no git; code SHA missing)
- MVP config: **A/B determinism runs**
- Smoke config: **single run**

---

## 3) Preconditions (Windows + Py3.12)

From repo root:

```powershell
py -3.12 --version
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e ".[dev]"
python -m inkswarm_detectlab doctor
```

**Record (paste into RR recording):**
- `py -3.12 --version` output
- `doctor` output (or key lines)

---

## 4) Canonical configs (locked)

- MVP: `configs\skynet_mvp.yaml`
- Smoke: `configs\skynet_smoke.yaml`

---

## 5) RR execution steps

### 5.1 Git mode — MVP determinism A/B

```powershell
python -m inkswarm_detectlab run mvp -c configs\skynet_mvp.yaml --run-id RR2_MVP_GIT_A_YYYYMMDD_01
python -m inkswarm_detectlab run mvp -c configs\skynet_mvp.yaml --run-id RR2_MVP_GIT_B_YYYYMMDD_01
```

### 5.2 Git mode — Smoke (single)

```powershell
python -m inkswarm_detectlab run mvp -c configs\skynet_smoke.yaml --run-id RR2_SMOKE_GIT_YYYYMMDD_01
```

### 5.3 Unpacked zip mode — MVP determinism A/B

Run from an **unpacked zip** folder. Expected: UI shows code as **(no git)**.

```powershell
python -m inkswarm_detectlab run mvp -c configs\skynet_mvp.yaml --run-id RR2_MVP_ZIP_A_YYYYMMDD_01
python -m inkswarm_detectlab run mvp -c configs\skynet_mvp.yaml --run-id RR2_MVP_ZIP_B_YYYYMMDD_01
```

### 5.4 Unpacked zip mode — Smoke (single)

```powershell
python -m inkswarm_detectlab run mvp -c configs\skynet_smoke.yaml --run-id RR2_SMOKE_ZIP_YYYYMMDD_01
```

---

## 6) Packaging the stakeholder artifact (required)

For the **MVP_SEND** run:

```powershell
python -m inkswarm_detectlab run mvp -c configs\skynet_mvp.yaml --run-id MVP_SEND_YYYYMMDD_01
```

Then zip:

```powershell
Compress-Archive -Path runs\MVP_SEND_YYYYMMDD_01\share\* `
  -DestinationPath MVP_SEND_YYYYMMDD_01__share.zip -Force
```

---

## 7) What must exist after each run

In `runs/<run_id>/`:

- `reports/summary.md`
- `reports/EXEC_SUMMARY.md`
- `reports/EXEC_SUMMARY.html`
- `reports/summary.html`
- `share/ui_bundle/index.html`
- `share/reports/EXEC_SUMMARY.html`
- `share/reports/summary.html`

---

## 8) Determinism checks (HARD PASS strictness)

For MVP A/B runs:

**HARD PASS requires BOTH:**
1) Signatures match:
   - `config_hash` matches across A/B
   - `code_sha` matches across A/B **in git mode**
     - in unpacked zip mode, `code_sha` missing and UI shows **(no git)** is expected
2) Headline metrics identical (where present):
   - if the pipeline emits headline JSON/CSV, compare key `user_holdout` headline metrics A vs B
   - any non-identical value ⇒ not HARD PASS

**QUALIFIED** means:
- mismatch exists but is explained and explicitly accepted

**FAIL** means:
- mismatch exists and is unexplained or unacceptable

---

## 9) Final manual confirmation (this replaces a separate MT ritual)

Evidence = **checklist + screenshots**. Save to:
- `docs/rr_evidence/RR-0002/YYYYMMDD/screenshots/`

### 9.1 UI opens (mandatory)

Open:
- `share/ui_bundle/index.html`

✅ PASS if:
- loads and displays runs
- truth split text visible
- config hash visible
- in unpacked zip mode: code shows **“(no git)”** (expected)

**Screenshot required:** UI landing page.

### 9.2 HTML reports open (mandatory)

Open:
- `share/reports/EXEC_SUMMARY.html`
- `share/reports/summary.html`

✅ PASS if:
- both open
- exec summary contains truth split + recommended actions
- content renders without broken formatting

**Screenshots required:** top of each HTML report.

### 9.3 Interpretation guidance (what to say)

- `user_holdout` = primary generalization truth
- `time_eval` = drift check
If `time_eval` materially worse: call out **drift risk** and recommend mitigations (retrain, recalibrate, monitor).

---

## 10) RR recording template (what to paste into a journal)

Use:
- `docs/release_readiness/RR-0002__recording_template.md`

Place evidence in:
- `docs/rr_evidence/RR-0002/YYYYMMDD/`
  - `commands.txt`
  - `run_ids.txt`
  - `screenshots/`
  - `artifacts/` (optional, e.g. share zip)

---

## 11) Included sandbox notes (format reference only)

This deliverable ships an example sandbox evidence bundle under:
- `docs/rr_evidence/RR-0001/SANDBOX_RR_FAST_001/`

It is useful as a formatting example only. It does **not** certify Windows/Py3.12 reproducibility.
