# Custom Tools & Skills for Azure SRE Agent

This directory contains ready-to-use custom tools and skills for the SRE Agent demo. Paste them directly into the Builder UI at https://sre.azure.com.

## Tools

### Python Tools (Builder > Subagent builder > Create > Tool > Python tool)

| Tool | File | What it does | How to create |
|------|------|-------------|---------------|
| **CalculateSLA** | `python/sla-calculator.py` | SLA compliance, error budget, SLO status | Paste code into Code tab |
| **CheckAppHealth** | `python/app-health-checker.py` | Deep health check against all app endpoints | Paste code into Code tab |
| **EstimateResourceCost** | `python/cost-estimator.py` | Monthly Azure cost estimation | Paste code into Code tab |
| **GenerateIncidentReport** | `python/incident-report-generator.py` | Structured incident report in markdown | Paste code into Code tab |
| **MapDependencies** | `python/dependency-mapper.py` | Resource topology and blast radius mapping | Paste code into Code tab |
| **AnalyzeResponseTimes** | `python/response-time-analyzer.py` | Performance baseline with p50/p95/p99 stats | Paste code into Code tab |

**To create a Python tool:**
1. Go to **Builder > Subagent builder**
2. Click **Create > Tool > Python tool**
3. Switch to the **Code** tab
4. Paste the Python code from the file (everything below the docstring)
5. Fill in the tool name and description from the docstring
6. Click **Test playground** tab to test with sample inputs
7. Click **Create tool**

### Kusto Tools (Builder > Subagent builder > Create > Tool > Kusto tool)

| Tool | File | What it queries |
|------|------|----------------|
| **QueryTopExceptions** | `kusto/top-exceptions.kql` | Top exceptions by count in time range |
| **ErrorRateByEndpoint** | `kusto/error-rate-by-endpoint.kql` | Error rate + latency per API endpoint |
| **RecentConfigChanges** | `kusto/recent-config-changes.kql` | Activity Log for config/deployment changes |
| **AvailabilityTimeline** | `kusto/availability-timeline.kql` | Time-bucketed availability percentages |
| **DocumentProcessingStats** | `kusto/document-processing-stats.kql` | Document processing success/failure rates |

**To create a Kusto tool:**
1. Go to **Builder > Subagent builder**
2. Click **Create > Tool > Kusto tool**
3. Fill in the tool name and description from the YAML header
4. Select your App Insights or Log Analytics connector
5. Paste the KQL query (everything below the YAML header)
6. Add parameters (using `##paramName##` syntax in the query)
7. Click **Test** to validate
8. Click **Create tool**

### Link Tools (Builder > Subagent builder > Create > Tool > Link tool)

| Tool | File | What it generates |
|------|------|------------------|
| **OpenGrafanaDashboard** | `link/grafana-dashboard.yaml` | Deep links to Grafana dashboards |
| **OpenPortalBlade** | `link/azure-portal-deeplinks.yaml` | Deep links to Azure Portal blades |

## Skills

Skills are procedures (SKILL.md) with tools attached. Create them in **Builder > Subagent builder > Create > Skill**.

| Skill | Directory | When the agent uses it |
|-------|-----------|----------------------|
| **App Service Troubleshooting** | `skills/app-service-troubleshooting/` | HTTP errors, health failures, config issues |
| **Incident Response** | `skills/incident-response/` | Any production incident or alert |
| **Performance Analysis** | `skills/performance-analysis/` | Latency investigations, capacity planning |
| **SLA Reporting** | `skills/sla-reporting/` | SLA compliance, error budgets, availability |
| **Daily Health Check** | `skills/daily-health-check/` | Routine proactive monitoring |

**To create a skill:**
1. Go to **Builder > Subagent builder**
2. Click **Create > Skill**
3. Enter the name and description from `config.yaml`
4. Paste the content of `SKILL.md` into the skill file
5. Attach the tools listed in `config.yaml`
6. Click **Create**

## Tool → Skill → Subagent Architecture

```
Subagent: "App Service Expert"
  ├── Skill: app-service-troubleshooting
  │     ├── SKILL.md (procedure)
  │     └── Tools: RunAzCliReadCommands, QueryTopExceptions, CheckAppHealth, ...
  ├── Skill: incident-response
  │     ├── SKILL.md (procedure)
  │     └── Tools: All investigation tools
  └── Direct tools: MapDependencies, GenerateIncidentReport
```

Tools are atomic capabilities. Skills combine tools with procedures. Subagents combine skills with a persona and tool set.
