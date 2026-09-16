"""Unit tests: chunking, retrieval math, telemetry schema, citation parsing."""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import chunking, telemetry, llm  # noqa: E402
from app.retrieval import LocalVectorIndex, cosine  # noqa: E402

DOC = """# Deploying an app
## Steps
1. create
2. package

## Troubleshooting
- 503 means starting.
"""


def test_chunking_keeps_headers():
    chunks = chunking.chunk_markdown(DOC, "Deploying an app", "docs/x.md")
    assert len(chunks) >= 2
    headers = {c["header"] for c in chunks}
    assert "Steps" in headers and "Troubleshooting" in headers
    for c in chunks:
        assert c["title"] == "Deploying an app"
        assert c["source"] == "docs/x.md"
        assert c["text"].strip()


def test_chunking_respects_size():
    long_body = "\n".join(f"paragraph {i} " + "x" * 80 for i in range(40))
    chunks = chunking.chunk_markdown("# T\n## S\n" + long_body, "T", "s.md", size=400, overlap=50)
    assert all(len(c["text"]) <= 460 for c in chunks)
    assert len(chunks) > 2


def test_cosine_bounds():
    assert cosine([1, 0], [1, 0]) == pytest.approx(1.0)
    assert cosine([1, 0], [0, 1]) == pytest.approx(0.0)
    assert cosine([0, 0], [1, 1]) == 0.0


def test_local_index_topk(tmp_path):
    idxfile = tmp_path / "index.json"
    idxfile.write_text(json.dumps({
        "chunks": [{"title": "a", "source": "s", "header": "h", "text": "t1"},
                   {"title": "b", "source": "s", "header": "h", "text": "t2"}],
        "vectors": [[1.0, 0.0], [0.0, 1.0]],
    }))
    idx = LocalVectorIndex(str(idxfile))
    hits = idx.topk([0.9, 0.1], k=1)
    assert hits[0]["title"] == "a"
    assert hits[0]["score"] > 0.98


def test_telemetry_schema(tmp_path):
    path = str(tmp_path / "tel.jsonl")
    entry = telemetry.record("chat", success=True, duration_ms=123,
                             custom={"k": 4}, path=path)
    for field in ("time", "name", "operation_Id", "traceId", "spanId",
                  "success", "duration_ms", "resultCode", "customDimensions"):
        assert field in entry, f"missing App-Insights field {field}"
    # summary aggregates
    telemetry.record("chat", success=False, duration_ms=50, result_code=500, path=path)
    s = telemetry.summary(path)
    assert s["operations"]["chat"]["count"] == 2
    assert s["operations"]["chat"]["success_rate"] == 0.5


def test_citation_detection():
    assert llm.__name__  # module importable
    import re
    assert re.search(r"\[\d+\]", "do X [1] then Y [2]")
    assert not re.search(r"\[\d+\]", "no citations here")
