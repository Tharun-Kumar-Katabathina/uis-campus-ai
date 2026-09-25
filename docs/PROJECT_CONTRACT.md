# UIS CampusAI — Multi-Agent Development Architecture

> This is the shared project contract referenced by `CLAUDE.md`. Every Claude Code
> session working on this repo should read this file before making changes.
> Modules 0-8 are fully defined in §11 below. Acceptance criteria for a module
> already in progress may still be refined with interface decisions as it's
> built (see Module 1/2's "Interface decision" notes) — keep this file updated
> so it stays the single source of truth.

## 1. Objective

Build **UIS CampusAI**, an AI-powered university knowledge assistant using a multi-agent software-development workflow.

The application should support:

* Academic information
* Academic calendars
* University policies
* Library information
* Campus events
* Student organizations
* Department information
* Student services
* Official university documents
* Approved internal information when explicitly authorized
* Source-backed answers
* Citations
* Hybrid retrieval
* RAG
* LLM-based generation
* Answer verification
* Evaluation
* Observability
* Scheduled knowledge ingestion
* Security
* Role-based access where required

The development process itself must be coordinated by a **Main Orchestrator Agent** that controls multiple specialized Working Agents and Testing Agents.

---

## 2. Core Multi-Agent Development Architecture

The development workflow must follow:

```text
                         MAIN ORCHESTRATOR
                                |
                 +--------------+--------------+
                 |              |              |
                 v              v              v
            MODULE AGENT   MODULE AGENT   MODULE AGENT
                 |              |              |
                 v              v              v
             WORKING         WORKING         WORKING
              AGENT           AGENT           AGENT
                 |              |              |
                 v              v              v
              TEST            TEST            TEST
              AGENT           AGENT           AGENT
                 |              |              |
              PASS?           PASS?           PASS?
              /   \           /   \           /   \
            YES    NO       YES    NO       YES    NO
             |      |        |      |        |      |
             |      +--------+      +--------+      |
             |               |               |
             v               v               v
        MAIN ORCHESTRATOR REVIEWS MODULE
                         |
                         v
                  INTEGRATION CHECK
                         |
                         v
                    NEXT MODULE
```

The Main Orchestrator is always responsible for controlling the overall workflow.

> **Implementation note:** in an actual Claude Code session, the "Main
> Orchestrator" and each "Working Agent" are the same session — one Claude
> Code instance plays both roles for a module it's actively building. The
> "Testing Agent" is implemented as a real, separate subagent
> (`.claude/agents/qa-tester.md`) so verification isn't self-reported.
> "Module Agents" running in parallel are only real if you deliberately turn
> on Agent Teams for a stretch of genuinely independent modules — see
> `CLAUDE.md`.

---

## 3. Agent Roles

### Agent 1 — Main Orchestrator Agent

This is the highest-level agent.

Responsibilities:

1. Understand the complete CampusAI requirements.
2. Maintain the master project plan.
3. Divide the project into modules.
4. Define module dependencies.
5. Define acceptance criteria for each module.
6. Assign each module to a specialized Working Agent.
7. Allow independent modules to run in parallel when dependencies permit.
8. Track implementation progress.
9. Review completed modules.
10. Trigger Testing Agents.
11. Receive test reports.
12. If testing fails, send the module back to its Working Agent with required changes.
13. Ensure failed modules are fixed and retested.
14. Integrate completed modules.
15. Run integration checks after module completion.
16. Maintain architectural consistency.
17. Prevent agents from introducing conflicting technologies or designs.
18. Maintain a project-level TODO/progress tracker.
19. Decide when the project is ready for the next phase.
20. Perform final system validation.

The Main Agent must NOT blindly trust that a Working Agent completed its task.

It must verify:

```text
Implementation
+
Tests
+
Acceptance Criteria
+
Integration
+
Documentation
```

before marking a module complete.

---

## 4. Working Agents

Each major module receives its own specialized Working Agent.

A Working Agent is responsible for:

1. Understanding the assigned module.
2. Reviewing the existing codebase.
3. Understanding the module requirements.
4. Designing the module.
5. Implementing the module.
6. Writing unit tests.
7. Writing integration tests where applicable.
8. Updating documentation.
9. Reporting exactly what was implemented.
10. Reporting known limitations.
11. Reporting files changed.
12. Reporting how the implementation satisfies acceptance criteria.

A Working Agent must NOT:

* Redesign the entire project.
* Change unrelated modules.
* Replace architecture without approval.
* Introduce unnecessary technologies.
* Claim completion without testing.
* Modify another agent's module without coordination.

---

## 5. Testing / QA Agents

Every module must have a Testing Agent.

The Testing Agent must independently verify:

```text
Requirements
      +
Acceptance Criteria
      +
Implementation
      +
Tests
      +
Integration
```

The Testing Agent should inspect the actual implementation rather than trusting the Working Agent's report.

The Testing Agent must produce:

```text
PASS
or
FAIL
```

with evidence.

---

## 6. Testing Agent Responsibilities

For every module:

### Requirement verification

Check:

* Did the agent implement everything requested?
* Are edge cases handled?
* Are required APIs present?
* Are required data structures present?
* Are security requirements satisfied?

### Code verification

Check:

* Correctness
* Maintainability
* Architecture consistency
* Error handling
* Type safety
* Security
* Performance where relevant

### Testing verification

Check:

* Unit tests
* Integration tests
* Failure cases
* Edge cases
* Regression cases

### Documentation verification

Check:

* README/documentation
* API documentation
* Environment variables
* Setup instructions
* Architecture documentation

---

## 7. Test Failure Loop

If a module fails:

```text
Working Agent
      |
      v
Implementation
      |
      v
Testing Agent
      |
      v
FAIL
      |
      v
Detailed Failure Report
      |
      v
Main Orchestrator
      |
      v
Working Agent
      |
      v
Fix
      |
      v
Testing Agent
      |
      v
Retest
```

Do NOT mark the module complete until the Testing Agent passes it.

---

## 8. Main Agent Control Rule

After every module:

```text
STOP
   |
   v
Main Agent Review
   |
   +--> Requirements satisfied?
   |
   +--> Tests passed?
   |
   +--> Architecture consistent?
   |
   +--> Integration successful?
   |
   +--> Documentation updated?
   |
   v
YES
   |
   v
Mark COMPLETE
   |
   v
Move to next module
```

If any answer is NO:

```text
DO NOT PROCEED
```

Send the module back for correction.

---

## 9. Parallel Development

The Main Agent should identify modules that can be developed independently.

For example:

```text
                 MAIN AGENT
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
      Frontend     Backend     Ingestion
       Agent        Agent        Agent
          |           |           |
          v           v           v
       Tester       Tester       Tester
```

These can run in parallel if their interfaces are already defined.

However, dependent modules must wait.

Example:

```text
Ingestion
    |
    v
Embedding
    |
    v
Vector Search
    |
    v
Reranking
```

Do not allow the Vector Search Agent to invent a different data model while the Ingestion Agent is implementing another one.

---

## 10. Shared Project Contract

Before parallel development starts, the Main Agent must create a shared project contract.

Create:

```text
/docs/PROJECT_CONTRACT.md
```

It should define:

* Architecture
* Technology stack
* Folder structure
* API contracts
* Database contracts
* Data models
* Environment variables
* Naming conventions
* Error-handling conventions
* Authentication model
* Retrieval architecture
* LLM interface
* Testing standards
* Acceptance criteria
* Module dependencies

All agents must follow this contract.

---

## 11. Recommended CampusAI Modules

The Main Agent should divide UIS CampusAI into the following modules.

---

### MODULE 0 — Project Foundation

#### Goal

Create the base repository and development standards.

#### Responsibilities

* Repository structure
* Frontend initialization
* Backend initialization
* Environment configuration
* Docker foundation
* Git configuration
* Code formatting
* Linting
* Basic CI
* README
* Project contract

#### Suggested stack

Frontend:

```text
Next.js
TypeScript
Tailwind CSS
```

Backend:

```text
Python
FastAPI
Pydantic
```

Data:

```text
PostgreSQL
Qdrant
Redis
```

Development:

```text
Docker
GitHub Actions
```

#### Package managers

* Frontend: `npm`
* Backend: `poetry`

#### Acceptance criteria

1. `frontend/` — Next.js + TypeScript + Tailwind app that runs with
   `npm run dev` and shows a placeholder page.
2. `backend/` — FastAPI + Pydantic app with a `GET /health` endpoint
   returning 200, runnable via `poetry run uvicorn`.
3. `docker-compose.yml` — brings up `frontend`, `backend`, `postgres`,
   `qdrant`, `redis`; `docker compose up` succeeds with no manual steps
   beyond copying `.env.example` to `.env`.
4. `.env.example` present at root, documenting every variable each service
   needs.
5. Linting/formatting configured for both frontend (ESLint + Prettier) and
   backend (ruff + black), running clean on the initial commit.
6. A GitHub Actions workflow that runs lint + a trivial test on push/PR and
   passes.
7. Root `README.md` with setup instructions another engineer could follow
   cold (clone → env → docker compose up → verify health).
8. `docs/PROJECT_CONTRACT.md` exists and `CLAUDE.md` /
   `.claude/agents/qa-tester.md` exist.

---

### MODULE 1 — Ingestion Pipeline (Extraction, Cleaning, Chunking, Metadata)

#### Goal

Build the offline batch pipeline that turns raw source documents into
cleaned, structure-aware, metadata-tagged chunks. This is separate from the
live chat request path (roadmap §17) and is what Module 2 (Embedding &
Vector Search) will consume.

#### Scope

In scope:

* HTML and PDF extraction.
* Cleaning/normalization (strip boilerplate, preserve headings/lists/URLs).
* Structure-aware chunking, target ~300–700 tokens, with overlap.
* Metadata attached to every chunk per roadmap §15's schema.
* Content-hash based change detection and per-document versioning
  (roadmap §30) — unchanged sources are skipped on re-run.
* A small set of **synthetic** UIS-style sample source documents (not
  live-scraped) so the pipeline and its tests run fully offline. Roadmap
  §7.6/§34 explicitly sanction synthetic data for this portfolio project;
  live scraping of uis.edu is deferred to a later "Scheduled Ingestion"
  module and is out of scope here.
* Enforcing roadmap §8: the pipeline must refuse to ingest any source
  manifest entry marked `access_level: restricted`.

Out of scope (later modules): embeddings, vector DB writes, live web
crawling/scheduling, reranking.

#### Interface decision

`ingestion/` is its own top-level Python package with its own
`pyproject.toml` (poetry), sibling to `backend/` — it needs HTML/PDF
parsing libraries the API layer doesn't, and roadmap §46's repo structure
already treats it as a separate top-level directory.

#### Acceptance criteria

1. `ingestion/` package with extractor, cleaner, chunker, and metadata
   modules, plus a `pipeline.py` that runs end-to-end over the sample
   sources via a single command and requires no network access.
2. At least one HTML extractor and one PDF extractor, each covered by a
   unit test using local fixture files.
3. Cleaner strips boilerplate/whitespace while preserving headings, lists,
   and URLs — covered by a before/after unit test.
4. Chunker produces chunks within the ~300–700 token target range
   (approximate tokenization is acceptable and must be documented), with
   configurable overlap — covered by a unit test with bounds assertions.
5. Every output chunk carries the full roadmap §15 metadata schema
   (document_id, chunk_id, title, source, department, document_type, url,
   published_date, updated_date, effective_date, expiration_date,
   academic_year, access_level, version) — covered by a schema test.
6. Change detection: re-running the pipeline on unchanged sources is a
   no-op (same output, same version); changing one source's content bumps
   only that document's version and regenerates only its chunks — covered
   by a test that runs the pipeline twice with a mutated fixture.
7. A source manifest entry with `access_level: restricted` causes the
   pipeline to skip that source and record why, not ingest it.
8. `poetry run pytest`, `poetry run ruff check .`, `poetry run black
   --check .` all pass inside `ingestion/`.
9. `ingestion/README.md` (or root README update) documents how to run the
   pipeline, what the sample data is, and the output format/location.
10. CI updated with an `ingestion` job running the same lint/format/test
    commands.

---

### MODULE 2 — Embedding & Vector Search

#### Goal

Generate real semantic embeddings for Module 1's chunk output and make
them queryable (roadmap §17, §21-22).

#### Interface decisions

* Embedding + indexing extends the offline `ingestion/` pipeline (it
  continues extract→clean→chunk→metadata with →embed→index, matching
  roadmap §17's single pipeline diagram), rather than being a new
  top-level package.
* Embedding library: **fastembed** (ONNX-based, ships with `qdrant-client`
  integration, no torch dependency) running a small local model — real
  local semantic embeddings per `EMBEDDING_PROVIDER=local`, lighter than
  raw sentence-transformers.
* Vector DB: Qdrant (already in `docker-compose.yml`). Tests use
  `qdrant-client`'s in-memory mode (`location=":memory:"`) — no live
  service or Docker required in CI.
* Deviation from Modules 0-1: unlike those modules, this module's
  real-embedding integration test needs network access once, to download
  the ONNX model — cached in CI via `actions/cache`. Pure ranking/filter
  logic stays covered by fast, network-free unit tests using a stub
  `Embedder`.

#### Acceptance criteria

1. `ingestion/ingestion/embedder.py` — an `Embedder` protocol plus a
   `FastEmbedEmbedder` implementation.
2. `ingestion/ingestion/vector_store.py` — Qdrant client wrapper:
   create-collection-if-missing, upsert by `chunk_id` (idempotent — rerun
   produces no duplicate points).
3. Pipeline extended (or a new `ingestion/ingestion/index.py`) to read
   `output/chunks.jsonl`, embed, and upsert into Qdrant.
4. `backend/app/retrieval/vector_search.py` — `semantic_search(query,
   top_k, filters)` embeds the query and returns scored results with
   metadata + content, supporting metadata filters (e.g. `document_type`,
   `access_level`).
5. Unit tests for ranking/filtering use a deterministic stub `Embedder`
   (no network).
6. One integration test uses the real `FastEmbedEmbedder` + in-memory
   Qdrant to index sample chunks and assert a semantically relevant query
   ranks the right chunk first.
7. `poetry run pytest`, `ruff check`, `black --check` pass in both
   `ingestion/` and `backend/`.
8. README documents the embedding model choice and how to index/query.

---

### MODULE 3 — Hybrid Retrieval

#### Goal

Combine semantic search with keyword search, metadata filtering, and
reranking into one retrieval function; add query classification (roadmap
§10-14, §24-25).

#### Interface decisions

* BM25's corpus is loaded from Qdrant payloads (`load_records_from_qdrant`),
  not from `ingestion/`'s local `chunks.jsonl` — Qdrant is kept as the
  single source of truth for chunk content (per Module 2), and `backend/`
  stays independent of the `ingestion/` package.
* Reranking uses a documented scoring combination (RRF score boosted by
  query/title word overlap), not a cross-encoder — avoids another model
  download for a corpus this small, per the acceptance criterion's own
  "otherwise a documented scoring combination" allowance.
* Same network exception as Module 2: BM25/RRF/reranker/classifier unit
  tests are network-free, but the one Recall@K/MRR quality benchmark test
  uses the real embedding model (already required and cached by Module 2)
  — "no network required" below refers to that unit-test majority, not
  the single quality benchmark.

#### Acceptance criteria

1. `backend/app/retrieval/keyword_search.py` — BM25 over chunk content
   (pure-Python `rank_bm25` or equivalent, no network).
2. `backend/app/retrieval/hybrid.py` — `hybrid_search(query, top_k,
   filters)` merges semantic + keyword candidates (e.g. reciprocal rank
   fusion) before reranking.
3. `backend/app/retrieval/reranker.py` — reranks the merged candidate set;
   uses a lightweight local reranker if one fits without heavy new
   dependencies, otherwise a documented scoring combination.
4. `backend/app/retrieval/query_classifier.py` — rule/keyword-based
   classification into roadmap §10's intents (no LLM call — that's Module
   5).
5. Retrieval quality measured with Recall@K/MRR against a small
   hand-labeled query→expected-chunk set built from Module 1's sample
   sources — a test asserts a minimum threshold.
6. Unit tests (BM25, RRF, reranker, classifier), lint, format pass with no
   network required; see the interface decision above for the one
   quality-benchmark exception.
7. README documents the retrieval architecture and how to evaluate it.

---

### MODULE 4 — RBAC (Role-Based Access Control)

#### Goal

Enforce roadmap §9's role-based document filtering end-to-end.

#### Interface decisions

* Role→access_level mapping (not a per-chunk `allowed_roles` list as
  roadmap §9's example JSON sketches): `public` is visible to all four
  roles; `authorized` is visible to faculty/staff/admin only, not
  students; `restricted` is visible to no one (defense in depth — it
  should never reach Qdrant at all per Module 1 AC7). Adding a real
  per-chunk `allowed_roles` field would mean changing the already-shipped
  `ChunkRecord` schema from Modules 1-3; the coarser access_level mapping
  covers the same policy intent without that migration.
* `hybrid_search`'s new `roles` param filters the fused candidate list
  before reranking/truncation (`app/retrieval/access_control.py`), so a
  disallowed chunk can never occupy a `top_k` slot just because it scored
  higher than a permitted one.
* A protected `GET /me` endpoint (`app/api/me.py`) was added as the
  concrete proof for AC4 — the first real usage of `get_current_user`,
  ahead of Module 5's `/chat` endpoint.

#### Acceptance criteria

1. `backend/app/core/auth.py` — JWT issue/verify with a `role` claim
   (student/faculty/staff/admin), using `JWT_SECRET`.
2. `backend/app/models/` — minimal `User` model + role enum.
3. `hybrid_search` (Module 3) accepts `roles: list[str]` and filters out
   any chunk the requester's role doesn't satisfy — a test proves a
   student-role query never returns a staff-only chunk even when it's the
   best semantic match.
4. A FastAPI dependency (`get_current_user`) rejects unauthenticated/
   invalid-token requests with 401.
5. Tests, lint, format pass.
6. README documents the auth model and role→access_level mapping.

---

### MODULE 5 — LLM Generation & Citation Verification

#### Goal

Wire retrieval into an LLM for grounded, cited answers, verified before
returning to the user (roadmap §23, §26-28, §33).

#### Interface decisions

* Only `LLM_PROVIDER=local` (Ollama) is actually implemented behind the
  `LLMClient` interface; an unsupported provider raises `NotImplementedError`
  with a clear message rather than silently no-op'ing. No Ollama
  installation exists in this dev environment, so it's untested by the
  suite — README documents the manual setup.
* Grounding verification (`app/verification/grounding.py`) is a
  **deterministic lexical-overlap check** (cited evidence vs. answer word
  overlap ≥ 0.3), not an LLM-judge — avoids a second model call/cost for
  every response and keeps verification itself deterministic and
  network-free to test. It's a real, non-trivial check: manually proven
  against live Qdrant retrieval to both accept a genuinely grounded
  answer and reject a fabricated one that cited a real evidence index but
  stated a date that evidence didn't contain.
* The response `Source` model matches roadmap §45's shape exactly
  (`title`, `url`, `relevance`) — internal fields like `chunk_id` are not
  exposed in the API response.
* The prompt-injection test (AC6) verifies the *structural* half of the
  defense — that the static `SYSTEM_PROMPT` constant can never be altered
  by retrieved content, and that such content is confined to a clearly
  labeled untrusted evidence block. Whether a real LLM actually honors
  that separation isn't testable without a live model call, so that part
  is out of scope for the automated suite.

#### Acceptance criteria

1. `backend/app/generation/llm_client.py` — provider-abstracted LLM
   client (`LLM_PROVIDER=local` via Ollama, or an API provider) behind one
   interface.
2. `backend/app/generation/prompt.py` — system prompt enforcing roadmap
   §23's grounding rules and §33's prompt-injection defense (retrieved
   content is data, never instructions).
3. `backend/app/verification/grounding.py` (claims are supported by
   evidence) and `backend/app/verification/citations.py` (every citation
   maps to an actually-retrieved chunk, no fabricated citations).
4. No-answer behavior: insufficient evidence returns the roadmap §28
   refusal instead of a fabricated answer — covered by a test with an
   out-of-scope sample question.
5. `POST /chat` wires classification → retrieval → generation →
   verification → response with sources, matching roadmap §45's shape.
6. Prompt-injection test: a chunk containing an embedded "ignore previous
   instructions" string must not change model behavior.
7. Tests use a stubbed/mocked LLM client so CI stays network-free and
   deterministic; a documented manual path covers running against a real
   local Ollama model.
8. README documents the chat endpoint and its request/response shape.

---

### MODULE 6 — Evaluation & Observability

#### Goal

Measurable retrieval/generation quality and structured logging (roadmap
§35-40).

#### Interface decisions

* `evaluation/` is its own top-level poetry package (matching
  `ingestion/`/`backend/`'s precedent), depending on `backend/` via a
  local path dependency (`campusai-backend @ file:../backend`) so it can
  import `app.retrieval`/`app.verification` directly rather than
  reimplementing them.
* Generation-quality metrics (faithfulness, citation correctness,
  hallucination catch rate, abstention quality) are measured **via the
  verification layer** (`app/verification/grounding.py`,
  `app/verification/citations.py`) against synthetically constructed
  good/bad answers, not a live LLM call — there's no Ollama installed in
  CI or most dev environments. This measures whether the verification
  layer correctly passes truthful, evidence-grounded answers and rejects
  fabricated ones at dataset scale, which is the actual reliability
  mechanism `POST /chat` depends on — not literally "is the LLM's prose
  good," which isn't testable without a live model.
* The dataset (`evaluation/datasets/eval_questions.json`) has 30
  questions, not the roadmap's aspirational 50-100 (§39) — the sample
  corpus is only 5 synthetic documents (Module 1), so padding past what
  those documents can meaningfully support would be duplication, not
  real coverage. 30 spans every category the corpus supports plus 8
  genuine no-answer cases; see `evaluation/README.md`.
* CI regression gate is a pytest file with per-metric floor assertions
  (`evaluation/tests/test_evaluate.py`), reusing the same
  `poetry run pytest -q` pattern every other job already uses, rather
  than a bespoke script-output-parsing CI step.

#### Acceptance criteria

1. `evaluation/datasets/` — eval question set (extends Module 3's set
   toward the roadmap's 50-100 question target; spans categories,
   including no-answer/ambiguous cases).
2. `evaluation/evaluate.py` — computes Recall@K, Precision@K, MRR, Hit
   Rate (retrieval) and faithfulness/citation-correctness/abstention
   quality (generation, via Module 5's verification checks); outputs a
   report.
3. Backend structured logging (query, intent, retrieved doc ids + scores,
   latency, verification result); a real observability backend (e.g.
   Langfuse) is documented as a follow-on, not a hard dependency.
4. CI runs the evaluation suite against the sample corpus and fails the
   build if scores regress below a defined floor.
5. README documents how to run evaluation and read the report.

---

### MODULE 7 — Frontend (Chat UI)

#### Goal

Replace Module 0's placeholder page with the real chat UI (roadmap
§41-43).

#### Interface decisions

* No user-registration/login module exists (none of Modules 0-6 built
  one). Added `POST /auth/demo-login` (`backend/app/api/auth.py`): given
  a role, mints a token for a fixed demo user of that role, no
  credentials. Clearly documented in its own docstring as a portfolio-only
  mechanism, never a pattern for real deployment. The frontend's
  `RoleSelector` calls it instead of a real sign-in form.
* `POST /feedback` (`backend/app/api/feedback.py`) has no persistence
  layer to write to (no Postgres/ORM module exists) — it records
  feedback as a structured log event, the same mechanism Module 6 uses
  for chat requests, rather than introducing a database dependency out
  of scope for this module.
* CORS middleware added to `backend/app/main.py` (dev-friendly default:
  `http://localhost:3000`) — needed once a real browser client exists.
* Conversation history and the demo session (role + token) are both
  stored in `sessionStorage` (`frontend/src/lib/storage.ts`), per
  roadmap §42's "initial version" guidance.
* **Bug found and fixed during manual verification**: an initial
  implementation used a separate "load messages on mount" effect plus a
  "save messages on change" effect; React Strict Mode's dev-mode double
  effect invocation exposed a real race where the save effect's first
  run captured the pre-load `[]` closure and overwrote real
  `sessionStorage` history with an empty array before the load effect's
  state update landed. Fixed by using a lazy `useState` initializer
  (`useState(() => loadMessages())`) instead of a separate load effect,
  which is safe here specifically because `ChatWindow` only ever mounts
  client-side, after `page.tsx` has already confirmed a session exists
  (never during SSR) — see the comment in `ChatWindow.tsx`.
* **Manually verified end-to-end with a real local LLM**, not just
  mocks: installed Ollama (`brew install ollama`), pulled `llama3.2`,
  and drove the actual running app in a browser — real Qdrant retrieval,
  real local generation, real citation/grounding verification, a
  correctly-refused answer when the small model's response didn't meet
  the grounding bar, correctly-grounded cited answers with clickable
  sources on other queries, working feedback buttons (confirmed via the
  backend's structured log), and confirmed conversation history now
  survives a page refresh after the fix above.

#### Acceptance criteria

1. Chat interface: message list, input box, source citations (roadmap
   §41 mockup), thumbs up/down feedback (§40).
2. Calls the backend's `/chat` endpoint (Module 5); streaming is a bonus,
   single-shot request/response is acceptable for this module.
3. `POST /feedback` wired from the UI to a backend endpoint that records
   it.
4. Conversation history stored client-side (session-based) per roadmap
   §42's "initial version" guidance.
5. Component tests for the chat flow; lint, format, build pass.
6. README/screenshots document the UI.

---

### MODULE 8 — Scheduled Ingestion

#### Goal

Turn Module 1's manual pipeline into a recurring, automated job (roadmap
§31).

#### Acceptance criteria

1. A scheduled GitHub Actions workflow runs ingestion (Module 1) +
   embedding/indexing (Module 2) on a cron schedule.
2. The workflow fails visibly (and is easy to notice) if the pipeline
   errors.
3. A live scheduled run demonstrates idempotency (relies on Module 1's
   already-tested change detection).
4. README documents the schedule and how to trigger it manually.
