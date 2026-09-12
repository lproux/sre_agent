# Daily Health Check Procedure

Run this check daily (recommended: 9 AM UTC) to verify environment health proactively. Keep the execution read-only unless the requester explicitly asks for remediation.

## Check 1: Application and Telemetry Health

1. Check Application Insights request and exception telemetry for the prior 24 hours. Report request count, failures, 5xx count, error rate, and latest event timestamp.
2. Check the linked Log Analytics workspace for the same request/error totals and latest ingestion timestamp.
3. Treat an empty or stale result as an observability incident, not as proof of zero errors. Confirm that the source has current rows before concluding the application is healthy.
4. If public network access is disabled, do not treat an external 403 as an application health result. Use an authorized private-network probe for `/health`, `/api/status`, and `/api/process`.
5. If `/health` returns 503, correlate it with current exception text and the deployed health-check implementation before naming a cause.

Expected: Fresh telemetry, successful health requests, and no unexplained errors. State explicitly when any of these cannot be verified.

## Check 2: Resource Status

Inventory all accessible resources and inspect the workload control plane separately:
```
az resource list --resource-group rg-sre-agent-demo --output table
az webapp show --name <app-name> --resource-group rg-sre-agent-demo --query "{state:state,availabilityState:availabilityState,contentAvailabilityState:contentAvailabilityState,runtimeAvailabilityState:runtimeAvailabilityState,publicNetworkAccess:publicNetworkAccess}" --output json
az appservice plan show --name <plan-name> --resource-group rg-sre-agent-demo --query "{status:status,powerState:powerState,workers:currentNumberOfWorkers,maxWorkers:maximumNumberOfWorkers}" --output json
```

`Running`, `Ready`, and `Normal` are control-plane signals only; do not use them as proof of application availability. If Azure Resource Health cannot be queried, report that coverage gap.

## Check 3: Alert Status

```
az monitor metrics alert list --resource-group rg-sre-agent-demo --query "[].{name:name,enabled:enabled,severity:severity,metric:criteria.allOf[0].metricName,threshold:criteria.allOf[0].threshold}" --output table
```

Verify alert instances separately when the provider is available. Enabled rules do not prove that notifications were delivered or that an active incident was captured.

## Check 4: Capacity and Performance

Use native metric grains for the App Service:
- `Requests`, `Http5xx`, `CpuTime`, and `AverageMemoryWorkingSet`: `PT1M`
- `HealthCheckStatus`: `PT5M`
- `FileSystemUsage`: `PT6H`

Report the latest non-null timestamp and peak value for CPU, memory, health, and filesystem metrics. Do not interpret a raw filesystem value as a quota percentage until its unit and capacity threshold are confirmed. If the metric definition describes `FileSystemUsage` as a percentage but the returned values are raw units, report the raw values and flag the unit discrepancy; only calculate a percentage after validating the effective quota and conversion. Use request telemetry for latency only when it is fresh.

## Check 5: Certificates

1. Record the configured minimum TLS version.
2. List uploaded or custom App Service certificates and identify certificates expiring within 30 days.
3. For a private-only endpoint or proxy-intercepted connection, state that external certificate inspection is not authoritative. Do not report a proxy certificate as the App Service certificate.

## Report Format

Summarize as:

**Daily Health Check — [UTC date and time]**
- Overall status: HEALTHY / DEGRADED / CRITICAL
- Application: current request/error evidence, endpoint status, and the latest telemetry timestamp
- Resources: control-plane state and any Azure Resource Health coverage gap
- Alerts: rule configuration, active-instance result, and any notification coverage limitation
- Capacity: CPU, memory, filesystem trend, and the freshness of each metric
- TLS and certificates: minimum TLS, custom certificates expiring within 30 days, and any inspection limitation
- Action required: specific next steps, including an authorized private probe or observability restoration when needed
- Changes made: explicitly state `None` for a read-only execution
