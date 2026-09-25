# UIS CampusAI

AI-powered university knowledge & information assistant. See
[`docs/UIS_CampusAI_End_to_End_Roadmap.md`](docs/UIS_CampusAI_End_to_End_Roadmap.md)
for the full product/architecture roadmap and
[`docs/PROJECT_CONTRACT.md`](docs/PROJECT_CONTRACT.md) for the module
contract this codebase is built against.

> Independent portfolio project. Not affiliated with or endorsed by the
> University of Illinois Springfield.

## Status

**Modules 0-2 complete:** Project Foundation, Ingestion Pipeline, and
Embedding & Vector Search. Chunks can be embedded and semantically
searched, but there's no hybrid (keyword+rerank) retrieval, RBAC, or LLM
generation/chat yet — see `docs/PROJECT_CONTRACT.md` §11 for what's next.

## Stack

- Frontend: Next.js, TypeScript, Tailwind CSS (`npm`)
- Backend: Python, FastAPI, Pydantic (`poetry`)
- Ingestion: Python — extraction, cleaning, chunking, metadata (`poetry`)
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

Open http://localhost:3000 and you should see the UIS CampusAI placeholder
page.

## Development

Backend (from `backend/`):

```bash
poetry run pytest      # tests
poetry run ruff check . # lint
poetry run black --check . # format check
```

Frontend (from `frontend/`):

```bash
npm run lint          # eslint
npm run format:check  # prettier check
npm run build          # production build
```

Ingestion (from `ingestion/`):

```bash
poetry run pytest -q          # tests
poetry run ruff check .       # lint
poetry run black --check .    # format check
poetry run python -m ingestion.pipeline   # run the pipeline over sample sources
```

See [`ingestion/README.md`](ingestion/README.md) for what it does and its
output format.

## Repository structure

```text
frontend/   Next.js UI
backend/    FastAPI app (api, core, models, services, retrieval,
            generation, verification, tools)
ingestion/  Extraction, cleaning, chunking, metadata pipeline
            (sample sources, tests, output/ — see ingestion/README.md)
docs/       Architecture, roadmap, and the project contract
.github/    CI workflows
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
