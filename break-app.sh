#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Azure SRE Agent Demo - Break the App
# Sets APP_HEALTHY=false to trigger failures and alerts
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Error: .env file not found. Run setup-sre-demo.sh first."
  exit 1
fi

source "$ENV_FILE"

echo "============================================"
echo "  SRE Agent Demo - Breaking the App"
echo "============================================"
echo ""

# Set APP_HEALTHY=false to trigger failure mode
echo "[1/2] Setting APP_HEALTHY=false..."
az webapp config appsettings set \
  --name "$WEB_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --settings APP_HEALTHY="false" \
  --output none

# Restart the app to ensure the setting takes effect immediately
echo "[2/2] Restarting web app to apply changes..."
az webapp restart \
  --name "$WEB_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --output none

APP_URL="https://${WEB_APP_NAME}.azurewebsites.net"

echo ""
echo "  App is now BROKEN!"
echo ""
echo "  What will happen:"
echo "    - /health returns 503"
echo "    - /api/process returns 500"
echo "    - All endpoints have high latency"
echo "    - Application Insights logs exceptions"
echo "    - Azure Monitor alerts will fire within ~5 minutes"
echo ""
echo "  Generating error traffic to accelerate alert triggers..."
echo ""

# Send a burst of requests to ensure alerts fire quickly
for i in $(seq 1 20); do
  curl -s -o /dev/null "$APP_URL/health" 2>/dev/null &
  curl -s -o /dev/null -X POST "$APP_URL/api/process" \
    -H "Content-Type: application/json" \
    -d '{"documentType":"invoice","fileName":"test.pdf"}' 2>/dev/null &
done
wait

echo "  20 error requests sent."
echo ""
echo "  Verify: curl $APP_URL/health"
echo "  Fix with: ./fix-app.sh"
echo ""
