"""API contract tests with mocked LLM/embeddings (no network)."""
import os
import sys
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import main  # noqa: E402
from app.retrieval import LocalVectorIndex  # noqa: E402

FAKE_INDEX = LocalVectorIndex.__new__(LocalVectorIndex)
FAKE_INDEX.chunks = [{"title": "Deploying a web app to Azure App Service",
                      "source": "data/support_docs/azure-app-service-deploy.md",
                      "header": "Steps", "text": "az webapp create..."}]
FAKE_INDEX.vecs = [[1.0, 0.0]]


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "_INDEX", FAKE_INDEX)
    with TestClient(main.app) as c:
        yield c


def test_healthz(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok" and body["index_chunks"] == 1


def test_search_contract(client):
    with mock.patch("app.main.embeddings.embed_one", return_value=[1.0, 0.0]):
        r = client.post("/api/search", json={"question": "how to deploy app service"})
    assert r.status_code == 200
    body = r.json()
    assert body["results"][0]["title"].startswith("Deploying")
    assert "operation_Id" in body


def test_chat_happy_path(client):
    with mock.patch("app.main.embeddings.embed_one", return_value=[1.0, 0.0]), \
         mock.patch("app.main.llm.generate",
                    return_value={"answer": "Run az webapp up [1].", "cited": True}):
        r = client.post("/api/chat", json={"question": "how to deploy app service"})
    assert r.status_code == 200
    body = r.json()
    assert body["answer"].startswith("Run az webapp up")
    assert body["citations"][0]["title"].startswith("Deploying")
    assert body["latency_ms"] >= 0 and "operation_Id" in body


def test_chat_llm_failure_records_telemetry(client, tmp_path):
    monkey_tel = tmp_path / "tel.jsonl"
    with mock.patch("app.main.embeddings.embed_one", return_value=[1.0, 0.0]), \
         mock.patch("app.main.llm.generate",
                    side_effect=RuntimeError("LLM API 500: quota")), \
         mock.patch("app.telemetry._default_path", return_value=str(monkey_tel)):
        r = client.post("/api/chat", json={"question": "how to deploy app service"})
    assert r.status_code == 500
    lines = monkey_tel.read_text().strip().splitlines()
    assert lines and '"success": false' in lines[-1]


def test_validation_rejects_short_questions(client):
    r = client.post("/api/chat", json={"question": "hi"})
    assert r.status_code == 422
