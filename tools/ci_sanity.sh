#!/usr/bin/env bash
set -euo pipefail

python -m compileall src
pytest -q
python -m inkswarm_detectlab doctor
detectlab config check-parquet
./tools/dependency_check.sh
