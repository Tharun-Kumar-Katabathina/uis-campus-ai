# UIS CampusAI

AI-powered university knowledge & information assistant. See
[`docs/UIS_CampusAI_End_to_End_Roadmap.md`](docs/UIS_CampusAI_End_to_End_Roadmap.md)
for the full product/architecture roadmap and
[`docs/PROJECT_CONTRACT.md`](docs/PROJECT_CONTRACT.md) for the module
contract this codebase is built against.

> Independent portfolio project. Not affiliated with or endorsed by the
> University of Illinois Springfield.

## Status

**Modules 0-7 complete:** Project Foundation, Ingestion Pipeline,
Embedding & Vector Search, Hybrid Retrieval, RBAC, LLM Generation &
Citation Verification, Evaluation & Observability, and the Frontend Chat
UI. There's a real, working chat interface — pick a role, ask a
question, get a grounded/cited/role-filtered answer with sources and
feedback buttons — backed by a CI-gated evaluation harness. Verified
end-to-end in a real browser against a real local LLM (Ollama +
llama3.2, not installed by default — see `frontend/README.md`). Only
Scheduled Ingestion (turning the manual pipeline into a recurring job) is
left — see `docs/PROJECT_CONTRACT.md` §11.

## Stack

- Frontend: Next.js, TypeScript, Tailwind CSS (`npm`)
- Backend: Python, FastAPI, Pydantic (`poetry`)
- Ingestion: Python — extraction, cleaning, chunking, metadata (`poetry`)
- Evaluation: Python — retrieval/generation quality regression gate (`poetry`)
- Data: PostgreSQL, Qdrant, Redis
- Dev: Docker, GitHub Actions

## Prerequisites

- Node.js 20+ and npm
- Python 3.11+ and [Poetry](https://python-poetry.org/)
- Docker (for `docker compose up`)

## Setup

1. Clone the repo and copy the environment template:

   ```bash
   cp .env.example .env
   ```

2a. **Run everything with Docker** (recommended — starts frontend, backend,
    Postgres, Qdrant, and Redis together):

   ```bash
   docker compose up --build
   ```

   - Frontend: http://localhost:3000
   - Backend health check: http://localhost:8000/health

2b. **Or run services locally** without Docker:

   ```bash
   # Backend
   cd backend
   poetry install
   poetry run uvicorn app.main:app --reload

   # Frontend (separate terminal)
   cd frontend
   npm install
   npm run dev
   ```

## Verify it's working

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

Open http://localhost:3000 — pick a role (no account needed) and ask a
question. Note: without a running Ollama instance (see
`frontend/README.md`), `/chat` will error on the LLM call; everything up
through retrieval still works, and the frontend's own tests mock the LLM
entirely so `npm run test` doesn't need it either.

## Development

Backend (from `backend/`):

```bash
poetry run pytest      # tests
poetry run ruff check . # lint
poetry run black --check . # format check
```

See [`backend/README.md`](backend/README.md) for the retrieval
architecture (hybrid search, reranking, query classification) and how to
run the retrieval-quality benchmark.

Frontend (from `frontend/`):

```bash
npm run test           # Vitest + React Testing Library (mocks the backend)
npm run lint            # eslint
npm run format:check    # prettier check
npm run build             # production build
```

See [`frontend/README.md`](frontend/README.md) for the chat UI's
architecture and how it was manually verified end-to-end.

Ingestion (from `ingestion/`):

```bash
poetry run pytest -q          # tests
poetry run ruff check .       # lint
poetry run black --check .    # format check
poetry run python -m ingestion.pipeline   # run the pipeline over sample sources
```

See [`ingestion/README.md`](ingestion/README.md) for what it does and its
output format.

Evaluation (from `evaluation/`):

```bash
poetry install                # also installs backend/ as a local dependency
poetry run python evaluate.py # prints a retrieval/generation quality report
poetry run pytest -q          # the same evaluation, as CI's regression gate
```

See [`evaluation/README.md`](evaluation/README.md) for the methodology
and metric floors.

## Repository structure

```text
frontend/    Next.js UI
backend/     FastAPI app (api, core, models, retrieval, generation,
             verification)
ingestion/   Extraction, cleaning, chunking, metadata, embedding pipeline
             (sample sources, tests, output/ — see ingestion/README.md)
evaluation/  Retrieval/generation quality regression gate
             (see evaluation/README.md)
docs/        Architecture, roadmap, and the project contract
.github/     CI workflows
```

## Environment variables

See [`.env.example`](.env.example) for the full list, covering database,
vector store, cache, LLM provider, embeddings, observability, and auth
configuration.

## Contributing / agent workflow

This repo is developed under a Main-Orchestrator/Working-Agent/QA-Agent
workflow — see [`CLAUDE.md`](CLAUDE.md) and
[`docs/PROJECT_CONTRACT.md`](docs/PROJECT_CONTRACT.md) before making
changes.
