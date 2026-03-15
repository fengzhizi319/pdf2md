from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class PipelineConfig:
    markdown_dir: Path = Path("data/markdown")
    chroma_dir: Path = Path("data/chroma")
    manifest_dir: Path = Path("data/manifests")
    collection_name: str = "pdf-knowledge-base"
    chunk_size: int = 1200
    chunk_overlap: int = 200
    embedder_type: str = "sentence-transformers"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    batch_size: int = 32
    hash_embedding_dimensions: int = 384

