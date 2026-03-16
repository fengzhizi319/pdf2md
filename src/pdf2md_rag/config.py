from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MARKDOWN_DIR = PROJECT_ROOT / "pdf"
DEFAULT_CHROMA_DIR = PROJECT_ROOT / "data/chroma"
DEFAULT_MANIFEST_DIR = PROJECT_ROOT / "data/manifests"


@dataclass(slots=True)
class PipelineConfig:
    markdown_dir: Path = DEFAULT_MARKDOWN_DIR
    chroma_dir: Path = DEFAULT_CHROMA_DIR
    manifest_dir: Path = DEFAULT_MANIFEST_DIR
    collection_name: str = "pdf-knowledge-base"
    chunk_size: int = 1200
    chunk_overlap: int = 200
    embedder_type: str = "sentence-transformers"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    batch_size: int = 32
    hash_embedding_dimensions: int = 384
