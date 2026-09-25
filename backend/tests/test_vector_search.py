from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from app.retrieval.vector_search import COLLECTION_NAME, semantic_search
from tests.stub_embedder import StubEmbedder

RECORD_A = {
    "chunk_id": "doc_a_chunk_000",
    "document_id": "doc_a",
    "title": "Library Hours",
    "content": "The library is open Monday through Thursday.",
    "url": "https://example.edu/library",
    "source": "Test Source",
    "department": "Library",
    "document_type": "library_hours",
    "access_level": "public",
    "version": "1.0",
}
RECORD_B = {
    "chunk_id": "doc_b_chunk_000",
    "document_id": "doc_b",
    "title": "Academic Calendar",
    "content": "Registration opens in July.",
    "url": "https://example.edu/calendar",
    "source": "Test Source",
    "department": "Registrar",
    "document_type": "academic_calendar",
    "access_level": "public",
    "version": "1.0",
}


def _seeded_client(embedder: StubEmbedder) -> QdrantClient:
    client = QdrantClient(location=":memory:")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=embedder.dim, distance=Distance.COSINE),
    )
    vectors = embedder.embed([RECORD_A["content"], RECORD_B["content"]])
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(id=1, vector=vectors[0], payload=RECORD_A),
            PointStruct(id=2, vector=vectors[1], payload=RECORD_B),
        ],
    )
    return client


def test_semantic_search_returns_scored_results():
    embedder = StubEmbedder()
    client = _seeded_client(embedder)

    results = semantic_search("library hours", top_k=5, embedder=embedder, client=client)

    assert len(results) == 2
    assert {r.document_id for r in results} == {"doc_a", "doc_b"}
    assert all(isinstance(r.score, float) for r in results)


def test_semantic_search_respects_metadata_filters():
    embedder = StubEmbedder()
    client = _seeded_client(embedder)

    results = semantic_search(
        "opens",
        top_k=5,
        filters={"document_type": "academic_calendar"},
        embedder=embedder,
        client=client,
    )

    assert len(results) == 1
    assert results[0].document_id == "doc_b"


def test_semantic_search_returns_empty_when_collection_missing():
    embedder = StubEmbedder()
    client = QdrantClient(location=":memory:")  # no collection created

    results = semantic_search("anything", embedder=embedder, client=client)

    assert results == []
