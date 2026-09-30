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
| plan-sre-demo | App Service Plan | Linux Free F1, 1 worker | Hosts the web app |
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
- **Public access**: Disabled on the App Service resource
- **Custom domain**: None (uses *.azurewebsites.net)
- **TLS**: HTTPS-only is enabled; both default hostname SSL bindings are disabled and no `Microsoft.Web/certificates` resource is currently present
- **IP restrictions**: None recorded in the site configuration
- **VNet integration**: None recorded in the site configuration

## Security Configuration
- **SRE Agent permissions**: Read access is available for resource and monitoring inspection; write operations require the appropriate authorization
- **Authentication**: Endpoint reachability must be assessed through approved monitoring paths because public network access is disabled
- **Managed identity**: System-assigned and user-assigned identities are configured for the SRE Agent

## Cost Estimate
- App Service plan: Free F1; no paid compute charge is expected for the plan
- Application Insights: Consumption depends on current ingestion and retention configuration
- Log Analytics: Consumption depends on current ingestion and retention configuration
- **Total estimated**: Not maintained here; use current Azure pricing and resource usage for a cost assessment

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
