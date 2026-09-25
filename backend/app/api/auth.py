from fastapi import APIRouter
from pydantic import BaseModel

from app.core.auth import create_access_token
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
    role-filtered chat without building a full auth system. Never use
    this pattern for a real deployment."""
    token = create_access_token(f"demo-{request.role.value}", request.role)
    return DemoLoginResponse(access_token=token, role=request.role)
