# Evaluation

Measures retrieval and generation-reliability quality against a
hand-labeled question set (roadmap §35-40) — this is the regression gate
CI runs on every push; see `docs/PROJECT_CONTRACT.md` Module 6.

## Running it

```bash
poetry install     # installs backend/ as a local editable dependency
poetry run python evaluate.py
```

```text
(grounding lexical-overlap floor: 0.3)
Questions: 30 (22 answerable, 8 no-answer)
Retrieval:
  Recall@3:    0.955
  Precision@3: 0.318
  MRR:         0.909
  Hit Rate:    1.000
Generation reliability (via verification layer):
  Faithfulness rate:         1.000
  Citation correctness rate: 1.000
  Hallucination catch rate:  1.000
  Abstention quality:        1.000
```

`poetry run pytest` runs the same evaluation as a regression gate
(`tests/test_evaluate.py`) — every metric has a floor set with margin
below the measured baseline above; CI fails if any metric regresses past
its floor.

## Dataset (`datasets/eval_questions.json`)

30 hand-labeled questions: 22 answerable (spanning academic, library,
administrative/graduation, organizations, and policy/registration — the
5 categories the Module 1 sample corpus actually covers) plus 8
deliberate no-answer questions (private records, future tuition,
confidential procedures — roadmap §54's failure-case examples).

This is smaller than the roadmap's aspirational 50-100 question target
(§39) — deliberately: the sample corpus is 5 synthetic documents (Module
1), so a 50-100 question set would mostly be near-duplicate phrasings of
the same handful of facts, not a meaningfully broader test. 30 questions
across every category the corpus supports, plus real no-answer cases, is
an honest "extends toward" that target rather than padding for its own
sake. Growing the dataset further is a natural next step once real
ingested content exists (Module 8 / production sources).

## Methodology

**Retrieval metrics** (`evaluation/metrics.py`, roadmap §37) — Recall@3,
Precision@3, MRR, Hit Rate — are computed the standard way: run
`hybrid_search` for each answerable question, compare the ranked
`document_id`s against the expected one.

**Generation reliability is measured via the verification layer, not a
live LLM call** (documented interface decision, `docs/PROJECT_CONTRACT.md`
Module 6): there's no Ollama installation in CI or most dev environments,
so "faithfulness" can't mean "ask an LLM to judge the LLM's answer."
Instead, for each answerable question:

- A **good answer** is built directly from the top retrieved chunk's own
  content, citing it — `verify_answer()` should accept it
  (**faithfulness rate**) and `validate_citations()` should accept its
  citation (**citation correctness rate**).
- A **bad answer** cites the same real chunk but states an unrelated
  claim with ~zero lexical overlap with it — `verify_answer()` should
  reject it (**hallucination catch rate**).

For no-answer questions, a **confidently-wrong answer** is built the same
way over whatever (necessarily irrelevant) evidence retrieval returns;
**abstention quality** is the fraction where either no evidence came back
at all, or that confidently-wrong answer was correctly rejected — i.e.
the same defense-in-depth mechanism `POST /chat` actually relies on for
out-of-scope questions (see `backend/README.md`'s Module 5 section) is
what's being measured here, at dataset scale rather than a handful of
hand-picked unit tests.

This means the "generation" metrics here are really measuring **the
verification layer's ability to pass good answers and reject bad ones
over realistic evidence** — a real, meaningful, network-free
(mostly — see below) signal, distinct from asking whether a live LLM
writes good prose, which this project can't test without Ollama
installed.

## Corpus & network

`evaluation/evaluation/corpus.py` duplicates the same 5-document sample
corpus `backend/tests/test_retrieval_quality.py` uses (documented, small,
deliberate duplication — same precedent as the embedder classes
duplicated between `ingestion/` and `backend/`). Retrieval uses the real
embedding model (`fastembed`, `BAAI/bge-small-en-v1.5`) against an
in-memory Qdrant instance, so — like Module 2/3's real-model tests —
running this needs network once to download model weights (cached
afterward; CI caches `~/.cache/fastembed`).

## Development

```bash
poetry run pytest -q          # regression gate + unit tests for metrics.py
poetry run ruff check .       # lint
poetry run black --check .    # format check
```
