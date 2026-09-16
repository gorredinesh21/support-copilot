# Support Copilot — Design & Build Plan

**Author:** Senior Engineer (owner of this service)
**Status:** Implemented (v1) · Date: 2026-09-16
**Input from management:** *"Build a support copilot: a chat front-end over a RAG pipeline that answers questions from our support-doc corpus, with telemetry feeding an operational dashboard showing query success and latency."*

Everything below is my decision — stack, structure, contracts, testing, and rollout.

---

## 1. Problem & Goals

Customer-support engineers spend a large fraction of their day re-reading the same internal
documentation. The copilot gives them grounded, cited answers in seconds and produces the
operational telemetry (success rate, latency, failure modes) a product owner needs to trust it.

**Goals**
1. Grounded Q&A over a markdown support-doc corpus — every answer must cite its sources.
2. Measurable quality: retrieval hit-rate and answer-citation rate tracked by an eval harness.
3. Operational telemetry in an **App-Insights-compatible schema**, queryable with **KQL (Kusto)**.
4. Provider-agnostic by design: swap LLM/embeddings/search/telemetry sink via config, not code.

**Non-goals (v1):** multi-tenant auth, streaming responses, ticket-system integration,
fine-tuning, write access to docs.

## 2. Key Decisions (ADR summary)

| # | Decision | Choice | Rationale | Swap path (production) |
|---|---|---|---|---|
| D1 | Backend | **Python + FastAPI** | Async, typed, OpenAPI out of the box; strongest RAG ecosystem | — |
| D2 | Frontend | **React + Vite** | JD/industry-standard SPA; tiny footprint; fast builds | — |
| D3 | LLM | **Vertex AI `gemini-2.5-flash`** | Credentials available on this machine (ADC); fast, cheap, grounded-prompt friendly | One class: `AzureOpenAIGenerator` (same interface) — documented |
| D4 | Embeddings | **Vertex AI `text-embedding-004` (768d)** | Same credential path; strong retrieval quality; disk-cached | Same interface; `AzureOpenAIEmbedder` |
| D5 | Vector search | **Local `VectorIndex` (cosine)** | Corpus is small (~30 docs, ~120 chunks); zero infra; deterministic tests | `SearchProvider` interface ships with an **Azure AI Search** provider stub — swap by config |
| D6 | Chunking | **Header-aware markdown splitter**, 900 chars, 120 overlap | Keeps procedure steps together; proven heuristic for support docs | — |
| D7 | Telemetry | **App-Insights-compatible JSONL exporter** (`operation_Id`, `traceId`, `success`, `duration_ms`, `customDimensions`) | Real OTel/Azure Monitor exporters need an Azure resource; schema compatibility means the production exporter is a config change, and the KQL dashboard works unchanged today | `OTLPExporter → Azure Monitor App Insights` |
| D8 | Dashboard | **Kusto container (Azure Data Explorer) + KQL** | KQL is the target skill; ADX container is the real engine locally | Point connection string at production ADX cluster |
| D9 | Eval | **Golden-set harness (15 Qs)**: retrieval hit@3 + citation rate + latency | "If you didn't measure it, it doesn't work"; runs in CI minus network tests | — |
| D10 | CI | **GitHub Actions**: unit+API tests, frontend build | Modern engineering practice baseline | — |

## 3. Architecture

```
┌──────────────┐   POST /api/chat {question}   ┌───────────────────────────────┐
│  React SPA   │ ─────────────────────────────▶│  FastAPI backend              │
│  (Vite)      │◀──── answer + citations +     │                               │
│              │      latency + opId           │  1. embed(question)  ────────▶ Vertex text-embedding-004
└──────────────┘                               │  2. VectorIndex.topK(k=4)     │
                                               │  3. grounded prompt            │
   GET /healthz  (UI health dot)               │  4. LLM answer + citations ──▶ Vertex gemini-2.5-flash
                                               │  5. telemetry record ────────▶ app_insights_compat.jsonl
                                               └───────────────────────────────┘
                                                        │ (ingest)
                                                        ▼
                                               ┌───────────────────────────────┐
                                               │  Kusto (ADX container)        │
                                               │  KQL dashboard: success rate, │
                                               │  p50/p95 latency, failures,   │
                                               │  top questions                │
                                               └───────────────────────────────┘
   Ingestion (offline): data/support_docs/*.md → chunk → embed (cached) → index.json
```

## 4. API Contract

- `GET /healthz` → `{status:"ok", index_chunks, model}` — liveness + readiness in one.
- `POST /api/chat` `{question, k?}` → `{answer, citations:[{title, source, score}], latency_ms, operation_Id, model}` — 200 on success; 500 (with telemetry `success=false`) on LLM failure.
- `POST /api/search` `{question, k?}` → retrieval only (debug/eval).
- `GET /api/telemetry/summary` → aggregates over the local JSONL (success rate, p50/p95, counts).

## 5. Telemetry Schema (App-Insights-compatible)

| Field | Type | Notes |
|---|---|---|
| `time` | ISO-8601 | UTC |
| `name` | string | `chat`, `search`, `ingest`, `llm`, `embed` |
| `operation_Id` | uuid | ties a request's spans together |
| `traceId`/`spanId` | hex | W3C-style ids |
| `success` | bool | business outcome |
| `duration_ms` | int | wall clock |
| `resultCode` | int | 200/4xx/5xx |
| `customDimensions` | object | `k`, `top_doc`, `model`, `question_len`, `cited` |

KQL dashboard (`kusto/dashboard.kql`): success rate trend, p50/p95 latency per operation,
failure breakdown, top questions by count, no-answer rate.

## 6. Testing Strategy

1. **Unit** (no network): chunker boundaries; telemetry schema; cosine math; citation parsing.
2. **API** (mocked LLM/embeddings via DI): contract, error path (LLM 500 → telemetry `success=false`).
3. **Eval** (network, `pytest -m eval`, excluded from CI): 15 golden questions →
   retrieval hit@3 ≥ 0.8 target, citation rate ≥ 0.9 target, p95 latency budget < 6s.
4. **E2E manual**: `uvicorn` + real GCP call + Kusto ingestion + dashboard queries.

## 7. Rollout Plan (what a 2–3 week schedule looks like)

- **Week 1 — Core:** corpus, chunker, embeddings client (cached), vector index, /api/search, unit tests. *(shipped)*
- **Week 2 — Copilot & UI:** grounded prompt + citations, /api/chat, React chat UI, API tests. *(shipped)*
- **Week 3 — Ops & quality:** telemetry schema, Kusto container + KQL dashboard, eval harness, CI, docs. *(shipped)*

Production Azure deployment path (documented, not deployed): App Service (backend),
Static Web Apps (frontend), Azure AI Search (swap D5), Azure OpenAI (swap D3/D4),
App Insights via Azure Monitor exporter (swap D7), ADX cluster (D8 connection string).

## 8. Risks & Mitigations

- **Vertex quota/latency spikes** → embedding disk-cache + request timeout + graceful 500 with telemetry (observed, not swallowed).
- **Hallucination** → grounded-only prompt: "answer only from context; cite [n]; if not present, say you don't know"; citation rate tracked in eval.
- **Corpus drift** → ingestion is a single command (`python -m app.ingest`); index versioned with corpus hash.
- **Laptop resource limits** → Kusto container optional (docker-compose profile); everything else runs without Docker.
