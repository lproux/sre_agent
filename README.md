<p align="center">
  <img src="https://img.shields.io/badge/Azure-SRE%20Agent-0078D4?style=for-the-badge&logo=microsoft-azure&logoColor=white" alt="Azure SRE Agent"/>
  <img src="https://img.shields.io/badge/Node.js-20%20LTS-339933?style=for-the-badge&logo=node.js&logoColor=white" alt="Node.js"/>
  <img src="https://img.shields.io/badge/App%20Service-Linux%20B1-0078D4?style=for-the-badge&logo=microsoft-azure&logoColor=white" alt="App Service"/>
  <img src="https://img.shields.io/badge/Region-Sweden%20Central-blue?style=for-the-badge" alt="Region"/>
</p>

# Azure SRE Agent — Live Demo Environment

> A fully scripted demo environment for showcasing **Azure SRE Agent** in customer presentations. Deploy a realistic document-processing application to Azure App Service, simulate a production incident, and watch SRE Agent detect, investigate, and produce a root cause analysis — all live.

---

## Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Setup Walkthrough](#setup-walkthrough)
- [Demo Workflow](#demo-workflow)
- [The Demo App](#the-demo-app)
- [Script Reference](#script-reference)
- [SRE Agent Portal Setup](#sre-agent-portal-setup)
- [Demo Talking Points](#demo-talking-points)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Azure — Sweden Central                          │
│                    rg-sre-agent-demo                                 │
│                                                                     │
│  ┌──────────────┐     ┌──────────────────┐     ┌────────────────┐  │
│  │  App Service  │────▶│ Application      │────▶│ Log Analytics  │  │
│  │  (Node.js 20) │     │ Insights         │     │ Workspace      │  │
│  │  Linux B1     │     │ (ai-sre-demo)    │     │ (law-sre-demo) │  │
│  └──────┬───────┘     └────────┬─────────┘     └────────────────┘  │
│         │                      │                                    │
│         │              ┌───────▼─────────┐                          │
│         │              │  Azure Monitor   │                          │
│         │              │  Alert Rules     │                          │
│         │              │  • HTTP 5xx > 5  │                          │
│         │              │  • Resp time > 3s│                          │
│         │              │  • Health < 100% │                          │
│         │              └───────┬─────────┘                          │
│         │                      │                                    │
│         │              ┌───────▼─────────┐                          │
│         └──────────────│   SRE Agent      │                          │
│                        │  (Reader role)   │                          │
│                        │  Monitors RG     │                          │
│                        └─────────────────┘                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Data flow:**
1. App Service runs the demo Node.js app, sending telemetry to Application Insights
2. Application Insights forwards data to the Log Analytics workspace
3. Azure Monitor evaluates metric alert rules against App Service metrics
4. When alerts fire, SRE Agent detects and begins autonomous investigation
5. SRE Agent queries App Insights, activity logs, and resource config to build an RCA

---

## Prerequisites

| Requirement | Details |
|-------------|---------|
| **Azure CLI** | v2.50+ — [Install](https://learn.microsoft.com/cli/azure/install-azure-cli) |
| **Subscription** | With permissions to create App Service, App Insights, Log Analytics |
| **curl & jq** | For traffic generation and testing |
| **zip** | For packaging the app for deployment |
| **Bash** | Linux, macOS, or WSL on Windows |

Verify your setup:

```console
$ az version
{
  "azure-cli": "2.67.0",
  ...
}

$ curl --version | head -1
curl 8.5.0 (x86_64-pc-linux-gnu)

$ jq --version
jq-1.7
```

---

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/lproux/sre_agent.git
cd sre_agent
chmod +x *.sh

# 2. Deploy everything to Azure
./setup-sre-demo.sh

# 3. Create SRE Agent in Azure Portal (see instructions below)

# 4. Generate baseline traffic (run 30 min before demo)
./generate-traffic.sh

# 5. During demo — break the app
./break-app.sh

# 6. Watch SRE Agent investigate... then fix
./fix-app.sh

# 7. After demo — clean up
./cleanup.sh
```

---

## Setup Walkthrough

### Step 1: Run the Setup Script

```console
$ ./setup-sre-demo.sh
============================================
  Azure SRE Agent Demo - Environment Setup
============================================

Resources will be created in: swedencentral
Resource Group: rg-sre-agent-demo

[1/8] Logging into Azure...
  Subscription set to: d334f2cd-3efd-494e-9fd3-2470b1a13e4c
[2/8] Creating resource group...
  Resource group 'rg-sre-agent-demo' ready.
[3/8] Creating Log Analytics workspace...
  Log Analytics workspace 'law-sre-demo' ready.
[4/8] Creating Application Insights...
  Application Insights 'ai-sre-demo' ready.
[5/8] Creating App Service Plan (Linux B1)...
  App Service Plan 'plan-sre-demo' ready.
[6/8] Creating Web App...
  Web App 'app-sre-demo-a1b2c3' ready.
[7/8] Deploying application code...
  Application deployed.
[8/8] Creating Azure Monitor alert rules...
  Alert rules created.

============================================
  Setup Complete!
============================================

  Web App URL : https://app-sre-demo-a1b2c3.azurewebsites.net
  App Insights: ai-sre-demo
  Resource Grp: rg-sre-agent-demo
  Config saved: /path/to/sre_agent/.env

  Next steps:
    1. Create SRE Agent in Azure Portal (Sweden Central)
    2. Connect it to resource group 'rg-sre-agent-demo'
    3. Run ./generate-traffic.sh 30 min before demo
```

The script creates all resources and saves the configuration to `.env` for the other scripts to use.

### Step 2: Verify Deployment

```console
$ curl -s https://app-sre-demo-a1b2c3.azurewebsites.net/health | jq
{
  "status": "healthy",
  "timestamp": "2026-03-16T10:00:00.000Z"
}
```

Open the app URL in a browser to see the live dashboard:

> **Dashboard**: Open the app URL in a browser to see the dark-themed live dashboard with health status, metrics, API docs, and a "Test Document Processing" button. It auto-refreshes every 5 seconds.

### Step 3: Create SRE Agent in Portal

See [SRE Agent Portal Setup](#sre-agent-portal-setup) below.

---

## Demo Workflow

### Before the Demo (30 minutes)

Start the traffic generator to populate Application Insights with baseline data:

```console
$ ./generate-traffic.sh
============================================
  SRE Agent Demo - Traffic Generator
============================================

  Target : https://app-sre-demo-a1b2c3.azurewebsites.net
  Duration: 1800s
  Interval: 2s between requests

  Press Ctrl+C to stop early.

  [1] GET /health -> 200
  [2] POST /api/process (invoice) -> 200
  [3] GET /api/documents -> 200
  [4] GET /health -> 200
  [5] GET /api/documents/doc-sample-3 -> 200
  [6] GET /api/status -> 200
  ...
```

This sends a realistic mix of traffic (health checks, document processing, listings) for 30 minutes.

### During the Demo — Break It

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

  Verify: curl https://app-sre-demo-a1b2c3.azurewebsites.net/health
  Fix with: ./fix-app.sh
```

The dashboard immediately turns red:

> **Dashboard turns red**: The health indicator pulses red, a warning banner appears ("SERVICE DEGRADED"), and the accent color shifts from blue to red across the entire UI.

Verify from the terminal:

```console
$ curl -s https://app-sre-demo-a1b2c3.azurewebsites.net/health | jq
{
  "status": "unhealthy",
  "timestamp": "2026-03-16T10:32:00.000Z",
  "error": "Service degraded"
}

$ curl -s -o /dev/null -w "HTTP %{http_code} - %{time_total}s\n" \
    -X POST https://app-sre-demo-a1b2c3.azurewebsites.net/api/process \
    -H "Content-Type: application/json" \
    -d '{"documentType":"invoice","fileName":"test.pdf"}'
HTTP 500 - 1.247s
```

**What to show in the portal:**
- **Application Insights > Live Metrics** — Red error spikes appearing
- **Azure Monitor > Alerts** — Alert rules transitioning to "Fired" state
- **Application Insights > Failures** — Exception drilldown showing stack traces

> **In the portal**: Azure Monitor Alerts show "Fired" state. Application Insights Failures blade shows exception drilldowns with stack traces.

### SRE Agent Investigates

Within 1-2 minutes of alerts firing, SRE Agent detects the incident and starts investigating:

> **SRE Agent dashboard**: The agent opens an investigation thread, queries Application Insights for exceptions, checks the Activity Log for recent changes, and correlates evidence.

**What SRE Agent does:**
1. Detects the fired Azure Monitor alerts
2. Queries Application Insights for recent exceptions
3. Correlates timing with activity log changes
4. Checks resource health and configuration
5. Produces a structured Root Cause Analysis

> **RCA output**: The agent produces a structured root cause analysis identifying the `APP_HEALTHY` config change, with evidence timestamps and a recommended fix.

### During the Demo — Fix It

```console
$ ./fix-app.sh
============================================
  SRE Agent Demo - Fixing the App
============================================

[1/2] Setting APP_HEALTHY=true...
[2/2] Restarting web app to apply changes...

  App is now FIXED!

  All endpoints will return healthy responses.
  Azure Monitor alerts will auto-resolve within ~5 minutes.

  Verify: curl https://app-sre-demo-a1b2c3.azurewebsites.net/health
```

```console
$ curl -s https://app-sre-demo-a1b2c3.azurewebsites.net/health | jq
{
  "status": "healthy",
  "timestamp": "2026-03-16T10:45:00.000Z"
}
```

### After the Demo — Cleanup

```console
$ ./cleanup.sh
============================================
  SRE Agent Demo - Cleanup
============================================

  This will DELETE the following resources:
    - Resource Group: rg-sre-agent-demo
    - Web App:        app-sre-demo-a1b2c3
    - App Insights:   ai-sre-demo
    - Log Analytics:  law-sre-demo
    - App Service:    plan-sre-demo
    - All alert rules

  Are you sure? (y/N): y

[1/2] Deleting resource group 'rg-sre-agent-demo' (this may take a few minutes)...
[2/2] Removing local config...

  Cleanup initiated!
  Resource group deletion runs in background (~2-5 minutes).
```

---

## The Demo App

The app simulates a **document processing platform** — a realistic scenario for enterprise customers. It runs on Node.js 20 with Express and Application Insights SDK.

### Dashboard

The app serves a live HTML dashboard at `/` with:
- Real-time health status (auto-refreshes every 5s)
- Uptime, memory, and Node.js version metrics
- API endpoint documentation
- Interactive "Test Document Processing" button
- Visual state change when unhealthy (red theme + warning banner)

### API Endpoints

| Method | Path | Description | Healthy | Broken |
|--------|------|-------------|---------|--------|
| `GET` | `/` | Live dashboard | Dashboard UI | Red degraded UI |
| `GET` | `/health` | Health probe (used by App Service) | `200` | `503` |
| `GET` | `/api/status` | Detailed app status | `200` (fast) | `200` (slow, +200ms CPU) |
| `POST` | `/api/process` | Process a document | `200` + extracted fields | `500` + exception logged |
| `GET` | `/api/documents` | List processed documents | `200` | `200` (slow, +300ms CPU) |
| `GET` | `/api/documents/:id` | Get document details | `200` | `500` + exception logged |

### Failure Mode

When `APP_HEALTHY=false`:
- **Health endpoint** returns `503` with `"status": "unhealthy"`
- **Process endpoint** returns `500` with `"Document processing engine failure - connection pool exhausted"`
- **All endpoints** add artificial CPU load (100-500ms) to spike response times
- **Application Insights** receives:
  - `trackException()` calls with severity Error/Critical
  - `DocumentProcessingFailed` custom events
  - Elevated response times in request telemetry
- **Azure Monitor** triggers:
  - `alert-http-5xx` (HTTP 5xx > 5 in 5 min window)
  - `alert-response-time` (avg response time > 3s)
  - `alert-health-check` (health check status < 100%)

---

## Script Reference

### `setup-sre-demo.sh`

Provisions the complete Azure environment in one run.

| What it creates | Resource name | SKU / Config |
|----------------|---------------|--------------|
| Resource Group | `rg-sre-agent-demo` | Sweden Central |
| Log Analytics Workspace | `law-sre-demo` | 30-day retention |
| Application Insights | `ai-sre-demo` | Web, connected to LAW |
| App Service Plan | `plan-sre-demo` | Linux B1 |
| Web App | `app-sre-demo-<random>` | Node.js 20 LTS |
| Alert Rule | `alert-http-5xx` | 5xx > 5 in 5m, Sev 1 |
| Alert Rule | `alert-response-time` | Avg > 3s in 5m, Sev 2 |
| Alert Rule | `alert-health-check` | Health < 100% in 5m, Sev 1 |

**Outputs:** Saves all resource names to `.env` for use by other scripts.

### `generate-traffic.sh`

Sends a realistic mix of API traffic to populate Application Insights.

```bash
./generate-traffic.sh              # Default: 30 min, 2s interval
./generate-traffic.sh 600          # Custom: 10 min
./generate-traffic.sh 3600 1       # Custom: 1 hour, 1s interval
```

**Traffic mix:** 30% health checks, 20% document listings, 20% document detail, 20% document processing, 10% status checks.

### `break-app.sh`

Sets `APP_HEALTHY=false`, restarts the app, and sends 20 concurrent error requests to accelerate alert triggering.

### `fix-app.sh`

Sets `APP_HEALTHY=true` and restarts the app. Alerts auto-resolve within ~5 minutes.

### `cleanup.sh`

Deletes the entire resource group (with confirmation prompt). Resource group deletion cascades to all contained resources.

---

## SRE Agent Portal Setup

> SRE Agent must be created in **Sweden Central** during the initial GA rollout.

### Step 1: Create the Resource

1. Go to [portal.azure.com](https://portal.azure.com)
2. Click **Create a resource**
3. Search for **"SRE Agent"**
4. Click **Create**

> Go to [sre.azure.com](https://sre.azure.com), sign in, and click **Create agent**.

### Step 2: Configure

| Setting | Value |
|---------|-------|
| Subscription | *(your subscription)* |
| Resource Group | `rg-sre-agent-demo` |
| Region | **Sweden Central** |
| App Insights workspace | `ai-sre-demo` |
| Managed resource groups | `rg-sre-agent-demo` |
| Permission level | **Reader** (recommended for demos) |

### Step 3: Verify

After creation (~2-3 minutes), open the SRE Agent resource to see the dashboard:

> The agent dashboard shows monitored resource groups, resource inventory, and a chat interface.

The agent uses **On-Behalf-Of (OBO) flow** — it acts with the permissions of the user who created it (Reader in our case), so it can investigate but not modify resources.

---

## Demo Talking Points

### Level 100 (~10 min) — "See it in action"

| Time | What to do | What to say |
|------|-----------|-------------|
| 0:00 | Show the app + App Insights | *"We have a document processing app running on Azure, monitored by Application Insights"* |
| 2:00 | Show SRE Agent dashboard | *"SRE Agent is connected to this resource group, watching for incidents"* |
| 3:00 | Run `./break-app.sh` | *"Let's simulate a production incident — a bad config change"* |
| 4:00 | Show Live Metrics + Alerts | *"Errors are flooding in, alerts are firing"* |
| 5:00 | Show SRE Agent investigating | *"Watch — the agent detected the incident and is already investigating"* |
| 7:00 | Show the RCA | *"It found the root cause: the APP_HEALTHY config change"* |
| 8:00 | Run `./fix-app.sh` | *"Let's fix it and watch everything recover"* |
| 9:00 | Show recovery | *"Back to green. The whole cycle — detect, investigate, RCA — in minutes"* |

### Level 200 (~20 min) — "Under the hood"

Adds to Level 100:
- **Custom sub-agents**: Show how to add domain-specific investigation logic
- **Scheduled tasks**: Demonstrate proactive health monitoring
- **GitHub integration**: Show automated issue creation with investigation details
- **Code Interpreter**: Show SRE Agent generating analysis charts

> See [DEMO-GUIDE.md](DEMO-GUIDE.md) for a complete presenter script with detailed talking points.

---

## Troubleshooting

| Problem | Diagnosis | Fix |
|---------|-----------|-----|
| **App not responding** | `az webapp show -n <app> -g rg-sre-agent-demo --query state` | `az webapp start -n <app> -g rg-sre-agent-demo` |
| **App Insights not showing data** | Check connection string in app settings | `az webapp config appsettings list -n <app> -g rg-sre-agent-demo -o table` |
| **Alerts not firing** | Check alert rules exist | `az monitor metrics alert list -g rg-sre-agent-demo -o table` |
| **SRE Agent not detecting** | Verify alerts are in "Fired" state | Run `./break-app.sh` again to send more error traffic |
| **Setup script fails** | Check Azure CLI login | `az login --tenant 2b9d9f47-1fb6-400a-a438-39fe7d768649` |
| **Slow deployment** | SCM build may take time | Wait 2-3 min after deploy, then check `/health` |
| **"Resource not found" in scripts** | `.env` file missing or stale | Re-run `./setup-sre-demo.sh` |
| **Portal loading slowly** | Browser cache or extensions | Use InPrivate/Incognito window |

### Verify Everything Is Working

```bash
# Check all resources exist
az resource list -g rg-sre-agent-demo -o table

# Check app is running
source .env
curl -s "https://${WEB_APP_NAME}.azurewebsites.net/health" | jq

# Check alert rules
az monitor metrics alert list -g rg-sre-agent-demo -o table

# Check App Insights is receiving data
az monitor app-insights metrics show \
  --app ai-sre-demo \
  -g rg-sre-agent-demo \
  --metric requests/count \
  --interval PT5M
```

---

## Project Structure

```
sre_agent/
├── README.md                  # This file
├── DEMO-GUIDE.md              # Presenter script (Level 100/200)
├── FULL-DEMO-PLAYBOOK.md      # Complete 1400-line playbook
├── .gitignore
│
├── app/                       # Node.js demo application
│   ├── package.json
│   ├── server.js              # Express app with 6 endpoints + failure mode
│   ├── web.config
│   ├── .deployment
│   └── public/
│       └── index.html         # Live dashboard UI (dark theme)
│
├── knowledge/                 # Upload to SRE Agent knowledge base
│   ├── architecture.md        # System architecture & request flows
│   ├── runbooks.md            # 5 operational runbooks
│   ├── slos.md                # SLO definitions & error budget policy
│   ├── oncall.md              # Escalation procedures
│   ├── known-issues.md        # Known issues with agent guidance
│   ├── deployments.md         # Deployment procedures
│   ├── contacts.md            # Team ownership matrix
│   └── environment.md         # Full resource inventory
│
├── tools/                     # Custom tools for SRE Agent Builder
│   ├── README.md              # Setup instructions for each tool type
│   ├── python/                # 6 Python tools
│   ├── kusto/                 # 5 parameterized KQL queries
│   └── link/                  # 2 deep-link generators
│
├── skills/                    # Skills (procedure + tools)
│   ├── app-service-troubleshooting/
│   ├── incident-response/
│   ├── performance-analysis/
│   ├── sla-reporting/
│   └── daily-health-check/
│
├── setup-sre-demo.sh          # Provision Azure resources
├── generate-traffic.sh        # Pre-demo traffic generator
├── break-app.sh               # Inject failures
├── fix-app.sh                 # Restore health
├── cleanup.sh                 # Delete all Azure resources
│
└── docs/
    ├── SCREENSHOTS.md
    └── images/
```

---

<p align="center">
  <sub>Built for Azure SRE Agent customer demos</sub>
</p>
