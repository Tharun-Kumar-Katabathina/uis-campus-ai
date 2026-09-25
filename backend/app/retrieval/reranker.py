from app.retrieval.keyword_search import tokenize
from app.retrieval.vector_search import SearchResult

# A lightweight cross-encoder reranker would need another model download
# (network + extra runtime cost) for marginal benefit at this corpus size.
# Per docs/PROJECT_CONTRACT.md Module 3, we use a documented scoring
# combination instead: boost a candidate's fused rank score when the
# query's own words appear in its title, since a title match is a strong
# relevance signal BM25/RRF alone under-weight for short queries.
_TITLE_MATCH_WEIGHT = 0.15


def rerank(query: str, candidates: list[SearchResult]) -> list[SearchResult]:
    query_terms = set(tokenize(query))

    def boosted_score(candidate: SearchResult) -> float:
        title_terms = set(tokenize(candidate.title))
        overlap = len(query_terms & title_terms)
        return candidate.score * (1 + _TITLE_MATCH_WEIGHT * overlap)

    return sorted(candidates, key=boosted_score, reverse=True)
