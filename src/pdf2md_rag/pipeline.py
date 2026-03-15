from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .chunking import chunk_markdown
from .config import PipelineConfig
from .embeddings import build_embedder
from .pdf_to_markdown import extract_markdown
from .vectorstore import upsert_chunks


@dataclass(slots=True)
class IngestResult:
    pdf_path: str
    markdown_path: str
    manifest_path: str
    collection_name: str
    chunk_count: int
    vector_count: int
    page_count: int
    embedder_type: str
    embedding_model: str


def ingest_pdf(pdf_path: str | Path, config: PipelineConfig) -> IngestResult:
    config.markdown_dir.mkdir(parents=True, exist_ok=True)
    config.chroma_dir.mkdir(parents=True, exist_ok=True)
    config.manifest_dir.mkdir(parents=True, exist_ok=True)

    document = extract_markdown(pdf_path)
    markdown_path = config.markdown_dir / f"{document.source_path.stem}.md"
    markdown_path.write_text(document.text, encoding="utf-8")

    chunks = chunk_markdown(
        document,
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap,
    )
    texts = [chunk.text for chunk in chunks]
    embedder = build_embedder(
        embedder_type=config.embedder_type,
        model_name=config.embedding_model,
        hash_dimensions=config.hash_embedding_dimensions,
    )
    embeddings = embedder.embed_texts(texts)
    vector_summary = upsert_chunks(
        chunks=chunks,
        embeddings=embeddings,
        persist_directory=config.chroma_dir,
        collection_name=config.collection_name,
    )

    result = IngestResult(
        pdf_path=str(document.source_path),
        markdown_path=str(markdown_path),
        manifest_path=str(config.manifest_dir / f"{document.source_path.stem}.json"),
        collection_name=config.collection_name,
        chunk_count=len(chunks),
        vector_count=vector_summary["count"],
        page_count=document.page_count,
        embedder_type=config.embedder_type,
        embedding_model=config.embedding_model,
    )

    manifest_payload: dict[str, Any] = asdict(result)
    manifest_payload["chunk_preview"] = [
        {
            "chunk_id": chunk.chunk_id,
            "metadata": chunk.metadata,
            "preview": chunk.text[:240],
        }
        for chunk in chunks[:20]
    ]
    Path(result.manifest_path).write_text(
        json.dumps(manifest_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return result

