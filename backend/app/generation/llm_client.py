from typing import Protocol

import httpx

from app.core.config import settings


class LLMClient(Protocol):
    def generate(self, system_prompt: str, user_prompt: str) -> str: ...


class OllamaLLMClient:
    """LLM_PROVIDER=local — calls a local Ollama server. Requires Ollama
    running with the given model pulled; see backend/README.md for the
    manual setup (not exercised by the network-free test suite)."""

    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = httpx.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False,
            },
            timeout=60.0,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]


def get_llm_client() -> LLMClient:
    """FastAPI dependency provider. Only LLM_PROVIDER=local is
    implemented; a hosted API provider would add a client class here
    behind the same LLMClient interface, keeping the app provider-
    independent (roadmap §48-49)."""
    if settings.llm_provider == "local":
        return OllamaLLMClient()
    raise NotImplementedError(
        f"LLM_PROVIDER={settings.llm_provider!r} is not implemented. "
        "Only 'local' (Ollama) is currently supported."
    )
