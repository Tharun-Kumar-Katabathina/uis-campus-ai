import httpx
import pytest

from app.core.config import settings
from app.generation.llm_client import OllamaLLMClient, get_llm_client


def test_get_llm_client_returns_ollama_client_for_local_provider():
    original = settings.llm_provider
    settings.llm_provider = "local"
    try:
        client = get_llm_client()
        assert isinstance(client, OllamaLLMClient)
    finally:
        settings.llm_provider = original


def test_get_llm_client_raises_for_unsupported_provider():
    original = settings.llm_provider
    settings.llm_provider = "some_future_hosted_provider"
    try:
        with pytest.raises(NotImplementedError):
            get_llm_client()
    finally:
        settings.llm_provider = original


def test_ollama_client_posts_chat_messages_and_returns_content(monkeypatch):
    captured = {}

    def fake_post(url, json, timeout):
        captured["url"] = url
        captured["json"] = json
        return httpx.Response(
            200,
            json={"message": {"content": "Fall registration opens July 6 [1]."}},
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(httpx, "post", fake_post)

    client = OllamaLLMClient(model="test-model", base_url="http://fake-ollama:11434")
    result = client.generate("system instructions", "user question with evidence")

    assert result == "Fall registration opens July 6 [1]."
    assert captured["url"] == "http://fake-ollama:11434/api/chat"
    assert captured["json"]["model"] == "test-model"
    assert captured["json"]["messages"] == [
        {"role": "system", "content": "system instructions"},
        {"role": "user", "content": "user question with evidence"},
    ]
