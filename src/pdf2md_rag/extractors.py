"""Cross-platform PDF extractors and fallbacks.

Provides a lightweight PyMuPDF-based extractor used on non-macOS platforms
when `marker` is not installed. The extractor aims to provide a simple
Markdown-like output (page headers + plain text) so the rest of the pipeline
can continue to chunk and embed content.
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import fitz  # pymupdf

from .models import MarkdownDocument


def extract_with_pymupdf(pdf_path: str | Path) -> MarkdownDocument:
    """Extract plain text from PDF using PyMuPDF and return a MarkdownDocument.

    This is a best-effort fallback: it preserves page boundaries but does not
    attempt sophisticated layout/LaTeX recovery that Marker provides.
    """
    source_path = Path(pdf_path).expanduser().resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"PDF not found: {source_path}")

    doc = fitz.open(str(source_path))
    page_texts = []
    for i, page in enumerate(doc, start=1):
        text = page.get_text("text")
        # Simple page header to make sources identifiable in downstream code
        header = f"# Page {i}\n\n"
        page_texts.append(header + text.strip())

    markdown = "\n\n".join(page_texts).strip()
    return MarkdownDocument(source_path=source_path, text=markdown, page_count=len(doc))

