# Support Copilot

A customer-support knowledge assistant: a **React chat UI over a RAG pipeline** that answers
questions from a support-doc corpus with **grounded, cited answers** — plus
**App-Insights-compatible operational telemetry** queryable with **KQL (Kusto)**.

```
React (Vite) ──POST /api/chat──▶ FastAPI ──▶ embed question ──▶ Vertex text-embedding-004
                                       │
                                       ├─▶ VectorIndex.topK(4)  (Azure AI Search-ready interface)
                                       ├─▶ grounded LLM answer  ─▶ Vertex gemini-2.5-flash
                                       └─▶ telemetry (App-Insights-compatible JSONL)
                                                    │
                                              Kusto / ADX ──▶ KQL dashboard (success rate,
                                                              p50/p95 latency, no-answer rate)
```

## Features

- **Grounded answers with citations** — the prompt forbids answering outside retrieved
  context; every claim cites `[n]`; unknown questions return an explicit no-answer.
- **Header-aware markdown chunking** (900 chars / 120 overlap) — procedures stay whole.
- **Provider-agnostic by design** (see `DESIGN.md` decision table):
  - LLM: Vertex `gemini-2.5-flash` today → Azure OpenAI is one class swap
  - Embeddings: `text-embedding-004` today → same interface for Azure
  - Search: local vector index today → `AzureAISearchProvider` ships in `retrieval.py`
  - Telemetry: App-Insights-compatible JSONL today → Azure Monitor OTel exporter is config
- **Golden-set evaluation** — retrieval hit@3, citation rate, p95 latency; targets enforced
  by `pytest -m eval` (releases block on regressions).
- **KQL operational dashboard** — `kusto/dashboard.kql` runs unchanged against the local
  ADX/Kusto container or production App Insights.

## Live demo

**https://support-copilot-441384612427.us-central1.run.app** — hosted on Google Cloud Run
(project `personal-project-dg21`, scale-to-zero, single container serving the React SPA + API).
Ask it a support question; answers are grounded in the corpus with citations and live latency stats.

## Quickstart

```bash
# Backend (needs gcloud ADC: `gcloud auth application-default login` or an active account)
cd backend
pip install -r requirements.txt
python -m app.ingest          # build the vector index (embeds corpus, disk-cached)
uvicorn app.main:app --reload # http://localhost:8000  (GET /api/healthz)

# Frontend
cd frontend
npm install && npm run dev    # http://localhost:5173

# Optional: local Kusto engine for the KQL dashboard (~2GB RAM)
docker compose --profile kusto up
```

## Verification

```bash
cd backend
pytest -v              # unit + API tests (mocked providers — runs in CI, no cloud needed)
pytest -m eval -v -s   # golden-set eval against live GCP (hit@3, citation rate, latency)
curl -s localhost:8000/api/telemetry/summary   # same numbers as the KQL dashboard
```

## Repository layout

```
backend/
  app/            FastAPI service, chunking, embeddings (cached), LLM, retrieval, telemetry
  data/support_docs/   30-article support knowledge corpus (markdown)
  tests/          unit + API (mocked) + golden-set eval (network)
frontend/         React + Vite chat UI with citations and latency stats
kusto/            schema.kql + dashboard.kql (success rate, p95, no-answer rate, top docs)
DESIGN.md         the full engineering decision record (ADRs, architecture, rollout)
```

## Honest scope notes

- Telemetry is exported to an App-Insights-**compatible** JSONL file; pointing the same
  schema at a real App Insights resource (Azure Monitor OTel exporter) is a config change.
- The vector index is local (cosine) — sized for this corpus. `AzureAISearchProvider`
  implements the same interface for production Azure AI Search.
- The LLM/embeddings run on Google Vertex AI with this repo's available credentials;
  Azure OpenAI equivalents are drop-in via the documented interfaces.

## License

MIT
