from fastapi.testclient import TestClient

from app.core.auth import create_access_token
from app.main import app
from app.models.user import Role

client = TestClient(app)


def test_me_requires_authentication():
    response = client.get("/me")
    assert response.status_code == 401


def test_me_rejects_invalid_token():
    response = client.get("/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401


def test_me_returns_user_for_valid_token():
    token = create_access_token("user-42", Role.FACULTY)

    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {"user_id": "user-42", "role": "faculty"}
