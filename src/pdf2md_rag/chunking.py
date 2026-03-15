from __future__ import annotations

import re
import uuid
from pathlib import Path

from .models import Chunk, MarkdownDocument

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")
_PAGE_RE = re.compile(r"^##\s+Page\s+(\d+)\s*$", re.IGNORECASE)


def chunk_markdown(document: MarkdownDocument, chunk_size: int = 1200, chunk_overlap: int = 200) -> list[Chunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be >= 0")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    blocks = _split_blocks(document.text)
    chunks: list[Chunk] = []
    current_heading = "Document"
    current_page: int | None = None
    current_parts: list[str] = []
    current_length = 0

    for block in blocks:
        heading_match = _HEADING_RE.match(block)
        page_match = _PAGE_RE.match(block)
        block_heading = heading_match.group(2).strip() if heading_match else current_heading
        block_page = int(page_match.group(1)) if page_match else current_page

        if current_parts and current_length + len(block) + 2 > chunk_size:
            chunks.append(
                _build_chunk(
                    document=document,
                    heading=current_heading,
                    page=current_page,
                    text="\n\n".join(current_parts).strip(),
                    index=len(chunks),
                )
            )
            current_parts = [] if (heading_match or page_match) else _carry_overlap(current_parts, chunk_overlap)
            current_length = sum(len(part) for part in current_parts) + max(0, len(current_parts) - 1) * 2

        if len(block) > chunk_size:
            if current_parts:
                chunks.append(
                    _build_chunk(
                        document=document,
                        heading=current_heading,
                        page=current_page,
                        text="\n\n".join(current_parts).strip(),
                        index=len(chunks),
                    )
                )
                current_parts = []
                current_length = 0
            for piece in _split_large_block(block, chunk_size, chunk_overlap):
                chunks.append(
                    _build_chunk(
                        document=document,
                        heading=block_heading,
                        page=block_page,
                        text=piece,
                        index=len(chunks),
                    )
                )
            current_heading = block_heading
            current_page = block_page
            continue

        if not current_parts:
            current_heading = block_heading
            current_page = block_page

        current_parts.append(block)
        current_length += len(block) + 2

    if current_parts:
        chunks.append(
            _build_chunk(
                document=document,
                heading=current_heading,
                page=current_page,
                text="\n\n".join(current_parts).strip(),
                index=len(chunks),
            )
        )

    return chunks


def _split_blocks(markdown: str) -> list[str]:
    return [part.strip() for part in re.split(r"\n\s*\n+", markdown) if part.strip()]


def _split_large_block(block: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    pieces: list[str] = []
    start = 0
    step = chunk_size - chunk_overlap
    while start < len(block):
        end = min(len(block), start + chunk_size)
        pieces.append(block[start:end].strip())
        if end == len(block):
            break
        start += step
    return [piece for piece in pieces if piece]


def _carry_overlap(parts: list[str], chunk_overlap: int) -> list[str]:
    if chunk_overlap == 0:
        return []

    carried: list[str] = []
    total = 0
    for part in reversed(parts):
        carried.insert(0, part)
        total += len(part)
        if total >= chunk_overlap:
            break
    return carried


def _build_chunk(document: MarkdownDocument, heading: str, page: int | None, text: str, index: int) -> Chunk:
    source_name = Path(document.source_path).stem
    chunk_key = f"{source_name}-{index}-{uuid.uuid5(uuid.NAMESPACE_URL, text)}"
    return Chunk(
        chunk_id=chunk_key,
        text=text,
        metadata={
            "source_path": str(document.source_path),
            "source_name": source_name,
            "heading": heading,
            "page": page,
            "chunk_index": index,
            "text_length": len(text),
        },
    )
