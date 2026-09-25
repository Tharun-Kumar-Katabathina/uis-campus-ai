import uuid

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from ingestion.embedder import VECTOR_SIZE
from ingestion.metadata import ChunkRecord

DEFAULT_COLLECTION = "campusai_chunks"
_ID_NAMESPACE = uuid.UUID("6f6f6f2e-6361-6d70-7573-616924646465")  # arbitrary, fixed


def chunk_point_id(chunk_id: str) -> str:
    """Deterministic UUID for a chunk_id — Qdrant point IDs must be an
    unsigned int or UUID, and this makes upserts idempotent: the same
    chunk_id always maps to the same point, so re-indexing overwrites
    rather than duplicates."""
    return str(uuid.uuid5(_ID_NAMESPACE, chunk_id))


class VectorStore:
    def __init__(
        self,
        client: QdrantClient,
        collection_name: str = DEFAULT_COLLECTION,
        vector_size: int = VECTOR_SIZE,
    ):
        self.client = client
        self.collection_name = collection_name
        if not self.client.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    def upsert(self, records: list[ChunkRecord], vectors: list[list[float]]) -> None:
        points = [
            PointStruct(
                id=chunk_point_id(record.chunk_id),
                vector=vector,
                payload=record.model_dump(mode="json"),
            )
            for record, vector in zip(records, vectors, strict=True)
        ]
        if points:
            self.client.upsert(collection_name=self.collection_name, points=points)

    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        filters: dict[str, str] | None = None,
    ) -> list[dict]:
        query_filter = None
        if filters:
            query_filter = Filter(
                must=[FieldCondition(key=k, match=MatchValue(value=v)) for k, v in filters.items()]
            )

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            query_filter=query_filter,
        ).points

        return [{"score": point.score, **point.payload} for point in results]
