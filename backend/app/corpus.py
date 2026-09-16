"""Corpus loader: markdown files under data/support_docs."""
import os

from . import config


def load_corpus(corpus_dir=None) -> list:
    """Returns [{title, source, text}] for every .md file in the corpus dir."""
    d = corpus_dir or config.CORPUS_DIR
    docs = []
    for fname in sorted(os.listdir(d)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(d, fname)
        with open(path) as f:
            text = f.read()
        title = _first_header(text) or fname[:-3]
        docs.append({"title": title, "source": f"data/support_docs/{fname}",
                     "text": text})
    return docs


def _first_header(text: str):
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None
