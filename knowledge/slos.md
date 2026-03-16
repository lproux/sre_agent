# Service Level Objectives

## Document Processing API

### Availability SLO
- Target: 99.9% monthly (allows ~43 min downtime/month)
- Measurement: Percentage of /health checks returning 200 over rolling 30-day window
- Data source: Application Insights `requests` table, filtered to /health
- Burn rate alert: >1% error budget consumed in 1 hour

### Latency SLO
- Target: p95 response time < 2 seconds for POST /api/process
- Measurement: 95th percentile of request duration for /api/process
- Data source: Application Insights `requests` table, filtered to /api/process
- Threshold: Alert when p95 > 3s (50% above SLO) for 5 minutes

### Error Rate SLO
- Target: < 0.1% server errors (5xx) across all endpoints
- Measurement: Count of 5xx responses / total responses over 5-minute windows
- Data source: App Service HTTP 5xx metric
- Current alert: Fires when total 5xx > 5 in 5 minutes

## SLO Definitions for SRE Agent

When investigating incidents, these SLOs define what "normal" looks like:
- Normal health check response: 200, < 100ms
- Normal /api/process response: 200, 100-500ms
- Normal /api/documents response: 200, < 200ms
- Normal /api/status response: 200, < 100ms
- Normal error rate: 0% (demo app has no expected errors)
- Normal CPU: < 30% on B1 instance
- Normal memory: < 200MB RSS

## Error Budget Policy
- When error budget is > 50% remaining: Normal development velocity
- When error budget is 25-50% remaining: Halt non-critical deployments
- When error budget is < 25% remaining: All hands on reliability, incident review required
- When error budget is exhausted: Feature freeze until budget recovers
