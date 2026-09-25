from datetime import date
from typing import Literal

from pydantic import BaseModel

AccessLevel = Literal["public", "authorized", "restricted"]


class SourceManifestEntry(BaseModel):
    """One row of ingestion/sources/manifest.json — describes a raw source
    document and the metadata that should be attached to every chunk
    produced from it."""

    document_id: str
    type: Literal["html", "pdf"]
    path: str
    title: str
    source: str
    department: str
    document_type: str
    url: str
    published_date: date | None = None
    updated_date: date | None = None
    effective_date: date | None = None
    expiration_date: date | None = None
    academic_year: str | None = None
    access_level: AccessLevel = "public"
    version: str = "1.0"


class ChunkMetadata(BaseModel):
    """Metadata schema per docs/PROJECT_CONTRACT.md Module 1 / roadmap §15.
    Attached to every chunk produced by the pipeline."""

    document_id: str
    chunk_id: str
    title: str
    source: str
    department: str
    document_type: str
    url: str
    published_date: date | None = None
    updated_date: date | None = None
    effective_date: date | None = None
    expiration_date: date | None = None
    academic_year: str | None = None
    access_level: AccessLevel
    version: str


class ChunkRecord(ChunkMetadata):
    """A ChunkMetadata plus the chunk's own text and provenance fields,
    matching one line of the pipeline's output JSONL file."""

    chunk_index: int
    content: str
    content_hash: str
