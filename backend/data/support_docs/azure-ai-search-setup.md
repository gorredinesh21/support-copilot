# Azure AI Search vector index setup
## Overview
Azure AI Search (formerly Cognitive Search) supports vector and hybrid retrieval with semantic ranking.
## Steps
1. Create the service (Basic tier minimum for semantic ranker).
2. Create an index with a `Edm.Single` collection field `contentVector` with dimensions matching your embedding model (e.g. 768 for text-embedding-004, 1536 for ada-002).
3. Configure a vectorizer and a vector search algorithm (HNSW): `exhaustiveKnn` for small corpora.
4. Push documents with the REST SDK or indexers pulling from Blob Storage.
## Hybrid retrieval
Combine `searchText` plus `vectorQueries` and add `queryType=semantic` for reranking.
## Quotas
Basic tier: 15 indexes, 2 GB per index. Standard 1: 50 indexes.