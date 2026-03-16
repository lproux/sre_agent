# Application Architecture — YooZ Document Processing Platform

> **Owner:** SRE Team — ITESOFT
> **Last updated:** 2026-03-10
> **Classification:** Internal — Engineering
> **Review cadence:** Quarterly or after any significant infrastructure change

---

## Overview

YooZ is a document processing SaaS platform purpose-built for accounts payable automation. It handles invoice capture, OCR-based field extraction, validation, and multi-step approval workflows for enterprise customers.

| Attribute | Value |
|---|---|
| **Runtime** | Azure App Service (Linux, Node.js 20 LTS) |
| **Primary region** | Sweden Central (`swedencentral`) |
| **Secondary region** | None — this is a demo/staging environment |
| **Customer base** | ITESOFT customers across EMEA |
| **Deployment model** | Single-tenant App Service Plan, continuous deployment from GitHub Actions |
| **SLA target** | 99.5% availability (demo tier — production target is 99.95%) |

The platform ingests scanned invoices and structured document files, runs them through an OCR and field-extraction pipeline, and returns structured metadata (vendor name, amount, currency, date, confidence score) to downstream ERP and approval systems.

---

## Component Diagram

```
                          ┌─────────────────────────────────┐
                          │          End Users / API         │
                          │        Clients (EMEA)            │
                          └───────────────┬─────────────────┘
                                          │
                                          │ HTTPS (TLS 1.2+)
                                          ▼
                          ┌─────────────────────────────────┐
                          │      Azure App Service           │
                          │  ┌───────────┐ ┌──────────────┐ │
                          │  │ Frontend  │ │   REST API   │ │
                          │  │ (Static)  │ │  (Express)   │ │
                          │  └───────────┘ └──────┬───────┘ │
                          │        Linux · Node.js 20 LTS   │
                          │        Plan: B1 (1 vCPU, 1.75G) │
                          └──────────┬──────────┬───────────┘
                                     │          │
                    ┌────────────────┘          └────────────────┐
                    │ Telemetry (non-blocking)                   │ Health / Logs
                    ▼                                            ▼
     ┌──────────────────────────┐              ┌──────────────────────────┐
     │   Application Insights   │──────────────│  Log Analytics Workspace │
     │   (SDK auto-collection   │   export     │  (Centralized logs,      │
     │    + custom events)      │──────────────│   KQL query target)      │
     └──────────────────────────┘              └────────────┬─────────────┘
                                                            │
                                                            │ Alert rules
                                                            ▼
                                               ┌──────────────────────────┐
                                               │      Azure Monitor       │
                                               │  (Metric alerts, action  │
                                               │   groups, dashboards)    │
                                               └──────────────────────────┘

     ┌──────────────────────────────────────────────────────────────────────┐
     │                     FUTURE COMPONENTS (not yet deployed)            │
     │                                                                      │
     │  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────────┐  │
     │  │  Azure Cosmos DB │  │ Azure Blob       │  │ Azure AI Document  │  │
     │  │  (Document       │  │ Storage          │  │ Intelligence       │  │
     │  │   metadata,      │  │ (Raw document    │  │ (OCR, field        │  │
     │  │   audit trail)   │  │  files, exports) │  │  extraction)       │  │
     │  └─────────────────┘  └──────────────────┘  └────────────────────┘  │
     └──────────────────────────────────────────────────────────────────────┘
```

---

## Service Dependencies

### Runtime Dependencies

| Dependency | Type | Criticality | Health Check | Failure Impact |
|---|---|---|---|---|
| **Document Processing Engine** | Internal (simulated) | **Critical** | Controlled by `APP_HEALTHY` env var | When unhealthy, all `/api/process` calls fail with 500. Simulates connection pool exhaustion to backend processing service. |
| **Application Insights** | Azure PaaS | Non-blocking | SDK heartbeat (automatic) | Telemetry loss only. The application continues to serve requests normally. Events are buffered briefly and dropped if the sink is unreachable. |
| **Log Analytics Workspace** | Azure PaaS | Non-blocking | Ingestion pipeline (managed by Azure) | Query and alerting delay. No direct impact on request serving. |

### Future Dependencies (not yet wired)

