"""One integration test that uses the real embedding model (downloads
ONNX weights from Hugging Face on first run — see docs/PROJECT_CONTRACT.md
Module 2's "Interface decisions"). Every other test in this suite stays
network-free via StubEmbedder."""

from qdrant_client import QdrantClient

from ingestion.embedder import FastEmbedEmbedder
from ingestion.metadata import ChunkRecord
from ingestion.vector_store import VectorStore


def _record(document_id: str, content: str, document_type: str) -> ChunkRecord:
    return ChunkRecord(
        document_id=document_id,
        chunk_id=f"{document_id}_chunk_000",
        chunk_index=0,
        content=content,
        content_hash="hash",
        title=document_id,
        source="Test Source",
        department="Test Dept",
        document_type=document_type,
        url="https://example.edu/test",
        access_level="public",
        version="1.0",
    )


def test_real_embedder_ranks_semantically_relevant_chunk_first():
    embedder = FastEmbedEmbedder()
    client = QdrantClient(location=":memory:")
    store = VectorStore(client, collection_name="integration_test", vector_size=384)

    records = [
        _record(
            "academic_calendar",
            "Fall 2026 classes begin on August 24, 2026. Registration opens in July.",
            "academic_calendar",
        ),
        _record(
            "library_hours",
            "The library is open Monday through Thursday from 8am to 11pm.",
            "library_hours",
        ),
    ]
    vectors = embedder.embed([r.content for r in records])
    store.upsert(records, vectors)

    query_vector = embedder.embed(["When do fall classes start?"])[0]
    results = store.search(query_vector, top_k=2)

    assert results[0]["document_id"] == "academic_calendar"
