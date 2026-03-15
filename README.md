# pdf2md-rag

本项目提供一套本地可运行的 RAG 知识库构建流程：

`PDF -> Markdown -> Chunks -> Embedding -> Chroma`

适合在 macOS / Apple Silicon 上把单个 PDF 或一批 PDF 建成可检索的本地知识库。

## 功能

- PDF 提取为 Markdown（优先 `pymupdf4llm`，失败时回退到 `PyMuPDF`）
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

> 当前机器默认 `python3` 是 3.13，但本地 embedding 依赖通常在 3.12 更稳，建议显式使用 `python3.12` 创建虚拟环境。

## 安装

```bash
cd /Users/charles/PycharmProjects/pdf2md
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

## 导入示例 PDF

```bash
cd /Users/charles/PycharmProjects/pdf2md
source .venv/bin/activate
pdf2md-rag ingest \
  "/Users/charles/Documents/2zkvm/理论资料/Understanding Lasso – A Novel Lookup Argument Protocol.pdf" \
  --collection understanding-lasso \
  --embedding-model BAAI/bge-small-en-v1.5
```

默认输出：

- Markdown: `data/markdown/`
- Chroma: `data/chroma/`
- Manifest: `data/manifests/`

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

不想先下载模型时，可以先用 `hash` embedder 验证全链路：

```bash
cd /Users/charles/PycharmProjects/pdf2md
source .venv/bin/activate
pdf2md-rag ingest \
  "/Users/charles/Documents/2zkvm/理论资料/Understanding Lasso – A Novel Lookup Argument Protocol.pdf" \
  --collection understanding-lasso-hash \
  --embedder hash
```

## 目录结构

- `src/pdf2md_rag/`：主代码
- `tests/`：单元测试与 smoke test

## Apple Silicon 说明

- 默认 embedding 代码会优先尝试 `mps`，不可用时回退到 CPU。
- 首次运行 `sentence-transformers` 会下载模型，需要联网。
- 若你更关注速度，`BAAI/bge-small-en-v1.5` 是一个比较稳妥的起点。
- 若使用本地 LLM，Ollama 是最省事的方式；若使用远程或自托管 OpenAI 兼容接口，直接指向对应 `base_url` 即可。
