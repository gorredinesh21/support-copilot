"""Configuration — env-driven, provider-agnostic knobs."""
import os

PROJECT = os.environ.get("GCP_PROJECT", "homatri-503308")
REGION = os.environ.get("GCP_REGION", "us-central1")
LLM_MODEL = os.environ.get("LLM_MODEL", "gemini-2.5-flash")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "text-embedding-004")
EMBED_DIM = int(os.environ.get("EMBED_DIM", "768"))

CORPUS_DIR = os.environ.get("CORPUS_DIR", os.path.join(os.path.dirname(__file__), "..", "data", "support_docs"))
INDEX_PATH = os.environ.get("INDEX_PATH", os.path.join(os.path.dirname(__file__), "..", "data", "index.json"))
CACHE_DIR = os.environ.get("CACHE_DIR", os.path.join(os.path.dirname(__file__), "..", "..", ".cache"))
TELEMETRY_DIR = os.environ.get("TELEMETRY_DIR", os.path.join(os.path.dirname(__file__), "..", "data", "telemetry"))

CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "900"))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", "120"))
DEFAULT_K = int(os.environ.get("DEFAULT_K", "4"))
LLM_TIMEOUT_S = float(os.environ.get("LLM_TIMEOUT_S", "30"))

# Search provider: "local" (default) or "azure_ai_search" (production swap; see retrieval.py)
SEARCH_PROVIDER = os.environ.get("SEARCH_PROVIDER", "local")
