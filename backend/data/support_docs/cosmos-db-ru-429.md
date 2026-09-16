# Cosmos DB 429 rate limiting
## Cause
Consumed RU/s exceeded provisioned throughput on a logical partition.
## Fixes
1. Read the `x-ms-request-charge` header; log RU per operation.
2. Scale: increase RU/s or switch to autoscale with 10-100% burst.
3. Hot partition: check partition key cardinality; high-frequency keys cause one physical partition to absorb all load.
4. Client: implement the SDK's built-in retry with exponential backoff (default 9 retries).
## Sizing heuristic
Plan RU/s >= peak RU/s of the hottest partition * replication factor headroom of 1.25.