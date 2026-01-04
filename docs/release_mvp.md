# MVP Release Procedure (D-0012)

This document describes how to produce a **stakeholder-sendable** MVP artifact and (optionally) a git-tagged release.

> Fail-closed: a release is only "hard" once **RR-0001 passes on Windows + Python 3.12** and the evidence is recorded.

## Inputs
- Config: `configs/skynet_mvp.yaml`
- RR script: `scripts/rr_mvp.ps1` / `scripts/rr_mvp.sh`
- Docs: `docs/release_readiness_mvp.md`, `docs/windows_repro.md`

## Step 0 — Preflight (Windows)
```powershell
python -m inkswarm_detectlab doctor
```

## Step 1 — RR-0001 (authoritative)
Run RR (two-run determinism, fail-closed):
```powershell
.\scripts\rr_mvp.ps1 -Config "configs/skynet_mvp.yaml" -RunId "RR_MVP_20251219_001"
```

RR outputs:
- `rr_evidence/RR-0001/<base_run_id>/rr_mvp.log`
- `rr_evidence/RR-0001/<base_run_id>/signature_A.json`
- `rr_evidence/RR-0001/<base_run_id>/signature_B.json`
- `rr_evidence/RR-0001/<base_run_id>/ui_bundle/` (comparison viewer)
- `journals/inkswarm-detectlab__RR_EVIDENCE__RR-0001__<base_run_id>.md`

**Rule:** treat the RR script exit code + logs as the source of truth.

## Step 2 — Produce the canonical share artifact (zip-and-send)
RR cleans up A/B run folders. After RR PASS, run one final full MVP run to generate the share bundle:
```powershell
python -m inkswarm_detectlab run mvp -c configs\skynet_mvp.yaml --run-id MVP_SEND_20251219_001
```

Then zip:
```powershell
.\scripts\make_share_zip.ps1 -RunId MVP_SEND_20251219_001
```

The output zip is the canonical artifact to send to a stakeholder:
- `<run_id>__share.zip` containing `runs/<run_id>/share/*`

## Step 3 — (Optional) Git release/tag
If you are running from a git checkout:
- ensure `manifest.code.github_sha` is populated in `runs/<run_id>/manifest.json`
- tag after RR PASS:
```bash
git status
git add -A
git commit -m "Release: MVP (post RR-0001)"
git tag -a v0.1.0 -m "Inkswarm DetectLab MVP"
git push --follow-tags
```

If running from an unpacked zip (no `.git`), `code_sha` will be null; in that case rely on:
- `config_hash` in the manifest
- `signature_digest` from RR evidence

## Step 4 — Freeze anchor (recommended)
After a hard MVP release, create a new freeze snapshot:
- `CODE_FREEZE__CF-0003.md`
- `inkswarm-detectlab__MASTERPROMPT_CF-0003__Code-Freeze-Restart.md`

See those templates in the repo root.
