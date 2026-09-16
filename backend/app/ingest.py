"""Offline ingestion: corpus -> chunks -> embeddings -> data/index.json."""
import hashlib
import json

from . import config, corpus, chunking, embeddings, telemetry


def build_index() -> dict:
    docs = corpus.load_corpus()
    chunks = []
    for d in docs:
        chunks.extend(chunking.chunk_markdown(d["text"], d["title"], d["source"]))
    texts = [f"{c['title']} | {c['header']}\n{c['text']}" for c in chunks]
    vectors = embeddings.embed(texts)
    corpus_hash = hashlib.sha1(
        "".join(sorted(d["text"] for d in docs)).encode()).hexdigest()[:12]
    index = {"corpus_hash": corpus_hash, "model": config.EMBED_MODEL,
             "dim": config.EMBED_DIM, "chunks": chunks, "vectors": vectors}
    with open(config.INDEX_PATH, "w") as f:
        json.dump(index, f)
    return {"docs": len(docs), "chunks": len(chunks), "corpus_hash": corpus_hash}


if __name__ == "__main__":
    import time
    t0 = time.time()
    stats = build_index()
    stats["duration_ms"] = int((time.time() - t0) * 1000)
    telemetry.record("ingest", success=True, duration_ms=stats["duration_ms"],
                     custom={"chunks": stats["chunks"], "docs": stats["docs"]})
    print("index built:", stats)
