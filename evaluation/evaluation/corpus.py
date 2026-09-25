"""The same 5-document synthetic sample corpus used by
backend/tests/test_retrieval_quality.py — duplicated rather than shared
(evaluation/ and backend/tests/ aren't a shared importable package; see
docs/PROJECT_CONTRACT.md Module 2 for the precedent on this kind of
small, deliberate duplication for package independence)."""

from app.retrieval.keyword_search import KeywordIndex
from app.retrieval.vector_search import COLLECTION_NAME, Embedder
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

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


def seed(embedder: Embedder) -> tuple[QdrantClient, KeywordIndex]:
    """In-memory Qdrant + BM25 index, both built from CORPUS. No network
    beyond whatever the given embedder itself needs."""
    client = QdrantClient(location=":memory:")
    client.create_collection(
        COLLECTION_NAME, vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )
    vectors = embedder.embed([doc["content"] for doc in CORPUS])
    client.upsert(
        COLLECTION_NAME,
        points=[PointStruct(id=i, vector=vectors[i], payload=doc) for i, doc in enumerate(CORPUS)],
    )
    return client, KeywordIndex(CORPUS)
