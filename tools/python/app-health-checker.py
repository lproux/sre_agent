"""
Tool Name: CheckAppHealth
Description: Perform a deep health check on the demo application by calling
its /health and /api/status endpoints directly. Returns real-time health
state, uptime, memory usage, and response times.
Use when asked to check application health, verify the app is running,
or diagnose connectivity issues.

Parameters:
  - app_url (str): The base URL of the application (e.g. https://app-sre-demo-176aec.azurewebsites.net)
"""

import time

def main(app_url: str) -> dict:
    """Check application health by calling its endpoints directly."""
    import requests

    app_url = app_url.rstrip("/")
    results = {}

    # Check /health endpoint
    try:
        start = time.time()
        resp = requests.get(f"{app_url}/health", timeout=10)
        health_latency_ms = round((time.time() - start) * 1000, 1)
        results["health"] = {
            "status_code": resp.status_code,
            "response": resp.json(),
            "latency_ms": health_latency_ms,
            "healthy": resp.status_code == 200
        }
    except requests.exceptions.Timeout:
        results["health"] = {"error": "Timeout after 10s", "healthy": False}
    except requests.exceptions.ConnectionError:
        results["health"] = {"error": "Connection refused", "healthy": False}
    except Exception as e:
        results["health"] = {"error": str(e), "healthy": False}

    # Check /api/status endpoint
    try:
        start = time.time()
        resp = requests.get(f"{app_url}/api/status", timeout=10)
        status_latency_ms = round((time.time() - start) * 1000, 1)
        results["status"] = {
            "status_code": resp.status_code,
            "response": resp.json(),
            "latency_ms": status_latency_ms
        }
    except Exception as e:
        results["status"] = {"error": str(e)}

    # Test document processing endpoint
    try:
        start = time.time()
        resp = requests.post(
            f"{app_url}/api/process",
            json={"documentType": "invoice", "fileName": "health-check-test.pdf"},
            timeout=15
        )
        process_latency_ms = round((time.time() - start) * 1000, 1)
        results["process"] = {
            "status_code": resp.status_code,
            "latency_ms": process_latency_ms,
            "functional": resp.status_code == 200
        }
        if resp.status_code == 200:
            results["process"]["sample_result"] = resp.json()
        else:
            results["process"]["error"] = resp.json()
    except Exception as e:
        results["process"] = {"error": str(e), "functional": False}

    # Overall assessment
    is_healthy = results.get("health", {}).get("healthy", False)
    is_functional = results.get("process", {}).get("functional", False)
    health_latency = results.get("health", {}).get("latency_ms", 0)
    process_latency = results.get("process", {}).get("latency_ms", 0)

    if is_healthy and is_functional and process_latency < 1000:
        overall = "HEALTHY — All endpoints responding normally"
    elif is_healthy and is_functional:
        overall = "DEGRADED — Endpoints responding but with high latency"
    elif is_healthy and not is_functional:
        overall = "PARTIAL OUTAGE — Health OK but processing is failing"
    else:
        overall = "DOWN — Application is unhealthy"

    results["overall_assessment"] = overall
    results["app_url"] = app_url

    return results
