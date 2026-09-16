# Local Kusto (Azure Data Explorer container)
## Run
`docker run -e ACCEPT_EULA=Y -m 2G -p 8080:8080 mcr.microsoft.com/azuredataexplorer/kustainer-linux:latest`
Connect at `http://localhost:8080` with any client (Kusto.Cli, Kusto.Explorer, or the Python `azure-kusto-data` SDK); no auth by default locally.
## Ingest files
`.ingest inline into table <| <csv rows>` for small sets; use `.create table` first.
## When local vs cloud
Local container for demos/CI; production telemetry goes to a real ADX cluster or App Insights with the same KQL.