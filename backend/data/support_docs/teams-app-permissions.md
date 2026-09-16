# Teams app permissions
## Delegated vs application
Delegated scopes act as the signed-in user; application permissions act as the app alone and need admin consent.
## Minimum-scope rule
Request only the scopes used; `Sites.Read.All` beats `Sites.FullControl.All` for reading.
## Consent errors
`AADSTS65001` — user/admin has not granted consent: admin consent link must be used for application permissions. `invalid_grant` usually means expired secret or redirect URI mismatch.