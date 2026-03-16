# Performance Analysis Guide

You are performing a performance analysis on the demo application. This skill provides a systematic approach to measuring, analyzing, and reporting on application performance.

## Step 1: Current Performance Baseline

Run `AnalyzeResponseTimes` against the app to measure real-time performance across all endpoints.

Healthy baselines for this application:
| Endpoint | Expected p95 | Alert Threshold |
|----------|-------------|----------------|
| GET /health | < 50ms | > 500ms |
| GET /api/status | < 100ms | > 1000ms |
| POST /api/process | < 500ms | > 3000ms |
| GET /api/documents | < 200ms | > 1000ms |

## Step 2: Historical Analysis

Use `ErrorRateByEndpoint` with timeRange=24h to see error rates and latency trends per endpoint.

Use `AvailabilityTimeline` with timeRange=24h and bucketSize=1h to see the availability pattern over the last day.

## Step 3: Identify Bottlenecks

If latency is elevated:
1. Check if APP_HEALTHY=false (causes artificial CPU load of 200-500ms)
2. Check CPU metrics — is the B1 plan saturated?
3. Check if specific endpoints are slower than others
4. Look for correlation between request volume and latency

## Step 4: Capacity Assessment

Use `EstimateResourceCost` to understand current costs and what scaling up would cost.

Current capacity (B1):
- 1 core, 1.75 GB RAM
- Handles ~30 req/min comfortably when healthy
- Under artificial load (APP_HEALTHY=false): CPU hits 80-100%

Scaling recommendations:
| Load Level | Recommended SKU | Monthly Cost |
|-----------|----------------|-------------|
| Demo (30 req/min) | B1 | ~$13 |
| Light production (100 req/min) | S1 | ~$69 |
| Medium production (500 req/min) | P1v3 | ~$139 |
| Heavy production (2000+ req/min) | P2v3 + autoscale | ~$277+ |

## Step 5: Generate Report

Summarize findings with:
1. Current performance vs baselines
2. Any endpoints outside normal range
3. Error rate analysis
4. Capacity utilization
5. Cost optimization recommendations
