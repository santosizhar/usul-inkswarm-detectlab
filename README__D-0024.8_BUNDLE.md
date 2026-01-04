# D-0024.8 — RR Patch: Notebook bootstrap robust

Fixes the first notebook cell to resolve CFG_PATH robustly using the installed package location (inkswarm_detectlab.__file__), avoiding Jupyter CWD issues.

Usage:
- Optionally set env var INKSWARM_CFG to choose a config basename (default: skynet_smoke.yaml)
- Restart kernel after unzipping over the repo.
