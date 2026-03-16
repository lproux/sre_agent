"""
Tool Name: CalculateSLA
Description: Calculate SLA compliance percentage from Application Insights
availability data. Returns whether the service meets its SLO target.
Use when asked about SLA, uptime, availability, or compliance.

Parameters:
  - uptime_minutes (int): Total minutes the service was available
  - downtime_minutes (int): Total minutes the service was unavailable
  - target_sla (float): SLO target percentage (default: 99.9)
"""

def main(uptime_minutes: int, downtime_minutes: int, target_sla: float = 99.9) -> dict:
    """Calculate SLA compliance from uptime and downtime minutes."""
    total_minutes = uptime_minutes + downtime_minutes

    if total_minutes == 0:
        return {
            "error": "Total minutes cannot be zero",
            "sla_percent": None,
            "meets_target": False
        }

    sla_percent = round((uptime_minutes / total_minutes) * 100, 4)
    meets_target = sla_percent >= target_sla

    # Calculate error budget
    allowed_downtime = total_minutes * (1 - target_sla / 100)
    remaining_budget = allowed_downtime - downtime_minutes
    budget_consumed_percent = round((downtime_minutes / allowed_downtime) * 100, 2) if allowed_downtime > 0 else 100.0

    # Determine status
    if budget_consumed_percent < 50:
        status = "Healthy — error budget is well within limits"
    elif budget_consumed_percent < 75:
        status = "Warning — error budget consumption is elevated"
    elif budget_consumed_percent < 100:
        status = "Critical — error budget nearly exhausted"
    else:
        status = "Breached — SLO target not met, error budget exhausted"

    return {
        "sla_percent": sla_percent,
        "target_sla": target_sla,
        "meets_target": meets_target,
        "total_minutes": total_minutes,
        "uptime_minutes": uptime_minutes,
        "downtime_minutes": downtime_minutes,
        "allowed_downtime_minutes": round(allowed_downtime, 2),
        "remaining_budget_minutes": round(remaining_budget, 2),
        "budget_consumed_percent": budget_consumed_percent,
        "status": status
    }
