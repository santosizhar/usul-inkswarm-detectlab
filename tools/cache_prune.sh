#!/usr/bin/env bash
set -euo pipefail

echo "[detectlab] cache prune (features older than 30 days)"
python -m inkswarm_detectlab.cli cache prune --older-than-days 30 --yes "$@"
