#!/usr/bin/env bash
set -euo pipefail

CONFIG="${1:-configs/skynet_mvp.yaml}"
RUN_ID="${2:-RR_MVP_$(date +%Y%m%d)_001}"

echo "RR MVP: config=$CONFIG run_id=$RUN_ID"

python -m inkswarm_detectlab doctor || true

detectlab run skynet -c "$CONFIG" --run-id "$RUN_ID"
detectlab features build -c "$CONFIG" --run-id "$RUN_ID" --force
detectlab baselines run -c "$CONFIG" --run-id "$RUN_ID" --force

echo "RR MVP: verifying key artifacts..."
test -f "runs/$RUN_ID/manifest.json"
test -f "runs/$RUN_ID/reports/summary.md"
test -f "runs/$RUN_ID/features/login_attempt/features.parquet"
test -f "runs/$RUN_ID/models/login_attempt/baselines/metrics.json"
test -f "runs/$RUN_ID/models/login_attempt/baselines/report.md"

echo "RR MVP OK: $RUN_ID"
