# Operational Runbooks

## RB-001: High HTTP 5xx Error Rate

### Alert
- Name: alert-http-5xx
- Condition: Total HTTP 5xx > 5 in 5-minute window
- Severity: 1 (Critical)

### Triage Steps
1. Check /health endpoint: `curl https://<app>.azurewebsites.net/health`
2. Check Application Insights > Failures blade for exception details
3. Check Application Insights > Live Metrics for real-time error rate
4. Review recent deployments in Activity Log (portal > Activity Log, filter last 1h)
5. Check app settings for unexpected changes: `az webapp config appsettings list`

### Common Root Causes
- APP_HEALTHY set to "false" (misconfiguration or intentional test)
- Application Insights connection string missing or invalid
- Node.js process crash (check Kudu logs: https://<app>.scm.azurewebsites.net/api/logstream)
- App Service plan out of resources (check CPU/memory metrics)

### Remediation
- If APP_HEALTHY=false: Set to "true" and restart: `az webapp config appsettings set --settings APP_HEALTHY=true` then `az webapp restart`
- If process crash: Check /home/LogFiles/application logs via Kudu, restart app
- If resource exhaustion: Scale up the App Service plan

### Escalation
- If not resolved within 15 min: Escalate to application team
- If infrastructure issue: Escalate to Azure support

---

## RB-002: High Response Time

### Alert
- Name: alert-response-time
- Condition: Average HttpResponseTime > 3 seconds in 5-minute window
- Severity: 2 (Warning)

### Triage Steps
1. Check /api/status for current app state and uptime
2. Check Application Insights > Performance blade for slow endpoints
3. Check CPU and memory metrics on App Service
4. Check if issue correlates with 5xx errors (often same root cause)
5. Check Application Insights > Application Map for dependency bottlenecks

### Common Root Causes
- APP_HEALTHY=false causes CPU-intensive simulation (artificial load)
- High concurrent request volume exceeding B1 capacity
- Upstream dependency slowness (in production: Cosmos DB, AI Document Intelligence)
- Node.js event loop blocking

### Remediation
- If caused by APP_HEALTHY=false: Same as RB-001
- If load-related: Scale up plan or reduce traffic
- If dependency: Check dependency health in Application Map

---

## RB-003: Health Check Failures

### Alert
- Name: alert-health-check
- Condition: Average HealthCheckStatus < 100% in 5-minute window
- Severity: 1 (Critical)

### Triage Steps
1. Directly call /health endpoint
2. Check if the app process is running (App Service > Overview > Status)
3. Check for recent restarts in Activity Log
4. Check if APP_HEALTHY setting changed recently

### Common Root Causes
- APP_HEALTHY=false (most common in this environment)
- App Service instance unhealthy / cold start
- Application crash during startup

### Remediation
- Verify APP_HEALTHY setting and correct if needed
- Restart the web app: `az webapp restart`
- If persistent: Check startup logs in Kudu

---

## RB-004: Application Not Starting

### Triage Steps
1. Check App Service > Deployment Center > Logs for build errors
2. Check Kudu logs: https://<app>.scm.azurewebsites.net/api/logstream
3. Verify Node.js runtime version matches package.json engines
4. Check if package.json has valid "start" script
5. Verify SCM_DO_BUILD_DURING_DEPLOYMENT is "true"

### Common Root Causes
- Missing dependencies (npm install failed during deployment)
- Invalid server.js syntax
- Port binding issue (must use process.env.PORT)

### Remediation
- Redeploy: `az webapp up` from the app/ directory
- Check and fix package.json, redeploy

---

## RB-005: Application Insights Data Missing

### Triage Steps
1. Check APPLICATIONINSIGHTS_CONNECTION_STRING in app settings
2. Verify App Insights resource exists: `az monitor app-insights component show --app ai-sre-demo -g rg-sre-agent-demo`
3. Check if the app process initialized the SDK (look for startup logs)
4. Check App Insights > Overview for ingestion latency

### Common Root Causes
- Connection string not set or incorrect
- App Insights resource deleted
- Ingestion delay (can be 2-5 minutes for non-live data)

### Remediation
- Re-set connection string from App Insights resource
- Wait 5 min for data propagation
- Restart app to reinitialize SDK
