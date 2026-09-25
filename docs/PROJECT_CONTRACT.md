# UIS CampusAI — Multi-Agent Development Architecture

> This is the shared project contract referenced by `CLAUDE.md`. Every Claude Code
> session working on this repo should read this file before making changes.
> **Note:** this document is truncated at the end of Module 0's acceptance
> criteria in the source it was authored from — Modules 1+ are not yet defined.
> Append them here as they're written so this stays the single source of truth.

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

### MODULE 2+ — Not yet defined

> Add the remaining modules here (suggested from §1's requirement list:
> Embedding & Vector Search, Hybrid Retrieval, RBAC, LLM Generation &
> Citation Verification, Evaluation & Observability, Frontend, Scheduled
> Ingestion) before starting parallel development per §9.
