# Deploying a web app to Azure App Service
## Overview
App Service is Azure's managed HTTP hosting platform. Deployment supports zip deploy, git push, GitHub Actions and containers.
## Steps
1. Create the App Service: `az webapp create -n myapp -p myplan -g myrg --runtime "PYTHON:3.12"`.
2. Package the app: `zip -r app.zip . -x .git/*`.
3. Deploy: `az webapp deployment zip-config -n myapp --src app.zip` or use `az webapp up`.
## Deployment slots
Use staging slots to validate before swap. Slot swap is near-instant and keeps the previous version for instant rollback.
## Troubleshooting
- **503 after deploy**: the container is still starting; check `az webapp log tail`.
- **App starts but crashes**: check startup command; for Python set `startupFile` or `appCmdLine` in config.
## Escalation
If deployments consistently fail with 409 conflicts, capture the deployment ID and escalate to the App Service on-call.