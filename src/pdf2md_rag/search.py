from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .embeddings import build_embedder
from .vectorstore import query_collection


@dataclass(slots=True)
class SearchHit:
    rank: int
    chunk_id: str
    text: str
    distance: float
    score: float
    source_path: str
    source_name: str
    heading: str | None
    page: int | None
    chunk_index: int | None
    text_length: int | None

    @property
    def citation(self) -> str:
        parts = [self.source_name]
        if self.page is not None:
            parts.append(f"p.{self.page}")
        if self.heading:
            parts.append(self.heading)
        return " | ".join(parts)


@dataclass(slots=True)
class SearchResult:
    question: str
    collection_name: str
    top_k: int
    hits: list[SearchHit]
    context_text: str
    sources: list[str]
    retrieval_meta: dict[str, Any]


def search_chunks(
    question: str,
    collection_name: str,
    persist_directory: str | Path = "data/chroma",
    top_k: int = 5,
    embedder_type: str = "sentence-transformers",
    embedding_model: str = "BAAI/bge-small-en-v1.5",
    hash_dimensions: int = 384,
    max_context_chars: int = 6000,
) -> SearchResult:
    embedder = build_embedder(
        embedder_type=embedder_type,
        model_name=embedding_model,
        hash_dimensions=hash_dimensions,
    )
    rows = query_collection(
        question=question,
        query_embedding=embedder.embed_query(question),
        persist_directory=persist_directory,
        collection_name=collection_name,
        top_k=top_k,
    )
    hits = [_row_to_hit(index + 1, row) for index, row in enumerate(rows)]
    context_text = _build_context_text(question=question, hits=hits, max_context_chars=max_context_chars)
    sources = [hit.citation for hit in hits]
    return SearchResult(
        question=question,
        collection_name=collection_name,
        top_k=top_k,
        hits=hits,
        context_text=context_text,
        sources=sources,
        retrieval_meta={
            "embedding_model": embedding_model,
            "embedder_type": embedder_type,
            "persist_directory": str(Path(persist_directory)),
            "hit_count": len(hits),
            "max_context_chars": max_context_chars,
        },
    )


def _row_to_hit(rank: int, row: dict[str, Any]) -> SearchHit:
    metadata = row.get("metadata") or {}
    distance = float(row.get("distance", 1.0))
    score = max(0.0, 1.0 - distance)
    return SearchHit(
        rank=rank,
        chunk_id=str(row.get("id", "")),
        text=str(row.get("document", "")).strip(),
        distance=distance,
        score=score,
        source_path=str(metadata.get("source_path", "")),
        source_name=str(metadata.get("source_name", "unknown")),
        heading=metadata.get("heading"),
        page=metadata.get("page"),
        chunk_index=metadata.get("chunk_index"),
        text_length=metadata.get("text_length"),
    )


def _build_context_text(question: str, hits: list[SearchHit], max_context_chars: int) -> str:
    sections: list[str] = [f"Question: {question}", "Relevant context:"]
    remaining = max_context_chars

    for hit in hits:
        prefix = f"[Source {hit.rank}] {hit.citation}\n"
        body_budget = max(0, remaining - len(prefix) - 2)
        if body_budget <= 0:
            break
        excerpt = hit.text[:body_budget].strip()
        if not excerpt:
            continue
        section = f"{prefix}{excerpt}"
        sections.append(section)
        remaining -= len(section)
        if remaining <= 0:
            break

    return "\n\n".join(sections).strip()

