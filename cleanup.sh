#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Azure SRE Agent Demo - Cleanup
# Deletes all Azure resources created by setup-sre-demo.sh
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Error: .env file not found. Nothing to clean up."
  exit 1
fi

source "$ENV_FILE"

echo "============================================"
echo "  SRE Agent Demo - Cleanup"
echo "============================================"
echo ""
echo "  This will DELETE the following resources:"
echo "    - Resource Group: $RESOURCE_GROUP"
echo "    - Web App:        $WEB_APP_NAME"
echo "    - App Insights:   $APP_INSIGHTS"
echo "    - Log Analytics:  $LOG_ANALYTICS"
echo "    - App Service:    $APP_SERVICE_PLAN"
echo "    - All alert rules"
echo ""
read -rp "  Are you sure? (y/N): " CONFIRM

if [[ "${CONFIRM,,}" != "y" ]]; then
  echo "  Cleanup cancelled."
  exit 0
fi

echo ""
echo "[1/2] Deleting resource group '$RESOURCE_GROUP' (this may take a few minutes)..."
az group delete \
  --name "$RESOURCE_GROUP" \
  --yes \
  --no-wait \
  --output none

echo "[2/2] Removing local config..."
rm -f "$ENV_FILE"

echo ""
echo "  Cleanup initiated!"
echo "  Resource group deletion runs in background (~2-5 minutes)."
echo "  Verify: az group exists --name $RESOURCE_GROUP"
echo ""
