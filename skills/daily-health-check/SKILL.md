# Daily Health Check Procedure

Run this check daily (recommended: 9 AM UTC) to verify environment health proactively.

## Scope and evidence rules

- Control-plane status such as `Running` or `Normal` does not prove an application endpoint is reachable.
- Treat a zero count with a null last-seen timestamp as a telemetry coverage gap, not a healthy or zero-error workload.
- Do not generate synthetic traffic or bypass network restrictions. For a private-only application, record runtime availability as **UNVERIFIED** unless an approved private-network probe is available.
- Do not send a report unless the recipient is an explicitly documented SRE distribution list and the mail connector is healthy.

## Check 1: Subscription and resource status

List the accessible subscriptions, then inventory the demo resource group:
```
az account list --query "[].{name:name,id:id,state:state,isDefault:isDefault}" --output table
az resource list --resource-group rg-sre-agent-demo --query "[].{name:name,type:type,location:location}" --output table
```

Inspect the App Service state and availability fields. Record any resource whose state is not expected, but do not infer endpoint health from these fields alone.

## Check 2: Resource Health and recent changes

Query Resource Health for every accessible subscription. Project nested timestamps to a scalar before ordering:
```
az graph query -q "HealthResources | extend occurredTime=todatetime(properties.occurredTime) | project id, name, availabilityState=tostring(properties.availabilityState), summary=tostring(properties.summary), occurredTime | order by occurredTime desc" --subscriptions <subscription-id> --first 100
```

Also query Activity Log events for the last 24 hours on the monitored App Service. No accessible Resource Health records is a coverage limitation, not confirmation of health.

## Check 3: Runtime reachability

First inspect the App Service `publicNetworkAccess` and health-check configuration.

- If public access is enabled and an approved probe path exists, check only the approved endpoint and compare latency against the documented baseline.
- If public access is disabled or the path is not approved, do not probe `/health`, `/api/status`, or `/api/process` from outside the private network. Report application runtime as **UNVERIFIED** and request an approved private-network probe.
- A null `HealthCheckStatus` metric means the platform health-check signal is unavailable; it is not a passing result.

## Check 4: Telemetry and error trends (last 24 hours)

Query Application Insights for request volume, failed requests, server errors, exceptions, and the latest telemetry timestamp. Query Log Analytics for a schema-agnostic telemetry-presence check:
```
search * | where TimeGenerated >= ago(24h) | summarize Records=count(), LastSeen=max(TimeGenerated)
```

Use a table-specific warning/error query only after sampling the actual table schema. Do not assume `SeverityLevel` exists in `search *` output.

Expected behavior: nonzero recent request or log volume with low error rate. If Application Insights or Log Analytics returns zero records and a null last-seen timestamp, escalate the observability gap and check the last telemetry timestamp over 30 days.

## Check 5: Capacity and platform metrics

For the App Service, review CPU, memory, HTTP 5xx, filesystem use, and health-check status over the last 24 hours. Use metric-specific supported intervals:

- `CpuTime`, `AverageMemoryWorkingSet`, `Http5xx`: `PT1H`
- `FileSystemUsage`: `PT6H`
- `HealthCheckStatus`: `PT5M`

Query metrics with incompatible supported intervals in separate calls; Azure Monitor rejects a combined request unless all requested metrics share the same interval.

Zero CPU, memory, and 5xx samples with no corroborating traffic should be reported as insufficient workload evidence, not as healthy utilization. Record stable filesystem use as a capacity observation, but do not assume the raw metric value is a percentage without confirming its unit.

## Check 6: Certificates and alerts

List `Microsoft.Web/certificates` resources and flag any expiry within 30 days. An empty certificate inventory means no Azure-managed certificate was found; it does not assess certificates managed outside Azure.

List metric alert rules and confirm they are enabled and scoped to the expected App Service. If active alert instances or delivery history are not accessible, state that limitation explicitly.

## Check 7: Report delivery

Before sending, verify both of the following:

1. An approved SRE distribution-list address is documented in the team contacts or task configuration.
2. The Office 365 connection has `connectionState=Enabled` and `overallStatus=Connected` or an equivalent healthy status.

If either check fails, do not guess recipients or retry authentication. Record the delivery failure and its error code in the report.

## Report Format

Summarize as:

**Daily Health Check — [Date]**
- Application: HEALTHY / DEGRADED / DOWN
- Resources: ALL OK / [list issues]
- Alerts: None firing / [list firing alerts]
- Performance: Within baselines / [list deviations]
- Error rate (24h): X%
- Action required: None / [list actions]
