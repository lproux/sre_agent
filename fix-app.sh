#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Azure SRE Agent Demo - Fix the App
# Restores APP_HEALTHY=true to return app to normal operation
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Error: .env file not found. Run setup-sre-demo.sh first."
  exit 1
fi

source "$ENV_FILE"

echo "============================================"
echo "  SRE Agent Demo - Fixing the App"
echo "============================================"
echo ""

# Set APP_HEALTHY=true to restore normal operation
echo "[1/2] Setting APP_HEALTHY=true..."
az webapp config appsettings set \
  --name "$WEB_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --settings APP_HEALTHY="true" \
  --output none

# Restart to apply immediately
echo "[2/2] Restarting web app to apply changes..."
az webapp restart \
  --name "$WEB_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --output none

APP_URL="https://${WEB_APP_NAME}.azurewebsites.net"

echo ""
echo "  App is now FIXED!"
echo ""
echo "  All endpoints will return healthy responses."
echo "  Azure Monitor alerts will auto-resolve within ~5 minutes."
echo ""
echo "  Verify: curl $APP_URL/health"
echo ""
