# SRE Agent Demo - Presenter Guide

> Detailed walkthrough for delivering the Azure SRE Agent demo. Covers both Level 100 (10 min) and Level 200 (20 min) presentations.

## Pre-Demo Checklist (1 hour before)

- [ ] Verify Azure subscription access: `az account show`
- [ ] Confirm all resources are running: `az group show -n rg-sre-agent-demo`
- [ ] Verify the app is healthy: `curl https://<app-name>.azurewebsites.net/health`
- [ ] Start traffic generation: `./generate-traffic.sh`
- [ ] Open browser tabs:
  - Azure Portal > rg-sre-agent-demo
  - Application Insights > Live Metrics
  - Application Insights > Application Map
  - SRE Agent dashboard
- [ ] Test break/fix cycle once: `./break-app.sh` then `./fix-app.sh`

---

## Level 100 Demo Script (~10 minutes)

### Act 1: Set the Scene (2 min)

**What to say:**
> "Let me show you Azure SRE Agent in action. We have a document processing application running on Azure App Service — think of it as a simplified version of a platform like YooZ that processes invoices, receipts, and purchase orders."

**What to show:**
- App Service overview in portal (resource group view)
- Quick curl to show the app is healthy:

```console
$ curl -s https://app-sre-demo-xxxx.azurewebsites.net/health | jq
{
  "status": "healthy",
  "timestamp": "2026-03-16T10:30:00.000Z"
}
```

- Application Insights Live Metrics — point out the steady green traffic

**What to say:**
> "Everything looks normal. We've got Application Insights collecting telemetry, Azure Monitor alert rules watching for HTTP 5xx errors and response time degradation, and SRE Agent connected to this resource group."

### Act 2: Break Things (2 min)

**What to say:**
> "Now let's simulate a production incident. Imagine a bad deployment just went out — maybe a config change broke the connection to our document processing engine."

**What to do:**
Run the break script in your terminal (keep it visible):

```console
$ ./break-app.sh
============================================
  SRE Agent Demo - Breaking the App
============================================

[1/2] Setting APP_HEALTHY=false...
[2/2] Restarting web app to apply changes...

  App is now BROKEN!

  What will happen:
    - /health returns 503
    - /api/process returns 500
    - All endpoints have high latency
    - Application Insights logs exceptions
    - Azure Monitor alerts will fire within ~5 minutes

  Generating error traffic to accelerate alert triggers...

  20 error requests sent.
```

**What to show:**
- Curl the health endpoint to prove it's broken:

```console
$ curl -s https://app-sre-demo-xxxx.azurewebsites.net/health | jq
{
  "status": "unhealthy",
  "timestamp": "2026-03-16T10:32:00.000Z",
  "error": "Service degraded"
}
```

- Switch to Application Insights Live Metrics — show the red errors appearing
- Switch to Azure Monitor Alerts — show alerts transitioning to "Fired"

### Act 3: SRE Agent Detects & Investigates (4 min)

**What to say:**
> "Now watch what happens. SRE Agent is monitoring these alerts. Within minutes, it detects the incident and begins its investigation — completely autonomously."

**What to show:**
- SRE Agent dashboard — the incident should appear
- Click into the investigation — show the agent's thought process:
  - It checks Application Insights for exceptions
  - It correlates the timing with recent changes
  - It looks at dependency health
  - It analyzes the error patterns

**What to say:**
> "Notice how the agent is doing exactly what an experienced SRE would do — it's checking logs, correlating signals, and building a root cause analysis. But it does it in minutes instead of hours, and at 3 AM it doesn't need coffee."

- Show the RCA output — the agent should identify the APP_HEALTHY config change as the root cause

### Act 4: Resolution (2 min)

**What to say:**
> "Now let's fix the issue and watch everything recover."

```console
$ ./fix-app.sh
============================================
  SRE Agent Demo - Fixing the App
============================================

[1/2] Setting APP_HEALTHY=true...
[2/2] Restarting web app to apply changes...

  App is now FIXED!
```

**What to show:**
- Curl health endpoint — back to 200
- Live Metrics — errors stop, green traffic resumes
- Azure Monitor Alerts — transitioning to "Resolved"
- SRE Agent — incident marked as resolved

---

## Level 200 Demo Script (~20 minutes)

> Includes everything from Level 100, plus the following additional sections.

### Extended: Custom Sub-Agents (5 min)

**What to say:**
> "SRE Agent comes with built-in investigation capabilities, but you can also configure custom sub-agents for your specific environment."

**What to show:**
- SRE Agent settings > Sub-agents configuration
- Show how you can add custom instructions like:
  - "When investigating App Service issues, always check the Kudu logs"
  - "For this application, high CPU is expected during batch processing windows (2-4 AM UTC)"

### Extended: Scheduled Tasks (3 min)

**What to say:**
> "SRE Agent doesn't just react to incidents — it can proactively monitor your environment on a schedule."

**What to show:**
- SRE Agent > Scheduled Tasks
- Show a configured task: "Check application health and performance trends daily at 9 AM"
- Show a sample proactive report output

### Extended: GitHub Integration (2 min)

**What to say:**
> "When SRE Agent finds something actionable, it can create GitHub issues automatically, complete with investigation details and suggested remediation."

**What to show:**
- A GitHub issue created by SRE Agent (or show the configuration)
- Point out the structured format: summary, investigation details, suggested fix

---

## Common Questions & Answers

**Q: Does SRE Agent make changes to my resources?**
> A: With Reader permissions (recommended for demos), it can only read and investigate. With Contributor permissions, it can take remediation actions — but that's configurable.

**Q: What data does SRE Agent access?**
> A: It reads Azure Monitor metrics, Application Insights telemetry, resource configurations, and activity logs — all within the resource groups you assign to it.

**Q: How quickly does it detect incidents?**
> A: Detection depends on your Azure Monitor alert rules. Once an alert fires, SRE Agent typically begins investigation within 1-2 minutes.

**Q: What regions is SRE Agent available in?**
> A: During initial GA rollout, SRE Agent must be created in Sweden Central. It can monitor resources in any region.

**Q: How is this different from Azure Monitor Smart Detection?**
> A: Smart Detection identifies anomalies. SRE Agent goes further — it investigates, correlates across data sources, and produces structured root cause analysis, similar to what a human SRE would do.

---

## Troubleshooting During Demo

| Problem | Quick Fix |
|---------|-----------|
| App not responding | `az webapp restart -n <app-name> -g rg-sre-agent-demo` |
| Alerts not firing | Send more error traffic: run `./break-app.sh` again |
| SRE Agent not detecting | Verify alert rules: `az monitor metrics alert list -g rg-sre-agent-demo -o table` |
| App Insights empty | Check connection string: `az webapp config appsettings list -n <app-name> -g rg-sre-agent-demo -o table` |
| Slow portal loading | Use portal.azure.com in InPrivate/Incognito window |

---

## Post-Demo

1. Run `./fix-app.sh` if the app is still broken
2. If done for the day: `./cleanup.sh` to remove Azure resources
3. Save any SRE Agent investigation screenshots for follow-up materials
