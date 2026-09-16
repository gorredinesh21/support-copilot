"""Vertex AI embedding client with a disk cache (keys: sha1(text)).

Provider-agnostic: implement `EmbeddingProvider` and swap in main.py for
Azure OpenAI embeddings in production.
"""
import hashlib
import json
import os
import subprocess
import time

import requests

from . import config


class EmbeddingError(RuntimeError):
    pass


def _token() -> str:
    # On GCP (Cloud Run/GCE): use the metadata server of the attached service account.
    try:
        r = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token",
            headers={"Metadata-Flavor": "Google"}, timeout=3)
        if r.status_code == 200:
            return r.json()["access_token"]
    except requests.RequestException:
        pass
    # Local development: fall back to the gcloud CLI.
    out = subprocess.run(["gcloud", "auth", "print-access-token"],
                         capture_output=True, text=True, timeout=30)
    if out.returncode != 0:
        raise EmbeddingError(f"gcloud auth failed: {out.stderr[:200]}")
    return out.stdout.strip()


_token_cache = {"tok": None, "exp": 0}


def auth_header() -> dict:
    now = time.time()
    if _token_cache["tok"] is None or now > _token_cache["exp"]:
        _token_cache["tok"] = _token()
        _token_cache["exp"] = now + 45 * 60  # refresh well before expiry
    return {"Authorization": f"Bearer {_token_cache['tok']}"}


class Cache:
    def __init__(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.path = path
        self.data = {}
        if os.path.exists(path):
            with open(path) as f:
                self.data = json.load(f)

    def get(self, key):
        return self.data.get(key)

    def put(self, key, vec):
        self.data[key] = vec
        with open(self.path, "w") as f:
            json.dump(self.data, f)


_cache = None


def _cachefile():
    global _cache
    if _cache is None:
        _cache = Cache(os.path.join(config.CACHE_DIR, "embeddings.json"))
    return _cache


def _key(text: str) -> str:
    return hashlib.sha1(f"{config.EMBED_MODEL}|{text}".encode()).hexdigest()


def embed(texts: list, batch_size: int = 5) -> list:
    """Embed a list of texts; returns list of float lists. Cached per text."""
    results, missing, keys = [None] * len(texts), [], []
    cf = _cachefile()
    for i, t in enumerate(texts):
        k = _key(t)
        cached = cf.get(k)
        if cached is not None:
            results[i] = cached
        else:
            missing.append(t)
            keys.append((i, k))
    # batch the misses (retry on 429 quota with backoff, honoring Retry-After)
    for start in range(0, len(missing), batch_size):
        batch = missing[start:start + batch_size]
        url = (f"https://{config.REGION}-aiplatform.googleapis.com/v1/projects/"
               f"{config.PROJECT}/locations/{config.REGION}/publishers/google/"
               f"models/{config.EMBED_MODEL}:predict")
        payload = {"instances": [{"content": t} for t in batch],
                   "parameters": {"outputDimensionality": config.EMBED_DIM}}
        for attempt in range(6):
            r = requests.post(url, headers=auth_header(), json=payload, timeout=60)
            if r.status_code == 429:
                wait = int(r.headers.get("Retry-After", 25)) + attempt * 5
                print(f"[embeddings] 429 quota; backing off {wait}s "
                      f"(attempt {attempt + 1}/6, batch at {start})")
                time.sleep(wait)
                continue
            break
        if r.status_code != 200:
            raise EmbeddingError(f"embedding API {r.status_code}: {r.text[:200]}")
        preds = r.json().get("predictions", [])
        if len(preds) != len(batch):
            raise EmbeddingError(f"expected {len(batch)} embeddings, got {len(preds)}")
        for offset, p in enumerate(preds):
            vec = p["embeddings"]["values"]
            idx, k = keys[start + offset]
            results[idx] = vec
            cf.put(k, vec)
    return results


def embed_one(text: str) -> list:
    return embed([text])[0]
