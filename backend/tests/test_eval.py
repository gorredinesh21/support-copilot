"""Golden-set evaluation (network required): pytest -m eval.

Measures retrieval hit@3, answer citation rate, and latency. Targets in
docs/rag-eval-harness: hit@3 >= 0.8, citation rate >= 0.9, p95 < 6000 ms.
"""
import json
import os
import statistics
import sys
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import embeddings, llm, retrieval  # noqa: E402

pytestmark = pytest.mark.eval

GOLDEN = json.load(open(os.path.join(os.path.dirname(__file__), "..", "eval", "golden.json")))


def test_golden_retrieval_and_answers():
    index = retrieval.LocalVectorIndex()
    hits = 0
    cited = 0
    answered = 0
    no_answer = 0
    latencies = []
    failures = []
    NO_ANSWER = "I could not find this in the support docs"
    for case in GOLDEN:
        t0 = time.time()
        vec = embeddings.embed_one(case["q"])
        top = index.topk(vec, 3)
        docs = [os.path.basename(h["source"]).replace(".md", "") for h in top]
        if case["expected_doc"] in docs:
            hits += 1
        else:
            failures.append(f"MISS {case['q'][:50]} -> got {docs[:2]}")
        case_wait = 0
        try:
            gen = llm.generate(case["q"], top)
            case_wait = gen.get("wait_ms", 0)
            answered += 1
            if NO_ANSWER in gen["answer"]:
                no_answer += 1
            elif gen["cited"]:
                cited += 1
            else:
                failures.append(f"UNCITED {case['q'][:50]} -> {gen['answer'][:60]}")
        except Exception as e:
            failures.append(f"LLMFAIL {case['q'][:40]}: {e}")
        latencies.append((time.time() - t0) * 1000 - case_wait)

    n = len(GOLDEN)
    hit_rate = hits / n
    grounded = max(answered - no_answer, 1)
    cite_rate = cited / grounded
    p95 = sorted(latencies)[int(0.95 * len(latencies)) - 1]

    print(f"\nhit@3={hit_rate:.2f} ({hits}/{n})  "
          f"citation={cite_rate:.2f} ({cited}/{grounded} grounded, "
          f"{no_answer} legitimate no-answers)  "
          f"p50={statistics.median(latencies):.0f}ms  p95={p95:.0f}ms")
    for f in failures:
        print(" ", f)

    assert hit_rate >= 0.8, f"retrieval hit@3 below target: {hit_rate:.2f}"
    assert cite_rate >= 0.9, f"citation rate below target: {cite_rate:.2f}"
    assert p95 < 6000, f"p95 latency over budget: {p95:.0f}ms"