| Dependency | Type | Criticality | Notes |
|---|---|---|---|
| Azure AI Document Intelligence | Azure Cognitive Services | Critical | Will replace the simulated OCR engine. Latency budget: 2-5s per page. |
| Azure Cosmos DB | Azure PaaS | Critical | Document metadata store. Expected RU consumption: 400-1000 RU/s. |
| Azure Blob Storage | Azure PaaS | High | Raw file storage. Expected throughput: ~50 MB/min during peak. |

### Dependency Chain

```
Client Request
  └─► App Service (Express API)
        ├─► Document Processing Engine [CRITICAL — gates response]
        └─► Application Insights [NON-BLOCKING — fire-and-forget telemetry]
```

When the document processing engine is unavailable, the API returns HTTP 500 immediately. There is no retry logic, circuit breaker, or fallback path in the current demo implementation. In production, a circuit breaker (e.g., `opossum`) and a dead-letter queue would be expected.

---

## Configuration

All configuration is managed through Azure App Service Application Settings (environment variables). There are no config files on disk.

| Variable | Required | Default | Description |
|---|---|---|---|
| `APP_HEALTHY` | Yes | `"true"` | Controls the simulated health of the document processing engine. When set to `"false"`, the application enters a degraded state: the `/api/process` endpoint simulates CPU-intensive work (~500ms burn loop) followed by a "connection pool exhausted" exception. This is the primary knob for triggering and resolving demo incidents. |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | Yes | *(none)* | Full connection string for the Application Insights resource. Used by the `applicationinsights` SDK for auto-collection of requests, dependencies, exceptions, and custom events/metrics. Format: `InstrumentationKey=...;IngestionEndpoint=...;LiveEndpoint=...` |
| `PORT` | No | `8080` | TCP port the Express server listens on. Azure App Service overrides this automatically via its platform injection. Do not hardcode a different port. |

### Configuration Change Procedure

1. Update the App Setting in the Azure Portal or via `az webapp config appsettings set`.
2. App Service automatically restarts the application (rolling restart on multi-instance plans; immediate on single-instance B1).
3. Verify health via the `/health` endpoint within 60 seconds.
4. Confirm telemetry flow in Application Insights Live Metrics.

**Important:** Changing `APP_HEALTHY` from `"true"` to `"false"` will cause an immediate service degradation. All in-flight and subsequent `/api/process` requests will fail. The `/health` endpoint will begin returning HTTP 503 within the next polling cycle.

---

## Request Flow

### Happy Path — `POST /api/process`

```
Client                    App Service (Express)              App Insights
  │                              │                                │
  │  POST /api/process           │                                │
  │  { type, fileName }         │                                │
  │─────────────────────────────►│                                │
  │                              │                                │
  │                              │ 1. Validate input              │
  │                              │    (type ∈ [invoice, receipt,  │
  │                              │     purchase_order, credit_note])
  │                              │                                │
  │                              │ 2. Call document processing    │
  │                              │    engine (simulated)          │
  │                              │    └─ Random latency: 100-500ms│
  │                              │                                │
  │                              │ 3. Engine extracts fields:     │
  │                              │    - vendor (string)           │
  │                              │    - amount (float)            │
  │                              │    - currency (ISO 4217)       │
  │                              │    - date (ISO 8601)           │
  │                              │    - confidence (0.85-0.99)    │
  │                              │                                │
  │                              │ 4. trackEvent ─────────────────►
  │                              │    "DocumentProcessed"         │
  │                              │    { type, fileName,           │
  │                              │      processingTime,           │
  │                              │      confidence }              │
  │                              │                                │
  │  200 OK                      │ 5. trackMetric ────────────────►
  │  { status, documentId,       │    "ProcessingTime" (ms)       │
  │    result, processingTime }  │                                │
  │◄─────────────────────────────│                                │
```

**Response example (200):**
```json
{
  "status": "processed",
  "documentId": "doc-a1b2c3d4",
  "result": {
    "vendor": "Acme Corp",
    "amount": 1234.56,
    "currency": "EUR",
    "date": "2026-03-15",
    "confidence": 0.94
  },
  "processingTime": 287
}
```

