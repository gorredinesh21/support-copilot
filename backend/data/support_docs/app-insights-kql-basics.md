# KQL basics in App Insights
## Where to query
Logs pane of the App Insights resource (or Azure Monitor / ADX with the same syntax).
## Core tables
`requests` (server calls), `traces` (log lines), `dependencies` (outbound calls), `exceptions`.
## Recipes
- Failed requests: `requests | where success == false | summarize count() by resultCode, name`.
- p95 latency: `requests | summarize p95=percentile(duration, 95) by name`.
- Join errors to traces: `exceptions | join traces on operation_Id`.
## Tip
Every correlated call shares `operation_Id`; start all investigations from it.