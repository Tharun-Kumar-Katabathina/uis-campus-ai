# Backend

FastAPI gateway and the live-request retrieval path. See
`docs/PROJECT_CONTRACT.md` for the full module contract.

## Retrieval architecture (Module 2 + 3)

```text
                         query
                           |
                           v
                  query_classifier.classify()
                     (roadmap §10 intent)
                           |
                           v
              +------------+------------+
              |                         |
    vector_search.semantic_search   keyword_search.KeywordIndex.search
        (fastembed + Qdrant)              (BM25 over Qdrant payloads)
              |                         |
              +------------+------------+
                           |
                           v
              hybrid.reciprocal_rank_fusion
                           |
                           v
                    reranker.rerank
              (RRF score boosted by query/title
                     word overlap)
                           |
                           v
                    top_k SearchResult
```

Qdrant (populated by `ingestion/`'s pipeline — see `ingestion/README.md`)
is the single source of truth for chunk content: both the vector index
and the BM25 corpus (`keyword_search.load_records_from_qdrant`) are built
from it, so there's nothing else to keep in sync.

- `app/retrieval/vector_search.py` — semantic search (Module 2).
- `app/retrieval/keyword_search.py` — BM25 keyword search, no network.
- `app/retrieval/hybrid.py` — `hybrid_search()`: reciprocal rank fusion of
  the two, then reranking.
- `app/retrieval/reranker.py` — a documented scoring combination (title
  word overlap boosts the fused RRF score), used instead of a
  cross-encoder to avoid another model download for this corpus size.
- `app/retrieval/query_classifier.py` — rule-based intent classification
  (roadmap §10); not LLM-based — that's Module 5.

## Evaluating retrieval quality

`tests/test_retrieval_quality.py` runs `hybrid_search` over a small
hand-labeled query → expected-document set (12 queries across the 5
sample source documents) and asserts Recall@3 ≥ 0.8 and MRR ≥ 0.6:

```bash
poetry run pytest tests/test_retrieval_quality.py -v
```

This is the one test in the suite that needs network access (to download
the real embedding model on first run — cached afterward, same model
Module 2 already requires). Every other retrieval test (`test_hybrid.py`,
`test_keyword_search.py`, `test_reranker.py`, `test_query_classifier.py`)
is network-free, using a deterministic stub embedder.

## Authentication & RBAC (Module 4)

Auth is JWT-based (`app/core/auth.py`), HS256, signed with `JWT_SECRET`.
A token carries `sub` (user id) and `role`. There is no user registration
or login endpoint yet — `create_access_token(user_id, role)` is how a
future auth flow (or a manual script) would issue one; for now it's
exercised directly by tests and can be used to mint a token for manual
API testing:

```bash
poetry run python -c "
from app.core.auth import create_access_token
from app.models.user import Role
print(create_access_token('demo-user', Role.STAFF))
"
```

`GET /me` is the first protected route — send the token as
`Authorization: Bearer <token>`; without a valid one it returns 401.

**Role → access_level mapping** (`app/retrieval/access_control.py`):

| access_level | student | faculty | staff | admin |
|---|---|---|---|---|
| `public`     | ✅ | ✅ | ✅ | ✅ |
| `authorized` | ❌ | ✅ | ✅ | ✅ |
| `restricted` | ❌ | ❌ | ❌ | ❌ (never ingested — see Module 1) |

`hybrid_search(..., roles=[user.role.value])` filters the fused candidate
list against this table before reranking, so a higher-scoring disallowed
chunk can never push out a permitted one.

`JWT_SECRET` has no default — an unset/empty secret fails loudly (PyJWT
refuses to sign with an empty key) rather than silently signing tokens
with a weak fallback. Set a real value (32+ bytes recommended) in `.env`
for local/dev use; tests set their own via `tests/conftest.py`.

## Development

```bash
poetry run pytest -q          # tests
poetry run ruff check .       # lint
poetry run black --check .    # format check
```
