from typing import Protocol

from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.http.models import FieldCondition, Filter, MatchValue

from app.core.config import settings

MODEL_NAME = "BAAI/bge-small-en-v1.5"
COLLECTION_NAME = "campusai_chunks"  # must match ingestion/ingestion/vector_store.py


class Embedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


class FastEmbedEmbedder:
    """Real local semantic embeddings — same model as the ingestion
    pipeline, duplicated here rather than shared, since backend/ and
    ingestion/ are intentionally separate poetry packages (see
    docs/PROJECT_CONTRACT.md Module 2)."""

    def __init__(self, model_name: str = MODEL_NAME):
        from fastembed import TextEmbedding

        self._model = TextEmbedding(model_name=model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [vector.tolist() for vector in self._model.embed(texts)]


class SearchResult(BaseModel):
    score: float
    chunk_id: str
    document_id: str
    title: str
    content: str
    url: str
    source: str
    department: str
    document_type: str
    access_level: str
    version: str


def _default_client() -> QdrantClient:
    if settings.qdrant_url:
        return QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None)
    return QdrantClient(location=":memory:")


def semantic_search(
    query: str,
    top_k: int = 5,
    filters: dict[str, str] | None = None,
    embedder: Embedder | None = None,
    client: QdrantClient | None = None,
) -> list[SearchResult]:
    embedder = embedder or FastEmbedEmbedder()
    client = client or _default_client()

    query_vector = embedder.embed([query])[0]

    query_filter = None
    if filters:
        query_filter = Filter(
            must=[FieldCondition(key=k, match=MatchValue(value=v)) for k, v in filters.items()]
        )

    if not client.collection_exists(COLLECTION_NAME):
        return []

    points = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        query_filter=query_filter,
    ).points

    return [SearchResult(score=point.score, **point.payload) for point in points]
