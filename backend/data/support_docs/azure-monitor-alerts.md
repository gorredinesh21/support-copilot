# Actionable alerts
## Principles
Alert on symptoms users feel (availability, error rate, latency), not on CPU vanity metrics.
## Setup
1. Availability test (ping + content match) per public endpoint.
2. Metric alert: `requests/failed > 2% for 10 min` via dynamic thresholds.
3. Log alert: `traces | where severity_level == 3` fired per operation_Id.
## Action groups
Page on Sev1 signal only; email the team channel otherwise. Every alert links to a runbook doc; alerts without runbooks are deleted at review time.