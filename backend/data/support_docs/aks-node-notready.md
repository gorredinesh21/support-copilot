# AKS NotReady nodes
## Diagnosis
`kubectl describe node <n>` — check conditions and events. Common: disk pressure, kubelet stopped, VM allocation failure during surge.
## Quick remediation
1. Cordon and drain the node, then delete; the cluster autoscaler replaces it.
2. If all nodes NotReady: check control plane status and resource group locks.
## Prevention
Upgrade surge `maxSurge=33%`, pod disruption budgets on critical DaemonSets, and node problem detector alerts into App Insights.