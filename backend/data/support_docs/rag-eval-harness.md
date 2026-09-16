# Golden-set evaluation
## What runs
`pytest -m eval` (network required). For each golden question:
1. Embed and retrieve top-3; hit if the expected doc is among them.
2. Generate the answer; citation rate counts answers containing [n] markers.
3. Record latency.
## Targets (v1)
- Retrieval hit@3 >= 0.8
- Citation rate >= 0.9
- p95 latency < 6000 ms
## Adding questions
Append to eval/golden.json with the expected doc id; questions must come from real user asks, not invented ones, to avoid overfitting.