from fastapi.testclient import TestClient

import app.api.chat as chat_module
from app.core.auth import create_access_token
from app.generation.llm_client import get_llm_client
from app.main import app
from app.models.user import Role
from app.retrieval.vector_search import SearchResult
from tests.fake_llm_client import FakeLLMClient

client = TestClient(app)


def _token(role: Role = Role.STUDENT) -> str:
    return create_access_token("user-1", role)


def _evidence() -> list[SearchResult]:
    return [
        SearchResult(
            score=0.9,
            chunk_id="academic_calendar_chunk_000",
            document_id="academic_calendar",
            title="2026-2027 Academic Calendar",
            content="Fall registration opens on July 6, 2026 for continuing students.",
            url="https://example.edu/calendar",
            source="Test",
            department="Registrar",
            document_type="academic_calendar",
            access_level="public",
            version="1.0",
        )
    ]


def test_chat_requires_authentication():
    response = client.post("/chat", json={"message": "hi"})
    assert response.status_code == 401


def test_chat_returns_no_answer_when_no_evidence(monkeypatch):
    monkeypatch.setattr(chat_module, "hybrid_search", lambda *a, **kw: [])
    # if the endpoint didn't actually short-circuit before calling the
    # LLM, this response text would leak into the answer and fail below
    app.dependency_overrides[get_llm_client] = lambda: FakeLLMClient("should never be called")

    try:
        response = client.post(
            "/chat",
            json={"message": "What will tuition be in 2035?"},
            headers={"Authorization": f"Bearer {_token()}"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["verified"] is True
    assert body["sources"] == []
    assert "couldn't verify" in body["answer"]


def test_chat_returns_grounded_cited_answer(monkeypatch):
    monkeypatch.setattr(chat_module, "hybrid_search", lambda *a, **kw: _evidence())
    app.dependency_overrides[get_llm_client] = lambda: FakeLLMClient(
        "Fall registration opens on July 6, 2026 [1]."
    )

    try:
        response = client.post(
            "/chat",
            json={"message": "When does fall registration open?"},
            headers={"Authorization": f"Bearer {_token()}"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["verified"] is True
    assert body["intent"] == "registration"
    assert body["sources"] == [
        {
            "title": "2026-2027 Academic Calendar",
            "url": "https://example.edu/calendar",
            "relevance": 0.9,
        }
    ]


def test_chat_refuses_when_answer_fails_verification(monkeypatch):
    monkeypatch.setattr(chat_module, "hybrid_search", lambda *a, **kw: _evidence())
    app.dependency_overrides[get_llm_client] = lambda: FakeLLMClient(
        "The university mascot is a friendly dragon."  # uncited, ungrounded
    )

    try:
        response = client.post(
            "/chat",
            json={"message": "When does fall registration open?"},
            headers={"Authorization": f"Bearer {_token()}"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["verified"] is False
    assert body["sources"] == []
    assert "couldn't verify" in body["answer"]


def test_chat_passes_requesters_role_into_retrieval(monkeypatch):
    captured = {}

    def fake_hybrid_search(query, top_k=5, roles=None, **kwargs):
        captured["roles"] = roles
        return []

    monkeypatch.setattr(chat_module, "hybrid_search", fake_hybrid_search)
    app.dependency_overrides[get_llm_client] = lambda: FakeLLMClient("unused")

    try:
        client.post(
            "/chat",
            json={"message": "anything"},
            headers={"Authorization": f"Bearer {_token(Role.STAFF)}"},
        )
    finally:
        app.dependency_overrides.clear()

    assert captured["roles"] == ["staff"]
