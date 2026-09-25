import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from ingestion.chunkers import chunk_text
from ingestion.cleaners import clean_text
from ingestion.extractors import extract_html, extract_pdf
from ingestion.metadata import ChunkRecord, SourceManifestEntry

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = PACKAGE_ROOT / "sources" / "manifest.json"
DEFAULT_RAW_DIR = PACKAGE_ROOT / "sources" / "raw"
DEFAULT_OUTPUT_PATH = PACKAGE_ROOT / "output" / "chunks.jsonl"
DEFAULT_STATE_PATH = PACKAGE_ROOT / "output" / "state.json"


@dataclass
class PipelineResult:
    processed: list[str] = field(default_factory=list)
    skipped_unchanged: list[str] = field(default_factory=list)
    skipped_restricted: list[tuple[str, str]] = field(default_factory=list)
    chunk_count: int = 0


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _bump_version(version: str) -> str:
    parts = version.split(".")
    try:
        parts[-1] = str(int(parts[-1]) + 1)
    except ValueError:
        return f"{version}.1"
    return ".".join(parts)


def _extract(entry: SourceManifestEntry, raw_dir: Path) -> str:
    raw_path = raw_dir / entry.path
    if entry.type == "html":
        return extract_html(raw_path)
    return extract_pdf(raw_path)


def run(
    manifest_path: Path = DEFAULT_MANIFEST,
    raw_dir: Path = DEFAULT_RAW_DIR,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    state_path: Path = DEFAULT_STATE_PATH,
) -> PipelineResult:
    manifest = [SourceManifestEntry(**row) for row in json.loads(manifest_path.read_text())]

    state: dict[str, dict[str, str]] = {}
    if state_path.exists():
        state = json.loads(state_path.read_text())

    result = PipelineResult()
    records: list[ChunkRecord] = []

    for entry in manifest:
        if entry.access_level == "restricted":
            result.skipped_restricted.append(
                (entry.document_id, "access_level=restricted is not permitted for ingestion")
            )
            continue

        cleaned = clean_text(_extract(entry, raw_dir))
        content_hash = _content_hash(cleaned)
        previous = state.get(entry.document_id)

        if previous is None:
            version = entry.version
            result.processed.append(entry.document_id)
        elif previous["content_hash"] == content_hash:
            version = previous["version"]
            result.skipped_unchanged.append(entry.document_id)
        else:
            version = _bump_version(previous["version"])
            result.processed.append(entry.document_id)

        state[entry.document_id] = {"content_hash": content_hash, "version": version}

        for index, chunk in enumerate(chunk_text(cleaned)):
            records.append(
                ChunkRecord(
                    document_id=entry.document_id,
                    chunk_id=f"{entry.document_id}_chunk_{index:03d}",
                    chunk_index=index,
                    content=chunk,
                    content_hash=content_hash,
                    title=entry.title,
                    source=entry.source,
                    department=entry.department,
                    document_type=entry.document_type,
                    url=entry.url,
                    published_date=entry.published_date,
                    updated_date=entry.updated_date,
                    effective_date=entry.effective_date,
                    expiration_date=entry.expiration_date,
                    academic_year=entry.academic_year,
                    access_level=entry.access_level,
                    version=version,
                )
            )

    records.sort(key=lambda r: (r.document_id, r.chunk_index))
    result.chunk_count = len(records)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(record.model_dump_json() + "\n")

    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True))

    return result


def main() -> None:
    result = run()
    print(f"processed: {result.processed}")
    print(f"skipped (unchanged): {result.skipped_unchanged}")
    print(f"skipped (restricted): {result.skipped_restricted}")
    print(f"chunks written: {result.chunk_count} -> {DEFAULT_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
