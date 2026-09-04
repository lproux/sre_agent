# Daily Health Check Procedure

Run this check daily (recommended: 9 AM UTC) to verify environment health proactively. Use a read-only posture unless a separately authorized incident response requires a change.

## Check 1: Resource and Control-Plane Status

Enumerate the monitored resources and inspect each critical resource's ARM state.

```
az resource list --resource-group rg-sre-agent-demo --query "[].{name:name,type:type,provisioningState:provisioningState}" --output table
```

For App Service, verify that `state=Running`, `enabled=true`, `availabilityState=Normal`, and the App Service plan is Ready. These are control-plane signals only: do not treat them as proof that application endpoints are healthy.

If Azure CLI authentication or a provider is unavailable, record the exact scope that could not be checked rather than reporting the resource group as healthy.

## Check 2: Application Health and Reachability

Use an authorized network path to probe `/health`, `/api/status`, and `/api/process`, recording status code and latency. Expected baseline:

- `/health`: HTTP 200, < 50 ms
- `/api/status`: HTTP 200, < 100 ms
- `/api/process`: expected status documented by the application, < 500 ms

If the app has private or disabled public network access, do not use a public `403` as an application result. Report application health as unverified until the probe is run from an approved private path.

## Check 3: Alert Rules and Active Alerts

Inspect the configured metric-alert rules:

```
az monitor metrics alert list --resource-group rg-sre-agent-demo --query "[].{name:name,enabled:enabled,severity:severity}" --output table
```

Verify the HTTP 5xx, response-time, and health-check rules are enabled. Query active alert instances separately; enabled rules do not establish that no alert is firing. Record unavailable active-alert queries as a reporting limitation.

## Check 4: Application Insights Error Trends (Last 24 Hours)

First confirm that Application Insights has recent rows. Then calculate request totals, failed requests, failure rate, endpoint/result-code distribution, and the first/last timestamp.

Expected: 0% failures and current telemetry. A zero-row query is not a 0% error rate: treat it as an observability gap and investigate telemetry ingestion before declaring recovery.

Also summarize recent exceptions and warning/error traces. Include the freshness timestamp in the report.

## Check 5: Log Analytics Warnings and Errors (Last 24 Hours)

First sample available tables/rows to confirm the workspace is receiving data. Then query warnings and errors using the actual table schema and log format.

If no rows are present in the workspace, report a Log Analytics ingestion gap. Do not state that there were no warnings or errors without first confirming data freshness.

## Check 6: Capacity and Health Metrics

List supported metrics before querying them. Review `HealthCheckStatus`, `Http5xx`, `Requests`, `CpuTime`, `AverageMemoryWorkingSet`, and `FileSystemUsage`.

Use compatible time grains:

- `HealthCheckStatus`: five minutes or coarser
- `CpuTime`, `AverageMemoryWorkingSet`, `Requests`, `Http5xx`: one minute or coarser
- `FileSystemUsage`: six hours or coarser

Do not interpret zero-valued CPU, memory, request, or 5xx metrics as healthy or idle when application telemetry is stale or health-status values are missing. Report capacity as indeterminate in that case.

## Check 7: TLS Certificates

Verify the configured minimum TLS version and inspect the application certificate's `notAfter` date from an authorized network path. Flag certificates expiring within 30 days.

Do not use a certificate presented by an egress TLS-interception proxy as the application's certificate. If the leaf certificate cannot be inspected, report certificate expiry as unverified.

## Report and Notification

Summarize and email the SRE team:

**Daily Health Check — [UTC date and time]**
- Overall status: HEALTHY / DEGRADED / CRITICAL
- Application: verified result or explicitly unverified scope
- Resources: control-plane state and any resource-health limitations
- Alerts: configured rules and active-alert status separately
- Application Insights and Log Analytics: error results and latest data timestamp
- Capacity: CPU, memory, storage, and health-check findings or limitations
- TLS: minimum version, expiry result, and any inspection limitation
- Action required: concrete next step; confirm whether any changes were made

Use high importance for a CRITICAL report. No Azure resource change should occur during the scheduled check.
