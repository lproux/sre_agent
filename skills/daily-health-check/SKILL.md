# Daily Health Check Procedure

Run this check daily (recommended: 9 AM UTC) to verify environment health proactively.

## Check 1: Application Health

Call `CheckAppHealth` to verify documented endpoints are responding.

Expected: All required endpoints return 200, latency < 500ms. Record an unexpected 404 separately from an availability failure.

## Check 2: Resource Status and Resource Health

1. Enumerate monitored resources in every accessible subscription and inspect service-specific state where available. A null `provisioningState` in generic resource inventory is not, by itself, a failure.
2. Query Azure Resource Health for monitored production resources.
3. If `Microsoft.ResourceHealth` or `availabilityStatuses` is not registered or cannot be read, report the visibility limitation. Do not register providers or change roles during this read-only check.

Example inventory command:
```
az resource list --resource-group rg-sre-agent-demo --subscription <subscription-id> --query "[].{name:name,type:type,location:location}" --output table
```

## Check 3: Alert Status

```
az monitor metrics alert list --resource-group rg-sre-agent-demo --subscription <subscription-id> --query "[].{name:name,enabled:enabled,severity:severity,scopes:scopes}" --output table
```

Confirm rule configuration and retrieve active alert instances separately when the alert-management read path is available. If alert instances cannot be queried, state that limitation rather than reporting that no alerts are firing.

## Check 4: Endpoint Performance

Run `AnalyzeResponseTimes` with `num_requests=5`, or equivalent external HTTPS probes, for documented endpoints.

Compare against baselines:
- /health: < 50ms
- /api/status: < 100ms
- /api/process: < 500ms when that endpoint is implemented

Record each status code and latency. A health endpoint returning 5xx or exceeding its timeout is a critical application-health failure even if another endpoint responds normally.

## Check 5: Application Insights and Log Analytics (Last 24h)

1. Use `ErrorRateByEndpoint` with `timeRange=24h`, or query Application Insights `requests`, `exceptions`, and relevant `traces` directly.
2. Report request count, failed count, failure rate, result codes, affected operations, exception count, and the first and last failure timestamps.
3. Query Log Analytics warning and error events. First sample raw rows to confirm table and severity-field shape before aggregating.
4. Treat fresh application traces as evidence of current application state. Do not treat an empty log result as proof of health without first confirming the source has recent rows.

Expected: 0% error rate across required endpoints and no unexplained warnings or errors.

## Check 6: TLS and Capacity

1. Inspect public TLS certificates and flag certificates expiring within 30 days.
2. Review CPU, memory, and filesystem/storage metrics over the same 24-hour window using supported metric intervals.
3. Report peak values and the latest non-zero samples. If metrics become zero-valued or stop arriving while the application is still serving traffic, report telemetry/process-lifecycle uncertainty; do not interpret those samples as idle capacity or recovery.

## Check 7: Report Delivery and Change Control

Send the SRE summary to the configured recipient or distribution list, mark the message high importance for critical degradation, and verify that it appears in Sent Items.

This procedure is read-only. Do not restart, scale, deploy, change app settings, grant roles, or register providers without explicit authorization and an approved change window.

## Report Format

Summarize as:

**Daily Health Check — [Date]**
- Application: HEALTHY / DEGRADED / DOWN
- Resources: ALL OK / [list issues]
- Alerts: None firing / [list firing alerts]
- Performance: Within baselines / [list deviations]
- Error rate (24h): X%
- Action required: None / [list actions]
