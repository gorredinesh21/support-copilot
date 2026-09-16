# APIM rate limiting
## Policies
`rate-limit-by-key` (client key) and `quota-by-key` (long window). Set retry-after in the response via the policy.
## Design
Return 429 with `Retry-After` seconds; clients must honor it. Pair with a spike-arrest subscription tier.
## Diagnostics
APIM insights in App Insights: filter `dependencies | where name startswith "apim"`; check `responseCode == 429` ratio per API per product.