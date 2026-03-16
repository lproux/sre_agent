# Team Contacts & Responsibilities

## Application Team
- **Responsibility**: Application code, business logic, API design
- **Scope**: Everything in the `app/` directory
- **Escalate when**: Application-level bugs, business logic errors, feature requests

## Platform / SRE Team
- **Responsibility**: Infrastructure, monitoring, alerting, SRE Agent configuration
- **Scope**: Azure resources, alert rules, deployment pipeline, knowledge files
- **Escalate when**: Infrastructure issues, monitoring gaps, SRE Agent configuration

## Cloud Infrastructure Team
- **Responsibility**: Azure subscription, networking, IAM, cost management
- **Scope**: Subscription-level configuration, RBAC, networking
- **Escalate when**: Permission issues, subscription quota limits, networking problems

## Key Azure Resources — Ownership

| Resource | Owner | Notes |
|----------|-------|-------|
| rg-sre-agent-demo | Platform/SRE | Demo resource group |
| app-sre-demo-* | Application Team | Demo web application |
| ai-sre-demo | Platform/SRE | Telemetry & monitoring |
| law-sre-demo | Platform/SRE | Log aggregation |
| plan-sre-demo | Platform/SRE | Compute infrastructure |
| alert-* | Platform/SRE | Alerting rules |
| SRE Agent | Platform/SRE | Automated investigation |

## Vendor Support
- **Azure Support**: For platform-level issues (App Service outages, regional incidents)
- **Check Azure Status**: https://status.azure.com
- **Check Service Health**: Azure Portal > Service Health (subscription-scoped)
