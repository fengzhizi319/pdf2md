from __future__ import annotations

from pathlib import Path

import fitz

from .models import MarkdownDocument


def extract_markdown(pdf_path: str | Path) -> MarkdownDocument:
    source_path = Path(pdf_path).expanduser().resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"PDF not found: {source_path}")

    try:
        import pymupdf4llm

        text = pymupdf4llm.to_markdown(str(source_path)).strip()
        if text:
            with fitz.open(source_path) as doc:
                return MarkdownDocument(
                    source_path=source_path,
                    text=text,
                    page_count=doc.page_count,
                )
    except Exception:
        pass

    with fitz.open(source_path) as doc:
        sections: list[str] = []
        for page_index, page in enumerate(doc, start=1):
            page_text = page.get_text("text").strip()
            if not page_text:
                continue
            cleaned_lines = [line.strip() for line in page_text.splitlines() if line.strip()]
            body = "\n\n".join(cleaned_lines)
            sections.append(f"## Page {page_index}\n\n{body}")

        markdown = "\n\n".join(sections).strip()
        if not markdown:
            raise ValueError(f"No extractable text found in PDF: {source_path}")

        return MarkdownDocument(
            source_path=source_path,
            text=markdown,
            page_count=doc.page_count,
        )

