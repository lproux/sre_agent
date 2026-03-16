#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Azure SRE Agent Demo - Traffic Generator
# Run 30 minutes before demo to populate App Insights with data
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Error: .env file not found. Run setup-sre-demo.sh first."
  exit 1
fi

source "$ENV_FILE"

APP_URL="https://${WEB_APP_NAME}.azurewebsites.net"
DURATION_SECONDS=${1:-1800}  # default: 30 minutes
INTERVAL=${2:-2}             # default: 2 seconds between requests

echo "============================================"
echo "  SRE Agent Demo - Traffic Generator"
echo "============================================"
echo ""
echo "  Target : $APP_URL"
echo "  Duration: ${DURATION_SECONDS}s"
echo "  Interval: ${INTERVAL}s between requests"
echo ""
echo "  Press Ctrl+C to stop early."
echo ""

DOC_TYPES=("invoice" "receipt" "purchase_order" "credit_note" "delivery_note")
FILE_NAMES=("INV-2024-001.pdf" "REC-55432.pdf" "PO-88210.pdf" "CN-12345.pdf" "DN-99001.pdf" "scan_batch_01.tiff" "email_attachment.pdf")

END_TIME=$(($(date +%s) + DURATION_SECONDS))
REQUEST_COUNT=0
ERROR_COUNT=0

while [[ $(date +%s) -lt $END_TIME ]]; do
  REQUEST_COUNT=$((REQUEST_COUNT + 1))

  # Mix of different request types
  RAND=$((RANDOM % 10))

  if [[ $RAND -lt 3 ]]; then
    # 30% - health check
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL/health" 2>/dev/null || echo "000")
    echo "  [$REQUEST_COUNT] GET /health -> $STATUS"

  elif [[ $RAND -lt 5 ]]; then
    # 20% - list documents
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL/api/documents" 2>/dev/null || echo "000")
    echo "  [$REQUEST_COUNT] GET /api/documents -> $STATUS"

  elif [[ $RAND -lt 7 ]]; then
    # 20% - get single document
    DOC_ID="doc-sample-$((RANDOM % 5 + 1))"
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL/api/documents/$DOC_ID" 2>/dev/null || echo "000")
    echo "  [$REQUEST_COUNT] GET /api/documents/$DOC_ID -> $STATUS"

  elif [[ $RAND -lt 9 ]]; then
    # 20% - process document
    DOC_TYPE=${DOC_TYPES[$((RANDOM % ${#DOC_TYPES[@]}))]}
    FILE_NAME=${FILE_NAMES[$((RANDOM % ${#FILE_NAMES[@]}))]}
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
      -X POST "$APP_URL/api/process" \
      -H "Content-Type: application/json" \
      -d "{\"documentType\":\"$DOC_TYPE\",\"fileName\":\"$FILE_NAME\"}" \
      2>/dev/null || echo "000")
    echo "  [$REQUEST_COUNT] POST /api/process ($DOC_TYPE) -> $STATUS"

  else
    # 10% - status check
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL/api/status" 2>/dev/null || echo "000")
    echo "  [$REQUEST_COUNT] GET /api/status -> $STATUS"
  fi

  if [[ "$STATUS" -ge 500 ]] || [[ "$STATUS" == "000" ]]; then
    ERROR_COUNT=$((ERROR_COUNT + 1))
  fi

  sleep "$INTERVAL"
done

echo ""
echo "============================================"
echo "  Traffic Generation Complete"
echo "============================================"
echo "  Total requests: $REQUEST_COUNT"
echo "  Errors (5xx):   $ERROR_COUNT"
echo ""
