# Azure SRE Agent Demo Environment

## Project Context
This is a demo environment for Azure SRE Agent, used for customer presentations.
The demo app is a Node.js service deployed to Azure App Service that simulates
a document processing platform (similar to ITESOFT's YooZ).

## Architecture
- **Resource Group**: rg-sre-agent-demo (Sweden Central)
- **App Service**: Linux B1 plan, Node.js 20 LTS
- **Application Insights**: Connected to Log Analytics workspace
- **Azure Monitor**: Alert rules for HTTP 5xx and response time
- **SRE Agent**: Created via Azure Portal (no IaC yet), monitors the resource group

## Key Commands

### Setup (run once)
```bash
chmod +x setup-sre-demo.sh && ./setup-sre-demo.sh
```

### Before Demo (30 min before)
```bash
./generate-traffic.sh
```

### During Demo - Break the App
```bash
./break-app.sh
```
This sets APP_HEALTHY=false, causing:
- /health returns 503
- /api/process returns 500
- High CPU simulation (slow responses)
- Application Insights exceptions logged
- Azure Monitor alerts fire

### During Demo - Fix the App
```bash
./fix-app.sh
```

### After Demo - Cleanup
```bash
./cleanup.sh
```

## Demo Talking Points

### Level 100 Demo (~10 min)
1. Show SRE Agent dashboard in portal
2. Break the app
3. Watch agent detect and investigate
4. Show the RCA output
5. Fix the app

### Level 200 Demo (~20 min)
1. All of Level 100
2. Show custom sub-agent configuration
3. Demonstrate scheduled tasks (proactive checks)
4. Walk through GitHub issue creation
5. Show Code Interpreter generating analysis charts

## SRE Agent Portal Setup Steps
1. portal.azure.com > Create resource > search "SRE Agent"
2. Select subscription + resource group (rg-sre-agent-demo)
3. Connect App Insights workspace (ai-sre-demo)
4. Add resource group to manage
5. Permission: Reader (safer for demo, uses OBO flow)
6. Create

## Troubleshooting
- If SRE Agent does not detect incident: check that Azure Monitor alerts are firing
- If app not deploying: verify App Service plan is running (az webapp start)
- If App Insights not showing data: check connection string in app settings
- Agent creation region must be Sweden Central during initial GA rollout
