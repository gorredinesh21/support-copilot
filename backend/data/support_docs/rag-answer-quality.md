# RAG quality playbook
## Levers, in order of impact
1. **Chunking**: header-aware 800-1200 char chunks with 100-150 overlap; keep procedures whole.
2. **Retrieval k**: start at 4; measure hit@k on a golden set before tuning.
3. **Prompt**: answer only from context; require [n] citations; explicit no-answer fallback sentence.
4. **Reranking**: cross-encoder rerank of top-20 to top-4 helps at moderate latency cost.
## Measurement
Golden set of >= 15 real questions; track hit@3, citation rate, no-answer correctness. Regressions block release.