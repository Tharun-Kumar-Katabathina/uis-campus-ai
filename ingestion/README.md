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
  -> embed + index     (ingestion/embedder.py, ingestion/index.py)
  -> Qdrant collection "campusai_chunks"
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

## Embedding & vector search (Module 2)

```bash
# 1. produce output/chunks.jsonl (see above)
poetry run python -m ingestion.pipeline

# 2. embed + index into Qdrant
poetry run python -m ingestion.index
```

By default `ingestion.index` indexes into an **in-memory** Qdrant instance
(nothing persists — useful for a quick local check). To index into the
real Qdrant service from `docker-compose.yml`, set `QDRANT_URL`:

```bash
QDRANT_URL=http://localhost:6333 poetry run python -m ingestion.index
```

- **Embedding model:** `BAAI/bge-small-en-v1.5` (384-dim) via
  [fastembed](https://github.com/qdrant/fastembed) — real local semantic
  embeddings, ONNX runtime, no torch dependency. Weights download from
  Hugging Face on first use (see "Notes on implementation choices" below).
- **Collection:** `campusai_chunks`, cosine distance. Point IDs are a
  deterministic UUID5 of `chunk_id`, so re-indexing is idempotent —
  upserts overwrite rather than duplicate.
- **Querying:** the live query-time search function is
  `app.retrieval.vector_search.semantic_search()` in the backend (not
  here) — it embeds the query with the same model and searches this same
  collection, optionally filtered by metadata (e.g. `document_type`,
  `access_level`).

## Development

```bash
poetry run pytest -q          # tests
poetry run ruff check .       # lint
poetry run black --check .    # format check
```

## Scheduled ingestion (Module 8)

`.github/workflows/scheduled-ingestion.yml` runs the full pipeline —
extract → clean → chunk → metadata → embed → index — automatically:

- **Schedule**: every Monday at 06:00 UTC (`cron: "0 6 * * 1"`).
- **Manual trigger**: from the GitHub UI (Actions → Scheduled Ingestion →
  Run workflow), or via the CLI:
  ```bash
  gh workflow run scheduled-ingestion.yml
  gh run watch   # follow the run that was just triggered
  ```
- **Where it indexes to**: a real Qdrant instance run as a GitHub Actions
  service container for the duration of the job — this project has no
  persistent hosted Qdrant deployment to point at yet. Pointing
  `QDRANT_URL` at a real deployment instead (once one exists) is a config
  change, not a code change.
- **Failure visibility**: every step's exit code fails the job as usual,
  plus an explicit step queries the indexed point count afterward and
  fails with an `::error::` annotation if it's zero — so a silent
  failure upstream (e.g. an empty manifest) still shows up as a failed,
  clearly-annotated run rather than a deceptively "green" one with no
  data indexed.

## Notes on implementation choices

- **Chunk sizing uses an approximate tokenizer** (`ingestion/chunkers/chunker.py`,
  ~1.3 tokens/word) rather than a real embedding-model tokenizer, to avoid a
  dependency that needs network access to download vocab files. Module 2
  can swap in the real tokenizer once an embedding model is chosen.
- **Versioning** is pipeline-owned, not the manifest's static `version`
  field: a document's version only advances when its cleaned content's hash
  changes between runs; the manifest's `version` is just the starting value
  for a brand-new document.
- **Embedding library is fastembed, not raw sentence-transformers**: it
  avoids a torch dependency, ships native Qdrant integration, and is
  meaningfully lighter/faster to install — see
  `docs/PROJECT_CONTRACT.md` Module 2 for the full reasoning.
- **Tests use Qdrant's in-memory mode** (`QdrantClient(location=":memory:")`),
  not a live service — no Docker/network needed to run the suite, except
  the one real-embedding integration test, which needs network on first
  run to download model weights (cached afterward).
