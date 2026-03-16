"""
Tool Name: AnalyzeResponseTimes
Description: Analyze application response times by calling multiple endpoints
and computing statistics (min, max, avg, p50, p95, p99). Useful for performance
baselining and detecting degradation.
Use when asked about performance, latency, response times, or to run a
performance baseline.

Parameters:
  - app_url (str): The base URL of the application
  - num_requests (int): Number of requests to send per endpoint. Default: 10
"""

import time

def main(app_url: str, num_requests: int = 10) -> dict:
    """Analyze response times across application endpoints."""
    import requests
    import statistics

    app_url = app_url.rstrip("/")

    endpoints = [
        {"method": "GET", "path": "/health", "name": "Health Check"},
        {"method": "GET", "path": "/api/status", "name": "Status API"},
        {"method": "GET", "path": "/api/documents", "name": "List Documents"},
        {"method": "POST", "path": "/api/process", "name": "Process Document",
         "body": {"documentType": "invoice", "fileName": "perf-test.pdf"}},
    ]

    results = {}

    for ep in endpoints:
        latencies = []
        errors = 0
        status_codes = {}

        for _ in range(num_requests):
            try:
                start = time.time()
                if ep["method"] == "GET":
                    resp = requests.get(f"{app_url}{ep['path']}", timeout=15)
                else:
                    resp = requests.post(
                        f"{app_url}{ep['path']}",
                        json=ep.get("body", {}),
                        timeout=15
                    )
                latency_ms = round((time.time() - start) * 1000, 1)
                latencies.append(latency_ms)

                code = str(resp.status_code)
                status_codes[code] = status_codes.get(code, 0) + 1

                if resp.status_code >= 500:
                    errors += 1
            except Exception:
                errors += 1

            time.sleep(0.2)  # Don't hammer the app

        if latencies:
            sorted_lat = sorted(latencies)
            p50_idx = int(len(sorted_lat) * 0.50)
            p95_idx = min(int(len(sorted_lat) * 0.95), len(sorted_lat) - 1)
            p99_idx = min(int(len(sorted_lat) * 0.99), len(sorted_lat) - 1)

            stats = {
                "min_ms": min(sorted_lat),
                "max_ms": max(sorted_lat),
                "avg_ms": round(statistics.mean(sorted_lat), 1),
                "median_ms": round(statistics.median(sorted_lat), 1),
                "p95_ms": sorted_lat[p95_idx],
                "p99_ms": sorted_lat[p99_idx],
                "std_dev_ms": round(statistics.stdev(sorted_lat), 1) if len(sorted_lat) > 1 else 0
            }
        else:
            stats = {"error": "No successful requests"}

        results[ep["name"]] = {
            "endpoint": f"{ep['method']} {ep['path']}",
            "requests_sent": num_requests,
            "successful": num_requests - errors,
            "errors": errors,
            "status_codes": status_codes,
            "latency": stats
        }

    # Overall assessment
    all_p95 = [r["latency"].get("p95_ms", 0) for r in results.values() if "error" not in r.get("latency", {})]
    all_errors = sum(r["errors"] for r in results.values())

    if all_errors == 0 and all(p < 1000 for p in all_p95):
        assessment = "HEALTHY — All endpoints within normal latency range, no errors"
    elif all_errors == 0 and any(p >= 1000 for p in all_p95):
        assessment = "DEGRADED — No errors but some endpoints have elevated latency"
    elif all_errors > 0 and all_errors < num_requests * len(endpoints):
        assessment = "PARTIAL FAILURE — Some requests failing"
    else:
        assessment = "CRITICAL — Widespread failures detected"

    return {
        "app_url": app_url,
        "total_requests": num_requests * len(endpoints),
        "total_errors": all_errors,
        "assessment": assessment,
        "endpoints": results
    }
