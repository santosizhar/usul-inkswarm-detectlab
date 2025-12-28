#!/usr/bin/env bash
set -euo pipefail

echo "[detectlab] dependency check" 
python -m pip check || true

echo "[detectlab] outdated packages" 
python -m pip list --outdated --format=columns || true
