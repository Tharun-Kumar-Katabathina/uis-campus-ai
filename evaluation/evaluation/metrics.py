"""Retrieval metrics (roadmap §37), computed over
list[(retrieved_document_ids_in_rank_order, expected_document_id)] pairs.
Pure functions — no I/O, easy to unit test in isolation from retrieval."""


def recall_at_k(results: list[tuple[list[str], str]]) -> float:
    if not results:
        return 0.0
    hits = sum(1 for retrieved, expected in results if expected in retrieved)
    return hits / len(results)


def precision_at_k(results: list[tuple[list[str], str]], k: int) -> float:
    """Mean fraction of each result's top-k that is the expected doc —
    with a single expected doc per query this is 1/k on a hit, else 0."""
    if not results:
        return 0.0
    scores = []
    for retrieved, expected in results:
        top_k = retrieved[:k]
        relevant = sum(1 for doc_id in top_k if doc_id == expected)
        scores.append(relevant / max(len(top_k), 1))
    return sum(scores) / len(scores)


def mean_reciprocal_rank(results: list[tuple[list[str], str]]) -> float:
    if not results:
        return 0.0
    reciprocal_ranks = []
    for retrieved, expected in results:
        if expected in retrieved:
            reciprocal_ranks.append(1.0 / (retrieved.index(expected) + 1))
        else:
            reciprocal_ranks.append(0.0)
    return sum(reciprocal_ranks) / len(reciprocal_ranks)


def hit_rate(results: list[tuple[list[str], str]]) -> float:
    """Fraction of queries where retrieval found at least one result at
    all (roadmap §37) — distinct from recall, which requires the
    *correct* document; this only asks whether retrieval returned
    anything."""
    if not results:
        return 0.0
    hits = sum(1 for retrieved, _ in results if retrieved)
    return hits / len(results)
