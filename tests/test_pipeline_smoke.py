from pathlib import Path

import fitz

from pdf2md_rag.config import PipelineConfig
from pdf2md_rag.pipeline import ingest_pdf


def test_ingest_pdf_end_to_end_with_hash_embedder(tmp_path: Path) -> None:
    pdf_path = tmp_path / "demo.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Lasso lookup protocol makes lookup arguments efficient.")
    page = doc.new_page()
    page.insert_text((72, 72), "This second page mentions RAG chunking and vector storage.")
    doc.save(pdf_path)
    doc.close()

    config = PipelineConfig(
        markdown_dir=tmp_path / "markdown",
        chroma_dir=tmp_path / "chroma",
        manifest_dir=tmp_path / "manifests",
        collection_name="smoke-test",
        embedder_type="hash",
        hash_embedding_dimensions=64,
        chunk_size=120,
        chunk_overlap=20,
    )

    result = ingest_pdf(pdf_path, config)

    assert result.page_count == 2
    assert result.chunk_count >= 1
    assert Path(result.markdown_path).exists()
    assert Path(result.manifest_path).exists()

