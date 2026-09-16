"""Support Copilot API — FastAPI service."""
import time
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import config, embeddings, llm, retrieval, telemetry

app = FastAPI(title="Support Copilot", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
                   allow_headers=["*"])


class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    k: int = Field(default=config.DEFAULT_K, ge=1, le=10)


class SearchRequest(ChatRequest):
    pass


def _index():
    global _INDEX
    if _INDEX is None:
        _INDEX = retrieval.get_provider()
    return _INDEX


_INDEX = None


@app.get("/api/healthz")
def healthz():
    try:
        n = len(_index().chunks)
    except Exception:
        n = 0
    return {"status": "ok", "index_chunks": n,
            "model": config.LLM_MODEL, "embed_model": config.EMBED_MODEL}


@app.post("/api/search")
def search(req: SearchRequest):
    op = str(uuid.uuid4())
    t0 = time.time()
    try:
        vec = embeddings.embed_one(req.question)
        hits = _index().topk(vec, req.k)
        telemetry.record("search", operation_id=op, success=True,
                         duration_ms=int((time.time() - t0) * 1000),
                         custom={"k": req.k, "top_doc": hits[0]["title"] if hits else None})
        return {"operation_Id": op, "results": hits}
    except Exception as e:
        telemetry.record("search", operation_id=op, success=False,
                         duration_ms=int((time.time() - t0) * 1000),
                         result_code=500, custom={"error": str(e)[:200]})
        raise HTTPException(status_code=500, detail=str(e)[:200])


@app.post("/api/chat")
def chat(req: ChatRequest):
    op = str(uuid.uuid4())
    t0 = time.time()
    try:
        vec = embeddings.embed_one(req.question)
        hits = _index().topk(vec, req.k)
        if not hits:
            answer, cited = "I could not find this in the support docs.", False
        else:
            gen = llm.generate(req.question, hits)
            answer, cited = gen["answer"], gen["cited"]
        latency = int((time.time() - t0) * 1000)
        telemetry.record("chat", operation_id=op, success=True,
                         duration_ms=latency, result_code=200,
                         custom={"k": req.k, "model": config.LLM_MODEL,
                                 "cited": cited, "question_len": len(req.question),
                                 "top_doc": hits[0]["title"] if hits else None})
        citations = [{"n": i + 1, "title": h["title"], "header": h["header"],
                      "source": h["source"], "score": h["score"]}
                     for i, h in enumerate(hits)]
        return {"answer": answer, "citations": citations,
                "latency_ms": latency, "operation_Id": op,
                "model": config.LLM_MODEL}
    except Exception as e:
        telemetry.record("chat", operation_id=op, success=False,
                         duration_ms=int((time.time() - t0) * 1000),
                         result_code=500, custom={"error": str(e)[:200]})
        raise HTTPException(status_code=500, detail=str(e)[:200])


@app.get("/api/telemetry/summary")
def telemetry_summary():
    return telemetry.summary()


# Serve the built SPA (frontend/dist copied into the image) on the same origin.
import os as _os
from fastapi.staticfiles import StaticFiles as _StaticFiles

# Container layout: /app/app/main.py with SPA at /app/static (../static).
# Repo layout: backend/app/main.py with SPA at repo root ../.. (dev only).
for _cand in ("../static", "../../static"):
    _p = _os.path.normpath(_os.path.join(_os.path.dirname(__file__), _cand))
    if _os.path.isdir(_p):
        app.mount("/", _StaticFiles(directory=_p, html=True), name="spa")
        break
