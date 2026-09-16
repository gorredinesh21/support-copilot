# Key Vault access
## Two permission models
1. **Access policies** (legacy): vault-level secrets/get grants.
2. **Azure RBAC** (recommended): `Key Vault Secrets User` role at the vault scope.
## Common 403 scenarios
- Managed identity missing the role (RBAC mode): error `AccessDenied`.
- Access policy exists but the app uses a different identity than expected.
- Firewall enabled and the app's outbound IPs not allow-listed.
## Diagnostics
Use `az keyvault show --query properties.enableRbacAuthorization` first; grant in the same model the vault is in. Mixing modes is the #1 misconfiguration.