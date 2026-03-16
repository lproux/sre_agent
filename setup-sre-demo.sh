#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Azure SRE Agent Demo - Setup Script
# Provisions all Azure resources for the demo environment
# ============================================================

TENANT_ID="2b9d9f47-1fb6-400a-a438-39fe7d768649"
SUBSCRIPTION_ID="d334f2cd-3efd-494e-9fd3-2470b1a13e4c"
RESOURCE_GROUP="rg-sre-agent-demo"
LOCATION="swedencentral"
APP_SERVICE_PLAN="plan-sre-demo"
WEB_APP_NAME="app-sre-demo-$(openssl rand -hex 3)"
LOG_ANALYTICS="law-sre-demo"
APP_INSIGHTS="ai-sre-demo"

echo "============================================"
echo "  Azure SRE Agent Demo - Environment Setup"
echo "============================================"
echo ""
echo "Resources will be created in: $LOCATION"
echo "Resource Group: $RESOURCE_GROUP"
echo ""

# ---------- Login & Subscription ----------

echo "[1/8] Logging into Azure..."
az login --tenant "$TENANT_ID" --output none 2>/dev/null || true
az account set --subscription "$SUBSCRIPTION_ID"
echo "  Subscription set to: $SUBSCRIPTION_ID"

# ---------- Resource Group ----------

echo "[2/8] Creating resource group..."
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --output none
echo "  Resource group '$RESOURCE_GROUP' ready."

# ---------- Log Analytics Workspace ----------

echo "[3/8] Creating Log Analytics workspace..."
az monitor log-analytics workspace create \
  --resource-group "$RESOURCE_GROUP" \
  --workspace-name "$LOG_ANALYTICS" \
  --location "$LOCATION" \
  --retention-time 30 \
  --output none
LAW_ID=$(az monitor log-analytics workspace show \
  --resource-group "$RESOURCE_GROUP" \
  --workspace-name "$LOG_ANALYTICS" \
  --query id --output tsv)
echo "  Log Analytics workspace '$LOG_ANALYTICS' ready."

# ---------- Application Insights ----------

echo "[4/8] Creating Application Insights..."
az monitor app-insights component create \
  --app "$APP_INSIGHTS" \
  --location "$LOCATION" \
  --resource-group "$RESOURCE_GROUP" \
  --workspace "$LAW_ID" \
  --kind web \
  --application-type web \
  --output none
AI_CONNECTION_STRING=$(az monitor app-insights component show \
  --app "$APP_INSIGHTS" \
  --resource-group "$RESOURCE_GROUP" \
  --query connectionString --output tsv)
echo "  Application Insights '$APP_INSIGHTS' ready."

# ---------- App Service Plan ----------

echo "[5/8] Creating App Service Plan (Linux B1)..."
az appservice plan create \
  --name "$APP_SERVICE_PLAN" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --sku B1 \
  --is-linux \
  --output none
echo "  App Service Plan '$APP_SERVICE_PLAN' ready."

# ---------- Web App ----------

echo "[6/8] Creating Web App..."
az webapp create \
  --name "$WEB_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --plan "$APP_SERVICE_PLAN" \
  --runtime "NODE:20-lts" \
  --output none

# Configure app settings
az webapp config appsettings set \
  --name "$WEB_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --settings \
    APPLICATIONINSIGHTS_CONNECTION_STRING="$AI_CONNECTION_STRING" \
    APP_HEALTHY="true" \
    WEBSITE_NODE_DEFAULT_VERSION="~20" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
  --output none

# Enable health check
az webapp config set \
  --name "$WEB_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --generic-configurations '{"healthCheckPath": "/health"}' \
  --output none

echo "  Web App '$WEB_APP_NAME' ready."

# ---------- Deploy App Code ----------

echo "[7/8] Deploying application code..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/app"

# Zip deploy
zip -r /tmp/sre-demo-app.zip . -x "node_modules/*" > /dev/null 2>&1
az webapp deploy \
  --name "$WEB_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --src-path /tmp/sre-demo-app.zip \
  --type zip \
  --output none
rm -f /tmp/sre-demo-app.zip

cd "$SCRIPT_DIR"
echo "  Application deployed."

# ---------- Azure Monitor Alert Rules ----------

echo "[8/8] Creating Azure Monitor alert rules..."

WEBAPP_ID=$(az webapp show \
  --name "$WEB_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query id --output tsv)

# Alert: HTTP 5xx errors > 5 in 5 minutes
az monitor metrics alert create \
  --name "alert-http-5xx" \
  --resource-group "$RESOURCE_GROUP" \
  --scopes "$WEBAPP_ID" \
  --condition "total Http5xx > 5" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --severity 1 \
  --description "HTTP 5xx errors exceeded threshold - SRE Agent should investigate" \
  --output none

# Alert: Average response time > 3 seconds
az monitor metrics alert create \
  --name "alert-response-time" \
  --resource-group "$RESOURCE_GROUP" \
  --scopes "$WEBAPP_ID" \
  --condition "avg HttpResponseTime > 3" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --severity 2 \
  --description "Response time exceeded 3s threshold - SRE Agent should investigate" \
  --output none

# Alert: Health check failures
az monitor metrics alert create \
  --name "alert-health-check" \
  --resource-group "$RESOURCE_GROUP" \
  --scopes "$WEBAPP_ID" \
  --condition "avg HealthCheckStatus < 100" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --severity 1 \
  --description "Health check failing - SRE Agent should investigate" \
  --output none

echo "  Alert rules created."

# ---------- Save config for other scripts ----------

CONFIG_FILE="$SCRIPT_DIR/.env"
cat > "$CONFIG_FILE" <<EOF
# Auto-generated by setup-sre-demo.sh - $(date -Iseconds)
TENANT_ID=$TENANT_ID
SUBSCRIPTION_ID=$SUBSCRIPTION_ID
RESOURCE_GROUP=$RESOURCE_GROUP
LOCATION=$LOCATION
WEB_APP_NAME=$WEB_APP_NAME
APP_INSIGHTS=$APP_INSIGHTS
LOG_ANALYTICS=$LOG_ANALYTICS
APP_SERVICE_PLAN=$APP_SERVICE_PLAN
EOF

echo ""
echo "============================================"
echo "  Setup Complete!"
echo "============================================"
echo ""
echo "  Web App URL : https://${WEB_APP_NAME}.azurewebsites.net"
echo "  App Insights: $APP_INSIGHTS"
echo "  Resource Grp: $RESOURCE_GROUP"
echo "  Config saved: $CONFIG_FILE"
echo ""
echo "  Next steps:"
echo "    1. Create SRE Agent in Azure Portal (Sweden Central)"
echo "    2. Connect it to resource group '$RESOURCE_GROUP'"
echo "    3. Run ./generate-traffic.sh 30 min before demo"
echo ""
