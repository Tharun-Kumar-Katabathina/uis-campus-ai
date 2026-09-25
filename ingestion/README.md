# Ingestion Pipeline

Offline batch pipeline that turns raw source documents into cleaned,
structure-aware, metadata-tagged chunks. It runs separately from the live
chat request path — see `docs/PROJECT_CONTRACT.md` Module 1 and
`docs/UIS_CampusAI_End_to_End_Roadmap.md` §17.

```text
Raw source (HTML/PDF)
  -> extractor        (ingestion/extractors)
  -> cleaner           (ingestion/cleaners)
  -> chunker            (ingestion/chunkers)
  -> metadata attach   (ingestion/metadata)
  -> output/chunks.jsonl + output/state.json
```

## Sample data

`sources/manifest.json` + `sources/raw/` contain a small set of
**synthetic** UIS-style sample documents (academic calendar, library hours,
student organizations, graduation application, a PDF registration policy),
plus one deliberately `access_level: restricted` entry with no backing raw
file, used to prove the pipeline refuses to ingest restricted content. None
of this is real UIS data or the result of scraping uis.edu — see
`docs/PROJECT_CONTRACT.md` Module 1 for why. The pipeline needs no network
access to run.

## Running it

```bash
poetry install
poetry run python -m ingestion.pipeline
```

This reads `sources/manifest.json` + `sources/raw/`, and writes:

- `output/chunks.jsonl` — one JSON object per chunk (the fields in
  `ingestion.metadata.ChunkRecord`), the artifact Module 2 (Embedding &
  Vector Search) will consume. Regenerated on every run; not committed.
- `output/state.json` — per-document `content_hash` + `version`, used to
  skip unchanged sources and version-bump changed ones on the next run.
  Also regenerated on every run; not committed.

To add a new source: add a raw file under `sources/raw/` and an entry to
`sources/manifest.json` with its metadata (see
`ingestion.metadata.SourceManifestEntry` for the required fields).

## Development

```bash
poetry run pytest -q          # tests
poetry run ruff check .       # lint
poetry run black --check .    # format check
```

## Notes on implementation choices

- **Chunk sizing uses an approximate tokenizer** (`ingestion/chunkers/chunker.py`,
  ~1.3 tokens/word) rather than a real embedding-model tokenizer, to avoid a
  dependency that needs network access to download vocab files. Module 2
  can swap in the real tokenizer once an embedding model is chosen.
- **Versioning** is pipeline-owned, not the manifest's static `version`
  field: a document's version only advances when its cleaned content's hash
  changes between runs; the manifest's `version` is just the starting value
  for a brand-new document.
