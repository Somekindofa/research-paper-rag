# Research RAG System - AI Agent Instructions

## Project Overview
A local, privacy-focused RAG system for research papers using LangGraph + Chroma + Jan LLM. Pipeline: `Query → HyDE → MMR Retrieval → Reranking → Generation`

## Architecture

### Pipeline Flow (LangGraph)
The RAG pipeline is a stateful graph in [src/graph/graph.py](../src/graph/graph.py):
- **Nodes**: preprocess → hyde → retrieve → rerank → generate ([src/graph/nodes.py](../src/graph/nodes.py))
- **State**: TypedDict in [src/graph/state.py](../src/graph/state.py) passes data between nodes
- **Invocation**: `RAGPipeline().invoke(query)` or `.stream(query)` for UI progress

### Key Components
- **HyDE (Hypothetical Document Embeddings)**: Generates academic paragraph answering query, embeds it for better retrieval ([src/retrieval/hyde.py](../src/retrieval/hyde.py))
- **MMR Search**: Maximal Marginal Relevance in [src/retrieval/vectorstore.py](../src/retrieval/vectorstore.py) - balances relevance with diversity (`lambda_mult: 0.7` in config)
- **Cross-Encoder Reranking**: ms-marco-MiniLM model re-scores documents for precision ([src/retrieval/reranker.py](../src/retrieval/reranker.py))
- **Jan Client**: OpenAI SDK wrapper for local LLM server at `http://10.201.20.44:1234/v1` ([src/integrations/jan_client.py](../src/integrations/jan_client.py))

## Configuration System

### Dual Config Strategy
- **YAML files** in `config/`: `settings.yaml` (all params), `prompts.yaml` (LLM templates)
- **Environment variables** override YAML: `JAN_BASE_URL`, `PDF_FOLDER_PATH`, `EMBEDDING_DEVICE`
- **Config loader** ([src/config.py](../src/config.py)) merges both, converts relative→absolute paths

### Critical Settings
- `jan.model`: Must match Jan's loaded model name (e.g., `openai/gpt-oss-20b`)
- `embeddings.device`: `cuda` for GPU, `cpu` fallback
- `retrieval.lambda_mult`: 0=max diversity, 1=max relevance (default 0.7)
- `chunking.chunk_size`: 800 chars with 140 overlap for semantic coherence

## Developer Workflows

### Starting the System
```powershell
# 1. Ensure Jan LLM server is running (separate app)
# 2. Start Chainlit UI
chainlit run src/ui/app.py
```

### Diagnostics
```powershell
python -m src.utils.diagnostics  # Check Jan connection, GPU, vector store health
```

### Indexing New PDFs
- Automatic: Chainlit UI detects new PDFs at startup, prompts user
- Manual: Add PDFs to `data/pdfs/`, restart UI, click "Index Now"
- Duplicate detection: SHA256 checksums in `data/metadata/checksums.json`

### Testing Components
```powershell
# Test graph pipeline
python src/graph/graph.py

# Test Jan client
python src/integrations/jan_client.py
```

## Project-Specific Patterns

### Error Handling: Graceful Degradation
- **HyDE fallback**: If Jan unavailable, falls back to direct query embedding (see [src/graph/nodes.py#hyde_node](../src/graph/nodes.py))
- **Reranking fallback**: If cross-encoder fails, uses original MMR order
- Never fail entire pipeline; return partial results with error messages

### Document Deduplication in Generation
[src/graph/nodes.py#generate_node](../src/graph/nodes.py) deduplicates by `doc_id` to prevent citing same paper multiple times:
```python
seen_docs = {}
for doc in docs:
    doc_id = doc["metadata"]["doc_id"]
    if doc_id not in seen_docs or score > seen_docs[doc_id]["score"]:
        seen_docs[doc_id] = {"doc": doc, "score": score}
```

### Chunking Strategy
[src/processing/chunker.py](../src/processing/chunker.py) uses character-based chunking (not token-based) with semantic separators:
- Priority: `\n\n` → `\n` → `. ` → ` `
- Preserves metadata (title, authors, year) in every chunk for citation
- Chunk IDs: `{doc_id}_{chunk_index}` (unique per PDF chunk)

### Batch Size Limits
Chroma has max ~5461 items/batch. [src/retrieval/vectorstore.py](../src/retrieval/vectorstore.py) uses 1000-item batches when adding chunks:
```python
batch_size = 1000  # Safe below Chroma's limit
for i in range(0, len(chunks), batch_size):
    # ... batch add
```

## External Dependencies

### Jan LLM Server (Critical)
- Separate desktop app, not part of this repo
- Must enable "Local API Server" in Jan settings (port 1234)
- Health check: `JanClient().health_check()` verifies connection + model availability
- Model loading is manual in Jan UI; not controllable from Python

### Zotero PDF Structure
PDF folder expects Zotero's `storage/{HASH}/file.pdf` structure (2-level depth):
```
data/pdfs/storage/
  ├── 9LDRQ5DL/paper.pdf
  └── AGVKIU3Y/another.pdf
```
Scanner uses `scan_depth: 2` in config to match this.

### GPU Acceleration
- Embeddings: `nomic-embed-text-v1.5` on CUDA via sentence-transformers
- Fallback: Set `EMBEDDING_DEVICE=cpu` in `.env` if GPU issues
- No GPU for reranking (cross-encoder is CPU-only in this setup)

## Chainlit UI Specifics

### Session Management
[src/ui/app.py](../src/ui/app.py) uses Chainlit's session storage:
- `cl.user_session.set("pipeline", pipeline)` caches RAGPipeline per user
- Actions for async indexing: `cl.Action` with callbacks

### Progress Reporting
Use `loop.run_in_executor()` to run blocking code (embeddings, LLM calls) without freezing UI:
```python
result = await loop.run_in_executor(None, lambda: pipeline.invoke(query))
```

### Indexing UX Pattern
1. `on_chat_start()` checks for new PDFs via `get_pending_pdfs()`
2. Shows action buttons: "Index Now" / "Skip for Now"
3. `on_index_pdfs()` callback runs `ingest_folder()` with progress updates
4. Streams status: "🔄 Processing...", "✅ Complete!"

## Common Pitfalls

1. **Jan model mismatch**: If `config/settings.yaml` `jan.model` doesn't match Jan's loaded model name, generation fails silently
2. **Empty vector store**: Check `store.count() == 0` before retrieval; UI should prompt indexing
3. **Metadata None values**: Chroma rejects None in metadata; [vectorstore.py](../src/retrieval/vectorstore.py) cleans with defaults (0 for ints, "Unknown" for strings)
4. **Relative path assumptions**: Always use `PROJECT_ROOT / path` in config loader; never assume CWD

## File Naming Conventions
- Modules: snake_case (`pdf_parser.py`, `jan_client.py`)
- Classes: PascalCase (`RAGPipeline`, `JanClient`, `VectorStore`)
- Functions: snake_case with descriptive verbs (`generate_hypothetical_document`, `rerank_documents`)
- Config keys: snake_case matching code (`chunk_size`, `lambda_mult`)
