from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.core.logging import log_event
from app.models.user import User

router = APIRouter()


class FeedbackRequest(BaseModel):
    conversation_id: str | None = None
    question: str
    answer: str
    helpful: bool
    comment: str | None = None


class FeedbackResponse(BaseModel):
    status: str = "ok"


@router.post("/feedback")
def submit_feedback(
    request: FeedbackRequest, user: User = Depends(get_current_user)
) -> FeedbackResponse:
    """Roadmap §40. No feedback table exists (no Postgres/ORM module is
    in scope yet — see docs/PROJECT_CONTRACT.md), so this records
    feedback the same way chat requests are observed: a structured log
    event (Module 6). Wiring it into real storage is a natural follow-on
    once a persistence module exists."""
    log_event(
        "feedback",
        user_id=user.user_id,
        conversation_id=request.conversation_id,
        question=request.question,
        answer=request.answer,
        helpful=request.helpful,
        comment=request.comment,
    )
    return FeedbackResponse()
