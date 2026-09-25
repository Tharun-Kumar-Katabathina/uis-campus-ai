import json

from fastapi.testclient import TestClient

import app.api.chat as chat_module
from app.core.auth import create_access_token
from app.generation.llm_client import get_llm_client
from app.main import app
from app.models.user import Role
from app.retrieval.vector_search import SearchResult
from tests.fake_llm_client import FakeLLMClient

client = TestClient(app)


def _evidence() -> list[SearchResult]:
    return [
        SearchResult(
            score=0.87,
            chunk_id="academic_calendar_chunk_000",
            document_id="academic_calendar",
            title="2026-2027 Academic Calendar",
            content="Fall registration opens on July 6, 2026.",
            url="https://example.edu/calendar",
            source="Test",
            department="Registrar",
            document_type="academic_calendar",
            access_level="public",
            version="1.0",
        )
    ]


def test_chat_logs_a_structured_json_event(monkeypatch, caplog):
    monkeypatch.setattr(chat_module, "hybrid_search", lambda *a, **kw: _evidence())
    app.dependency_overrides[get_llm_client] = lambda: FakeLLMClient(
        "Fall registration opens on July 6, 2026 [1]."
    )

    try:
        with caplog.at_level("INFO", logger="campusai"):
            response = client.post(
                "/chat",
                json={"message": "When does fall registration open?"},
                headers={"Authorization": f"Bearer {create_access_token('u1', Role.STUDENT)}"},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert len(caplog.records) == 1

    event = json.loads(caplog.records[0].message)
    assert event["event"] == "chat_request"
    assert event["query"] == "When does fall registration open?"
    assert event["intent"] == "registration"
    assert event["retrieved"] == [{"chunk_id": "academic_calendar_chunk_000", "score": 0.87}]
    assert event["verified"] is True
    assert isinstance(event["latency_ms"], (int, float))
    assert event["latency_ms"] >= 0
