from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.core.auth import create_access_token
from app.core.config import settings
from app.models.user import Role

router = APIRouter()


class DemoLoginRequest(BaseModel):
    role: Role


class DemoLoginResponse(BaseModel):
    access_token: str
    role: Role


@router.post("/auth/demo-login")
def demo_login(request: DemoLoginRequest) -> DemoLoginResponse:
    """No real user accounts exist (no module in docs/PROJECT_CONTRACT.md
    covers registration/login) — this mints a token for a fixed demo
    user of the chosen role, so the frontend (Module 7) can demonstrate
    role-filtered chat without building a full auth system.

    SECURITY: this endpoint hands out a valid token for ANY requested
    role with no authentication at all — an unauthenticated caller could
    otherwise mint an "admin" token and bypass RBAC entirely. It is
    gated to non-production environments only; APP_ENV must be
    "development" for it to respond. Never remove this gate."""
    if settings.app_env != "development":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    token = create_access_token(f"demo-{request.role.value}", request.role)
    return DemoLoginResponse(access_token=token, role=request.role)
