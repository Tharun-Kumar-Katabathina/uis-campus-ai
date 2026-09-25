from fastapi.testclient import TestClient

from app.core.auth import decode_access_token
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
