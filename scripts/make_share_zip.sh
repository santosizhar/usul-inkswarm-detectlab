#!/usr/bin/env bash
set -euo pipefail

RUN_ID="${1:-}"
if [[ -z "$RUN_ID" ]]; then
  echo "Usage: ./scripts/make_share_zip.sh <run_id>"
  exit 2
fi

SHARE_DIR="runs/${RUN_ID}/share"
if [[ ! -d "$SHARE_DIR" ]]; then
  echo "Missing share dir: $SHARE_DIR"
  exit 2
fi

OUT_ZIP="${RUN_ID}__share.zip"
rm -f "$OUT_ZIP"
(cd "$SHARE_DIR" && zip -qr "../../$OUT_ZIP" .)
echo "OK: wrote $OUT_ZIP"
