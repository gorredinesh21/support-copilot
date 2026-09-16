# Functions timeout and retries
## Limits
Consumption plan: default 5 min, max 10 min per invocation. Premium/Dedicated: 30 min default, unbounded possible on Dedicated.
## Configuration
`functionTimeout` in host.json. For longer work, switch to Durable Functions (chaining) or queue the work.
## Retries
Built-in retry (`retry.strategy=fixed|exponential` in function.json) max 5 attempts; for queues, drive retry with the poison-queue pattern (maxDequeueCount = 5).
## Idempotency
Make handlers idempotent: retries can duplicate side effects. Use a deterministic key in table storage to deduplicate.