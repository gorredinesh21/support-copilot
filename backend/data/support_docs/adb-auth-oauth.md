# OAuth for external analytics apps
## Pattern
Front-end acquires a token (auth code + PKCE) for the API's scope; API validates audience and issuer.
## Steps
1. Register the app in the identity provider; add redirect URI; expose an API scope.
2. Front-end: MSAL or oidc-client with PKCE — never client secrets in the browser.
3. API: validate-signature via JWKS, check `aud` and `iss`, map claims to roles.
## Common failure
`invalid audience` — the token was minted for a different scope/API. Fix the requested scope, not the API.