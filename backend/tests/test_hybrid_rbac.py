"""Proves RBAC filtering actually overrides ranking, not just happens to
agree with it: the "authorized" chunk here is the best possible match for
the query (exact content overlap), while the "public" chunk is only
loosely related. A student must never see the authorized chunk even
though every unfiltered ranking signal favors it."""

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from app.retrieval.hybrid import hybrid_search
from app.retrieval.keyword_search import KeywordIndex
from app.retrieval.vector_search import COLLECTION_NAME
from tests.stub_embedder import StubEmbedder

QUERY = "staff payroll internal procedure"

AUTHORIZED_RECORD = {
    "chunk_id": "staff_doc_chunk_000",
    "document_id": "staff_doc",
    "title": "Staff Payroll Internal Procedure",
    "content": "Staff payroll internal procedure steps for staff payroll internal procedure.",
    "url": "https://example.edu/internal/payroll",
    "source": "Test",
    "department": "HR",
    "document_type": "internal_record",
    "access_level": "authorized",
    "version": "1.0",
}
PUBLIC_RECORD = {
    "chunk_id": "public_doc_chunk_000",
    "document_id": "public_doc",
    "title": "Library Hours",
    "content": "The library is open Monday through Friday.",
    "url": "https://example.edu/library",
    "source": "Test",
    "department": "Library",
    "document_type": "library_hours",
    "access_level": "public",
    "version": "1.0",
}


def _seeded(embedder: StubEmbedder) -> tuple[QdrantClient, KeywordIndex]:
    client = QdrantClient(location=":memory:")
    client.create_collection(
        COLLECTION_NAME, vectors_config=VectorParams(size=embedder.dim, distance=Distance.COSINE)
    )
    records = [AUTHORIZED_RECORD, PUBLIC_RECORD]
    vectors = embedder.embed([r["content"] for r in records])
    client.upsert(
        COLLECTION_NAME,
        points=[PointStruct(id=i, vector=vectors[i], payload=records[i]) for i in range(2)],
    )
    return client, KeywordIndex(records)


def test_student_never_sees_the_authorized_chunk_even_as_best_match():
    embedder = StubEmbedder()
    client, keyword_index = _seeded(embedder)

    # Unfiltered: confirm the authorized chunk really is the top match,
    # so the RBAC test below is proving something, not vacuously true.
    unfiltered = hybrid_search(
        QUERY, top_k=2, keyword_index=keyword_index, embedder=embedder, client=client
    )
    assert unfiltered[0].document_id == "staff_doc"

    student_results = hybrid_search(
        QUERY,
        top_k=2,
        roles=["student"],
        keyword_index=keyword_index,
        embedder=embedder,
        client=client,
    )

    assert all(r.document_id != "staff_doc" for r in student_results)
    assert [r.document_id for r in student_results] == ["public_doc"]


def test_staff_still_sees_the_authorized_chunk():
    embedder = StubEmbedder()
    client, keyword_index = _seeded(embedder)

    staff_results = hybrid_search(
        QUERY,
        top_k=2,
        roles=["staff"],
        keyword_index=keyword_index,
        embedder=embedder,
        client=client,
    )

    assert staff_results[0].document_id == "staff_doc"
