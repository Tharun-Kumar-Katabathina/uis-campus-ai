from app.retrieval.reranker import rerank
from app.retrieval.vector_search import SearchResult


def _result(chunk_id: str, title: str, score: float) -> SearchResult:
    return SearchResult(
        score=score,
        chunk_id=chunk_id,
        document_id=chunk_id,
        title=title,
        content="content",
        url="https://example.edu",
        source="Test",
        department="Test",
        document_type="test",
        access_level="public",
        version="1.0",
    )


def test_rerank_boosts_title_match_above_higher_raw_score():
    # doc_b starts with a slightly higher fused score, but doc_a's title
    # matches every query word — the boost should flip the order.
    doc_a = _result("doc_a", "Library Hours", score=0.010)
    doc_b = _result("doc_b", "Graduation Application", score=0.011)

    reranked = rerank("library hours", [doc_a, doc_b])

    assert [r.chunk_id for r in reranked] == ["doc_a", "doc_b"]


def test_rerank_preserves_order_when_no_title_match():
    doc_a = _result("doc_a", "Library Hours", score=0.02)
    doc_b = _result("doc_b", "Graduation Application", score=0.01)

    reranked = rerank("unrelated query text", [doc_a, doc_b])

    assert [r.chunk_id for r in reranked] == ["doc_a", "doc_b"]
