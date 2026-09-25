class FakeLLMClient:
    """Deterministic stand-in for a real LLM — keeps the test suite
    network-free. Either returns a fixed response, or if given a
    callable, computes the response from (system_prompt, user_prompt) so
    a test can assert on what the client was actually asked."""

    def __init__(self, response):
        self._response = response

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if callable(self._response):
            return self._response(system_prompt, user_prompt)
        return self._response
