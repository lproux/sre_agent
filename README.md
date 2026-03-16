# SRE Agent – Azure

An automated **Site Reliability Engineering (SRE) agent** that monitors your Azure infrastructure, detects incidents via Azure Monitor alerts, and executes remediation actions – all without requiring manual intervention.

---

## Features

- 🔐 **Flexible authentication** – supports DefaultAzureCredential (for local dev / CI), Managed Identity (for workloads running in Azure), and Service Principal credentials
- 📊 **Azure Monitor integration** – polls fired alerts and normalises them into actionable `SREAlert` objects
- 🔧 **Pluggable remediation** – register your own remediation functions per alert severity (Sev0–Sev4)
- 🔁 **Retry & escalation** – configurable retry limit; unresolved alerts are automatically escalated
- 🏗️ **Resource management** – built-in helpers to restart VMs, scale VM Scale Sets, and refresh AKS node pools
- 🛡️ **Dry-run mode** – test remediation logic without touching production resources
- 📝 **Structured logging** – plain-text (development) or JSON (production) log output via `structlog`

---

## Quick Start

### 1. Install

```bash
# Editable install with dev dependencies
pip install -e ".[dev]"
```

### 2. Configure

All settings are read from environment variables prefixed with `SRE_AGENT_`.
Copy `.env.example` to `.env` and fill in your values:

```bash
# Required
SRE_AGENT_SUBSCRIPTION_ID=<your-azure-subscription-id>

# Optional – scope monitoring to a single resource group
SRE_AGENT_RESOURCE_GROUP=my-resource-group

# Authentication (default: DefaultAzureCredential)
# Options: default | managed_identity | service_principal
SRE_AGENT_AUTH_METHOD=default

# Service-principal credentials (required when AUTH_METHOD=service_principal)
SRE_AGENT_TENANT_ID=<azure-ad-tenant-id>
SRE_AGENT_CLIENT_ID=<service-principal-app-id>
SRE_AGENT_CLIENT_SECRET=<service-principal-secret>

# Agent behaviour
SRE_AGENT_POLL_INTERVAL_SECONDS=60   # how often to poll Azure Monitor
SRE_AGENT_MAX_REMEDIATION_RETRIES=3  # attempts before escalating
SRE_AGENT_DRY_RUN=false              # set to true to log-only

# Logging
SRE_AGENT_LOG_LEVEL=INFO             # DEBUG | INFO | WARNING | ERROR
SRE_AGENT_LOG_JSON=false             # set to true for JSON log output
```

### 3. Run

```bash
# Continuous polling loop
sre-agent run

# Single cycle (poll once and exit)
sre-agent run --once

# Dry-run (no real remediations)
sre-agent run --dry-run
```

---

## Custom Remediations

Register your own handlers for any alert severity:

```python
from sre_agent import SREAgent, AgentConfig
from sre_agent.azure.alerts import AlertSeverity, SREAlert

agent = SREAgent(config=AgentConfig())

@agent.alert_handler.register(AlertSeverity.CRITICAL)
def handle_critical(alert: SREAlert) -> bool:
    # Your custom logic here.
    # Return True to mark the alert as resolved, False to retry.
    print(f"Handling critical alert: {alert.name}")
    return True

agent.run()
```

---

## Project Structure

```
src/sre_agent/
├── __init__.py          # Public API (SREAgent, AgentConfig)
├── agent.py             # Core polling loop and orchestration
├── cli.py               # Click-based CLI entry-point
├── config.py            # Pydantic-settings configuration
└── azure/
    ├── __init__.py
    ├── client.py         # Azure credential factory (AzureClient)
    ├── monitor.py        # Azure Monitor alert fetching (AzureMonitor)
    ├── alerts.py         # Alert models and handler pipeline (AlertHandler)
    └── resources.py      # Remediation helpers – VM, VMSS, AKS (AzureResourceManager)

tests/
├── test_config.py        # AgentConfig unit tests
├── test_agent.py         # SREAgent unit tests
└── azure/
    ├── test_alerts.py    # AlertSeverity, SREAlert, AlertHandler tests
    ├── test_client.py    # AzureClient credential tests
    ├── test_monitor.py   # AzureMonitor tests
    └── test_resources.py # AzureResourceManager tests
```

---

## Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=sre_agent --cov-report=term-missing
```

---

## Azure Permissions Required

The identity used by the agent (service principal or managed identity) needs at minimum:

| Scope | Role |
|-------|------|
| Subscription / Resource Group | **Monitoring Reader** (read alerts & metrics) |
| VM / VMSS resources | **Virtual Machine Contributor** (restart / scale) |
| AKS clusters | **Azure Kubernetes Service Contributor** (node pool operations) |

---

## Security Notes

- **Never commit credentials** – use environment variables or Azure Key Vault references.
- **Prefer Managed Identity** when running inside Azure (no long-lived secrets).
- Enable **dry-run mode** when first deploying to validate remediation logic without impact.

