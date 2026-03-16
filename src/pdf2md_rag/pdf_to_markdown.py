from __future__ import annotations

import importlib
import importlib.util
import os
from functools import lru_cache
from pathlib import Path

from .models import MarkdownDocument


def get_marker_device(preferred_device: str | None = None) -> str:
    os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")

    if preferred_device:
        os.environ["TORCH_DEVICE"] = preferred_device
        return preferred_device

    env_device = os.environ.get("TORCH_DEVICE")
    if env_device:
        return env_device

    torch_spec = importlib.util.find_spec("torch")
    if torch_spec is None:
        device = "cpu"
    else:
        torch = importlib.import_module("torch")
        device = "mps" if torch.backends.mps.is_available() else "cpu"

    os.environ["TORCH_DEVICE"] = device
    return device


@lru_cache(maxsize=2)
def load_marker_models(device: str):
    try:
        from marker.models import create_model_dict
    except ImportError as exc:
        raise ImportError("Marker 未安装。请先在虚拟环境中安装 marker-pdf。") from exc

    return create_model_dict(device=device)


def extract_markdown(pdf_path: str | Path, device: str | None = None) -> MarkdownDocument:
    """使用 Marker 从 PDF 提取 Markdown，并尽量保留数学公式。"""
    source_path = Path(pdf_path).expanduser().resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"PDF not found: {source_path}")

    marker_device = get_marker_device(device)

    try:
        from marker.converters.pdf import PdfConverter
    except ImportError as exc:
        raise ImportError("当前环境缺少 Marker 的 PdfConverter，请确认已安装 marker-pdf。") from exc

    converter = PdfConverter(
        artifact_dict=load_marker_models(marker_device),
        config={
            "disable_multiprocessing": True,
            "output_format": "markdown",
        },
    )
    rendered = converter(str(source_path))
    markdown_text = rendered.markdown.strip()
    if not markdown_text:
        raise ValueError(f"Marker 未从 PDF 中提取到可用 Markdown: {source_path}")

    return MarkdownDocument(
        source_path=source_path,
        text=markdown_text,
        page_count=converter.page_count or 0,
    )
