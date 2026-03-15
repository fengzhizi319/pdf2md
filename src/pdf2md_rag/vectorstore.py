from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import Chunk


def upsert_chunks(
    chunks: list[Chunk],
    embeddings: list[list[float]],
    persist_directory: str | Path,
    collection_name: str,
) -> dict[str, Any]:
    if len(chunks) != len(embeddings):
        raise ValueError("chunks and embeddings must have the same length")

    import chromadb

    persist_path = Path(persist_directory)
    persist_path.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(persist_path))
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )
    collection.upsert(
        ids=[chunk.chunk_id for chunk in chunks],
        documents=[chunk.text for chunk in chunks],
        metadatas=[chunk.metadata for chunk in chunks],
        embeddings=embeddings,
    )
    count = collection.count()
    return {
        "collection_name": collection_name,
        "persist_directory": str(persist_path),
        "count": count,
    }


def query_collection(
    question: str,
    query_embedding: list[float],
    persist_directory: str | Path,
    collection_name: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    import chromadb

    client = chromadb.PersistentClient(path=str(Path(persist_directory)))
    collection = client.get_collection(collection_name)
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    rows: list[dict[str, Any]] = []
    ids = result.get("ids", [[]])[0]
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    for chunk_id, document, metadata, distance in zip(ids, documents, metadatas, distances):
        rows.append(
            {
                "id": chunk_id,
                "document": document,
                "metadata": metadata,
                "distance": distance,
                "question": question,
            }
        )
    return rows
