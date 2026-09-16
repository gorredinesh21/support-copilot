# Escalation policy
## Severity levels
- **Sev1**: production down or data loss. 15-min response SLA, page on-call immediately.
- **Sev2**: major feature degraded with no workaround. 1-hour response.
- **Sev3**: minor feature issue, workaround exists. 1 business day.
- **Sev4**: question / how-to. 2 business days.
## Path
L1 support -> service on-call (via the Support Copilot's 'not found' flow, create the ticket with the required fields) -> service owner for Sev1 within 30 minutes.
## Required fields when escalating
Tenant/customer ID, operation_Id from telemetry, reproduction steps, business impact statement.