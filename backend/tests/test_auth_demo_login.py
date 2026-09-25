from fastapi.testclient import TestClient

from app.core.auth import decode_access_token
from app.core.config import settings
from app.main import app
from app.models.user import Role

client = TestClient(app)


def test_demo_login_returns_a_token_for_the_requested_role():
    response = client.post("/auth/demo-login", json={"role": "staff"})

    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "staff"

    user = decode_access_token(body["access_token"])
    assert user.role == Role.STAFF


def test_demo_login_rejects_unknown_role():
    response = client.post("/auth/demo-login", json={"role": "superadmin"})
    assert response.status_code == 422


def test_demo_login_disabled_outside_development():
    """SECURITY: this endpoint mints a valid token for any requested role
    with no authentication — it must be unreachable whenever APP_ENV
    isn't "development", or any unauthenticated caller could mint an
    admin token and bypass RBAC entirely."""
    original = settings.app_env
    settings.app_env = "production"
    try:
        response = client.post("/auth/demo-login", json={"role": "admin"})
        assert response.status_code == 404
    finally:
        settings.app_env = original
