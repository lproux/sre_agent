# Azure SRE Agent — Complete Demo Playbook

> **Audience**: SRE practitioners who have never seen an AI agent.
> **Your role**: You are showing them how Azure SRE Agent transforms the incident lifecycle they already know.
> **Duration**: Flexible — 10 min (Level 100), 20 min (Level 200), or 45 min (deep dive).
> **Last updated**: March 2026

---

## Table of Contents

1. [Before You Read Anything Else — The One-Sentence Pitch](#1-before-you-read-anything-else)
2. [What Is an "Agent" — Explained for SREs](#2-what-is-an-agent--explained-for-sres)
3. [Traditional SRE vs. SRE Agent — Side by Side](#3-traditional-sre-vs-sre-agent--side-by-side)
4. [Full Demo Environment Setup (Step by Step)](#4-full-demo-environment-setup)
5. [Creating the SRE Agent in Azure Portal (Every Click)](#5-creating-the-sre-agent-in-azure-portal)
6. [Uploading Knowledge Files (Every Click)](#6-uploading-knowledge-files)
7. [Setting Up Incident Response (Every Click)](#7-setting-up-incident-response)
8. [Pre-Demo Checklist](#8-pre-demo-checklist)
9. [The Demo Script — Level 100 (10 Minutes)](#9-the-demo-script--level-100)
10. [The Demo Script — Level 200 (20 Minutes)](#10-the-demo-script--level-200)
11. [The Demo Script — Deep Dive (45 Minutes)](#11-the-demo-script--deep-dive)
12. [Exact Prompts to Type Into SRE Agent Chat](#12-exact-prompts-to-type-into-sre-agent-chat)
13. [What SRE Agent Does Behind the Scenes (Step by Step)](#13-what-sre-agent-does-behind-the-scenes)
14. [Screenshots to Capture](#14-screenshots-to-capture)
15. [PowerPoint Slide Deck Outline](#15-powerpoint-slide-deck-outline)
16. [Handling Audience Questions](#16-handling-audience-questions)
17. [Troubleshooting During the Demo](#17-troubleshooting-during-the-demo)
18. [Post-Demo Follow-Up](#18-post-demo-follow-up)
19. [Appendix A — Glossary for Non-Agent Audiences](#19-appendix-a--glossary)
20. [Appendix B — SRE Agent Pricing & Regions](#20-appendix-b--pricing--regions)
21. [Appendix C — All Azure CLI Commands Used](#21-appendix-c--all-azure-cli-commands)

---

## 1. Before You Read Anything Else

**The one-sentence pitch:**

> "Azure SRE Agent is an AI teammate that detects your production incidents, investigates them the way your best SRE would — querying logs, correlating metrics, checking recent deployments — and delivers a root cause analysis, all before a human opens a laptop."

That's it. Everything in this demo exists to prove that sentence is true.

---

## 2. What Is an "Agent" — Explained for SREs

Your audience knows SRE. They do not know what an "agent" means in the AI context. You **must** bridge this gap before the demo or they will be confused.

### The 60-Second Explanation

> "You all know what a monitoring dashboard does — it shows you data. You all know what an alert rule does — it fires when a threshold is crossed. You all know what a runbook does — it tells a human what steps to follow.
>
> An **agent** is the thing that **connects all three and does the work**.
>
> Think of it this way:
>
> - A **dashboard** is a pair of eyes — it sees.
> - An **alert** is a smoke detector — it screams.
> - A **runbook** is an instruction manual — it explains.
> - An **agent** is a junior SRE — it sees, it thinks, it investigates, and it reports back.
>
> Azure SRE Agent is an AI system that has access to your Azure Monitor metrics, your Application Insights logs, your Activity Log (deployment history), your resource configurations, and your team's knowledge base (runbooks, architecture docs). When an incident happens, the agent **autonomously** runs the same investigation steps your senior SRE would — but in minutes instead of hours, and at 3 AM without needing coffee."

### What Makes It Different From Existing Tools

| Tool | What it does | What it does NOT do |
|------|-------------|---------------------|
| **Azure Monitor Alert** | Fires when a metric crosses a threshold | Does not investigate WHY the metric crossed |
| **Application Insights Smart Detection** | Detects anomalies in telemetry | Does not correlate with deployments or config changes |
| **Azure Advisor** | Gives best-practice recommendations | Does not respond to incidents in real-time |
| **A Bash script / runbook** | Runs fixed steps regardless of context | Does not reason, adapt, or learn from past incidents |
| **Azure SRE Agent** | Detects, investigates, reasons, correlates, remembers, and acts | It's the first tool in this list that **thinks** |

### The Key Capabilities (use this as a verbal checklist)

1. **Detects** — Connects to Azure Monitor Alerts (or PagerDuty, ServiceNow). When alerts fire, the agent knows immediately.
2. **Investigates** — Queries Application Insights, Log Analytics, Azure Monitor metrics, Activity Logs, Resource Graph. Runs KQL. Checks resource configurations.
3. **Reasons** — Forms hypotheses about what went wrong. Tests each hypothesis against evidence. Rules out false leads.
4. **Remembers** — Stores knowledge from past incidents. References your uploaded runbooks. Gets smarter over time.
5. **Acts** — Can restart services, scale resources, apply fixes — either with human approval (Review mode) or autonomously. Has built-in safety guardrails (no deletes, no Key Vault access).
6. **Reports** — Produces structured root cause analyses with evidence chains, timelines, and recommended fixes.

---

## 3. Traditional SRE vs. SRE Agent — Side by Side

This is the **most important slide** in your presentation. Your audience knows the left column by heart. Your job is to show them the right column.

### The Incident Lifecycle — Before and After

#### Step 1: Detection

| Traditional SRE | With SRE Agent |
|-----------------|---------------|
| PagerDuty/OpsGenie wakes you up at 3 AM | SRE Agent detects the alert instantly |
| You groggily check your phone | Agent has already started investigating |
| You open your laptop, VPN in | Agent is 2 minutes into its analysis |
| **Time elapsed: 5-15 minutes** | **Time elapsed: 0 minutes** |

**What to say**: "The time between alert firing and investigation starting drops from minutes to zero. The agent doesn't sleep."

#### Step 2: Triage

| Traditional SRE | With SRE Agent |
|-----------------|---------------|
| Open Azure Portal | Agent queries Application Insights automatically |
| Open Application Insights | Agent checks Azure Monitor metrics |
| Open Log Analytics | Agent looks at Activity Log for recent changes |
| Open 4-5 browser tabs | Agent correlates everything in a single investigation |
| Try to remember what's normal for this service | Agent already knows baselines from uploaded knowledge |
| **Time elapsed: 10-20 minutes** | **Time elapsed: 2-3 minutes** |

**What to say**: "Think about how many tabs you open during an incident. The portal, App Insights, Log Analytics, the Activity Log, maybe Grafana, maybe your wiki. The agent does all of that in parallel, in 2-3 minutes."

#### Step 3: Root Cause Analysis

| Traditional SRE | With SRE Agent |
|-----------------|---------------|
| "I think it's the database…" (gut feeling) | Agent forms 2-4 hypotheses based on evidence |
| Run a KQL query, scroll through results | Agent runs KQL, correlates time series, traces requests |
| Try another theory, run another query | Agent tests each hypothesis systematically |
| After 30 min, you're 80% sure you found it | Agent provides a validated RCA with evidence chain |
| You write it up in the post-incident doc | Agent's RCA IS the documentation |
| **Time elapsed: 30-60 minutes** | **Time elapsed: 5-10 minutes** |

**What to say**: "When you debug at 3 AM, you're guessing. You follow your gut, you try things, you might go down the wrong path for 20 minutes. The agent doesn't guess — it forms hypotheses, gathers evidence, and systematically validates or invalidates each one. And it shows its work."

#### Step 4: Remediation

| Traditional SRE | With SRE Agent |
|-----------------|---------------|
| Find the right portal blade | Agent proposes: "Restart app-sre-demo" |
| Click through confirmation dialogs | You click **Approve** once |
| Wait for the operation | Agent executes and verifies the fix worked |
| Manually verify the fix | Agent confirms health is restored |
| **Time elapsed: 10-15 minutes** | **Time elapsed: 1-2 minutes** |

**What to say**: "The fix is the easy part once you know what's wrong. But the context-switching — finding the right blade, the right resource, clicking through confirmations — that's friction. The agent proposes a specific fix based on what it found, you approve it, and it executes."

#### Step 5: Knowledge Capture

| Traditional SRE | With SRE Agent |
|-----------------|---------------|
| "I'll write the post-mortem tomorrow" | Agent has already documented everything |
| Post-mortem gets delayed, then forgotten | Investigation thread IS the documentation |
| Next incident: start from scratch | Next incident: agent remembers what worked last time |
| Knowledge lives in one engineer's head | Knowledge is in the agent's memory + knowledge base |

**What to say**: "Be honest — how many post-mortems get written within 24 hours? The agent's investigation thread IS your post-mortem. And unlike a human, it remembers every incident. The next time a similar problem happens, it references what worked before."

### Total MTTR Comparison

| Metric | Traditional SRE | With SRE Agent |
|--------|----------------|---------------|
| Time to first investigation step | 5-15 min | < 1 min |
| Time to root cause | 30-60 min | 5-10 min |
| Time to remediation | 45-90 min | 10-15 min |
| Knowledge captured | Maybe, eventually | Automatically, always |
| Works at 3 AM | Poorly | Perfectly |
| Works on unfamiliar services | Very slowly | Effectively (knowledge base) |
| Scales with team size | Linearly | Agent handles multiple incidents |

---

## 4. Full Demo Environment Setup

### Prerequisites

Make sure you have:
- Azure CLI 2.50+ installed (`az version`)
- An Azure subscription with Owner or User Access Administrator permissions
- `curl` and `jq` available
- A modern browser (Edge or Chrome recommended for portal)

### Step 1: Clone the Repository

```bash
git clone https://github.com/lproux/sre_agent.git
cd sre_agent
chmod +x *.sh
```

### Step 2: Run the Setup Script

```bash
./setup-sre-demo.sh
```

This script takes approximately 5-8 minutes and creates:

| Resource | Name | What it does |
|----------|------|-------------|
| Resource Group | `rg-sre-agent-demo` | Container for all demo resources |
| Log Analytics Workspace | `law-sre-demo` | Centralized log storage (30-day retention) |
| Application Insights | `ai-sre-demo` | APM: request tracing, exceptions, custom events |
| App Service Plan | `plan-sre-demo` | Linux B1 (1 core, 1.75 GB RAM) |
| Web App | `app-sre-demo-<random>` | The demo Node.js application |
| Alert Rule | `alert-http-5xx` | Fires when total HTTP 5xx > 5 in 5 min |
| Alert Rule | `alert-response-time` | Fires when avg response time > 3s in 5 min |
| Alert Rule | `alert-health-check` | Fires when health check status < 100% |

The script saves all resource names to `.env` — this file is used by all other scripts.

### Step 3: Verify the Deployment

```bash
source .env
curl -s "https://${WEB_APP_NAME}.azurewebsites.net/health" | jq
```

Expected output:
```json
{
  "status": "healthy",
  "timestamp": "2026-03-16T10:00:00.000Z"
}
```

Open the URL in your browser — you should see the dark-themed dashboard with a green health indicator.

### Step 4: Test the Break/Fix Cycle

Run this **at least once** before your demo to make sure everything works:

```bash
# Break it
./break-app.sh

# Verify it's broken
curl -s "https://${WEB_APP_NAME}.azurewebsites.net/health" | jq
# Should return: {"status":"unhealthy","error":"Service degraded"}

# Fix it
./fix-app.sh

# Verify it's fixed
curl -s "https://${WEB_APP_NAME}.azurewebsites.net/health" | jq
# Should return: {"status":"healthy"}
```

---

## 5. Creating the SRE Agent in Azure Portal

> This section documents **every single click** so you can do it from memory during the demo.

### Step 5.1: Navigate to SRE Agent

1. Open your browser to **https://sre.azure.com**
2. Sign in with your Azure credentials if prompted
3. You'll see the SRE Agent landing page with an overview and a **Create agent** button
4. Click **Create agent**

> **Screenshot to capture**: `docs/images/05-sre-agent-create.png` — The creation wizard

### Step 5.2: Fill in the Basics

| Field | Value | Why |
|-------|-------|-----|
| **Subscription** | *(your subscription)* | The subscription containing your demo resources |
| **Resource group** | Select **Create new** → name it `rg-sre-agent` | The agent itself lives in its own RG, separate from the app |
| **Agent name** | `sre-demo-agent` | Descriptive, short |
| **Region** | **Sweden Central** | Required for GA rollout. Also available: East US 2, Australia East |

> **Important**: The agent resource group (`rg-sre-agent`) is **different** from the application resource group (`rg-sre-agent-demo`). The agent needs its own RG. This is a common point of confusion.

Click **Next**.

### Step 5.3: Select Resource Groups to Monitor

1. You'll see a list of all resource groups in your subscription
2. Find and **check the box** next to `rg-sre-agent-demo`
3. This is the resource group that contains your app, App Insights, and alerts

> **What this does**: Grants the agent's managed identity **Reader** access to all resources in `rg-sre-agent-demo`. The agent can now query logs, metrics, and configurations for everything in that group.

Click **Save**, then **Next**.

### Step 5.4: Choose Permission Level

| Option | What it means | Recommendation |
|--------|--------------|----------------|
| **Reader** | Agent can investigate but cannot make changes. Any write action requires your explicit approval via OBO flow. | **Select this for the demo** |
| **Privileged** | Agent can execute approved write actions directly using its managed identity | Use after you trust the agent |

Select **Reader** and click **Next**.

### Step 5.5: Review and Create

1. Review the summary:
   - Agent name: `sre-demo-agent`
   - Region: Sweden Central
   - Monitored resource groups: `rg-sre-agent-demo` (Reader)
2. Click **Create**
3. Wait 2-3 minutes for deployment

> **What happens during creation**: Azure provisions:
> - A Container App (the agent runtime)
> - A Managed Identity (for RBAC)
> - An Application Insights instance (for the agent's own telemetry)
> - A Log Analytics workspace (for the agent's own logs)
> - RBAC role assignments (Reader, Log Analytics Reader, Monitoring Reader on `rg-sre-agent-demo`)

### Step 5.6: Verify the Agent Works

1. When deployment completes, click **Chat with agent**
2. In the chat box, type:

```
What Azure resources can you see?
```

3. The agent should respond with something like:

> "I found resources in 1 resource group (rg-sre-agent-demo), including:
> - 1 App Service Plan (plan-sre-demo)
> - 1 Web App (app-sre-demo-176aec)
> - 1 Application Insights (ai-sre-demo)
> - 1 Log Analytics Workspace (law-sre-demo)
> - 3 metric alert rules"

> **Screenshot to capture**: `docs/images/06-sre-agent-dashboard.png` — The agent dashboard after creation

---

## 6. Uploading Knowledge Files

Knowledge files give the agent context about **your** environment. Without them, the agent gives generic answers. With them, it references your specific runbooks, architecture, and procedures.

### Step 6.1: Navigate to Knowledge Base

1. In the SRE Agent portal, click **Builder** in the left sidebar
2. Click **Knowledge base**
3. You'll see an empty state prompting you to add knowledge

### Step 6.2: Upload Files

1. Click **Add file**
2. Navigate to the `knowledge/` folder in your cloned repository
3. Upload ALL 8 files:

| File | What it teaches the agent |
|------|--------------------------|
| `architecture.md` | System components, request flows, what's normal |
| `runbooks.md` | Step-by-step procedures for common incidents |
| `slos.md` | SLO definitions — what "healthy" looks like in numbers |
| `oncall.md` | Escalation paths and severity definitions |
| `known-issues.md` | False positives to ignore (cold starts, ingestion delay) |
| `deployments.md` | How deployments work, what to check in Activity Log |
| `contacts.md` | Who owns what |
| `environment.md` | Complete resource inventory with SKUs and config |

4. Wait for indexing (usually instant)

> **Supported formats**: `.md`, `.txt`, `.csv`, `.json`, `.yaml`, `.pdf`, `.docx`, `.pptx`
> **Limits**: 16 MB per file, 100 MB per upload

### Step 6.3: Verify the Knowledge Base

In the chat, type:

```
What runbooks or procedures do you have in your knowledge base?
```

The agent should respond with a list referencing your uploaded files, with **Sources** links showing which document it used. If it gives generic answers instead of referencing your files, the upload didn't index correctly — try re-uploading.

> **Screenshot to capture**: Agent responding with sources from your knowledge base

### Why This Matters (Talking Point)

> "Without the knowledge base, the agent is a smart generalist. With the knowledge base, it's a team member who has read all your runbooks and architecture docs. It knows that CPU spikes during failure simulation are intentional, it knows your SLOs, and it knows who to escalate to. This is the difference between a generic answer and 'Based on your runbook RB-001, here are the steps…'"

---

## 7. Setting Up Incident Response

### Step 7.1: Verify Azure Monitor Connection

Azure Monitor connects automatically when you create the agent. Verify:

1. Click **Settings** in the left sidebar
2. Click **Incident platform**
3. You should see **Azure Monitor** listed as connected

> **What this means**: When your Azure Monitor alert rules fire (alert-http-5xx, alert-response-time, alert-health-check), the agent will automatically detect them and can start investigating.

### Step 7.2: Create an Incident Response Plan

1. Click **Builder** in the left sidebar
2. Click **Incident response plans** (or go to the Subagent builder canvas)
3. Click **Create response plan**
4. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `app-service-incident-response` |
| **Severity filter** | Sev 1, Sev 2 |
| **Impacted service** | *(leave blank to match all)* |
| **Response subagent** | Default (or create a custom one) |
| **Agent autonomy level** | **Review** (agent proposes, you approve) |

5. Click **Create**

> **What this does**: When an alert with severity 1 or 2 fires in `rg-sre-agent-demo`, the agent automatically:
> 1. Acknowledges the alert
> 2. Opens an investigation thread
> 3. Queries Application Insights, Azure Monitor, and Activity Log
> 4. Produces an RCA
> 5. Proposes remediation actions (which you approve or deny)

---

## 8. Pre-Demo Checklist

Run through this **1 hour before** your demo:

- [ ] **Azure resources running**: `az resource list -g rg-sre-agent-demo -o table`
- [ ] **App is healthy**: `curl -s "https://${WEB_APP_NAME}.azurewebsites.net/health" | jq`
- [ ] **SRE Agent is running**: Open https://sre.azure.com, verify agent status is "Running"
- [ ] **Knowledge files uploaded**: Ask agent "What knowledge documents do you have?"
- [ ] **Incident response plan active**: Check Builder > Incident response plans
- [ ] **Traffic generator started (30 min before)**: `./generate-traffic.sh`
- [ ] **Browser tabs open**:
  - Tab 1: SRE Agent chat (https://sre.azure.com)
  - Tab 2: Azure Portal > rg-sre-agent-demo > Overview
  - Tab 3: Application Insights > ai-sre-demo > Live Metrics
  - Tab 4: Application Insights > ai-sre-demo > Failures
  - Tab 5: Azure Monitor > Alerts
  - Tab 6: The app dashboard (https://<app-name>.azurewebsites.net)
  - Tab 7: Your terminal with `break-app.sh` and `fix-app.sh` ready
- [ ] **Test break/fix cycle once**: `./break-app.sh` then `./fix-app.sh`
- [ ] **Slides loaded** (if using PowerPoint)
- [ ] **Screen sharing set up** (if remote)

---

## 9. The Demo Script — Level 100

> **Duration**: 10 minutes
> **Audience**: Anyone who knows what SRE means
> **Goal**: See the agent detect and investigate an incident live

### Minute 0:00 — Set the Scene (2 min)

**[Show: App dashboard in browser]**

**Say:**

> "What you're looking at is a document processing application running on Azure App Service. Think invoice capture — customers upload invoices, the app extracts fields like vendor name, amount, and date. It's running on Node.js 20, monitored by Application Insights.
>
> Everything is green right now. Let me show you the metrics."

**[Switch to: Application Insights > Live Metrics]**

**Say:**

> "Here's our Live Metrics stream. You can see steady traffic coming in — about 30 requests per minute. No errors. Response times under 200 milliseconds. This is what normal looks like."

**[Switch to: Azure Monitor > Alerts]**

**Say:**

> "We have three alert rules watching this app:
> 1. HTTP 5xx errors — fires if we see more than 5 in 5 minutes
> 2. Response time — fires if average goes above 3 seconds
> 3. Health check — fires if the health endpoint starts failing
>
> All clear right now."

**[Switch to: SRE Agent chat]**

**Say:**

> "And this is Azure SRE Agent. It's connected to the same resource group as our app. It can query Application Insights, Azure Monitor, the Activity Log, and it has our team's runbooks in its knowledge base.
>
> Right now, it's just watching. Let's give it something to investigate."

### Minute 2:00 — Break the App (2 min)

**[Switch to: Terminal]**

**Say:**

> "Let's simulate a production incident. Imagine a bad config change just went out — someone set a flag that breaks the connection to our document processing engine."

**[Run]:**

```bash
./break-app.sh
```

**[Show the terminal output]:**

```
============================================
  SRE Agent Demo - Breaking the App
============================================

[1/2] Setting APP_HEALTHY=false...
[2/2] Restarting web app to apply changes...

  App is now BROKEN!

  Generating error traffic to accelerate alert triggers...
  20 error requests sent.
```

**[Switch to: App dashboard]**

**Say:**

> "Look at the dashboard — it's gone red. 'SERVICE DEGRADED — Document processing engine failure.' Let me verify from the terminal."

**[Run in terminal]:**

```bash
source .env && curl -s "https://${WEB_APP_NAME}.azurewebsites.net/health" | jq
```

**[Show output]:**

```json
{
  "status": "unhealthy",
  "timestamp": "2026-03-16T10:32:00.000Z",
  "error": "Service degraded"
}
```

**[Switch to: Application Insights > Live Metrics]**

**Say:**

> "Look at Live Metrics — you can see the errors flooding in. Request failures are spiking. Response times are through the roof."

### Minute 4:00 — SRE Agent Detects and Investigates (4 min)

**[Switch to: Azure Monitor > Alerts]**

**Say:**

> "The alert rules are firing. HTTP 5xx threshold exceeded. Health check failing. Response time degradation. In a traditional setup, this is where your PagerDuty goes off and someone opens a laptop.
>
> But we have SRE Agent connected. Let's see what it's doing."

**[Switch to: SRE Agent chat]**

> **Important**: The agent should have already opened an investigation thread automatically (if the incident response plan is configured and alerts have been firing for a few minutes). Look in the left sidebar under **Chats** for a new thread labeled with the alert name.

If the agent has auto-opened a thread:

**Say:**

> "Look — the agent already detected the alert and started investigating. I didn't tell it to do anything. Let's watch what it's doing."

If you need to prompt it manually (backup):

**[Type into chat]:**

```
Investigate the current alerts firing on app-sre-demo in rg-sre-agent-demo.
Check Application Insights for exceptions, check the health endpoint,
and look at the Activity Log for recent changes.
```

**[Wait for the agent to work — this takes 1-3 minutes. Narrate what you see]:**

**Say as the agent works:**

> "Watch what it's doing. First, it's querying Application Insights for recent exceptions. See — it found 'Document processing engine failure — connection pool exhausted.' It's noting the severity and frequency.
>
> Now it's checking the Activity Log — it's looking for recent configuration changes. And there it is — it found the APP_HEALTHY setting was changed to 'false'. It's correlating the timing: the exceptions started right after the config change.
>
> Now it's checking the health endpoint directly. 503. It's forming a hypothesis: 'The APP_HEALTHY configuration was changed, causing the application to simulate a degraded state.'
>
> And here's the RCA."

**[Point to the agent's output — it should show something like]:**

> **Root Cause Analysis:**
> - **What happened**: The application's health endpoint is returning 503 and document processing requests are failing with 500 errors.
> - **When it started**: [timestamp], correlating with an App Service configuration change.
> - **Root cause**: The `APP_HEALTHY` application setting was changed from `true` to `false`. This configuration controls the application's simulated health state. When set to `false`, the app enters a degraded mode that returns errors on all processing endpoints and adds artificial CPU load.
> - **Evidence**: Application Insights shows a spike in exceptions starting at [time]. The Activity Log shows a `Microsoft.Web/sites/config/write` operation at the same time.
> - **Recommended fix**: Set `APP_HEALTHY` back to `true` and restart the web app.

**Say:**

> "That's a full root cause analysis in 3 minutes. It didn't just say 'there are errors' — it told us **why** there are errors, **when** they started, **what changed**, and **how to fix it**. And it showed its evidence chain.
>
> Think about how long that takes a human at 3 AM."

### Minute 8:00 — Fix and Recover (2 min)

**[Switch to: Terminal]**

**Say:**

> "The agent told us to set APP_HEALTHY back to true. Let's do that."

**[Run]:**

```bash
./fix-app.sh
```

**[Show output]:**

```
============================================
  SRE Agent Demo - Fixing the App
============================================

[1/2] Setting APP_HEALTHY=true...
[2/2] Restarting web app to apply changes...

  App is now FIXED!
```

**[Switch to: App dashboard — should be green again]**

**[Switch to: Live Metrics — errors stopping, green traffic resuming]**

**Say:**

> "Back to green. The whole cycle — detect, investigate, root cause analysis — in about 5 minutes. No laptop opened at 3 AM. No guessing.
>
> And the best part? The agent remembers this incident. The next time something similar happens, it references what worked this time."

### Minute 10:00 — Wrap Up

**Say:**

> "To summarize what you just saw:
> 1. We broke a production application.
> 2. Azure Monitor alerts fired.
> 3. SRE Agent detected the alerts and started investigating — autonomously.
> 4. It queried Application Insights for exceptions, checked the Activity Log for recent changes, and correlated the evidence.
> 5. It produced a root cause analysis that identified the exact config change that caused the issue.
> 6. It recommended a specific fix.
> 7. Total time: about 5 minutes. Total human involvement: zero until the RCA was ready.
>
> That's Azure SRE Agent."

---

## 10. The Demo Script — Level 200

> **Duration**: 20 minutes
> **Includes everything from Level 100, plus the sections below**

### Minute 10:00 — Deep Investigation Mode (3 min)

**[Switch to: SRE Agent chat]**

**Say:**

> "What I showed you was a standard investigation. SRE Agent also has a **Deep Investigation** mode for complex, multi-layered incidents. Let me show you how it works."

**[Click the Deep Investigation icon (sparkle icon) in the chat, then type]:**

```
Run a deep investigation on the recent incident. I want to understand
all possible root causes and rule out any secondary issues.
```

**[Click Continue when the authorization card appears]**

**Say:**

> "Deep investigation works differently from a standard query. Instead of stopping at the first plausible explanation, it:
> 1. **Gathers context** — Collects logs, metrics, and configuration data
> 2. **Forms hypotheses** — Generates 2-4 theories about what went wrong
> 3. **Validates each one** — Tests hypotheses in parallel, up to 3 levels deep
> 4. **Explains its reasoning** — Shows validated, invalidated, and inconclusive paths
>
> Watch the hypothesis tree build in real time."

**[Point to the visualization as it works]:**

> "See the color coding? Blue means 'currently validating.' Green means 'evidence supports this hypothesis.' Red means 'ruled out.' Yellow means 'inconclusive.' You can click any node to see the full details, evidence, and reasoning."

### Minute 13:00 — Knowledge Base in Action (3 min)

**[Type into chat]:**

```
What does our team's runbook say about handling HTTP 5xx errors?
```

**Say:**

> "Watch the response — see the **Sources** citations? The agent is referencing our specific runbook, not giving a generic answer. It knows our triage steps, our escalation paths, our SLOs.
>
> This is the difference between a smart generalist and a team member who has read all your documentation. You upload your runbooks, architecture docs, known issues — and the agent uses them during every investigation."

### Minute 16:00 — Scheduled Tasks (2 min)

**[Navigate to: Builder > Scheduled tasks]**

**Say:**

> "SRE Agent doesn't just react to incidents — it can proactively monitor your environment on a schedule."

**[Click Create scheduled task and show the form]:**

| Field | Value |
|-------|-------|
| Name | `daily-health-check` |
| Description | Check application health and App Insights trends |
| When should this task run? | Every day at 9 AM UTC |
| How often should it run? | Every weekday at 9am UTC |
| Agent instructions | (see below) |

**Agent instructions to paste:**

```
Check the health of all resources in rg-sre-agent-demo:
1. Query the /health endpoint of the web app
2. Check Application Insights for error rate trends in the last 24 hours
3. Check for any unresolved Azure Monitor alerts
4. Verify the App Service plan has sufficient resources
5. Summarize findings. If any issues found, provide recommended actions.
```

**Say:**

> "You write instructions in plain English. The agent figures out which tools to use. It can even draft the cron expression for you — click 'Draft the cron for me.'"

**[Click Run task now to show it in action]**

### Minute 18:00 — Run Modes and Safety (2 min)

**Say:**

> "A question you're probably thinking: 'How much can this thing do without asking me?'
>
> The answer is: exactly as much as you allow. SRE Agent has three run modes:"

| Mode | What happens | Use when |
|------|-------------|----------|
| **Review** (default) | Agent proposes actions, you approve or deny | Production, critical infrastructure |
| **Autonomous** | Agent executes immediately, reports what it did | Staging, trusted recurring tasks |
| **ReadOnly** | Agent can only query and analyze, never takes action | Initial evaluation period |

**Say:**

> "Start with Review mode. Watch what the agent recommends for 2-4 weeks. When you find patterns you consistently approve — like 'restart the app when health check fails' — move that specific trigger to Autonomous.
>
> And there are built-in safety guardrails:
> - The agent **never** runs delete or remove commands
> - The agent **never** accesses Key Vault
> - The agent checks for Azure management locks before any write action
> - Every action is logged with full audit trail: who triggered it, what changed, why, and whether it succeeded."

---

## 11. The Demo Script — Deep Dive

> **Duration**: 45 minutes
> **Includes everything from Level 100 + 200, plus:**

### Minute 20:00 — Building Custom Subagents (10 min)

**[Navigate to: Builder > Subagent builder]**

**Say:**

> "The default agent is powerful out of the box, but you can create specialized subagents for different parts of your infrastructure."

Walk through creating a subagent:

1. Click **Create subagent**
2. Name: `app-service-specialist`
3. Instructions:

```
You are an App Service specialist. When investigating App Service issues:
1. Always check the health endpoint first
2. Check Application Insights for the top 5 exceptions in the last hour
3. Check the Activity Log for recent deployments and configuration changes
4. Check CPU and memory metrics on the App Service plan
5. Reference the team's runbooks in the knowledge base
6. For this specific application, know that APP_HEALTHY=false is an intentional
   test mode, not a real failure — but the effects are real (5xx errors, latency).
```

4. Assign tools: Application Insights, Azure CLI, Log Analytics, Knowledge Base search
5. Set mode: Review

**Say:**

> "Each subagent gets its own tools, instructions, and knowledge. You can have a database specialist, a networking specialist, an AKS specialist — each with deep domain knowledge.
>
> During an incident, the orchestrator automatically delegates to the right subagent based on what type of resource is affected."

### Minute 30:00 — Integrations Deep Dive (10 min)

Walk through the available integrations:

| Integration | What it adds |
|-------------|-------------|
| **GitHub** | Agent can search repos, look at recent commits, create issues |
| **Azure DevOps** | Work items, repos, wiki |
| **PagerDuty** | Receive incidents from PagerDuty, not just Azure Monitor |
| **ServiceNow** | Same, for ServiceNow |
| **Outlook** | Agent can send email reports |
| **Teams** | Agent can be tagged in a Teams channel |
| **Grafana** | Agent can query Grafana dashboards |
| **Custom MCP** | Connect any external tool via Model Context Protocol |

**Say:**

> "SRE Agent isn't locked to Azure Monitor. If your team uses PagerDuty for paging and Grafana for dashboards, the agent connects to all of them. MCP — Model Context Protocol — means you can connect literally any external tool or data source."

### Minute 40:00 — Q&A and Freeform Chat (5 min)

Let the audience ask the agent questions live. Suggestions:

```
Show me the top 5 slowest endpoints in the last hour
```

```
What would happen if I scaled up from B1 to S1?
```

```
Create a visualization of error rates over the last 6 hours
```

```
What best practices should I implement for this App Service?
```

---

## 12. Exact Prompts to Type Into SRE Agent Chat

These are tested, reliable prompts. Use them verbatim.

### Discovery

```
What Azure resources can you see in rg-sre-agent-demo?
```

```
Show me the current health status of all resources in my resource group.
```

```
What alert rules are configured for my web app?
```

### Investigation

```
Investigate the current alerts firing on my web app. Check Application Insights
for exceptions, the health endpoint, and the Activity Log for recent changes.
```

```
Why is app-sre-demo-176aec returning 503 errors? Run a full investigation.
```

```
Check Application Insights for the top exceptions in the last 30 minutes
and correlate them with any recent configuration changes.
```

### Deep Investigation

```
Run a deep investigation on the HTTP 5xx errors. Form multiple hypotheses
and validate each one with evidence.
```

### Knowledge Base

```
What runbooks or procedures do you have in your knowledge base?
```

```
Based on our team's runbooks, what are the triage steps for high HTTP 5xx errors?
```

```
What are our SLOs for the document processing API?
```

### Remediation (Review mode — agent will ask for approval)

```
Fix the health check failures on the web app by setting APP_HEALTHY to true.
```

```
Restart the web app to apply the configuration change.
```

### Visualization

```
Show me a chart of HTTP response codes for the last 2 hours.
```

```
Create a visualization of average response time over the last 6 hours.
```

### Proactive

```
Run a reliability assessment on my App Service configuration.
Check for best practices like AlwaysOn, health checks, and auto-heal.
```

```
Analyze the Application Insights data and tell me if there are any
concerning trends I should be aware of.
```

---

## 13. What SRE Agent Does Behind the Scenes

When you say "Investigate the current alerts," here's exactly what happens. Use this to narrate during the demo.

### Step 1: Context Gathering (30 seconds)

The agent's first moves:

| Action | Tool Used | What it gets |
|--------|----------|-------------|
| List fired alerts | Azure Monitor Alerts API | Alert names, severity, timestamps, state |
| Get app resource details | Azure Resource Graph | App Service config, SKU, runtime |
| Check recent activity | Activity Log query | Last 1 hour of operations on the RG |

### Step 2: Telemetry Analysis (60 seconds)

| Action | Tool Used | What it gets |
|--------|----------|-------------|
| Query exceptions | Application Insights KQL | Exception messages, stack traces, counts, timing |
| Query request performance | Application Insights KQL | Response times by endpoint, error rates, status codes |
| Check custom events | Application Insights KQL | `DocumentProcessingFailed` events with properties |
| Query metrics | Azure Monitor Metrics API | CPU, memory, HTTP 5xx, response time time-series |

Example KQL the agent runs internally:

```kusto
exceptions
| where timestamp > ago(1h)
| summarize count() by type, outerMessage
| order by count_ desc
| take 10
```

```kusto
requests
| where timestamp > ago(1h)
| summarize
    totalRequests = count(),
    failedRequests = countif(success == false),
    avgDuration = avg(duration),
    p95Duration = percentile(duration, 95)
  by name, resultCode
| order by failedRequests desc
```

### Step 3: Hypothesis Formation (30 seconds)

Based on the evidence, the agent forms hypotheses:

1. **Hypothesis A**: "Application configuration change caused failure mode" — Evidence: APP_HEALTHY changed to false in Activity Log, timing correlates with error spike
2. **Hypothesis B**: "Application crash or resource exhaustion" — Evidence: High CPU metrics, but RSS memory normal
3. **Hypothesis C**: "External dependency failure" — Evidence: No dependency failures in App Insights

### Step 4: Hypothesis Validation (60 seconds)

The agent tests each hypothesis:

- **Hypothesis A**: VALIDATED — Config change timestamp matches error start time exactly. The APP_HEALTHY setting is explicitly designed to trigger failure mode per the knowledge base.
- **Hypothesis B**: INVALIDATED — CPU spike is caused by the simulated load from Hypothesis A, not the other way around. Memory is within normal bounds.
- **Hypothesis C**: INVALIDATED — No external dependency failures detected. The application has no external dependencies in this demo environment.

### Step 5: RCA Output

The agent produces a structured report with:
- **Summary**: What happened in 1-2 sentences
- **Timeline**: When each symptom appeared
- **Root cause**: The validated hypothesis with evidence
- **Evidence chain**: Links to the specific log entries, metrics, and Activity Log operations
- **Recommended fix**: Specific action with exact command
- **Knowledge base references**: Cites your runbooks if relevant

---

## 14. Screenshots to Capture

Capture these during your first successful run. Put them in `docs/images/`.

| # | File Name | What to Show | When to Capture |
|---|-----------|-------------|----------------|
| 1 | `01-resource-group.png` | Azure Portal > rg-sre-agent-demo overview showing all resources | After setup |
| 2 | `02-app-service.png` | App Service overview blade | After setup |
| 3 | `03-app-insights-overview.png` | Application Insights overview with request/failure charts | After 30 min of traffic |
| 4 | `04-app-insights-live-metrics.png` | Live Metrics Stream with green healthy traffic | During traffic generation |
| 5 | `05-sre-agent-create.png` | SRE Agent creation wizard | During agent setup |
| 6 | `06-sre-agent-dashboard.png` | SRE Agent main dashboard after creation | After agent creation |
| 7 | `07-alert-rules.png` | Azure Monitor > Alerts > Alert rules list | After setup |
| 8 | `08-alert-firing.png` | Alerts in "Fired" state | After break-app.sh |
| 9 | `09-sre-agent-investigation.png` | SRE Agent investigation thread in progress | During investigation |
| 10 | `10-sre-agent-rca.png` | SRE Agent root cause analysis output | After investigation |
| 11 | `11-app-healthy.png` | App dashboard showing green/healthy | When app is healthy |
| 12 | `12-app-broken.png` | App dashboard showing red/degraded | After break-app.sh |
| 13 | `13-app-map.png` | Application Insights > Application Map | After traffic generation |
| 14 | `14-failure-analysis.png` | Application Insights > Failures blade | After break-app.sh |
| 15 | `15-performance-degradation.png` | Application Insights > Performance showing latency spike | After break-app.sh |
| 16 | `16-knowledge-base.png` | Builder > Knowledge base with uploaded files | After knowledge upload |
| 17 | `17-deep-investigation.png` | Deep investigation hypothesis tree | During deep investigation |
| 18 | `18-scheduled-task.png` | Scheduled tasks list | After creating a task |

**How to capture**: Use Win+Shift+S on Windows. Crop to the relevant portal area — no full browser chrome needed. Save as PNG, ~1200px wide.

---

## 15. PowerPoint Slide Deck Outline

Build a deck with these slides. Each slide has speaker notes below.

### Slide 1: Title

> **Azure SRE Agent**
> *Your AI-Powered Site Reliability Engineer*
> [Your name] — [Date]

### Slide 2: The Problem

> **Incident response hasn't fundamentally changed in 20 years.**
> - Alerts fire → Human wakes up → Human opens laptop → Human investigates manually → Human fixes
> - MTTR depends on who's on-call, their experience, and whether they're awake
> - Knowledge lives in senior engineers' heads
> - Post-mortems get written late (or never)

*Speaker notes: "Every SRE team has the same bottleneck: a human has to be awake, available, and experienced enough to investigate. Azure SRE Agent removes that bottleneck."*

### Slide 3: What is Azure SRE Agent?

> **An AI agent that investigates production incidents the way your best SRE would.**
> - Detects alerts from Azure Monitor, PagerDuty, ServiceNow
> - Investigates using App Insights, Log Analytics, Activity Log, Resource Graph
> - Reasons with hypothesis-driven root cause analysis
> - Acts with graduated trust (Review → Autonomous)
> - Remembers and learns from every incident

*Speaker notes: Use the "dashboard / alert / runbook / agent" analogy from Section 2.*

### Slide 4: The Incident Lifecycle — Before and After

> [Use the table from Section 3 — "Total MTTR Comparison"]

*Speaker notes: "Every step of the incident lifecycle gets faster. But the biggest impact is at 3 AM when nobody's awake."*

### Slide 5: Architecture Diagram

> [Show the ASCII diagram from the README or redraw it in PowerPoint]

*Speaker notes: "The agent has a managed identity that gives it Reader access to your resource group. It queries App Insights, Log Analytics, Azure Monitor, and the Activity Log — the same data sources you'd use manually."*

### Slide 6: Live Demo

> **Let's break something and watch the agent fix it.**
> [Full screen to browser]

### Slide 7: How Root Cause Analysis Works

> 1. Gather context (logs, metrics, activity log)
> 2. Form hypotheses (2-4 theories)
> 3. Validate each hypothesis against evidence
> 4. Show conclusion with full evidence chain
>
> [Show screenshot of deep investigation hypothesis tree]

*Speaker notes: "Unlike log searching — where you're manually correlating data across tools — the agent forms hypotheses and tests them. It rules out false leads and shows its reasoning."*

### Slide 8: Run Modes — Graduated Trust

> | Mode | Behavior | Use case |
> | Review | Agent proposes, you approve | Production |
> | Autonomous | Agent acts independently | Staging, trusted tasks |
> | ReadOnly | Agent only analyzes | Evaluation period |

*Speaker notes: "Start with Reader permissions and Review mode. This is the safest configuration. As you build trust, you can move specific triggers to Autonomous."*

### Slide 9: Safety Guardrails

> - Never runs `delete` or `remove` commands
> - Never accesses Key Vault
> - Checks management locks before any write
> - Full audit trail for every action
> - OBO flow: uses your permissions, not its own, for elevated actions

### Slide 10: Knowledge Base

> **Your runbooks, architecture docs, and procedures — in the agent's memory.**
> - Upload `.md`, `.txt`, `.pdf`, `.docx`
> - Agent references your docs during investigation
> - Sources are cited — you can verify
> - Agent also builds its own knowledge from past incidents

### Slide 11: Integrations

> | Category | Integrations |
> | Monitoring | Azure Monitor, App Insights, Log Analytics, Grafana |
> | Incident Mgmt | Azure Monitor Alerts, PagerDuty, ServiceNow |
> | Source Control | GitHub, Azure DevOps |
> | Communication | Outlook, Teams |
> | Data | Azure Data Explorer (Kusto), MCP servers |

### Slide 12: Getting Started

> 1. Go to https://sre.azure.com
> 2. Create an agent (5 min)
> 3. Assign resource groups (Reader access)
> 4. Upload your runbooks
> 5. Chat with your agent
>
> **Available in**: Sweden Central, East US 2, Australia East

### Slide 13: Pricing

> - **Always-on flow**: Continuous monitoring (included)
> - **Active flow**: Billed per Azure AI Unit (AAU) when the agent investigates or takes action
> - Adjustable monthly allocation (up to 200,000 AAU/month)
> - Start with minimal allocation and increase as usage grows

### Slide 14: Q&A

> **Questions?**
> - Documentation: https://learn.microsoft.com/azure/sre-agent
> - Portal: https://sre.azure.com

---

## 16. Handling Audience Questions

### "Does it have access to our production data?"

> "The agent sees what its managed identity has access to. When you create the agent, you choose which resource groups it can read. With Reader permissions, it can query logs, metrics, and configurations — the same data you'd query manually through the portal. It cannot read application data, database contents, or Key Vault secrets."

### "Can it break things?"

> "With Reader permissions (the default), it literally cannot. For write actions, there are three layers of protection:
> 1. **Permissions**: Its managed identity must have the right RBAC role
> 2. **Run mode**: In Review mode, you must approve every write action
> 3. **Safety guardrails**: Delete and remove commands are always blocked. Key Vault access is blocked.
>
> The safest starting point: Reader permissions + Review mode."

### "How is this different from Copilot?"

> "Azure Copilot helps you navigate the portal and write queries. It's an assistant that responds when you ask.
>
> SRE Agent is **autonomous**. It detects incidents on its own, investigates without being asked, and produces root cause analyses. It runs 24/7. It's the difference between a search engine and a teammate."

### "What if the agent's RCA is wrong?"

> "Two things. First, the agent shows its reasoning — you can follow the evidence chain and verify. It doesn't just say 'it's the database'; it says 'Database DTU was at 98%, validated by this KQL query at this time.'
>
> Second, the agent learns. If you correct it — 'That wasn't the root cause, the real issue was X' — it stores that in its memory and applies it to future incidents."

### "How long does it take to see value?"

> "Five minutes to create the agent. Five more minutes to upload your runbooks. Then it starts investigating your next alert. The first time it gives you a useful RCA, you'll see the value."

### "What does it cost?"

> "Billing is based on Azure AI Units (AAUs). Continuous monitoring (always-on flow) is included. Active investigation and actions consume AAUs. You set a monthly allocation — start low and increase as you use it. Think of it as paying for the agent's time when it's actively working, not when it's watching."

### "Can I use it with PagerDuty/ServiceNow?"

> "Yes. Azure Monitor is connected by default, but you can add PagerDuty or ServiceNow as incident sources. The agent receives incidents from those platforms, investigates using Azure telemetry, and can post updates back."

### "Is my data used to train AI models?"

> "No. Azure SRE Agent uses enterprise-grade AI services with strict data handling policies. Your data is not used to train any AI models."

---

## 17. Troubleshooting During the Demo

| Problem | What to Do |
|---------|-----------|
| **App not responding** | Run `az webapp restart -n <app-name> -g rg-sre-agent-demo`. Wait 30 seconds. |
| **Alerts not firing** | Run `./break-app.sh` again to send more error traffic. Alerts evaluate every 1 min with a 5-min window. |
| **Agent not detecting alerts** | Check Builder > Incident response plans — make sure a plan is active. Alternatively, manually prompt the agent to investigate. |
| **Agent investigation slow** | This is normal — complex investigations take 2-5 minutes. Narrate what the agent is doing while it works. |
| **"I can't see any resources"** | Check Settings > Managed resources — make sure `rg-sre-agent-demo` is listed. If not, add it. |
| **Knowledge base not referenced** | Ask explicitly: "Check your knowledge base for runbooks about HTTP 5xx errors." |
| **Portal slow** | Use an InPrivate/Incognito browser window. Close unneeded tabs. |
| **Deep investigation authorization timeout** | The authorization card expires after 10 min. Click **Continue** promptly. |
| **Generate-traffic.sh errors** | The app might still be starting after break/fix. Wait 30 seconds and the errors will stop. |

### Emergency Backup: Manual Investigation

If the agent is unresponsive, you can still demo the concept by manually chatting:

```
I have an App Service called app-sre-demo-176aec in resource group
rg-sre-agent-demo that is returning 503 errors on the health endpoint
and 500 errors on the process endpoint. Can you investigate what's
causing this? Check Application Insights for recent exceptions and
the Activity Log for recent configuration changes.
```

---

## 18. Post-Demo Follow-Up

### Immediate (same day)

- [ ] Run `./fix-app.sh` if the app is still broken
- [ ] Save SRE Agent investigation screenshots for follow-up materials
- [ ] Note any audience questions you couldn't answer

### If the audience wants to try it themselves

Share this checklist:

1. Go to https://sre.azure.com
2. Create an agent (need Owner or User Access Administrator on the subscription)
3. Assign your resource groups
4. Upload your existing runbooks
5. Ask the agent: "What resources can you see?"
6. Documentation: https://learn.microsoft.com/azure/sre-agent

### After the demo day — Cleanup

```bash
./cleanup.sh
```

This deletes `rg-sre-agent-demo` and all its resources. **Remember to also delete the SRE Agent resource group** (`rg-sre-agent`) from the Azure Portal separately, as it was created independently.

---

## 19. Appendix A — Glossary

| Term | Definition for SRE Audiences |
|------|------------------------------|
| **Agent** | An AI system that perceives its environment (your Azure resources), reasons about it (forms hypotheses, checks evidence), and takes action (proposes fixes). Unlike a chatbot, it works autonomously. |
| **Managed Identity** | An Azure identity assigned to the agent. It's like a service account — the agent authenticates as this identity when querying your resources. |
| **OBO Flow (On-Behalf-Of)** | When the agent needs to do something it doesn't have permissions for, it can request temporary access using YOUR permissions. You approve, and it acts on your behalf. |
| **Run Mode** | Controls whether the agent asks permission before acting (Review) or acts independently (Autonomous). |
| **Knowledge Base** | Your uploaded documents — runbooks, architecture docs, procedures. The agent searches these during investigations and cites them in responses. |
| **Subagent** | A specialized child agent with specific tools, instructions, and domain knowledge. Think "database expert" or "networking expert." |
| **Deep Investigation** | A multi-step investigation mode where the agent forms 2-4 hypotheses, validates each with evidence (up to 3 levels deep), and shows a visual tree of its reasoning. |
| **AAU (Azure AI Unit)** | The billing unit for SRE Agent. Active investigation and actions consume AAUs. Monitoring is included. |
| **MCP (Model Context Protocol)** | An open protocol for connecting AI agents to external tools and data sources. Like a plugin system for the agent. |
| **Skills** | Reusable procedures attached to the agent — think "runbook as code." Skills can have tools attached to execute steps. |
| **Hypothesis-Driven Investigation** | Instead of "show me all errors" (log searching), the agent says "I think it could be A, B, or C" and systematically tests each theory. This mirrors how experienced SREs think. |

---

## 20. Appendix B — Pricing & Regions

### Available Regions (as of March 2026)

| Region | Status |
|--------|--------|
| Sweden Central | GA |
| East US 2 | GA |
| Australia East | GA |

The agent can be created in any of these regions but can **monitor resources in any Azure region**.

### Billing Model

| Flow | What it covers | Billing |
|------|---------------|---------|
| **Always-on** | Continuous monitoring, learning your resources | Included |
| **Active** | Investigation, chat, remediation, scheduled tasks | Per AAU consumed |

- Adjustable monthly allocation: up to 200,000 AAU/month
- Changes take effect immediately
- Dashboard at Settings > Agent consumption shows usage

---

## 21. Appendix C — All Azure CLI Commands Used

### Setup Script

```bash
# Login
az login --tenant "2b9d9f47-1fb6-400a-a438-39fe7d768649"
az account set --subscription "d334f2cd-3efd-494e-9fd3-2470b1a13e4c"

# Resource Group
az group create --name rg-sre-agent-demo --location swedencentral

# Log Analytics
az monitor log-analytics workspace create \
  --resource-group rg-sre-agent-demo \
  --workspace-name law-sre-demo \
  --location swedencentral \
  --retention-time 30

# Application Insights
az monitor app-insights component create \
  --app ai-sre-demo \
  --location swedencentral \
  --resource-group rg-sre-agent-demo \
  --workspace "<LAW_ID>" \
  --kind web \
  --application-type web

# App Service Plan
az appservice plan create \
  --name plan-sre-demo \
  --resource-group rg-sre-agent-demo \
  --location swedencentral \
  --sku B1 \
  --is-linux

# Web App
az webapp create \
  --name app-sre-demo-<random> \
  --resource-group rg-sre-agent-demo \
  --plan plan-sre-demo \
  --runtime "NODE:20-lts"

# App Settings
az webapp config appsettings set \
  --name <APP_NAME> \
  --resource-group rg-sre-agent-demo \
  --settings \
    APPLICATIONINSIGHTS_CONNECTION_STRING="<CONNECTION_STRING>" \
    APP_HEALTHY="true"

# Deploy
az webapp up \
  --name <APP_NAME> \
  --resource-group rg-sre-agent-demo \
  --plan plan-sre-demo \
  --runtime "NODE:20-lts"

# Alert Rules
az monitor metrics alert create --name "alert-http-5xx" \
  --resource-group rg-sre-agent-demo --scopes "<WEBAPP_ID>" \
  --condition "total Http5xx > 5" --window-size 5m \
  --evaluation-frequency 1m --severity 1

az monitor metrics alert create --name "alert-response-time" \
  --resource-group rg-sre-agent-demo --scopes "<WEBAPP_ID>" \
  --condition "avg HttpResponseTime > 3" --window-size 5m \
  --evaluation-frequency 1m --severity 2

az monitor metrics alert create --name "alert-health-check" \
  --resource-group rg-sre-agent-demo --scopes "<WEBAPP_ID>" \
  --condition "avg HealthCheckStatus < 100" --window-size 5m \
  --evaluation-frequency 1m --severity 1
```

### Break Script

```bash
az webapp config appsettings set --name <APP_NAME> \
  --resource-group rg-sre-agent-demo --settings APP_HEALTHY="false"
az webapp restart --name <APP_NAME> --resource-group rg-sre-agent-demo
```

### Fix Script

```bash
az webapp config appsettings set --name <APP_NAME> \
  --resource-group rg-sre-agent-demo --settings APP_HEALTHY="true"
az webapp restart --name <APP_NAME> --resource-group rg-sre-agent-demo
```

### Cleanup

```bash
az group delete --name rg-sre-agent-demo --yes --no-wait
```

### Verification Commands

```bash
# Check all resources
az resource list -g rg-sre-agent-demo -o table

# Check app health
curl -s "https://<APP_NAME>.azurewebsites.net/health" | jq

# Check alerts
az monitor metrics alert list -g rg-sre-agent-demo -o table

# Check App Insights data
az monitor app-insights metrics show \
  --app ai-sre-demo -g rg-sre-agent-demo \
  --metric requests/count --interval PT5M
```

---

*This playbook was built for the Azure SRE Agent demo environment at https://github.com/lproux/sre_agent*
