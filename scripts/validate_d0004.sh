#!/usr/bin/env bash
set -euo pipefail

CONFIG="${1:-configs/skynet_smoke.yaml}"
RUN_ID="${2:-RUN_SAMPLE_SMOKE_0001}"

echo "== D-0004 Deferred Validation (Parquet-mandatory as of D-0005) =="
echo "Config: ${CONFIG}"
echo "RunId : ${RUN_ID}"

# If the run contains legacy CSV artifacts, migrate them to Parquet first.
detectlab dataset parquetify -c "${CONFIG}" --run-id "${RUN_ID}" --force

pytest -q

detectlab features build -c "${CONFIG}" --run-id "${RUN_ID}" --force
detectlab baselines run -c "${CONFIG}" --run-id "${RUN_ID}" --force

echo "Done. Check runs/${RUN_ID}/models/login_attempt/reports/baseline_report.md"
