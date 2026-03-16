# pdf2md-rag

本项目提供一套本地可运行的 RAG 知识库构建流程：

`PDF -> Markdown -> Chunks -> Embedding -> Chroma`

适合在 macOS / Apple Silicon 上把单个 PDF 或一批 PDF 建成可检索的本地知识库。

## 功能

- PDF 提取为 Markdown：默认使用 `Marker`，更适合学术论文、数学公式和 LaTeX 场景
- Markdown 感知式切块，保留章节上下文
- 本地 Embedding：默认 `sentence-transformers`
- 离线测试 Embedding：`hash` embedder
- 本地 Chroma 持久化
- 结构化检索层：`search.py` 返回适合 RAG 拼接的结果结构
- 简易问答脚本：`simple_qa.py` 直接把检索结果喂给本地/远程 LLM
- CLI 一键导入和检索

## 推荐环境

- macOS Apple Silicon（M 系列）
- Python `3.12`

> 当前机器默认 `python3` 是 3.13，但本地 embedding / OCR / Marker 相关依赖通常在 3.12 更稳，建议显式使用 `python3.12` 创建虚拟环境。

## 安装

```bash
cd /Users/charles/PycharmProjects/pdf2md
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

## 默认 PDF 提取器

整个项目现在默认使用 `Marker` 进行 PDF -> Markdown 提取，包括：

- `pdf2md_rag.pdf_to_markdown.extract_markdown`
- `pdf2md_rag.pipeline.ingest_pdf`
- `src/mac_rag_pipeline.py`

这意味着对包含大量数学公式、学术版式、LaTeX 表达式的论文，提取质量通常会明显好于普通纯文本抽取。

## 导入示例 PDF

```bash
cd /Users/charles/PycharmProjects/pdf2md
source .venv/bin/activate
pdf2md-rag ingest \
  "pdf/Understanding Lasso – A Novel Lookup Argument Protocol.pdf" \
  --collection understanding-lasso \
  --embedding-model BAAI/bge-small-en-v1.5
```

CLI 在完成后会：

- 打印 Markdown 和 Manifest 的输出路径
- 自动校验这两个输出文件确实存在
- 如果文件不存在，会直接退出并返回非零状态码

默认输出：

- Markdown: `pdf/`
- Chroma: `data/chroma/`
- Manifest: `data/manifests/`

## 纯代码调试示例

如果你想在 PyCharm / VS Code 里断点调试，不想用 CLI，可以直接运行仓库里的示例脚本：

```bash
cd /Users/charles/PycharmProjects/pdf2md
source .venv/bin/activate
python examples/debug_ingest.py
```

它内部直接调用：

- `PipelineConfig`
- `ingest_pdf(...)`

并会打印：

- 输入 PDF 路径
- Markdown 输出路径与是否存在
- Manifest 输出路径与是否存在
- 页数 / chunk 数 / 向量数

如果你想临时自己写一段最小调试代码，也可以直接用下面这个例子：

```python
from pathlib import Path

from pdf2md_rag.config import DEFAULT_CHROMA_DIR, DEFAULT_MANIFEST_DIR, DEFAULT_MARKDOWN_DIR, PipelineConfig
from pdf2md_rag.pipeline import ingest_pdf

pdf_path = Path("pdf/Understanding Lasso – A Novel Lookup Argument Protocol.pdf").resolve()

config = PipelineConfig(
    markdown_dir=DEFAULT_MARKDOWN_DIR,
    chroma_dir=DEFAULT_CHROMA_DIR,
    manifest_dir=DEFAULT_MANIFEST_DIR,
    collection_name="understanding-lasso-hash-debug",
    embedder_type="hash",
    embedding_model="unused",
)

