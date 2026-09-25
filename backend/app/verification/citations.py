import re

from pydantic import BaseModel

from app.retrieval.vector_search import SearchResult

_CITATION_RE = re.compile(r"\[(\d+)\]")


class Source(BaseModel):
    title: str
    url: str
    relevance: float


def extract_citation_indices(answer: str) -> list[int]:
    """1-based indices referenced by the answer, e.g. "...[1]... [2]" -> [1, 2]."""
    return sorted({int(m) for m in _CITATION_RE.findall(answer)})


def validate_citations(answer: str, evidence: list[SearchResult]) -> bool:
    """False if the answer cites an index that doesn't correspond to any
    retrieved evidence — i.e. a fabricated citation."""
    indices = extract_citation_indices(answer)
    return all(1 <= i <= len(evidence) for i in indices)


def citations_to_sources(answer: str, evidence: list[SearchResult]) -> list[Source]:
    """Only the citations the answer actually used, in citation order —
    not the full evidence list, so a response never implies support from
    a chunk the model didn't cite."""
    sources = []
    for i in extract_citation_indices(answer):
        if 1 <= i <= len(evidence):
            chunk = evidence[i - 1]
            sources.append(Source(title=chunk.title, url=chunk.url, relevance=chunk.score))
    return sources
