"""
Tool Name: EstimateResourceCost
Description: Estimate the monthly Azure cost for the demo environment based on
current resource configuration. Accounts for App Service, Application Insights,
and Log Analytics pricing.
Use when asked about costs, billing, pricing, or budget for the demo environment.

Parameters:
  - app_service_sku (str): The App Service plan SKU (e.g. B1, B2, S1, P1v3). Default: B1
  - avg_requests_per_day (int): Average daily request count for App Insights billing. Default: 50000
  - log_ingestion_gb_per_day (float): Daily log ingestion volume in GB. Default: 0.5
"""

def main(app_service_sku: str = "B1", avg_requests_per_day: int = 50000, log_ingestion_gb_per_day: float = 0.5) -> dict:
    """Estimate monthly Azure costs for the demo environment."""

    # App Service pricing (USD/month, Sweden Central)
    app_service_prices = {
        "F1": 0.00,
        "B1": 13.14,
        "B2": 26.28,
        "B3": 52.56,
        "S1": 69.35,
        "S2": 138.70,
        "S3": 277.40,
        "P1V3": 138.70,
        "P2V3": 277.40,
        "P3V3": 554.80,
    }

    sku = app_service_sku.upper()
    app_service_cost = app_service_prices.get(sku, None)
    if app_service_cost is None:
        return {"error": f"Unknown SKU: {sku}. Supported: {list(app_service_prices.keys())}"}

    # Application Insights pricing
    # First 5 GB/month free, then $2.30/GB
    monthly_requests = avg_requests_per_day * 30
    # Rough estimate: 1KB per request telemetry record
    ai_data_gb = (monthly_requests * 1) / (1024 * 1024)  # KB to GB
    ai_billable_gb = max(0, ai_data_gb - 5)
    ai_cost = round(ai_billable_gb * 2.30, 2)

    # Log Analytics pricing
    # First 5 GB/month free (per workspace), then $2.76/GB
    monthly_log_gb = log_ingestion_gb_per_day * 30
    la_billable_gb = max(0, monthly_log_gb - 5)
    la_cost = round(la_billable_gb * 2.76, 2)

    # Alert rules
    # Metric alerts: ~$0.10/rule/month
    alert_cost = round(3 * 0.10, 2)

    total_cost = round(app_service_cost + ai_cost + la_cost + alert_cost, 2)

    return {
        "sku": sku,
        "breakdown": {
            "app_service": {"sku": sku, "cost_usd": app_service_cost},
            "application_insights": {
                "estimated_data_gb": round(ai_data_gb, 2),
                "free_tier_gb": 5,
                "billable_gb": round(ai_billable_gb, 2),
                "cost_usd": ai_cost
            },
            "log_analytics": {
                "monthly_ingestion_gb": round(monthly_log_gb, 2),
                "free_tier_gb": 5,
                "billable_gb": round(la_billable_gb, 2),
                "cost_usd": la_cost
            },
            "alert_rules": {"count": 3, "cost_usd": alert_cost}
        },
        "total_monthly_cost_usd": total_cost,
        "recommendation": f"Current B1 at ${app_service_cost}/mo is appropriate for demo workloads. "
                         f"For production, consider S1 (${app_service_prices['S1']}/mo) for staging slots and auto-scale."
                         if sku == "B1" else f"Monthly cost for {sku}: ${total_cost}"
    }
