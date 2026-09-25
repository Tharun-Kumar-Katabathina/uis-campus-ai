from app.generation.prompt import NO_ANSWER_MESSAGE
from app.retrieval.vector_search import SearchResult
from app.verification.grounding import is_refusal, verify_answer


def _evidence(content: str) -> list[SearchResult]:
    return [
        SearchResult(
            score=0.9,
            chunk_id="chunk_1",
            document_id="doc_1",
            title="2026-2027 Academic Calendar",
            content=content,
            url="https://example.edu/calendar",
            source="Test",
            department="Registrar",
            document_type="academic_calendar",
            access_level="public",
            version="1.0",
        )
    ]


def test_is_refusal_detects_the_no_answer_message():
    assert is_refusal(NO_ANSWER_MESSAGE) is True
    assert is_refusal(f"Sorry — {NO_ANSWER_MESSAGE}") is True
    assert is_refusal("Fall registration opens July 6 [1].") is False


def test_refusal_is_always_verified():
    evidence = _evidence("Fall registration opens July 6, 2026.")
    assert verify_answer(NO_ANSWER_MESSAGE, evidence) is True


def test_grounded_cited_answer_passes():
    evidence = _evidence("Fall registration opens on July 6, 2026 for continuing students.")
    answer = "Fall registration opens on July 6, 2026 [1]."
    assert verify_answer(answer, evidence) is True


def test_uncited_answer_fails():
    evidence = _evidence("Fall registration opens on July 6, 2026.")
    answer = "Fall registration opens on July 6, 2026."  # no [1]
    assert verify_answer(answer, evidence) is False


def test_fabricated_citation_index_fails():
    evidence = _evidence("Fall registration opens on July 6, 2026.")
    answer = "Fall registration opens on July 6, 2026 [1] and also see [2]."  # only 1 evidence item
    assert verify_answer(answer, evidence) is False


def test_hallucinated_unrelated_answer_fails_lexical_grounding():
    evidence = _evidence("Fall registration opens on July 6, 2026 for continuing students.")
    # cites [1] but the claim has essentially no lexical connection to the evidence
    answer = "The university was founded in 1970 and has a beautiful campus lake [1]."
    assert verify_answer(answer, evidence) is False
