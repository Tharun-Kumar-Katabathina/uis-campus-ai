from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from app.retrieval.hybrid import hybrid_search, reciprocal_rank_fusion
from app.retrieval.keyword_search import KeywordIndex
from app.retrieval.vector_search import COLLECTION_NAME, SearchResult
from tests.stub_embedder import StubEmbedder


def _result(chunk_id: str, title: str, score: float) -> SearchResult:
    return SearchResult(
        score=score,
        chunk_id=chunk_id,
        document_id=chunk_id,
        title=title,
        content="content",
        url="https://example.edu",
        source="Test",
        department="Test",
        document_type="test",
        access_level="public",
        version="1.0",
    )


def test_reciprocal_rank_fusion_prioritizes_docs_ranked_high_in_both_lists():
    x, y, z = _result("x", "X", 0), _result("y", "Y", 0), _result("z", "Z", 0)
    fused = reciprocal_rank_fusion([[x, y, z], [x, y]])

    assert [r.chunk_id for r in fused] == ["x", "y", "z"]


def test_reciprocal_rank_fusion_includes_doc_present_in_only_one_list():
    x = _result("x", "X", 0)
    fused = reciprocal_rank_fusion([[x], []])

    assert [r.chunk_id for r in fused] == ["x"]


RECORD_A = {
    "chunk_id": "doc_a_chunk_000",
    "document_id": "doc_a",
    "title": "Library Hours",
    "content": "The library is open Monday through Thursday.",
    "url": "https://example.edu/library",
    "source": "Test",
    "department": "Library",
    "document_type": "library_hours",
    "access_level": "public",
    "version": "1.0",
}
RECORD_B = {
    "chunk_id": "doc_b_chunk_000",
    "document_id": "doc_b",
    "title": "Academic Calendar",
    "content": "Fall registration opens in July.",
    "url": "https://example.edu/calendar",
    "source": "Test",
    "department": "Registrar",
    "document_type": "academic_calendar",
    "access_level": "public",
    "version": "1.0",
}


def test_hybrid_search_merges_semantic_and_keyword_results_without_network():
    embedder = StubEmbedder()
    client = QdrantClient(location=":memory:")
    client.create_collection(
        COLLECTION_NAME, vectors_config=VectorParams(size=embedder.dim, distance=Distance.COSINE)
    )
    vectors = embedder.embed([RECORD_A["content"], RECORD_B["content"]])
    client.upsert(
        COLLECTION_NAME,
        points=[
            PointStruct(id=1, vector=vectors[0], payload=RECORD_A),
            PointStruct(id=2, vector=vectors[1], payload=RECORD_B),
        ],
    )
    keyword_index = KeywordIndex([RECORD_A, RECORD_B])

    results = hybrid_search(
        "library hours", top_k=5, keyword_index=keyword_index, embedder=embedder, client=client
    )

    assert len(results) == 2
    assert results[0].document_id == "doc_a"  # exact lexical + semantic match wins


def test_hybrid_search_works_with_no_keyword_index():
    embedder = StubEmbedder()
    client = QdrantClient(location=":memory:")
    client.create_collection(
        COLLECTION_NAME, vectors_config=VectorParams(size=embedder.dim, distance=Distance.COSINE)
    )
    vectors = embedder.embed([RECORD_A["content"]])
    client.upsert(COLLECTION_NAME, points=[PointStruct(id=1, vector=vectors[0], payload=RECORD_A)])

    results = hybrid_search("library hours", top_k=5, embedder=embedder, client=client)

    assert len(results) == 1
    assert results[0].document_id == "doc_a"
