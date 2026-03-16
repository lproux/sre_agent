# Daily Health Check Procedure

Run this check daily (recommended: 9 AM UTC) to verify environment health proactively.

## Check 1: Application Health

Call `CheckAppHealth` to verify all endpoints are responding.

Expected: All endpoints return 200, latency < 500ms.

## Check 2: Resource Status

Run Azure CLI:
```
az resource list --resource-group rg-sre-agent-demo --query "[].{name:name,type:type,provisioningState:provisioningState}" --output table
```

Expected: All resources show provisioningState=Succeeded.

## Check 3: Alert Status

```
az monitor metrics alert list --resource-group rg-sre-agent-demo --query "[].{name:name,enabled:enabled,severity:severity}" --output table
```

Expected: All 3 alert rules enabled, none currently firing.

## Check 4: Quick Performance Baseline

Run `AnalyzeResponseTimes` with num_requests=5 for a quick performance check.

Compare against baselines:
- /health: < 50ms
- /api/status: < 100ms
- /api/process: < 500ms

## Check 5: Error Trends (Last 24h)

Use `ErrorRateByEndpoint` with timeRange=24h.

Expected: 0% error rate across all endpoints.

## Report Format

Summarize as:

**Daily Health Check — [Date]**
- Application: HEALTHY / DEGRADED / DOWN
- Resources: ALL OK / [list issues]
- Alerts: None firing / [list firing alerts]
- Performance: Within baselines / [list deviations]
- Error rate (24h): X%
- Action required: None / [list actions]
