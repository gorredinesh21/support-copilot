# Responsible AI checklist
## Before launch
1. **Grounding**: answers restricted to retrieved context; no free-form hallucination path.
2. **Citations**: every answer links its sources; a no-answer fallback exists.
3. **Human oversight**: users can report a wrong answer in one click; reports feed the eval set.
4. **Privacy**: prompts/logs scrubbed of customer identifiers; retention <= 30 days by default.
5. **Bias/fairness**: eval set covers diverse phrasings; measure answer quality across them.
6. **Transparency**: UI states that answers are AI-generated.
## At review time
Attach eval run results (hit rate, citation rate) to the release PR.