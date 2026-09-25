from app.retrieval.vector_search import SearchResult
from app.verification.citations import (
    citations_to_sources,
    extract_citation_indices,
    validate_citations,
)


def _evidence(n: int) -> list[SearchResult]:
    return [
        SearchResult(
            score=0.9,
            chunk_id=f"chunk_{i}",
            document_id=f"doc_{i}",
            title=f"Title {i}",
            content=f"Content {i}",
            url=f"https://example.edu/{i}",
            source="Test",
            department="Test",
            document_type="test",
            access_level="public",
            version="1.0",
        )
        for i in range(1, n + 1)
    ]


def test_extract_citation_indices_dedupes_and_sorts():
    assert extract_citation_indices("See [2] and [1], also [2] again.") == [1, 2]


def test_extract_citation_indices_empty_when_no_citations():
    assert extract_citation_indices("No citations here.") == []


def test_validate_citations_true_when_all_in_range():
    assert validate_citations("Per [1] and [2].", _evidence(2)) is True


def test_validate_citations_false_on_fabricated_index():
    assert validate_citations("Per [1] and [3].", _evidence(2)) is False


def test_citations_to_sources_only_includes_cited_evidence_in_order():
    evidence = _evidence(3)
    sources = citations_to_sources("Per [2] and [1].", evidence)

    assert [s.title for s in sources] == ["Title 1", "Title 2"]
    assert sources[0].url == "https://example.edu/1"
    assert sources[0].relevance == 0.9
