"""Grounded generation with Vertex AI gemini. Citations [n] are required;
the prompt forbids answering outside the provided context.
"""
import re
import time

import requests

from . import config, embeddings as emb

PROMPT = """You are a customer-support knowledge assistant.
Answer the question using ONLY the numbered context excerpts below.
Cite every claim with [n] markers referencing the excerpt numbers.
Every answer that uses context MUST contain at least one [n] marker.
If the context does not contain the answer, reply exactly:
"I could not find this in the support docs." and nothing else.
Be concise (max ~120 words) and actionable.

Context:
{context}

Question: {question}

Answer:"""


class LLMError(RuntimeError):
    pass


def _call(prompt: str) -> tuple:
    """One LLM call with 429 backoff. Returns (text, wait_ms)."""
    import time as _time
    url = (f"https://{config.REGION}-aiplatform.googleapis.com/v1/projects/"
           f"{config.PROJECT}/locations/{config.REGION}/publishers/google/"
           f"models/{config.LLM_MODEL}:generateContent")
    payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
               "generationConfig": {"temperature": 0.1, "maxOutputTokens": 400}}
    waited = 0
    for attempt in range(6):
        r = requests.post(url, headers=emb.auth_header(), json=payload,
                          timeout=config.LLM_TIMEOUT_S)
        if r.status_code == 429:
            wait = int(r.headers.get("Retry-After", 20)) + attempt * 5
            print(f"[llm] 429 quota; backing off {wait}s (attempt {attempt + 1}/6)")
            _time.sleep(wait)
            waited += wait * 1000
            continue
        break
    if r.status_code != 200:
        raise LLMError(f"LLM API {r.status_code}: {r.text[:200]}")
    try:
        answer = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError) as e:
        raise LLMError(f"unexpected LLM response shape: {e}")
    return answer, waited


def generate(question: str, contexts: list) -> dict:
    """contexts: list of {title, header, text, score}.
    Returns {answer, cited, wait_ms}. Uncited answers get ONE enforcement retry
    (a grounded answer must cite its sources)."""
    ctx_lines = []
    for i, c in enumerate(contexts, 1):
        ctx_lines.append(f"[{i}] {c['title']} — {c['header']}\n{c['text']}")
    base_prompt = PROMPT.format(context="\n\n".join(ctx_lines), question=question)

    answer, wait_ms = _call(base_prompt)
    cited = bool(re.search(r"\[\d+\]", answer))
    if contexts and not cited and "could not find" not in answer.lower():
        retry_prompt = (base_prompt
                        + "\n\nREMINDER: your previous answer forgot the [n] citation "
                          "markers. Rewrite it, citing every claim with [n].")
        answer2, wait2 = _call(retry_prompt)
        if re.search(r"\[\d+\]", answer2):
            answer, cited = answer2, True
        wait_ms += wait2
    return {"answer": answer, "cited": cited, "wait_ms": wait_ms}
