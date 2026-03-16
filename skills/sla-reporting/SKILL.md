# SLA Reporting Guide

You are generating SLA compliance reports for the document processing platform.

## Service Level Objectives

| SLO | Target | Measurement |
|-----|--------|-------------|
| Availability | 99.9% monthly | /health returning 200 |
| Latency (p95) | < 2s for POST /api/process | App Insights request duration |
| Error Rate | < 0.1% server errors (5xx) | HTTP 5xx / total requests |

## Step 1: Gather Availability Data

Use `AvailabilityTimeline` with timeRange=30d and bucketSize=1h to get the full monthly view.

From the results, calculate:
- Total time windows
- Windows with 100% availability
- Windows with <100% availability
- Uptime minutes vs downtime minutes

## Step 2: Calculate SLA

Use `CalculateSLA` with the uptime and downtime minutes from Step 1.

The tool returns:
- SLA percentage
- Whether the target is met
- Error budget consumed
- Remaining budget in minutes

## Step 3: Error Rate Analysis

Use `ErrorRateByEndpoint` with timeRange=30d to see error rates per endpoint over the full period.

## Step 4: Document Processing Analysis

Use `DocumentProcessingStats` with timeRange=30d for processing-specific metrics.

## Step 5: Generate SLA Report

Structure the report as:

### Monthly SLA Report — [Month Year]

**Overall Availability**: X.XX% (Target: 99.9%)
**Status**: Met / Not Met

**Error Budget**:
- Allowed downtime: X minutes
- Actual downtime: X minutes
- Budget consumed: X%
- Budget remaining: X minutes

**Endpoint Performance**:
| Endpoint | Requests | Error Rate | p95 Latency | SLO Status |
|----------|----------|-----------|-------------|-----------|

**Document Processing**:
| Period | Processed | Failed | Success Rate |
|--------|-----------|--------|-------------|

**Recommendations**:
- List any areas needing attention
- Suggest improvements based on data
