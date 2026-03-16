# Environment Inventory

## Subscription
- **Subscription ID**: d334f2cd-3efd-494e-9fd3-2470b1a13e4c
- **Tenant ID**: 2b9d9f47-1fb6-400a-a438-39fe7d768649
- **Environment**: Demo / Pre-production
- **Region**: Sweden Central

## Resource Group: rg-sre-agent-demo

### Compute
| Resource | Type | SKU | Purpose |
|----------|------|-----|---------|
| plan-sre-demo | App Service Plan | Linux B1 (1 core, 1.75 GB) | Hosts the web app |
| app-sre-demo-* | App Service (Web App) | Node.js 20 LTS | Document processing API + dashboard |

### Monitoring & Observability
| Resource | Type | Purpose |
|----------|------|---------|
| ai-sre-demo | Application Insights | APM, request tracing, exception logging, custom events |
| law-sre-demo | Log Analytics Workspace | Centralized log storage, 30-day retention |

### Alert Rules
| Alert Name | Metric | Condition | Severity | Evaluation |
|-----------|--------|-----------|----------|------------|
| alert-http-5xx | Http5xx | Total > 5 in 5 min | Sev 1 | Every 1 min |
| alert-response-time | HttpResponseTime | Avg > 3s in 5 min | Sev 2 | Every 1 min |
| alert-health-check | HealthCheckStatus | Avg < 100% in 5 min | Sev 1 | Every 1 min |

### Application Configuration
| Setting | Value | Purpose |
|---------|-------|---------|
| APP_HEALTHY | true/false | Controls simulated health of document processing engine |
| APPLICATIONINSIGHTS_CONNECTION_STRING | (auto-configured) | Connects app to Application Insights |
| SCM_DO_BUILD_DURING_DEPLOYMENT | true | Runs npm install during deployment |
| WEBSITE_NODE_DEFAULT_VERSION | ~20 | Node.js runtime version |

## Network Configuration
- **Public access**: Enabled (demo environment)
- **Custom domain**: None (uses *.azurewebsites.net)
- **TLS**: Azure-managed certificate (HTTPS by default)
- **IP restrictions**: None
- **VNet integration**: None (demo environment)

## Security Configuration
- **SRE Agent permissions**: Reader (can investigate but not modify resources)
- **Authentication**: None (demo app, public endpoints)
- **Managed identity**: Not configured

## Cost Estimate
- App Service B1: ~$13/month
- Application Insights: Pay-per-GB (~$2-5/month at demo traffic levels)
- Log Analytics: Included with App Insights ingestion
- **Total estimated**: ~$15-20/month

## Differences from Production
This is a demo environment. A production deployment would additionally include:
- Azure Cosmos DB (document metadata storage)
- Azure Blob Storage (document file storage)
- Azure AI Document Intelligence (OCR and field extraction)
- Azure Front Door or Application Gateway (WAF, load balancing)
- VNet integration with private endpoints
- Managed identity for service-to-service auth
- Multiple instances with autoscaling
- Geo-redundancy (paired region)
- CI/CD pipeline (GitHub Actions or Azure DevOps)
