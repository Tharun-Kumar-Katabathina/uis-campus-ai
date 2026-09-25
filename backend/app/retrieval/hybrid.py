from qdrant_client import QdrantClient

from app.retrieval.access_control import filter_by_role
from app.retrieval.keyword_search import KeywordIndex
from app.retrieval.reranker import rerank
from app.retrieval.vector_search import Embedder, SearchResult, semantic_search

_RRF_K = 60  # standard reciprocal-rank-fusion constant


def reciprocal_rank_fusion(result_lists: list[list[SearchResult]]) -> list[SearchResult]:
    scores: dict[str, float] = {}
    by_id: dict[str, SearchResult] = {}

    for results in result_lists:
        for rank, result in enumerate(results, start=1):
            scores[result.chunk_id] = scores.get(result.chunk_id, 0.0) + 1.0 / (_RRF_K + rank)
            by_id[result.chunk_id] = result

    ranked_ids = sorted(scores, key=lambda chunk_id: -scores[chunk_id])
    return [
        by_id[chunk_id].model_copy(update={"score": scores[chunk_id]}) for chunk_id in ranked_ids
    ]


def hybrid_search(
    query: str,
    top_k: int = 5,
    filters: dict[str, str] | None = None,
    roles: list[str] | None = None,
    keyword_index: KeywordIndex | None = None,
    embedder: Embedder | None = None,
    client: QdrantClient | None = None,
) -> list[SearchResult]:
    """Combines semantic search (Module 2) with BM25 keyword search via
    reciprocal rank fusion, then reranks the fused candidates. `top_k` is
    the final result count; each underlying search pulls a wider
    candidate set so fusion has enough to work with.

    `roles` (Module 4 RBAC): when given, any candidate whose access_level
    none of these roles satisfies is dropped before reranking/truncation
    — a restricted document can never displace a permitted one into the
    top_k just because it scored higher."""
    candidate_pool = max(top_k * 3, 10)

    semantic_results = semantic_search(
        query, top_k=candidate_pool, filters=filters, embedder=embedder, client=client
    )
    keyword_results = (
        keyword_index.search(query, top_k=candidate_pool, filters=filters) if keyword_index else []
    )

    fused = reciprocal_rank_fusion([semantic_results, keyword_results])
    if roles is not None:
        fused = filter_by_role(fused, roles)
    return rerank(query, fused)[:top_k]
