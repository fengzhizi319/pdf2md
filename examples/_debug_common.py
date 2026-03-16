"""examples 目录共享的调试辅助函数。

这些工具专门服务于 debug 脚本：
- 统一样例 PDF 路径
- 统一打印格式
- 提供小型 demo chunk 数据

这样每个脚本都能专注演示某一个阶段，而不必重复样板代码。
"""

from __future__ import annotations

from pathlib import Path

from pdf2md_rag.models import Chunk

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = PROJECT_ROOT / "pdf/Understanding Lasso – A Novel Lookup Argument Protocol.pdf"


def print_title(title: str) -> None:
    """打印统一的章节标题，方便在终端里快速分辨脚本输出。"""
    print(f"\n=== {title} ===")


def print_kv(key: str, value) -> None:
    """把调试信息格式化成 key-value 形式，便于肉眼对齐查看。"""
    print(f"{key:<14}: {value}")


def preview_text(text: str, limit: int = 220) -> str:
    """把多行文本压成单行预览，适合在 debug 输出里快速扫一眼。"""
    single_line = " ".join(text.split())
    return single_line[:limit] + ("..." if len(single_line) > limit else "")


def build_demo_chunks() -> list[Chunk]:
    """构造一小组稳定的示例 chunk。

    这些数据不依赖真实 PDF 提取，适合：
    - embedding 调试
    - 向量库调试
    - search / QA 离线调试
    """
    return [
        Chunk(
            chunk_id="demo-1",
            text="Lasso is a lookup argument protocol for efficient verification in proof systems.",
            metadata={
                "source_path": str(PDF_PATH),
                "source_name": PDF_PATH.stem,
                "heading": "Overview",
                "page": 1,
                "chunk_index": 0,
                "text_length": 79,
            },
        ),
        Chunk(
            chunk_id="demo-2",
            text="RAG pipelines split markdown into chunks, embed them, and store them in Chroma.",
            metadata={
                "source_path": str(PDF_PATH),
                "source_name": PDF_PATH.stem,
                "heading": "Implementation",
                "page": 2,
                "chunk_index": 1,
                "text_length": 83,
            },
        ),
    ]
