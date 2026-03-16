# Incident Response Procedure

You are responding to a production incident. Follow this structured procedure to triage, investigate, and recommend remediation.

## Phase 1: Triage (First 2 minutes)

### 1.1 Assess Severity
Determine severity based on these criteria:

| Severity | Criteria |
|----------|----------|
| **Sev 1** | Health endpoint returning non-200, >5% error rate, or complete service outage |
| **Sev 2** | Response time >3s, intermittent errors, or partial functionality loss |
| **Sev 3** | Minor anomalies, no user impact, cosmetic issues |

### 1.2 Check Current Application State
- Call `CheckAppHealth` to verify what's actually happening RIGHT NOW
- This tells you immediately if the issue is ongoing or resolved

### 1.3 Check Fired Alerts
Run Azure CLI to see which alerts are currently firing:
```
az monitor metrics alert list --resource-group rg-sre-agent-demo --query "[?properties.currentSeverity!=null].{name:name,severity:properties.severity,state:properties.currentSeverity}" --output table
```

## Phase 2: Investigation (Next 3-5 minutes)

### 2.1 Understand the Error Pattern
- Use `QueryTopExceptions` with timeRange=1h for the most common exceptions
- Use `ErrorRateByEndpoint` with timeRange=1h for per-endpoint breakdown
- Use `AvailabilityTimeline` with timeRange=2h and bucketSize=5m to see when things started going wrong

### 2.2 Correlate with Changes
This is the most critical step. Most incidents are caused by changes.
- Use `RecentConfigChanges` with timeRange=6h
- Look for operations that happened BEFORE the error spike
- Common culprits:
  - Configuration changes (settings updated)
  - Deployments (new code pushed)
  - Restarts (could be intentional or crash-loop)
  - Scale operations (resource changes)

### 2.3 Check Dependencies
- Use `MapDependencies` to understand the architecture
- For each dependency, verify its health
- Check if the issue is in our app or in a dependency

### 2.4 Check Resource Metrics
```
az monitor metrics list --resource <webapp-resource-id> --metric "CpuPercentage" --interval PT5M --start-time <1-hour-ago>
az monitor metrics list --resource <webapp-resource-id> --metric "MemoryPercentage" --interval PT5M --start-time <1-hour-ago>
```

## Phase 3: Root Cause Analysis

### 3.1 Form Hypotheses
Based on evidence gathered, form 2-3 hypotheses:
- Was it a configuration change? (Check Activity Log)
- Was it a deployment? (Check Activity Log for publish operations)
- Was it resource exhaustion? (Check CPU/memory metrics)
- Was it a dependency failure? (Check Application Map)

### 3.2 Validate Each Hypothesis
For each hypothesis:
1. State the theory
2. List the evidence for and against
3. Mark as VALIDATED, INVALIDATED, or INCONCLUSIVE

### 3.3 Produce RCA
Structure your findings as:
1. **Incident Summary** — What happened in 1-2 sentences
2. **Timeline** — Chronological list of events with timestamps
3. **Root Cause** — The validated hypothesis with evidence
4. **Impact** — What was affected (endpoints, users, duration)
5. **Recommended Fix** — Specific, actionable remediation step
6. **Prevention** — How to prevent recurrence

## Phase 4: Remediation

### 4.1 Propose Fix
Based on the RCA, propose a specific remediation action. Common fixes:
- Set APP_HEALTHY=true and restart (if config-related)
- Rollback deployment (if code-related)
- Scale up App Service plan (if resource-related)

### 4.2 Verify Fix
After remediation is applied:
- Call `CheckAppHealth` again to verify recovery
- Check that error rates are dropping
- Confirm alerts begin resolving

## Reference: Known Issues
- CPU spikes when APP_HEALTHY=false are intentional (demo failure simulation)
- Cold start after restart causes 3-10s latency for first requests
- App Insights data has 2-5 minute ingestion delay
