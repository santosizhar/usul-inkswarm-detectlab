#!/usr/bin/env bash
set -euo pipefail

CONFIG="${1:-configs/skynet_mvp.yaml}"
BASE_RUN_ID="${2:-RR_MVP_$(date +%Y%m%d)_001}"

RUN_A="${BASE_RUN_ID}_A"
RUN_B="${BASE_RUN_ID}_B"

EVIDENCE_DIR="rr_evidence/RR-0001/${BASE_RUN_ID}"
mkdir -p "$EVIDENCE_DIR"
LOG_PATH="$EVIDENCE_DIR/rr_mvp.log"
ERR_PATH="$EVIDENCE_DIR/rr_error.txt"

cleanup_run() {
  local rid="$1"
  rm -rf "runs/$rid" || true
}

require_artifact() {
  local p="$1"
  test -f "$p" || { echo "Missing required artifact: $p"; return 2; }
}

run_one() {
  local rid="$1"
  echo "RR MVP: config=$CONFIG run_id=$rid"
  detectlab run skynet -c "$CONFIG" --run-id "$rid"
  detectlab features build -c "$CONFIG" --run-id "$rid" --force
  detectlab baselines run -c "$CONFIG" --run-id "$rid" --force

  echo "RR MVP: verifying key artifacts for $rid..."
  require_artifact "runs/$rid/manifest.json"
  require_artifact "runs/$rid/reports/summary.md"
  require_artifact "runs/$rid/features/login_attempt/features.parquet"
  require_artifact "runs/$rid/models/login_attempt/baselines/metrics.json"
  require_artifact "runs/$rid/models/login_attempt/baselines/report.md"
}

{
  echo "RR MVP: config=$CONFIG base_run_id=$BASE_RUN_ID"
  python -m inkswarm_detectlab doctor || true
  echo "---"

  run_one "$RUN_A"
  python -m inkswarm_detectlab.tools.rr_signature --run-id "$RUN_A" --out "$EVIDENCE_DIR/signature_A.json"

  run_one "$RUN_B"
  python -m inkswarm_detectlab.tools.rr_signature --run-id "$RUN_B" --out "$EVIDENCE_DIR/signature_B.json"

  if ! diff -q "$EVIDENCE_DIR/signature_A.json" "$EVIDENCE_DIR/signature_B.json" >/dev/null; then
    echo "Determinism check failed: signature_A.json != signature_B.json"
    exit 2
  fi

  # Export stakeholder UI bundle (self-contained HTML; compares runs)
  python -m inkswarm_detectlab ui export -c "$CONFIG" --run-ids "${RUN_A},${RUN_B}" --out-dir "$EVIDENCE_DIR/ui_bundle" --force

  python -m inkswarm_detectlab.tools.rr_evidence_md \
    --base-run-id "$BASE_RUN_ID" \
    --run-a "$RUN_A" \
    --run-b "$RUN_B" \
    --sig-a "$EVIDENCE_DIR/signature_A.json" \
    --sig-b "$EVIDENCE_DIR/signature_B.json" \
    --out "journals/inkswarm-detectlab__RR_EVIDENCE__RR-0001__${BASE_RUN_ID}.md"

  echo "RR MVP OK: $BASE_RUN_ID (two-run determinism OK)"
} 2>&1 | tee "$LOG_PATH" || {
  echo "RR MVP FAILED ($BASE_RUN_ID). Log: $LOG_PATH" | tee "$ERR_PATH"
  cleanup_run "$RUN_A"
  cleanup_run "$RUN_B"
  exit 2
}
