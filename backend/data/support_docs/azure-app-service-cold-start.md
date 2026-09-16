# Reducing cold start
## Symptoms
First request after idle takes 5-30 seconds.
## Causes
App Service plans scale to zero only on Free/Shared tiers. Functions on Consumption plan unload after idle.
## Mitigations
1. Always Ready: use Premium (EP1-EP3) plan with `minimumElasticInstanceCount = 1`.
2. For Functions: enable `alwaysReady` per function via host.json or set a timer ping every 4 minutes.
3. Keep dependencies lean; lazy-import heavy modules.
## Verification
Measure p95 of the first-request route in App Insights before and after the change.