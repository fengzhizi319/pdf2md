from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Protocol


class Embedder(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


@dataclass(slots=True)
class HashingEmbedder:
    dimensions: int = 384

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        values = [0.0] * self.dimensions
        encoded = text.encode("utf-8")
        digest_stream = b""
        while len(digest_stream) < self.dimensions * 4:
            encoded = hashlib.sha256(encoded).digest()
            digest_stream += encoded
        for index in range(self.dimensions):
            raw = digest_stream[index * 4 : (index + 1) * 4]
            value = int.from_bytes(raw, byteorder="big", signed=False)
            values[index] = (value / 2**32) * 2 - 1
        norm = sum(value * value for value in values) ** 0.5 or 1.0
        return [value / norm for value in values]


@dataclass(slots=True)
class SentenceTransformerEmbedder:
    model_name: str
    _model: Any = field(init=False, repr=False)

    def __post_init__(self) -> None:
        try:
            import torch
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ImportError(
                "sentence-transformers and torch are required for the default embedder"
            ) from exc

        device = "mps" if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available() else "cpu"
        self._model = SentenceTransformer(self.model_name, device=device)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        embeddings = self._model.encode(texts, normalize_embeddings=True)
        return [embedding.tolist() for embedding in embeddings]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]


def build_embedder(
    embedder_type: str,
    model_name: str,
    hash_dimensions: int = 384,
) -> Embedder:
    normalized = embedder_type.strip().lower()
    if normalized == "hash":
        return HashingEmbedder(dimensions=hash_dimensions)
    if normalized in {"sentence-transformers", "sentence_transformers", "st"}:
        return SentenceTransformerEmbedder(model_name=model_name)
    raise ValueError(f"Unsupported embedder_type: {embedder_type}")
