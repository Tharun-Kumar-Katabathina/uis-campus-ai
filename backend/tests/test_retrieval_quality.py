"""Retrieval quality benchmark for hybrid_search (Recall@3 / MRR) against
a small hand-labeled query set over a synthetic sample corpus mirroring
ingestion's sample sources. Uses the real embedding model — like Module
2's integration test, this needs network on first run to fetch weights
(cached afterward); every other test in this module stays network-free."""

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from app.retrieval.hybrid import hybrid_search
from app.retrieval.keyword_search import KeywordIndex
from app.retrieval.vector_search import COLLECTION_NAME, FastEmbedEmbedder

CORPUS = [
    {
        "chunk_id": "academic_calendar_chunk_000",
        "document_id": "academic_calendar",
        "title": "2026-2027 Academic Calendar",
        "content": (
            "Fall 2026 classes begin on August 24, 2026. Fall registration opens "
            "on July 6, 2026. Thanksgiving break runs November 25 through 29. "
            "Spring 2027 classes begin January 19, 2027."
        ),
        "url": "https://example.edu/calendar",
        "source": "Test",
        "department": "Registrar",
        "document_type": "academic_calendar",
        "access_level": "public",
        "version": "1.0",
    },
    {
        "chunk_id": "library_hours_chunk_000",
        "document_id": "library_hours",
        "title": "Brookens Library Hours",
        "content": (
            "Brookens Library is open Monday through Thursday from 8am to 11pm, "
            "Friday 8am to 6pm, Saturday 10am to 6pm, and Sunday noon to 11pm."
        ),
        "url": "https://example.edu/library",
        "source": "Test",
        "department": "Library",
        "document_type": "library_hours",
        "access_level": "public",
        "version": "1.0",
    },
    {
        "chunk_id": "graduation_application_chunk_000",
        "document_id": "graduation_application",
        "title": "Applying for Graduation",
        "content": (
            "Students must submit a graduation application through the student "
            "portal by the deadline for their term, confirm remaining "
            "requirements with an advisor, and pay the graduation fee."
        ),
        "url": "https://example.edu/graduation",
        "source": "Test",
        "department": "Registrar",
        "document_type": "graduation",
        "access_level": "public",
        "version": "1.0",
    },
    {
        "chunk_id": "student_organizations_chunk_000",
        "document_id": "student_organizations",
        "title": "Joining a Student Organization",
        "content": (
            "The university recognizes more than 80 student organizations. To "
            "join, browse the organization directory or attend the involvement "
            "fair. To start a new organization, submit a constitution and five "
            "founding members."
        ),
        "url": "https://example.edu/organizations",
        "source": "Test",
        "department": "Student Life",
        "document_type": "student_organizations",
        "access_level": "public",
        "version": "1.0",
    },
    {
        "chunk_id": "registration_policy_chunk_000",
        "document_id": "registration_policy",
        "title": "Course Registration Policy",
        "content": (
            "Undergraduate students may register for up to 18 credit hours per "
            "semester without approval. Prerequisites must be satisfied before "
            "registering for a course. Late registration requires instructor "
            "permission and a fee."
        ),
        "url": "https://example.edu/registration-policy",
        "source": "Test",
        "department": "Registrar",
        "document_type": "policy",
        "access_level": "public",
        "version": "1.0",
    },
]

EVAL_QUERIES = [
    ("When does fall registration open?", "academic_calendar"),
    ("When do fall classes start?", "academic_calendar"),
    ("When is Thanksgiving break?", "academic_calendar"),
    ("What are the library hours on Sunday?", "library_hours"),
    ("Is the library open on Saturday?", "library_hours"),
    ("How do I apply for graduation?", "graduation_application"),
    ("What do I need to do before I graduate?", "graduation_application"),
    ("How do I join a student organization?", "student_organizations"),
    ("How do I start a new club?", "student_organizations"),
    ("How many credit hours can I take without approval?", "registration_policy"),
    ("What happens if I register late?", "registration_policy"),
    ("Do I need to satisfy prerequisites before registering?", "registration_policy"),
]


def test_hybrid_search_recall_and_mrr_meet_threshold():
    embedder = FastEmbedEmbedder()
    client = QdrantClient(location=":memory:")
    client.create_collection(
        COLLECTION_NAME, vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )
    vectors = embedder.embed([doc["content"] for doc in CORPUS])
    client.upsert(
        COLLECTION_NAME,
        points=[PointStruct(id=i, vector=vectors[i], payload=doc) for i, doc in enumerate(CORPUS)],
    )
    keyword_index = KeywordIndex(CORPUS)

    hits = 0
    reciprocal_ranks = []
    for query, expected_doc_id in EVAL_QUERIES:
        results = hybrid_search(
            query, top_k=3, keyword_index=keyword_index, embedder=embedder, client=client
        )
        doc_ids = [r.document_id for r in results]
        if expected_doc_id in doc_ids:
            hits += 1
            reciprocal_ranks.append(1.0 / (doc_ids.index(expected_doc_id) + 1))
        else:
            reciprocal_ranks.append(0.0)

    recall_at_3 = hits / len(EVAL_QUERIES)
    mrr = sum(reciprocal_ranks) / len(reciprocal_ranks)

    assert recall_at_3 >= 0.8, f"Recall@3 too low: {recall_at_3} ({hits}/{len(EVAL_QUERIES)})"
    assert mrr >= 0.6, f"MRR too low: {mrr}"
