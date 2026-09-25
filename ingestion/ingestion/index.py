import json
import os
from pathlib import Path

from qdrant_client import QdrantClient

from ingestion.embedder import Embedder, FastEmbedEmbedder
from ingestion.metadata import ChunkRecord
from ingestion.pipeline import DEFAULT_OUTPUT_PATH
from ingestion.vector_store import DEFAULT_COLLECTION, VectorStore


def load_records(chunks_path: Path) -> list[ChunkRecord]:
    return [
        ChunkRecord.model_validate(json.loads(line))
        for line in chunks_path.read_text().splitlines()
        if line.strip()
    ]


def run(
    chunks_path: Path = DEFAULT_OUTPUT_PATH,
    client: QdrantClient | None = None,
    collection_name: str = DEFAULT_COLLECTION,
    embedder: Embedder | None = None,
) -> int:
    records = load_records(chunks_path)
    if not records:
        return 0

    embedder = embedder or FastEmbedEmbedder()
    vectors = embedder.embed([record.content for record in records])

    if client is None:
        qdrant_url = os.environ.get("QDRANT_URL")
        client = QdrantClient(url=qdrant_url) if qdrant_url else QdrantClient(location=":memory:")

    store = VectorStore(client, collection_name=collection_name)
    store.upsert(records, vectors)
    return len(records)


def main() -> None:
    qdrant_url = os.environ.get("QDRANT_URL")
    client = QdrantClient(url=qdrant_url) if qdrant_url else QdrantClient(location=":memory:")
    count = run(client=client)
    target = qdrant_url or "in-memory (set QDRANT_URL to index into a real Qdrant instance)"
    print(f"indexed {count} chunks into Qdrant at {target}")


if __name__ == "__main__":
    main()
