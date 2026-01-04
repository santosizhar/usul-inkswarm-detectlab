# JM-0015 — D-0006.5 — Shareable UI v1 (Static HTML Viewer)

## Artifact map
- CLI:
  - `src/inkswarm_detectlab/cli.py` (new `ui` subcommands)
  - `src/inkswarm_detectlab/ui/summarize.py`
  - `src/inkswarm_detectlab/ui/bundle.py`

- Docs:
  - `docs/mvp_user_guide.md` (Sharing results updated)
  - `docs/release_readiness_mvp.md` (evidence bundle now includes `ui_bundle/`)
  - `docs/index.md` (navigation mention)

- RR evidence:
  - `scripts/rr_mvp.ps1` and `scripts/rr_mvp.sh` export `ui_bundle/`

- Tests:
  - `tests/test_ui.py`

## How to use (quick)
1) After you have runs with baselines:
   - `python -m inkswarm_detectlab ui export -c configs/skynet_mvp.yaml --run-ids RUN_A,RUN_B --out-dir ui_bundle`
2) Open:
   - `ui_bundle/index.html`
3) Share the folder:
   - zip `ui_bundle/` and send it (self-contained).
