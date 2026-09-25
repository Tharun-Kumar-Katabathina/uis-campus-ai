_TOKENS_PER_WORD = 1.3  # rough BPE-style heuristic; avoids a real tokenizer
# dependency (and the network access some of them need) for Module 1.
# Module 2 can swap in the actual embedding model's tokenizer if the
# resulting chunk sizes need to be more exact.


def approx_tokens(text: str) -> int:
    return round(len(text.split()) * _TOKENS_PER_WORD)


def chunk_text(
    text: str,
    target_min_tokens: int = 300,
    target_max_tokens: int = 700,
    overlap_tokens: int = 50,
) -> list[str]:
    """Structure-aware chunking: walks the cleaned text line by line (each
    line already one heading/paragraph/list item — see extractors), and
    groups lines into chunks within [target_min_tokens, target_max_tokens],
    carrying the last `overlap_tokens` worth of lines into the next chunk
    for continuity (roadmap §20)."""
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []

    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0

    for line in lines:
        line_tokens = approx_tokens(line)
        if (
            current
            and current_tokens >= target_min_tokens
            and (current_tokens + line_tokens > target_max_tokens)
        ):
            chunks.append("\n".join(current))
            current, current_tokens = _overlap_tail(current, overlap_tokens)
        current.append(line)
        current_tokens += line_tokens

    if current:
        chunks.append("\n".join(current))

    return chunks


def _overlap_tail(lines: list[str], overlap_tokens: int) -> tuple[list[str], int]:
    tail: list[str] = []
    tail_tokens = 0
    for line in reversed(lines):
        line_tokens = approx_tokens(line)
        if tail_tokens + line_tokens > overlap_tokens:
            break
        tail.insert(0, line)
        tail_tokens += line_tokens
    return tail, tail_tokens
