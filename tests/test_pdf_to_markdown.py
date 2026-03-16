from pathlib import Path
import sys
import types

from pdf2md_rag.pdf_to_markdown import extract_markdown


class _FakeRendered:
    def __init__(self, markdown: str):
        self.markdown = markdown


def test_extract_markdown_uses_marker_by_default(tmp_path: Path, monkeypatch) -> None:
    pdf_path = tmp_path / "paper.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake content")

    marker_module = types.ModuleType("marker")
    converters_module = types.ModuleType("marker.converters")
    pdf_module = types.ModuleType("marker.converters.pdf")
    calls: dict[str, object] = {}

    class FakePdfConverter:
        def __init__(self, artifact_dict, config=None, **kwargs):
            calls["artifact_dict"] = artifact_dict
            calls["config"] = config or {}
            self.page_count = 3

        def __call__(self, filepath: str):
            calls["filepath"] = filepath
            return _FakeRendered("# Marker Title\n\n$$x^2+y^2=z^2$$")

    pdf_module.PdfConverter = FakePdfConverter
    marker_module.converters = converters_module
    converters_module.pdf = pdf_module

    monkeypatch.setitem(sys.modules, "marker", marker_module)
    monkeypatch.setitem(sys.modules, "marker.converters", converters_module)
    monkeypatch.setitem(sys.modules, "marker.converters.pdf", pdf_module)
    monkeypatch.setattr("pdf2md_rag.pdf_to_markdown.load_marker_models", lambda device: {"device": device})

    document = extract_markdown(pdf_path, device="mps")

    assert document.source_path == pdf_path.resolve()
    assert document.page_count == 3
    assert "$$x^2+y^2=z^2$$" in document.text
    assert calls["filepath"] == str(pdf_path.resolve())
    assert calls["artifact_dict"] == {"device": "mps"}
    assert calls["config"] == {"disable_multiprocessing": True, "output_format": "markdown"}

