# Daily Health Check Procedure

Run this check daily to assess all monitored Azure resources. Use read-only evidence first; do not restart, scale, modify app settings, or generate synthetic traffic as part of this procedure.

## Scope and Evidence Rules

1. Enumerate enabled subscriptions before querying resources. Record every subscription that is inaccessible.
2. Treat ARM `Running` or `Normal` as control-plane state only. It does not prove endpoint or application health.
3. Do not report a zero error rate when the telemetry source has no recent rows. Check the latest ingested record before interpreting a 24-hour query.
4. If the app is not reachable from the approved monitoring path (for example, public network access is disabled), do not bypass network controls with ad hoc probes. Report endpoint health as unknown unless an approved monitoring signal exists.
5. Do not send a report unless both an approved recipient and a healthy mail connector are documented.

## Check 1: Resource Health and Inventory

Discover enabled subscriptions:
```sh
az account list --query "[?state=='Enabled'].{name:name,id:id}" --output table
```

For each subscription, query Azure Resource Health:
```sh
az graph query -q "HealthResources | extend availability=tostring(properties.availabilityState), summary=tostring(properties.summary), reason=tostring(properties.reasonType), occurred=todatetime(properties.occurredTime) | project id, name, type, availability, summary, reason, occurred | order by occurred desc" --first 100 --subscription <subscription-id> --output json
```

An empty result means no Resource Health events were returned; it is not proof that workloads are healthy. Also collect the resource inventory and alert-rule configuration for each monitored resource group.

## Check 2: Application Health and Telemetry Freshness

Query the connected Application Insights resource for the last 24 hours:
```kusto
requests
| where timestamp >= ago(24h)
| summarize Requests=count(), Failed=countif(success == false), ServerErrors=countif(toint(resultCode) between (500 .. 599)), FailureRatePct=round(100.0 * countif(success == false) / count(), 2), Latest=max(timestamp)
```

Then query all-time freshness before interpreting the result:
```kusto
union requests, exceptions, traces
| summarize Rows=count(), Oldest=min(timestamp), Latest=max(timestamp) by itemType
| order by Latest desc
```

Classify telemetry as **stale** when its newest record is more than 15 minutes old. A stale source makes request-error, exception, and latency status **unknown**, not healthy.

## Check 3: Log Analytics Errors and Warnings

First confirm table freshness:
```kusto
union isfuzzy=true AppRequests, AppExceptions, AppTraces, AppPerformanceCounters, AppMetrics
| summarize Rows=count(), Oldest=min(TimeGenerated), Latest=max(TimeGenerated) by Type
| order by Latest desc
```

After confirming recent data exists, query errors from a table using columns that are present in that table. For example:
```kusto
AppTraces
| where TimeGenerated >= ago(24h)
| extend MessageText=tostring(Message)
| where MessageText has_any ('error', 'fail', 'warn', 'degraded')
| summarize Events=count(), Latest=max(TimeGenerated) by MessageText
| top 20 by Events desc
```

Do not combine table-specific columns in a `union` query unless the schema has been verified.

## Check 4: Certificates

List Azure-managed App Service certificate resources:
```sh
az resource list --resource-type Microsoft.Web/certificates --subscription <subscription-id> --output json
```

Report certificates expiring within 30 days. If no managed certificate resource exists, record that external certificate management was not assessed; do not infer certificate expiry from HTTPS-only configuration.

## Check 5: Capacity and Health Metrics

Use a time grain supported by each metric. For this App Service, use five minutes for `HealthCheckStatus`, `CpuTime`, and `AverageMemoryWorkingSet`, and six hours for `FileSystemUsage`:
```sh
az monitor metrics list --resource <webapp-resource-id> --metric HealthCheckStatus --interval PT5M --aggregation Average --start-time <utc-start> --end-time <utc-end> --subscription <subscription-id>
az monitor metrics list --resource <webapp-resource-id> --metric CpuTime AverageMemoryWorkingSet --interval PT5M --aggregation Average Maximum --start-time <utc-start> --end-time <utc-end> --subscription <subscription-id>
az monitor metrics list --resource <webapp-resource-id> --metric FileSystemUsage --interval PT6H --aggregation Average --start-time <utc-start> --end-time <utc-end> --subscription <subscription-id>
```

`CpuTime` is consumed CPU seconds, not CPU percentage. A metric response with timestamps but no aggregates is missing data, not a passing value. `FileSystemUsage` is reported in bytes; compare it with a known quota before asserting a percentage or capacity risk.

## Check 6: Report Delivery

Before sending, confirm that the report recipient is explicitly documented and the configured Outlook connection is healthy. If either prerequisite is missing, generate the report in the execution response and mark delivery as **blocked**. Do not guess a recipient or attempt connector reauthentication.

## Report Format

**Daily Health Check — [UTC date and window]**
- Application runtime: HEALTHY / DEGRADED / DOWN / UNKNOWN
- Telemetry freshness: current / stale, with latest timestamp
- Resources: Resource Health events or no events returned
- Alerts: enabled configuration and any known active conditions
- Certificates: expirations within 30 days or scope limitation
- Capacity: CPU, memory, storage, and missing-data caveats
- Report delivery: sent / blocked, including the exact blocker
- Action required: prioritized, concrete actions
