from typing import Protocol

DEFAULT_MODEL_NAME = "BAAI/bge-small-en-v1.5"
VECTOR_SIZE = 384


class Embedder(Protocol):
    """Anything that turns text into fixed-size dense vectors."""

    def embed(self, texts: list[str]) -> list[list[float]]: ...


class FastEmbedEmbedder:
    """Real local semantic embeddings via fastembed (ONNX runtime, no
    torch). Downloads model weights from Hugging Face on first use —
    the one place in this package that needs network access."""

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        from fastembed import TextEmbedding

        self._model = TextEmbedding(model_name=model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [vector.tolist() for vector in self._model.embed(texts)]
