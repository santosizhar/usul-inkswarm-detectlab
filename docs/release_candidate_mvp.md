# MVP Release Candidate (D-0013) — Procedure (Fail-Closed)

This is the release-candidate checklist/procedure to produce a stakeholder-sendable MVP artifact and (optionally) a release tag, and then create a freeze anchor (CF-0003).

**Important:** RR-0001 is the intended authoritative reproducibility gate (Windows + Python 3.12).
However, the final user may choose an **ADMIN CLOSE / PROVISIONAL** path (“closed for now”), which must be recorded explicitly and treated as **not proven** determinism.

---

## 0) Preconditions
- You have an unpacked repo zip (or a git checkout) on Windows.
- You have Python 3.12 installed and available as `py -3.12`.
- You have created and activated a virtualenv (recommended: `.venv`).
- You know which config is the “full MVP” config (default: `configs\skynet_mvp.yaml`).

---

## 1) Environment setup (recommended)
From repo root:

```powershell
py -3.12 --version
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install -U pip
pip install -e ".[dev]"
```

Optional preflight:

```powershell
python -m inkswarm_detectlab doctor
```

---

## 2) RR-0001 (authoritative gate OR admin-close)

### 2.1 Preferred: run RR-0001 (authoritative)
```powershell
.\scripts\rr_mvp.ps1 -Config "configs\skynet_mvp.yaml" -RunId "RR-0001_<YYYYMMDD>_01"
```

Expected evidence folder:
- `rr_evidence\RR-0001\RR-0001_<YYYYMMDD>_01\`
  - `rr_mvp.log`
  - `signature_A*.json`
  - `signature_B*.json`
  - (if FAIL) `rr_error.txt`

Record the result in journals using `docs/rr_recording_template.md`.

### 2.2 Allowed: ADMIN CLOSE / PROVISIONAL (final user decision)
If RR evidence is not available but the final user says to proceed “for now”:
- Record RR-0001 as **CLOSED (ADMIN OVERRIDE / PROVISIONAL)** in journals.
- Treat determinism as **not proven**.
- Any stakeholder send should include a short caveat (“provisional”).

Use `docs/rr_recording_template.md` and set:
- RR outcome: `ADMIN CLOSE / PROVISIONAL`

---

## 3) Produce the canonical “send-to-someone” artifact
RR scripts commonly clean A/B runs; regardless of RR path, produce a single “send” run:

```powershell
python -m inkswarm_detectlab run mvp -c configs\skynet_mvp.yaml --run-id "MVP_SEND_<YYYYMMDD>_01"
```

### 3.1 Zip the share bundle
Preferred (if you have the helper from D-0012):
```powershell
.\scripts\make_share_zip.ps1 -RunId "MVP_SEND_<YYYYMMDD>_01"
```

Fallback:
```powershell
Compress-Archive -Path runs\MVP_SEND_<YYYYMMDD>_01\share\* -DestinationPath MVP_SEND_<YYYYMMDD>_01__share.zip -Force
```

Canonical artifact to send:
- `MVP_SEND_<YYYYMMDD>_01__share.zip`
- Contains: `runs/<run_id>/share/` (UI bundle + reports)

---

## 4) Spot-check the shareable UI
Open:
- `runs\MVP_SEND_<YYYYMMDD>_01\share\ui_bundle\index.html`

Verify:
- The summary page renders.
- Headline split story is visible/consistent (`user_holdout` primary, `time_eval` drift).
- Slice/stability diagnostics are present if configured.
- Signature fields show:
  - `config_hash` (should exist)
  - `code_sha` may be empty if running from an unpacked zip (no `.git`)

---

## 5) Optional: version/tag (git checkout only)
If you are on a git checkout and you want a tag:
- Update versioning files per repo conventions.
- Commit.
- Tag.
- Push tag.

If running from an unpacked zip without git metadata:
- Skip tagging and rely on the share zip + config hash.

---

## 6) Freeze anchor (CF-0003)
Goal: create a clean restart anchor for this release candidate state.

Checklist:
- Ensure `CODE_FREEZE__CF-0003.md` exists and is updated with:
  - what is included
  - known caveats / deferred validations
  - how to reproduce (commands)
- Ensure `inkswarm-detectlab__MASTERPROMPT_CF-0003__Code-Freeze-Restart.md` exists and points to the correct “start next” ceremony/deliverable.
- Record CF-0003 in journals using `docs/cf_0003_recording_template.md`.

---

## 7) What to send to stakeholders
Send:
- `MVP_SEND_<YYYYMMDD>_01__share.zip`

Include a short note:
- `run_id`: `MVP_SEND_<YYYYMMDD>_01`
- config used: `configs\skynet_mvp.yaml`
- where to open UI: `share/ui_bundle/index.html`
- where headline metrics are: UI landing + `share/reports/summary.md`
- caveat if RR is provisional: “RR-0001 closed for now; determinism evidence pending”
