"""PDF -> Markdown 提取层。

这是整个项目默认的 PDF 提取入口，负责：
- 选择 Marker 运行设备（优先 MPS）
- 处理 Apple Silicon / MPS 兼容细节
- 调用 Marker 输出 Markdown
- 把结果封装成 `MarkdownDocument`

上层模块不需要关心 Marker / Surya 的底层实现，只需要调用 `extract_markdown`。
"""

from __future__ import annotations

import importlib
import importlib.util
import os
from functools import lru_cache
from pathlib import Path

from .models import MarkdownDocument

# 这些处理器会触发表格结构识别；而 Marker 当前依赖的
# `surya.TableRecEncoderDecoderModel` 在 MPS 上会强制退回 CPU。
# 为了保证“主路径始终跑在 MPS 上”，项目在 MPS 模式下会把它们剔除。
_TABLE_PROCESSOR_PATHS = {
    "marker.processors.table.TableProcessor",
    "marker.processors.llm.llm_table.LLMTableProcessor",
    "marker.processors.llm.llm_table_merge.LLMTableMergeProcessor",
}


def get_marker_device(preferred_device: str | None = None) -> str:
    """决定 Marker 本次运行使用的设备。

    优先级：显式传入参数 > 环境变量 > 自动探测。
    这样 CLI、调试脚本和测试都可以复用同一套设备选择逻辑。
    """
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


def should_disable_table_rec(marker_device: str) -> bool:
    """在 MPS 下禁用表格识别，避免 Surya 自动切回 CPU。"""
    return marker_device == "mps"


@lru_cache(maxsize=4)
def load_marker_models(device: str, disable_table_rec: bool = False):
    """按需加载 Marker / Surya 模型，并缓存结果。

    模型初始化成本很高，所以这里用缓存避免同一进程里重复加载。
    """
    try:
        from marker.models import (
            DetectionPredictor,
            FoundationPredictor,
            LayoutPredictor,
            OCRErrorPredictor,
            RecognitionPredictor,
            create_model_dict,
            surya_settings,
        )
    except ImportError as exc:
        raise ImportError("Marker 未安装。请先在虚拟环境中安装 marker-pdf。") from exc

    # 非 MPS 场景直接使用 Marker 官方默认模型集合。
    if not disable_table_rec:
        return create_model_dict(device=device)

    # MPS 场景只保留正文、版面、OCR、公式主路径需要的模型。
    return {
        "layout_model": LayoutPredictor(
            FoundationPredictor(checkpoint=surya_settings.LAYOUT_MODEL_CHECKPOINT, device=device)
        ),
        "recognition_model": RecognitionPredictor(
            FoundationPredictor(checkpoint=surya_settings.RECOGNITION_MODEL_CHECKPOINT, device=device)
        ),
        "detection_model": DetectionPredictor(device=device),
        "ocr_error_model": OCRErrorPredictor(device=device),
    }


def get_marker_processor_list(disable_table_rec: bool) -> list[str] | None:
    """在需要时从默认处理器链路里移除表格处理器。"""
    if not disable_table_rec:
        return None

    from marker.converters.pdf import PdfConverter

    processor_list: list[str] = []
    for processor_cls in PdfConverter.default_processors:
        processor_path = f"{processor_cls.__module__}.{processor_cls.__name__}"
        if processor_path in _TABLE_PROCESSOR_PATHS:
            continue
        processor_list.append(processor_path)
    return processor_list


def extract_markdown(pdf_path: str | Path, device: str | None = None) -> MarkdownDocument:
    """使用 Marker 从 PDF 提取 Markdown，并尽量保留数学公式。"""
    source_path = Path(pdf_path).expanduser().resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"PDF not found: {source_path}")

    marker_device = get_marker_device(device)
    disable_table_rec = should_disable_table_rec(marker_device)

    try:
        from marker.converters.pdf import PdfConverter
    except ImportError as exc:
        raise ImportError("当前环境缺少 Marker 的 PdfConverter，请确认已安装 marker-pdf。") from exc

    # `PdfConverter` 是 Marker 的总入口：传入模型字典、处理器链路和输出配置，
    # 最终返回 markdown / html / json 等不同格式。
    converter = PdfConverter(
        artifact_dict=load_marker_models(marker_device, disable_table_rec=disable_table_rec),
        processor_list=get_marker_processor_list(disable_table_rec),
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