### Failure Path — `POST /api/process` (when `APP_HEALTHY=false`)

```
Client                    App Service (Express)              App Insights
  │                              │                                │
  │  POST /api/process           │                                │
  │  { type, fileName }         │                                │
  │─────────────────────────────►│                                │
  │                              │                                │
  │                              │ 1. Validate input (passes)     │
  │                              │                                │
  │                              │ 2. Call document processing    │
  │                              │    engine (simulated FAILURE)  │
  │                              │    └─ CPU burn: ~500ms         │
  │                              │       (busy-wait loop to       │
  │                              │        simulate load)          │
  │                              │                                │
  │                              │ 3. Engine throws:              │
  │                              │    "Connection pool exhausted: │
  │                              │     unable to acquire          │
  │                              │     connection to document     │
  │                              │     processing backend"        │
  │                              │                                │
  │                              │ 4. trackException ─────────────►
  │                              │    severity: Error             │
  │                              │    { correlationId }           │
  │                              │                                │
  │                              │ 5. trackEvent ─────────────────►
  │                              │    "DocumentProcessingFailed"  │
  │                              │    { type, fileName, error,    │
  │                              │      correlationId }           │
  │                              │                                │
  │  500 Internal Server Error   │                                │
  │  { error, correlationId,     │                                │
  │    message }                 │                                │
  │◄─────────────────────────────│                                │
```

**Response example (500):**
```json
{
  "error": "Processing failed",
  "correlationId": "corr-e5f6g7h8",
  "message": "Connection pool exhausted: unable to acquire connection to document processing backend"
}
```

**Key observations for incident investigation:**
- The `correlationId` in the HTTP response matches the one in Application Insights, enabling end-to-end tracing.
- The CPU burn during failure mode will cause elevated CPU metrics on the App Service Plan. This is visible in Azure Monitor under `CpuPercentage`.
- Under sustained unhealthy load (~30 req/min), a single B1 instance will approach 80-100% CPU utilization due to the 500ms busy-wait per request.

---

## Scaling Characteristics

| Parameter | Current Value | Notes |
|---|---|---|
| **App Service Plan** | B1 (Basic) | 1 vCPU, 1.75 GB RAM, 10 GB storage |
| **Instance count** | 1 (fixed) | No autoscaling configured |
| **Expected load** | ~30 requests/min | Demo/testing workload |
| **Max concurrent requests** | ~120 (Node.js event loop) | Single-threaded; CPU-bound work blocks the loop |
| **Autoscale** | Not configured | Demo environment — would use Standard S1+ with rule-based scaling in production |

### Capacity Limits

Under **healthy** operation:
- The app handles 30 req/min comfortably. Processing is I/O-simulated (random delay, non-blocking), so the event loop stays responsive.
- Memory usage is stable at ~80-120 MB RSS.
- CPU utilization stays below 15%.

Under **unhealthy** operation (`APP_HEALTHY=false`):
- Each request burns ~500ms of synchronous CPU time (busy-wait loop).
- At 30 req/min (0.5 req/s), the single vCPU spends ~250ms/s on burn loops — roughly 25% CPU from burn alone, plus overhead.
- At higher request rates, CPU saturates and response latency increases sharply due to event loop blocking.
- Memory remains stable (no leak in failure mode).

### Scaling Recommendations (for production)

1. Upgrade to Standard S1 or Premium P1v3 for autoscale support.
2. Configure autoscale rules: scale out at 70% CPU, scale in at 30%.
3. Add at least 2 instances for high availability.
4. Consider Azure Front Door for geographic load balancing across EMEA.

---

## Health Checks

### Endpoint: `GET /health`

The `/health` endpoint is the primary liveness and readiness probe for the application.

| Condition | HTTP Status | Response Body | Meaning |
|---|---|---|---|
| `APP_HEALTHY=true` | `200 OK` | `{ "status": "healthy", "timestamp": "...", "version": "1.0.0" }` | All subsystems nominal. Ready to process documents. |
| `APP_HEALTHY=false` | `503 Service Unavailable` | `{ "status": "unhealthy", "timestamp": "...", "version": "1.0.0" }` | Document processing engine is down. API will reject process requests. |

