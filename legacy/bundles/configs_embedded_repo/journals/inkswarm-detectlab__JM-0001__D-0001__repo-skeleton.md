# D-0001 — JM-0001 (concise)

- Created repo skeleton (src layout), Typer CLI, Pydantic+YAML config, and schema v1 for `login_attempt` + `checkout_attempt` (support embedded in login).
- Standardized timezone to `America/Argentina/Buenos_Aires`; unified identifier to `user_id`.
- Implemented canonical run layout under `runs/<run_id>/raw/` + `manifest.json`.
- Added committed placeholder run `PLACEHOLDER_RUN_0001` + generator script (writes Parquet when available; CSV fallback used here).
- Added MkDocs docs skeleton + lore bible.
- Added notebooks and ensured they execute via pytest (nbclient).
- Added GitHub Actions CI running the single-line verification contract.
