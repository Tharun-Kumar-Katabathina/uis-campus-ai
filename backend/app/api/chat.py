import time

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.core.logging import log_event
from app.generation.llm_client import LLMClient, get_llm_client
from app.generation.prompt import NO_ANSWER_MESSAGE, SYSTEM_PROMPT, build_user_prompt
from app.models.user import User
from app.retrieval.hybrid import hybrid_search
from app.retrieval.query_classifier import classify
from app.verification.citations import Source, citations_to_sources
from app.verification.grounding import verify_answer

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    verified: bool
    intent: str


def _no_answer(intent: str, verified: bool = True) -> ChatResponse:
    return ChatResponse(answer=NO_ANSWER_MESSAGE, sources=[], verified=verified, intent=intent)


def _log_chat_request(
    query: str, intent: str, evidence: list, verified: bool, started_at: float
) -> None:
    log_event(
        "chat_request",
        query=query,
        intent=intent,
        retrieved=[{"chunk_id": e.chunk_id, "score": e.score} for e in evidence],
        verified=verified,
        latency_ms=round((time.perf_counter() - started_at) * 1000, 1),
    )


@router.post("/chat")
def chat(
    request: ChatRequest,
    user: User = Depends(get_current_user),
    llm_client: LLMClient = Depends(get_llm_client),
) -> ChatResponse:
    """Roadmap §10 end-to-end flow: classify -> retrieve (role-filtered)
    -> generate -> verify -> respond with sources, or refuse (§28) if
    there's no evidence or the generated answer fails verification."""
    started_at = time.perf_counter()
    intent = classify(request.message)

    evidence = hybrid_search(request.message, top_k=5, roles=[user.role.value])
    if not evidence:
        _log_chat_request(request.message, intent, evidence, verified=True, started_at=started_at)
        return _no_answer(intent)

    user_prompt = build_user_prompt(request.message, evidence)
    answer = llm_client.generate(SYSTEM_PROMPT, user_prompt)

    verified = verify_answer(answer, evidence)
    _log_chat_request(request.message, intent, evidence, verified=verified, started_at=started_at)

    if not verified:
        return _no_answer(intent, verified=False)

    return ChatResponse(
        answer=answer,
        sources=citations_to_sources(answer, evidence),
        verified=True,
        intent=intent,
    )
