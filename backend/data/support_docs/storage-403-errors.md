# Storage 403 AuthorizationPermissionMismatch
## Cause
The request reached the service authenticated, but the identity lacks the data-plane RBAC role (e.g. missing `Storage Blob Data Reader`).
## Fix
1. Assign the data-plane role: `az role assignment create --assignee <objectId> --role "Storage Blob Data Reader" --scope <container-resource-id>`.
2. Wait up to 5 minutes for propagation.
3. Distinguish from 401 (AuthenticationFailed): 401 is key/token invalid, 403 is permission.
## Network rule interplay
If the account has `defaultAction = Deny`, also grant the client subnet or use service endpoints; symptom is 403 `IpAddressRangeRestriction`.