### App Service Health Check Configuration

- **Path:** `/health`
- **Polling interval:** Every 30 seconds
- **Unhealthy threshold:** App Service marks the instance as unhealthy after consecutive 503 responses (platform default: 5 consecutive failures = 2.5 minutes).
- **Action on unhealthy:** On multi-instance plans, App Service routes traffic away from the unhealthy instance. On the current single-instance B1 plan, this has no practical effect — there is nowhere to route traffic.

### Monitoring the Health Check

To query health check results in Log Analytics:

```kql
AppServiceHTTPLogs
| where CsUriStem == "/health"
| where ScStatus == 503
| summarize count() by bin(TimeGenerated, 5m)
| order by TimeGenerated desc
```

To query application-level health events in Application Insights:

```kql
customEvents
| where name == "HealthCheckFailed" or name == "HealthCheckPassed"
| project timestamp, name, customDimensions
| order by timestamp desc
```

---

## Telemetry & Observability

### Application Insights Data Model

The application emits the following telemetry:

| Telemetry Type | Name | When | Key Properties |
|---|---|---|---|
| **Custom Event** | `DocumentProcessed` | Successful document processing | `type`, `fileName`, `processingTime`, `confidence` |
| **Custom Event** | `DocumentProcessingFailed` | Failed document processing | `type`, `fileName`, `error`, `correlationId` |
| **Custom Metric** | `ProcessingTime` | Every process request | Value in milliseconds |
| **Exception** | *(auto-captured)* | Unhandled errors in processing engine | Includes stack trace, `correlationId` in custom dimensions |
| **Request** | *(auto-collected)* | Every HTTP request | URL, status code, duration, success flag |
| **Dependency** | *(auto-collected)* | Outbound calls (future: Cosmos DB, Blob, AI) | Target, duration, success flag |

### Key KQL Queries for Incident Investigation

**Error rate over time:**
```kql
requests
| where success == false
| summarize errorCount = count() by bin(timestamp, 5m)
| render timechart
```

**Failed document processing events with correlation IDs:**
```kql
customEvents
| where name == "DocumentProcessingFailed"
| extend error = tostring(customDimensions.error)
| extend correlationId = tostring(customDimensions.correlationId)
| project timestamp, error, correlationId
| order by timestamp desc
```

**CPU-correlated failures (join metrics with exceptions):**
```kql
let failures = exceptions
| where timestamp > ago(1h)
| summarize failureCount = count() by bin(timestamp, 5m);
performanceCounters
| where name == "% Processor Time"
| summarize avgCpu = avg(value) by bin(timestamp, 5m)
| join kind=leftouter failures on timestamp
| project timestamp, avgCpu, failureCount = coalesce(failureCount, 0)
| render timechart
```

---

## Incident Response Playbook Reference

When Azure SRE Agent detects anomalies in this application, the following context should guide investigation:

1. **If error rate spikes on `/api/process`:** Check the `APP_HEALTHY` application setting. A value of `"false"` is the most likely root cause in the demo environment.

2. **If CPU is elevated:** Correlate with error rate. In failure mode, the CPU burn loop (~500ms per request) directly causes CPU spikes proportional to request volume.

3. **If `/health` returns 503:** The application is explicitly reporting itself as unhealthy. This is driven by the `APP_HEALTHY` flag, not by an actual infrastructure failure.

4. **If telemetry stops flowing:** Check the `APPLICATIONINSIGHTS_CONNECTION_STRING` setting and the Application Insights resource health. The app itself is likely still running.

5. **To resolve:** Set `APP_HEALTHY` to `"true"` via App Service configuration. The application will restart and begin serving healthy responses within 30-60 seconds.

---

## Disaster Recovery

| Aspect | Current State | Production Target |
|---|---|---|
| **RPO** | N/A (no persistent data) | 1 hour (Cosmos DB continuous backup) |
| **RTO** | ~5 minutes (App Service restart) | 15 minutes (regional failover) |
| **Backup** | None | Cosmos DB PITR, Blob soft-delete |
| **Multi-region** | No | Active-passive with Azure Front Door |

---

*This document is maintained by the SRE team. For questions or updates, contact the platform engineering channel.*
