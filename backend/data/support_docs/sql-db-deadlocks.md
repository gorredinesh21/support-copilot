# Azure SQL deadlocks
## Diagnosis
Query Store + `sys.dm_xe_database_sessions` deadlock events, or enable deadlock XML capture to blob.
## Common patterns
- Opposite-order updates in two transactions: rewrite both to touch tables in the same order.
- Long transactions holding locks: keep transactions short; avoid user interaction inside one.
## Mitigations
Retry logic on deadlock victim (error 1205) with jitter; snapshot isolation (RCSI) for read-heavy workloads (ON by default in Azure SQL).