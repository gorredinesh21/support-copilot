# Semantic ranker
## What it does
The semantic ranker reranks the top-50 BM25 or vector results using Microsoft's transformer models, improving top-1 relevance.
## How to enable
Set `queryType=semantic`, provide `semanticConfiguration` naming title/content/description priority fields.
## Semantic answers
With `answers=extractive`, the service extracts a short verbatim answer plus highlights. Requires the answer to exist literally in the documents.
## Cost note
Semantic ranker is billed per 1000 queries on Basic+; free tier has a small daily allowance.