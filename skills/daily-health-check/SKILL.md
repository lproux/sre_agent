# Daily Health Check Procedure

Run this check daily (recommended: 9 AM UTC) to verify environment health proactively.

## Safety and Evidence Rules

- Use read-only checks by default. Do not generate test traffic, change app settings, restart the app, alter alerts, scale resources, or reconnect integrations as part of this procedure.
- A normal ARM or Resource Health result proves control-plane state only. It does not prove user-facing availability.
- Direct endpoint checks are permitted only from an approved network location. If the app has private-only access or no approved probe is available, report application availability as **UNVERIFIED** rather than healthy.
- Empty telemetry is not a healthy result. Confirm whether the source has any recent rows, requests, metrics, or health-check values before drawing conclusions.

## Check 1: Application Health

Call `CheckAppHealth` to verify `/health`, `/api/status`, and `/api/process` only when the calling location is authorized to reach the app.

Expected: All endpoints return 200, with latency below the documented baselines.

If direct checks are unavailable, collect read-only fallback evidence:
- App Service ARM state, availability state, and public/private network access.
- App Service `HealthCheckStatus`, `Requests`, and `Http5xx` metrics using supported time grains.
- Application Insights request and exception activity.
- Log Analytics activity for the same window.

Do not infer runtime health from an empty fallback result; mark it **UNVERIFIED** and state the missing evidence.

## Check 2: Resource Status

Run Azure CLI:
```
az resource list --resource-group rg-sre-agent-demo --query "[].{name:name,type:type,provisioningState:provisioningState}" --output table
```

Also check Resource Health and recent resource-specific Activity Logs where supported.

Expected: Resources are present, provisioning is successful, and no Resource Health or recent administrative failure is reported. Record any scope or authorization limitation.

## Check 3: Alert Status

```
az monitor metrics alert list --resource-group rg-sre-agent-demo --query "[].{name:name,enabled:enabled,severity:severity}" --output table
```

Check active alert instances separately. Alert rules being enabled and no active alerts being returned do not establish availability when workload telemetry is missing.

Expected: All three alert rules are enabled, and active alerts are investigated when present.

## Check 4: Performance and Capacity Baseline

Run `AnalyzeResponseTimes` with `num_requests=5` only from an approved network location.

Compare against baselines:
- `/health`: < 50 ms
- `/api/status`: < 100 ms
- `/api/process`: < 500 ms

Also review App Service CPU, memory, and filesystem usage. Use a supported sampling grain for each metric; `FileSystemUsage` requires a coarser interval than CPU and memory. Treat zero CPU/memory together with no requests or telemetry as a signal-quality problem, not proof of low utilization.

## Check 5: Error Trends (Last 24h)

Use `ErrorRateByEndpoint` with `timeRange=24h` when request telemetry is present. Otherwise, query Application Insights and Log Analytics for total records, failures, exceptions, traces, and the most recent observed timestamp.

Expected: A current, non-empty workload signal and 0% error rate across all endpoints. If telemetry is absent, report the error rate as **NOT MEASURABLE**.

## Check 6: TLS, Certificates, and Report Delivery

- Check minimum TLS version and certificate inventory for certificates expiring in the next 30 days.
- Distinguish no certificate inventory from a certificate that is valid beyond 30 days.
- Before delivery, inspect the configured mail connector. If it is already in an error state, make one send attempt only when required by the scheduled task, capture the error, and do not retry.
- Send only to a configured SRE recipient or distribution list. If routing cannot be resolved from the task configuration or an authorized mailbox read, report delivery as **BLOCKED: recipient unavailable**; do not guess an address.

## Report Format

Summarize as:

**Daily Health Check — [Date]**
- Application: HEALTHY / DEGRADED / DOWN / UNVERIFIED
- Resources: ALL OK / [list issues and scope limitations]
- Alerts: None firing / [list firing alerts]
- Performance and capacity: Within baselines / [list deviations or missing signals]
- Error rate (24h): X% / NOT MEASURABLE
- Certificates: None expiring / [list certificates]
- Report delivery: Sent / Failed with reason
- Action required: None / [read-only validation or approved change-control action]
