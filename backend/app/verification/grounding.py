from app.generation.prompt import NO_ANSWER_MESSAGE
from app.retrieval.keyword_search import tokenize
from app.retrieval.vector_search import SearchResult
from app.verification.citations import extract_citation_indices, validate_citations

# Lexical-overlap floor between the answer's words and the evidence's
# words. Deterministic and network-free by design — no second LLM call
# to "judge" faithfulness — but real: it catches an answer with no
# textual connection to any retrieved evidence.
MIN_OVERLAP_RATIO = 0.3


def is_refusal(answer: str) -> bool:
    return NO_ANSWER_MESSAGE.lower() in answer.lower()


def verify_answer(answer: str, evidence: list[SearchResult]) -> bool:
    """PASS/FAIL per docs/PROJECT_CONTRACT.md Module 5 AC3. A refusal is
    always considered verified (it makes no claims to check). Otherwise
    the answer must cite only real evidence indices, cite at least one,
    and be lexically grounded in the cited evidence's content."""
    if is_refusal(answer):
        return True

    if not validate_citations(answer, evidence):
        return False

    cited_indices = extract_citation_indices(answer)
    if not cited_indices:
        return False

    answer_terms = set(tokenize(answer))
    if not answer_terms:
        return False

    evidence_terms: set[str] = set()
    for i in cited_indices:
        evidence_terms |= set(tokenize(evidence[i - 1].content))

    overlap_ratio = len(answer_terms & evidence_terms) / len(answer_terms)
    return overlap_ratio >= MIN_OVERLAP_RATIO
