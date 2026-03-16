# App Service Troubleshooting Guide

You are investigating an issue with an Azure App Service web application. Follow these steps systematically. Do NOT skip steps.

## Step 1: Establish Current State

Run the health check tool first to understand current application state:
- Call `CheckAppHealth` with the app URL to check /health, /api/status, and /api/process
- Note the HTTP status codes and response times
- If all endpoints return 200 with low latency, the issue may have self-resolved

## Step 2: Check Error Patterns

Query Application Insights for recent exceptions:
- Use `QueryTopExceptions` with timeRange=1h to see what's failing
- Use `ErrorRateByEndpoint` with timeRange=1h to identify which endpoints are affected
- Look for patterns: Are all endpoints failing? Just one? Is it intermittent?

Key exception patterns for this application:
- "Document processing engine failure - connection pool exhausted" → APP_HEALTHY is set to false
- "Health check failed - service degraded" → Same root cause (APP_HEALTHY=false)
- "Failed to retrieve document - storage timeout" → Same root cause

## Step 3: Correlate with Recent Changes

Check the Activity Log for what changed:
- Use `RecentConfigChanges` with timeRange=2h
- Look specifically for:
  - `Microsoft.Web/sites/config/write` — App settings changed
  - `Microsoft.Web/sites/publish` — New code deployed
  - `Microsoft.Web/sites/restart/action` — App restarted
- If APP_HEALTHY was changed to "false", that is the root cause

## Step 4: Check Resource Health

Run Azure CLI to check infrastructure:
```
az webapp show --name <app-name> --resource-group rg-sre-agent-demo --query "{state:state,healthCheckPath:siteConfig.healthCheckPath,alwaysOn:siteConfig.alwaysOn}"
```

```
az appservice plan show --name plan-sre-demo --resource-group rg-sre-agent-demo --query "{sku:sku.name,workers:numberOfWorkers,status:status}"
```

## Step 5: Check Application Settings

Verify the critical app settings:
```
az webapp config appsettings list --name <app-name> --resource-group rg-sre-agent-demo --query "[?name=='APP_HEALTHY' || name=='APPLICATIONINSIGHTS_CONNECTION_STRING'].{name:name,value:value}"
```

If APP_HEALTHY is "false", this is the root cause.

## Step 6: Produce Root Cause Analysis

Based on findings, produce an RCA with:
1. **What happened** — Describe the symptoms
2. **When** — Timeline from Activity Log
3. **Root cause** — The validated finding
4. **Evidence** — Specific data points (error counts, timestamps, config changes)
5. **Recommended fix** — Specific action to resolve

## Common Fixes

| Root Cause | Fix |
|-----------|-----|
| APP_HEALTHY=false | `az webapp config appsettings set --name <app> -g rg-sre-agent-demo --settings APP_HEALTHY=true` then `az webapp restart` |
| Missing App Insights connection string | Re-configure from App Insights resource |
| App not starting | Check Kudu logs at `https://<app>.scm.azurewebsites.net/api/logstream` |
| High CPU | Check if caused by APP_HEALTHY=false (artificial load), or scale up the plan |
