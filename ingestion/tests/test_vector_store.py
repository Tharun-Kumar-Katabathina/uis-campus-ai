from qdrant_client import QdrantClient

from ingestion.metadata import ChunkRecord
from ingestion.vector_store import VectorStore, chunk_point_id
from tests.stub_embedder import StubEmbedder


def _record(document_id: str, chunk_index: int, content: str, **overrides) -> ChunkRecord:
    base = dict(
        document_id=document_id,
        chunk_id=f"{document_id}_chunk_{chunk_index:03d}",
        chunk_index=chunk_index,
        content=content,
        content_hash="hash",
        title=document_id,
        source="Test Source",
        department="Test Dept",
        document_type="test",
        url="https://example.edu/test",
        access_level="public",
        version="1.0",
    )
    base.update(overrides)
    return ChunkRecord(**base)


def test_chunk_point_id_is_deterministic():
    assert chunk_point_id("doc_a_chunk_000") == chunk_point_id("doc_a_chunk_000")
    assert chunk_point_id("doc_a_chunk_000") != chunk_point_id("doc_a_chunk_001")


def test_upsert_is_idempotent_no_duplicate_points():
    embedder = StubEmbedder()
    client = QdrantClient(location=":memory:")
    store = VectorStore(client, collection_name="test_collection", vector_size=embedder.dim)

    records = [_record("doc_a", 0, "Fall registration opens in July.")]
    vectors = embedder.embed([r.content for r in records])

    store.upsert(records, vectors)
    store.upsert(records, vectors)  # re-index the same chunk

    count = client.count(collection_name="test_collection").count
    assert count == 1


def test_search_returns_payload_and_respects_filters():
    embedder = StubEmbedder()
    client = QdrantClient(location=":memory:")
    store = VectorStore(client, collection_name="test_collection", vector_size=embedder.dim)

    records = [
        _record("doc_a", 0, "Library hours are posted online.", document_type="library_hours"),
        _record("doc_b", 0, "Registration opens in July.", document_type="academic_calendar"),
    ]
    vectors = embedder.embed([r.content for r in records])
    store.upsert(records, vectors)

    query_vector = embedder.embed(["When does registration open?"])[0]
    results = store.search(query_vector, top_k=5)
    assert len(results) == 2
    assert {r["document_id"] for r in results} == {"doc_a", "doc_b"}

    filtered = store.search(query_vector, top_k=5, filters={"document_type": "library_hours"})
    assert len(filtered) == 1
    assert filtered[0]["document_id"] == "doc_a"
