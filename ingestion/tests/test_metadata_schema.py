from ingestion.metadata import ChunkRecord

REQUIRED_FIELDS = [
    "document_id",
    "chunk_id",
    "title",
    "source",
    "department",
    "document_type",
    "url",
    "access_level",
    "version",
]


def test_chunk_record_carries_full_metadata_schema():
    record = ChunkRecord(
        document_id="doc_001",
        chunk_id="doc_001_chunk_000",
        chunk_index=0,
        content="Some chunk text.",
        content_hash="deadbeef",
        title="2026-2027 Academic Calendar",
        source="UIS Academic Calendar",
        department="Registrar",
        document_type="academic_calendar",
        url="https://example.edu",
        published_date="2026-01-01",
        updated_date="2026-08-01",
        effective_date="2026-08-01",
        expiration_date=None,
        academic_year="2026-2027",
        access_level="public",
        version="1.2",
    )

    dumped = record.model_dump()
    for field in REQUIRED_FIELDS:
        assert dumped[field] is not None, f"{field} must not be null"

    assert dumped["expiration_date"] is None  # optional field allowed to be null