result = ingest_pdf(pdf_path, config)
print(result)
print(Path(result.markdown_path).exists(), result.markdown_path)
print(Path(result.manifest_path).exists(), result.manifest_path)
```

## 检索测试

```bash
cd /Users/charles/PycharmProjects/pdf2md
source .venv/bin/activate
pdf2md-rag query \
  --collection understanding-lasso \
  --question "What is the main idea of the Lasso lookup protocol?" \
  --top-k 5 \
  --embedding-model BAAI/bge-small-en-v1.5
```

## 在 Python 里调用结构化检索

`src/pdf2md_rag/search.py` 会返回一个更适合 RAG 拼接的 `SearchResult`：

- `hits`：每个 chunk 的结构化命中信息
- `context_text`：已经拼好的上下文文本，可直接喂给 LLM
- `sources`：便于引用的来源列表
- `retrieval_meta`：检索配置与统计信息

```bash
cd /Users/charles/PycharmProjects/pdf2md
source .venv/bin/activate
python - <<'PY'
from pdf2md_rag.search import search_chunks

result = search_chunks(
    question="What is the main idea of the Lasso lookup protocol?",
    collection_name="understanding-lasso-hash",
    persist_directory="data/chroma",
    top_k=3,
    embedder_type="hash",
    embedding_model="unused",
)
print(result.context_text)
print(result.sources)
PY
```

## 用本地 / 远程 LLM 做问答

### 1) Ollama 本地问答

```bash
cd /Users/charles/PycharmProjects/pdf2md
source .venv/bin/activate
pdf2md-rag-qa \
  "What is the main idea of the Lasso lookup protocol?" \
  --collection understanding-lasso-hash \
  --embedder hash \
  --embedding-model unused \
  --llm-provider ollama \
  --llm-model llama3.1 \
  --llm-base-url http://localhost:11434
```

### 2) OpenAI 兼容接口问答

这个接口可对接 OpenAI、vLLM、LM Studio、llama.cpp server 等兼容 `/v1/chat/completions` 的服务。

```bash
cd /Users/charles/PycharmProjects/pdf2md
source .venv/bin/activate
export OPENAI_API_KEY="your-api-key"
pdf2md-rag-qa \
  "Summarize the Lasso lookup protocol in 5 bullet points." \
  --collection understanding-lasso \
  --llm-provider openai-compatible \
  --llm-model gpt-4o-mini \
  --llm-base-url https://api.openai.com
```

## 离线快速测试

如果你只是不想先下载 embedding 模型，可以先用 `hash` embedder 验证向量化与入库链路：

```bash
cd /Users/charles/PycharmProjects/pdf2md
source .venv/bin/activate
pdf2md-rag ingest \
  "pdf/Understanding Lasso – A Novel Lookup Argument Protocol.pdf" \
  --collection understanding-lasso-hash \
  --embedder hash
```

> 注意：这里的“离线快速测试”只是不下载 embedding 模型；PDF 提取阶段仍会使用 `Marker`。

## Marker / Apple Silicon 说明

- 默认 PDF 提取器会优先尝试 `mps`，不可用时回退到 CPU。
- 为了避免 `surya` 的 `TableRecEncoderDecoderModel` 在 `mps` 上强制 fallback 到 CPU，项目在 `mps` 模式下会自动禁用表格识别相关处理器。
- 这意味着正文、标题、数学公式等主路径仍然使用 `Marker + mps` 加速，但复杂表格结构提取能力会有所下降。
- `Marker` 对学术论文、公式和 LaTeX 保留更友好，但首次运行可能需要初始化模型，耗时会比纯文本提取更长。
- 默认 embedding 代码也会优先尝试 `mps`，不可用时回退到 CPU。
- 首次运行 `sentence-transformers` 会下载 embedding 模型，需要联网。
- 若使用本地 LLM，Ollama 是最省事的方式；若使用远程或自托管 OpenAI 兼容接口，直接指向对应 `base_url` 即可。

## 目录结构

- `src/pdf2md_rag/`：主代码
- `tests/`：单元测试与 smoke test

