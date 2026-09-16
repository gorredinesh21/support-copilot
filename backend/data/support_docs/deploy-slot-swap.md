# Deployment slot swap
## Procedure
1. Deploy to the `staging` slot.
2. Warm it: hit the health endpoint on the staging hostname.
3. Swap: `az webapp deployment slot swap -n myapp --slot staging --target-slot production` with `--action swap`.
## Settings
Mark connection strings as `slot sticky` unless they must swap. App settings swap by default.
## Rollback
Swap back immediately; the previous bits are preserved on the staging slot.
## Failure mode
If swap hangs at "sealing", a background process holds a file lock; recycle the target slot after business-impact check.