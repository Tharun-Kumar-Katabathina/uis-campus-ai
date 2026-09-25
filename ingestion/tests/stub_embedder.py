import hashlib


class StubEmbedder:
    """Deterministic, offline, non-semantic embedder for unit tests that
    only need to exercise indexing/search/filtering plumbing — not real
    semantic quality. See test_index_integration.py for the one test that
    uses the real FastEmbedEmbedder."""

    def __init__(self, dim: int = 8):
        self.dim = dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dim
        for word in text.lower().split():
            digest = int(hashlib.sha256(word.encode()).hexdigest(), 16)
            vector[digest % self.dim] += 1.0
        norm = sum(v * v for v in vector) ** 0.5 or 1.0
        return [v / norm for v in vector]
