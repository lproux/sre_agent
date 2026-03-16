# Known Issues & Expected Behaviors

## KI-001: CPU Spikes During Failure Simulation
- **Symptom**: CPU utilization jumps to 80-100% when APP_HEALTHY=false
- **Root cause**: Intentional. The app uses synchronous CPU-burn loops to simulate a degraded backend. This is by design for the demo.
- **Impact**: All endpoints become slow (200-500ms added latency)
- **Resolution**: Set APP_HEALTHY=true and restart the app
- **Note for SRE Agent**: If you see high CPU correlated with APP_HEALTHY=false, this is the expected demo failure mode, not a real resource constraint.

## KI-002: Cold Start Latency After Restart
- **Symptom**: First few requests after `az webapp restart` take 3-10 seconds
- **Root cause**: Node.js process startup + Application Insights SDK initialization
- **Impact**: Temporary latency spike, may briefly trigger response time alert
- **Resolution**: No action needed — resolves within 30-60 seconds
- **Note for SRE Agent**: If response time spike occurs immediately after a restart (check Activity Log), this is a cold start, not a regression.

## KI-003: Application Insights Ingestion Delay
- **Symptom**: App Insights dashboards show data 2-5 minutes behind real-time
- **Root cause**: Normal Application Insights ingestion pipeline latency
- **Impact**: Live Metrics is real-time, but queries and dashboards have delay
- **Resolution**: Use Live Metrics for real-time view, wait for dashboard data
- **Note for SRE Agent**: When correlating events, account for up to 5-minute ingestion delay in App Insights data.

## KI-004: Health Check False Positives During Deployment
- **Symptom**: Brief health check failures during zip deployment
- **Root cause**: App restarts during deployment, /health temporarily unavailable
- **Impact**: May trigger health check alert briefly
- **Resolution**: Alert should auto-resolve within 5 minutes post-deployment
- **Note for SRE Agent**: If health check failures correlate with a deployment in Activity Log, this is expected and transient.

## KI-005: Memory Growth Over Extended Run
- **Symptom**: RSS memory gradually increases over hours of sustained traffic
- **Root cause**: Application Insights SDK buffering telemetry + V8 garbage collection patterns
- **Impact**: Minimal — stays well within B1 limits (1.75 GB) for demo duration
- **Resolution**: App restart resets memory. Not actionable unless RSS > 500 MB.
- **Note for SRE Agent**: Memory growth under 500 MB is normal. Only investigate if sustained above 500 MB.

## Expected Baseline Metrics
When everything is healthy, expect:
- CPU: 5-15% under normal load, spikes to 25% during process requests
- Memory (RSS): 60-120 MB
- Response times: /health < 50ms, /api/process 100-400ms, other endpoints < 100ms
- Error rate: 0%
- Request volume during traffic generation: ~30 req/min
