# Daily Health Check Procedure

Run this check daily (recommended: 9 AM UTC) to verify environment health proactively.

## Check 1: Functional Application Health

Use an external IPv4 HTTPS probe for each monitored endpoint. Do not infer functional health from App Service ARM state alone.

```bash
curl -4 -sS -o /dev/null -w 'http_code=%{http_code} remote_ip=%{remote_ip} total_time=%{time_total}\n' \
  --connect-timeout 10 --max-time 20 \
  https://<app-name>.azurewebsites.net/health
```

Expected: HTTP 200 and latency within the endpoint baseline. Record connection or response timeouts as application-down evidence. ARM `Running` or `availabilityState=Normal` does not override a failed end-to-end probe.

## Check 2: Resource and Control-Plane Status

Inventory the scoped resources, then inspect the App Service and plan directly:

```bash
az resource list --resource-group rg-sre-agent-demo --subscription <subscription-id> \
  --query "[].{name:name,type:type,location:location}" --output table

az webapp show --name <app-name> --resource-group rg-sre-agent-demo --subscription <subscription-id> \
  --query "{state:state,availabilityState:availabilityState,usageState:usageState,contentAvailabilityState:contentAvailabilityState,runtimeAvailabilityState:runtimeAvailabilityState,lastModifiedTimeUtc:lastModifiedTimeUtc}" --output json

az appservice plan show --name plan-sre-demo --resource-group rg-sre-agent-demo --subscription <subscription-id> \
  --query "{sku:sku.name,workers:numberOfWorkers,status:status}" --output json
```

Generic resource inventory does not reliably expose a provisioning state. Treat the direct resource reads as the control-plane result only; compare them with the public probe.

## Check 3: Alert Configuration and Active Instances

Verify both alert-rule configuration and active alert instances:

```bash
az monitor metrics alert list --resource-group rg-sre-agent-demo --subscription <subscription-id> \
  --query "[].{name:name,enabled:enabled,severity:severity,scopes:scopes}" --output table

az rest --method get \
  --url "https://management.azure.com/subscriptions/<subscription-id>/providers/Microsoft.AlertsManagement/alerts?api-version=2026-01-26-preview" \
  --subscription <subscription-id> --output json
```

Expected: all required rules are enabled. An empty active-alert result does not prove the application is healthy when monitoring ingestion has stopped; report that limitation explicitly.

## Check 4: Quick Performance Baseline

Use the public probe result from Check 1 and repeat it for each endpoint where a baseline exists. Compare successful response times against:
- `/health`: < 50 ms
- `/api/status`: < 100 ms
- `/api/process`: < 500 ms

Do not calculate a latency baseline from failed or timed-out requests. A timeout is an availability incident, not a slow-successful request.

## Check 5: Application Insights and Log Analytics Trends (Last 24h)

Query the connected Log Analytics workspace for request failures and the matching exception pattern:

```kusto
AppRequests
| where TimeGenerated >= ago(24h)
| summarize Requests=count(), Failed=countif(Success == false), ResultCodes=make_set(ResultCode), First=min(TimeGenerated), Last=max(TimeGenerated)

AppExceptions
| where TimeGenerated >= ago(24h)
| summarize Count=count(), First=min(TimeGenerated), Last=max(TimeGenerated) by ExceptionType, OuterMessage
| order by Count desc

AppTraces
| where TimeGenerated >= ago(24h)
| summarize Records=count(), WarningsOrErrors=countif(SeverityLevel >= 2), Latest=max(TimeGenerated)
```

Always check telemetry freshness before reporting a zero-error result:

```kusto
union withsource=SourceTable AppRequests, AppExceptions, AppTraces
| summarize Records=count(), Latest=max(TimeGenerated) by SourceTable
| order by SourceTable asc
```

If the latest records predate the check window or request/exception telemetry stops while the endpoint is unavailable, report an observability gap. Do not call the service recovered. If the exception is `Health check failed - service degraded`, follow the App Service troubleshooting procedure; only validate or change `APP_HEALTHY` after the required access and change authorization are documented.

## Check 6: Capacity, TLS, and Recent Changes

Query CPU and memory independently at a supported granularity. Query storage separately because `FileSystemUsage` requires a six-hour-or-larger interval:

```bash
az monitor metrics list --resource <app-resource-id> --metrics CpuTime AverageMemoryWorkingSet \
  --interval PT1M --aggregation Average --start-time <start-utc> --end-time <end-utc> \
  --subscription <subscription-id> --output json

az monitor metrics list --resource <app-resource-id> --metrics FileSystemUsage \
  --interval PT6H --aggregation Average --start-time <start-utc> --end-time <end-utc> \
  --subscription <subscription-id> --output json
```

Verify the public certificate and minimum TLS version:

```bash
printf '\n' | openssl s_client -connect <app-name>.azurewebsites.net:443 -servername <app-name>.azurewebsites.net 2>/dev/null \
  | openssl x509 -noout -issuer -subject -dates

az webapp config show --name <app-name> --resource-group rg-sre-agent-demo --subscription <subscription-id> \
  --query "{minTlsVersion:minTlsVersion}" --output json
```

Review App Service Activity Log events for the previous 24 hours, especially configuration writes, publishes, restarts, and deployment operations. If a metric or log source has no current data, identify the coverage gap rather than treating it as zero utilization or zero errors. Do not restart, scale, change configuration, or delete resources without documented justification, explicit approval, and a confirmed maintenance/change window.

## Report Format

Summarize as:

**Daily Health Check — [Date]**
- Application: HEALTHY / DEGRADED / DOWN
- Resources: ALL OK / [list issues]
- Alerts: None firing / [list firing alerts]
- Performance: Within baselines / [list deviations]
- Error rate (24h): X%
- Action required: None / [list actions]
