# On-Call & Escalation Procedures

## On-Call Rotation
- Primary: Application team (SRE Agent acts as first responder)
- Secondary: Platform engineering team
- Escalation: Cloud infrastructure team

## SRE Agent Role
SRE Agent serves as the automated first responder:
1. Detects alerts from Azure Monitor
2. Performs initial investigation (checks logs, metrics, dependencies)
3. Produces Root Cause Analysis
4. If Reader permissions: Reports findings, human takes remediation action
5. If Contributor permissions: Can take approved remediation actions

## Alert Severity Matrix

| Severity | Response Time | Examples | Action |
|----------|--------------|---------|--------|
| Sev 1 (Critical) | Immediate | Health check failing, 5xx spike | SRE Agent auto-investigates, page on-call |
| Sev 2 (Warning) | 15 minutes | Response time degradation | SRE Agent investigates, notify on-call |
| Sev 3 (Info) | Next business day | Minor anomalies | SRE Agent logs finding, no page |

## Incident Response Flow
1. Azure Monitor fires alert
2. SRE Agent detects and begins investigation
3. SRE Agent queries Application Insights, Activity Log, resource config
4. SRE Agent produces RCA with:
   - What happened (symptoms)
   - When it started (timeline)
   - Why it happened (root cause)
   - What to do (recommended fix)
5. Human reviews RCA and applies fix
6. Post-incident: Review SRE Agent's investigation for accuracy

## Communication Channels
- SRE Agent findings: Azure Portal > SRE Agent dashboard
- Incident updates: GitHub Issues (auto-created by SRE Agent if configured)
- Escalation: Teams channel #sre-incidents

## Post-Incident Review
After every Sev 1/2 incident:
- Review SRE Agent's RCA for accuracy
- Document any gaps in SRE Agent's investigation
- Update knowledge files if new failure modes discovered
- Adjust alert thresholds if needed
