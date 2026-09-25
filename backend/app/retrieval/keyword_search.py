import re

from qdrant_client import QdrantClient
from rank_bm25 import BM25Okapi

from app.retrieval.vector_search import COLLECTION_NAME, SearchResult

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class KeywordIndex:
    """In-memory BM25 index over a fixed set of chunk payload dicts (the
    same shape Qdrant stores — see ingestion.metadata.ChunkRecord). Pure
    lexical search, no network or embedding model involved."""

    def __init__(self, records: list[dict]):
        self._records = records
        self._bm25 = BM25Okapi([tokenize(r["content"]) for r in records]) if records else None

    def search(
        self,
        query: str,
        top_k: int = 5,
        filters: dict[str, str] | None = None,
    ) -> list[SearchResult]:
        if self._bm25 is None:
            return []

        scores = self._bm25.get_scores(tokenize(query))
        ranked_indices = sorted(range(len(scores)), key=lambda i: -scores[i])

        results = []
        for i in ranked_indices:
            score = scores[i]
            if score <= 0:
                break  # remaining scores are <= this one; no more matches
            record = self._records[i]
            if filters and any(record.get(k) != v for k, v in filters.items()):
                continue
            results.append(SearchResult(score=float(score), **record))
            if len(results) >= top_k:
                break
        return results


def load_records_from_qdrant(
    client: QdrantClient, collection_name: str = COLLECTION_NAME
) -> list[dict]:
    """Pulls every chunk payload out of Qdrant to build a BM25 corpus.
    Qdrant is the single source of truth for chunk content in this
    system (see docs/PROJECT_CONTRACT.md Module 2) — no separate document
    store to keep in sync."""
    if not client.collection_exists(collection_name):
        return []

    records: list[dict] = []
    offset = None
    while True:
        points, offset = client.scroll(
            collection_name=collection_name,
            limit=256,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        records.extend(point.payload for point in points)
        if offset is None:
            break
    return records
