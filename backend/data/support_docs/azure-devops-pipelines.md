# Azure DevOps pipelines
## Structure
`azure-pipelines.yml`: trigger, pool, stages/jobs/steps. Agents: Microsoft-hosted (free tier limits) or self-hosted.
## Common tasks
- `UsePythonVersion@0` to pin toolchain.
- `PublishTestResults@2` with pytest junit output.
- `PublishBuildArtifacts@1` for deployable bundles.
## Practices
Fail fast on lint; cache pip/npm directories by lockfile hash; protect the main branch with a required PR build.
## Parallelism
Free tier: 1,800 minutes/month, 1 parallel job. Self-hosted agents are unlimited.