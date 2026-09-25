import os
from pathlib import Path
from typing import Protocol

DEFAULT_MODEL_NAME = "BAAI/bge-small-en-v1.5"
VECTOR_SIZE = 384
# fastembed defaults to a system-tmpdir cache, which doesn't persist
# across CI runs. Pin it somewhere actions/cache can actually key on.
DEFAULT_CACHE_DIR = str(Path(os.path.expanduser("~")) / ".cache" / "fastembed")


class Embedder(Protocol):
    """Anything that turns text into fixed-size dense vectors."""

    def embed(self, texts: list[str]) -> list[list[float]]: ...


class FastEmbedEmbedder:
    """Real local semantic embeddings via fastembed (ONNX runtime, no
    torch). Downloads model weights from Hugging Face on first use —
    the one place in this package that needs network access."""

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME, cache_dir: str = DEFAULT_CACHE_DIR):
        from fastembed import TextEmbedding

        self._model = TextEmbedding(model_name=model_name, cache_dir=cache_dir)

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [vector.tolist() for vector in self._model.embed(texts)]
