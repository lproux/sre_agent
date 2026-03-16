"""
Tool Name: MapDependencies
Description: Map the dependencies and resource relationships for the demo
environment. Queries Azure Resource Graph to discover resources and their
connections. Returns a structured topology view.
Use when asked about architecture, dependencies, resource topology, or blast radius.

Parameters:
  - resource_group (str): The resource group to map. Default: rg-sre-agent-demo
"""

def main(resource_group: str = "rg-sre-agent-demo") -> dict:
    """Map resource dependencies in the demo environment."""

    # For the demo app, we know the architecture
    # In production, this would query Azure Resource Graph
    topology = {
        "resource_group": resource_group,
        "region": "swedencentral",
        "resources": [
            {
                "name": "app-sre-demo-*",
                "type": "Microsoft.Web/sites",
                "tier": "Basic B1",
                "runtime": "Node.js 20 LTS",
                "depends_on": ["plan-sre-demo", "ai-sre-demo"],
                "health_endpoint": "/health",
                "role": "Primary application — serves API and dashboard"
            },
            {
                "name": "plan-sre-demo",
                "type": "Microsoft.Web/serverfarms",
                "tier": "Basic B1 (1 core, 1.75 GB RAM)",
                "depends_on": [],
                "role": "Compute infrastructure for the web app"
            },
            {
                "name": "ai-sre-demo",
                "type": "Microsoft.Insights/components",
                "tier": "Pay-per-GB",
                "depends_on": ["law-sre-demo"],
                "role": "APM — collects requests, exceptions, custom events, live metrics"
            },
            {
                "name": "law-sre-demo",
                "type": "Microsoft.OperationalInsights/workspaces",
                "tier": "PerGB2018 (30-day retention)",
                "depends_on": [],
                "role": "Centralized log storage — backing store for App Insights"
            },
            {
                "name": "alert-http-5xx",
                "type": "Microsoft.Insights/metricAlerts",
                "condition": "total Http5xx > 5 in 5m",
                "severity": 1,
                "depends_on": ["app-sre-demo-*"],
                "role": "Detects HTTP 5xx error spikes"
            },
            {
                "name": "alert-response-time",
                "type": "Microsoft.Insights/metricAlerts",
                "condition": "avg HttpResponseTime > 3s in 5m",
                "severity": 2,
                "depends_on": ["app-sre-demo-*"],
                "role": "Detects response time degradation"
            },
            {
                "name": "alert-health-check",
                "type": "Microsoft.Insights/metricAlerts",
                "condition": "avg HealthCheckStatus < 100% in 5m",
                "severity": 1,
                "depends_on": ["app-sre-demo-*"],
                "role": "Detects health check failures"
            }
        ],
        "data_flow": [
            "Client -> App Service (HTTPS) -> Express.js routes",
            "Express.js -> Application Insights SDK (telemetry)",
            "Application Insights -> Log Analytics Workspace (storage)",
            "Azure Monitor -> Metric Alert Rules (evaluation every 1m)",
            "Alert Rules -> SRE Agent (incident detection)"
        ],
        "blast_radius": {
            "app_service_down": "All API endpoints unavailable. Dashboard unreachable. Health checks fail. All 3 alerts fire.",
            "app_insights_down": "No telemetry collection. App continues serving. Alerts based on App Service metrics still work.",
            "log_analytics_down": "App Insights queries fail. Live Metrics may still work. Historical data inaccessible.",
            "app_service_plan_down": "Same as app_service_down — plan hosts the app."
        }
    }

    return topology
