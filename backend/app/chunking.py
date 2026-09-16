"""Header-aware markdown chunking: keeps sections/procedures together."""
from . import config


def chunk_markdown(text: str, title: str, source: str,
                   size: int = None, overlap: int = None) -> list:
    """Split markdown into overlapping chunks at header boundaries.

    Strategy: split into sections on lines starting with '#'. Sections longer
    than `size` are further split on paragraph boundaries with `overlap`.
    """
    size = size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP
    chunks = []
    lines = text.splitlines()
    section, header = [], title

    def flush():
        nonlocal section, header
        body = "\n".join(section).strip()
        if body:
            for piece in _split_body(body, size, overlap):
                chunks.append({"title": title, "source": source,
                               "header": header, "text": piece})
        section = []

    for line in lines:
        if line.startswith("#"):
            flush()
            header = line.lstrip("# ").strip() or title
        section.append(line)
    flush()
    return chunks


def _split_body(body: str, size: int, overlap: int) -> list:
    if len(body) <= size:
        return [body]
    pieces, start = [], 0
    while start < len(body):
        end = min(start + size, len(body))
        # prefer breaking at a paragraph/line boundary near the end
        if end < len(body):
            cut = max(body.rfind("\n\n", start, end), body.rfind("\n", start, end))
            if cut > start + size // 2:
                end = cut
        pieces.append(body[start:end].strip())
        if end >= len(body):
            break
        start = max(end - overlap, start + 1)
    return [p for p in pieces if p]
