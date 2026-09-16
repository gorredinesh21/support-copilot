# Diagnosing Entra ID sign-in failures
## First checks
1. Sign-in logs: Entra admin center > Monitoring > Sign-in logs. Filter by user and failure status.
2. Read the error code: 50053 (account locked), 50126 (invalid credentials), 50076/50079 (MFA required/challenge failed), 53003 (blocked by Conditional Access).
## Conditional Access
Check which policy applied: the sign-in log's Conditional Access tab shows granted/failed policies per attempt.
## Locked accounts
Lockout is usually smart lockout: waits 30-60s. Persistent lockout requires a support ticket with the tenant ID and user object ID.
## Escalation
If failure code 50158 with external security challenge, escalate to the identity team; do not reset the user's password.