# VNet peering DNS
## Symptom
Peered VNets route fine (ping works by IP) but names don't resolve.
## Cause
Private DNS zones aren't linked to both VNets, or the VM uses the default Azure DNS with no custom resolution path.
## Fix
1. Create a private DNS zone per service (privatelink.database.azure.com etc).
2. Link the zone to BOTH VNets (`az network private-dns link vnet create`).
3. For hub-spoke with custom DNS servers, set spoke VNet DNS servers to the hub resolvers and re-DHCP the VMs.
## Validation
`nslookup <hostname>` should return a private 10.x address, not the public IP.