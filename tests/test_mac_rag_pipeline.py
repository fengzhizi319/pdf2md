from pathlib import Path
import sys
import types

from mac_rag_pipeline import chunk_markdown_with_math_protection, parse_pdf_to_md


class _FakeRendered:
    def __init__(self, markdown: str):
        self.markdown = markdown


def test_mac_rag_pipeline_uses_marker_and_chunks(tmp_path: Path, monkeypatch) -> None:
    pdf_path = tmp_path / "math-demo.pdf"
    output_md = tmp_path / "math-demo.marker.md"
    pdf_path.write_bytes(b"%PDF-1.4 fake content")

    marker_module = types.ModuleType("marker")
    converters_module = types.ModuleType("marker.converters")
    pdf_module = types.ModuleType("marker.converters.pdf")
    calls: dict[str, object] = {}

    class FakePdfConverter:
        def __init__(self, artifact_dict, config=None, **kwargs):
            calls["artifact_dict"] = artifact_dict
            calls["config"] = config or {}
            calls["kwargs"] = kwargs
            self.page_count = 2

        def __call__(self, filepath: str):
            calls["filepath"] = filepath
            return _FakeRendered("# Title\n\nEquation block:\n\n$$a^2+b^2=c^2$$\n")

    pdf_module.PdfConverter = FakePdfConverter
    marker_module.converters = converters_module
    converters_module.pdf = pdf_module

    monkeypatch.setitem(sys.modules, "marker", marker_module)
    monkeypatch.setitem(sys.modules, "marker.converters", converters_module)
    monkeypatch.setitem(sys.modules, "marker.converters.pdf", pdf_module)
    monkeypatch.setattr("pdf2md_rag.pdf_to_markdown.load_marker_models", lambda device: {"device": device})

    markdown_text = parse_pdf_to_md(pdf_path, output_md, device="mps")
    chunks = chunk_markdown_with_math_protection(markdown_text)

    assert output_md.exists()
    assert "$$a^2+b^2=c^2$$" in markdown_text
    assert len(chunks) >= 1
    assert any("$$a^2+b^2=c^2$$" in chunk for chunk in chunks)
    assert calls["filepath"] == str(pdf_path.resolve())
    assert calls["artifact_dict"] == {"device": "mps"}
    assert calls["config"] == {"disable_multiprocessing": True, "output_format": "markdown"}


def test_chunk_markdown_with_math_protection_preserves_formula_boundaries() -> None:
    markdown_text = "# Title\n\nIntro paragraph.\n\n$$a^2+b^2=c^2$$\n\nConclusion."

    chunks = chunk_markdown_with_math_protection(markdown_text)

    assert len(chunks) >= 1
    assert any("$$a^2+b^2=c^2$$" in chunk for chunk in chunks)
