# Deployment Procedures

## Current Deployment Method
- **Method**: Azure CLI zip deployment via `az webapp up`
- **Source**: `app/` directory in the sre_agent repository
- **Build**: SCM_DO_BUILD_DURING_DEPLOYMENT=true (npm install runs on Azure)
- **Runtime**: Node.js 20 LTS on Linux App Service

## Deployment Steps
1. Make code changes in `app/` directory
2. From `app/` directory, run: `az webapp up --name <app-name> --resource-group rg-sre-agent-demo`
3. Azure builds the app (runs npm install)
4. New code goes live automatically
5. Verify: `curl https://<app>.azurewebsites.net/health`

## Deployment Impact
- Brief downtime during deployment (10-30 seconds)
- Cold start latency for first few requests (see KI-002)
- Health check may briefly fail (see KI-004)

## Rollback
No automated rollback configured. To rollback:
1. Revert code changes locally
2. Redeploy with `az webapp up`

## Configuration Changes
App settings changes (like APP_HEALTHY) take effect after app restart:
```
az webapp config appsettings set --name <app> -g rg-sre-agent-demo --settings KEY=VALUE
az webapp restart --name <app> -g rg-sre-agent-demo
```

Changes to app settings are logged in the Azure Activity Log and visible to SRE Agent.

## Recent Deployment History
- Initial deployment: Setup script creates the environment from scratch
- No CI/CD pipeline configured (demo environment, manual deploys only)

## Note for SRE Agent
When investigating incidents, always check the Activity Log for recent:
- Deployment operations (Microsoft.Web/sites/publish)
- Configuration changes (Microsoft.Web/sites/config/write)
- Restart operations (Microsoft.Web/sites/restart/action)

These are the most common causes of state changes in this environment.
