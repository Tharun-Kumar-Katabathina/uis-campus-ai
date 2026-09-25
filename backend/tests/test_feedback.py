import json

from fastapi.testclient import TestClient

from app.core.auth import create_access_token
from app.main import app
from app.models.user import Role

client = TestClient(app)


def test_feedback_requires_authentication():
    response = client.post(
        "/feedback",
        json={"question": "q", "answer": "a", "helpful": True},
    )
    assert response.status_code == 401


def test_feedback_logs_a_structured_event_and_returns_ok(caplog):
    token = create_access_token("user-1", Role.STUDENT)

    with caplog.at_level("INFO", logger="campusai"):
        response = client.post(
            "/feedback",
            json={
                "conversation_id": "conv-1",
                "question": "When does registration open?",
                "answer": "July 6, 2026 [1].",
                "helpful": False,
                "comment": "Wrong date",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    assert len(caplog.records) == 1
    event = json.loads(caplog.records[0].message)
    assert event["event"] == "feedback"
    assert event["user_id"] == "user-1"
    assert event["conversation_id"] == "conv-1"
    assert event["helpful"] is False
    assert event["comment"] == "Wrong date"
