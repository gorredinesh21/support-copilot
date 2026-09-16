# VM scale set scale failures
## Common causes
1. **Quota exceeded**: family vCPU quota reached; request an increase or pick another family.
2. **Allocation failure** (cluster full): try another zone, another SKU, or reduce request.
3. **Image/SKU retired**: check the SKU availability list; pin image versions explicitly.
## Commands
`az vmss deallocate` then retry, or update the profile with `--vm-sku`.
## Safe rollout
Use rolling upgrade with `--max-batch-instance-percent 20` and health probes wired to a load balancer.