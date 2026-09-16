"""Retrieval: provider interface + local vector index (default).
Production swap: AzureAISearchProvider (Azure AI Search) — same interface,
selected via SEARCH_PROVIDER env; see DESIGN.md D5.
"""
import json
import math
import os

from . import config


class SearchProvider:
    def topk(self, question_vec: list, k: int) -> list:
        raise NotImplementedError


def cosine(a, b) -> float:
    num = sum(x * y for x, y in zip(a, b))
    da = math.sqrt(sum(x * x for x in a))
    db = math.sqrt(sum(x * x for x in b))
    return num / (da * db) if da and db else 0.0


class LocalVectorIndex(SearchProvider):
    """Chunks + embeddings loaded from index.json (built by app.ingest)."""

    def __init__(self, index_path=None):
        path = index_path or config.INDEX_PATH
        if not os.path.exists(path):
            raise FileNotFoundError(f"index not found at {path}; run `python -m app.ingest`")
        with open(path) as f:
            data = json.load(f)
        self.chunks = data["chunks"]
        self.vecs = data["vectors"]

    def topk(self, question_vec: list, k: int) -> list:
        scored = [(cosine(question_vec, v), c) for v, c in zip(self.vecs, self.chunks)]
        scored.sort(key=lambda x: -x[0])
        out = []
        for score, c in scored[:k]:
            d = dict(c)
            d["score"] = round(score, 4)
            out.append(d)
        return out


class AzureAISearchProvider(SearchProvider):
    """Production adapter (requires Azure AI Search service).

    Implements the same topk() contract against an Azure AI Search index with
    vector search enabled. Not used by default; wire in via SEARCH_PROVIDER
    once an Azure resource exists. Kept here so the swap is code-free.
    """

    def __init__(self, endpoint=None, index_name="support-docs", api_key=None):
        self.endpoint = endpoint or os.environ.get("AZSEARCH_ENDPOINT")
        self.index_name = index_name
        self.api_key = api_key or os.environ.get("AZSEARCH_API_KEY")

    def topk(self, question_vec: list, k: int) -> list:
        import requests  # local import: only needed on the Azure path
        url = f"{self.endpoint}/indexes('{self.index_name}')/docs/search.post.search"
        body = {"vectorQueries": [
            {"vector": question_vec, "k": k, "fields": "contentVector"}]}
        r = requests.post(url, headers={"api-key": self.api_key,
                                        "Content-Type": "application/json"},
                          json=body, timeout=20)
        r.raise_for_status()
        return [{"title": d.get("title"), "source": d.get("source"),
                 "header": d.get("header"), "text": d.get("content"),
                 "score": d.get("@search.score", 0)} for d in r.json()["value"]]


def get_provider() -> SearchProvider:
    if config.SEARCH_PROVIDER == "azure_ai_search":
        return AzureAISearchProvider()
    return LocalVectorIndex()
