# Research RAG System

A powerful, privacy-focused Retrieval-Augmented Generation system for PhD research with 100+ papers.

## ✨ Features

- 🔍 **HyDE-Enhanced Retrieval**: Hypothetical Document Embeddings for better semantic search
- 📊 **MMR Diversification**: Get diverse, non-redundant results
- 🔄 **Cross-Encoder Reranking**: Precision-focused result refinement
- 📝 **Cited Answers**: Every claim grounded in your papers with proper citations
- 🤖 **Model Selection**: Choose from multiple LLM models via UI dropdown
- 🎛️ **User Controls**: Adjust document count (1-20) and relevance threshold (50-100%)
- 🔘 **Force Retrieval Toggle**: Choose between simple LLM chat or full RAG mode
- 📚 **LLM-Generated Metadata**: Automatic extraction of summary, gap, methodology, results, discussions, and conclusions
- ⚡ **Background Indexing**: Non-blocking PDF processing with real-time progress
- 🖥️ **100% Local**: Your papers and queries never leave your machine (via remote LM Studio)
- 🚀 **GPU Accelerated**: Fast embeddings on your GPU
- 🎨 **Modern Gradio UI**: Clean, customizable interface designed for PhD research

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up LM Studio Server

This system uses **LM Studio** (not Jan) running on a remote workstation accessible via Tailscale:

1. Install LM Studio on your workstation
2. Load your preferred model (e.g., 30B parameter model)
3. Enable the server in LM Studio settings
4. Ensure it's accessible via Tailscale network

### 3. Configure Your Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and configure:

```bash
# LM Studio server URL (via Tailscale)
LM_STUDIO_BASE_URL=http://100.0.0.0:1234/v1  # Replace with your Tailscale IP

# Path to your PDF folder (Zotero export or other)
PDF_FOLDER_PATH=data/pdfs

# Embedding device (cuda for GPU, cpu for CPU)
EMBEDDING_DEVICE=cuda
```

### 4. Run Diagnostics

```bash
python -m src.utils.diagnostics
```

Ensure all checks pass before proceeding.

### 5. Start the UI

**New Gradio UI (Recommended):**
```bash
python src/ui/gradio_app.py
```

Open `http://localhost:7860` in your browser.

**Legacy Chainlit UI:**
```bash
chainlit run src/ui/app.py
```

Open `http://localhost:8000` in your browser.

## Gradio UI - Force Retrieval Toggle

The new Gradio interface features a prominent **Force Retrieval** toggle that lets you choose between two modes:

### Mode 1: Force Retrieval OFF (Simple LLM)
- Direct conversation with the LLM
- Fast response time (~2-5 seconds)
- No document search
- No citations
- **Use for:** General questions, definitions, quick answers

### Mode 2: Force Retrieval ON (Full RAG)
- Complete RAG pipeline with document retrieval
- Searches your research library
- Provides cited answers
- Shows source documents with metadata
- Response time: ~5-15 seconds
- **Use for:** Research questions, literature review, finding papers

Simply toggle the checkbox at the top of the chat to switch between modes!

## Architecture

The system now supports two modes via the Force Retrieval toggle:

### Simple LLM Mode (Force Retrieval OFF)
```
User Query → LM Studio Client → Direct Response
```
Fast and conversational, no document search.

### Full RAG Mode (Force Retrieval ON)
```
Query → Preprocess → HyDE Generation → Embed → MMR Retrieval → Rerank → Generate → Answer
                                                                              ↓
                                                              LLM-Generated Metadata
```
Complete pipeline with document retrieval and citations.

### Pipeline Flow

1. **Query Preprocessing**: Clean and normalize user input
2. **HyDE Generation**: Create hypothetical document for better retrieval
3. **Embedding**: Convert to vector representation
4. **MMR Retrieval**: Find diverse, relevant documents (respects user's document count)
5. **Reranking**: Precision scoring with cross-encoder
6. **Filtering**: Apply user's relevance threshold
7. **Generation**: Synthesize answer with citations (using selected model)

### Components

- **LangGraph**: Orchestrates the RAG pipeline with state management
- **Chroma**: Vector storage with cosine similarity and persistence
- **nomic-embed-text-v1.5**: GPU-accelerated embeddings
- **ms-marco-MiniLM**: Cross-encoder reranking
- **LM Studio**: Remote LLM inference (30B+ models supported)
- **Gradio**: Modern, customizable web UI with Force Retrieval toggle

## Project Structure

```
research-paper-rag/
├── config/
│   ├── settings.yaml       # Main configuration
│   └── prompts.yaml        # Prompt templates (including metadata extraction)
├── data/
│   ├── pdfs/               # Your PDF papers
│   ├── chroma_db/          # Vector store
│   └── metadata/           # Checksums, etc.
├── public/
│   ├── custom.css          # Professional UI styling
│   └── custom.js           # UI interaction handlers
├── src/
│   ├── graph/              # LangGraph pipeline with state
│   ├── processing/         # PDF ingestion with metadata generation
│   ├── retrieval/          # Embeddings, MMR search, reranking
│   ├── integrations/       # LM Studio client
│   ├── ui/
│   │   ├── gradio_app.py   # New Gradio UI with Force Retrieval
│   │   └── app.py          # Legacy Chainlit UI
│   └── utils/              # Diagnostics
├── .env                    # Your configuration
├── chainlit.md             # Welcome message
└── requirements.txt        # Dependencies
```

## Configuration

### Key Settings (config/settings.yaml)

| Setting | Default | Description |
|---------|---------|-------------|
| `lm_studio.base_url` | http://100.0.0.0:1234/v1 | LM Studio server URL |
| `lm_studio.model` | local-model | Default model (overridden by UI) |
| `embeddings.device` | cuda | GPU or CPU for embeddings |
| `chunking.chunk_size` | 800 | Characters per chunk |
| `retrieval.k` | 5 | Default number of documents |
| `retrieval.score_threshold` | 0.75 | Default relevance threshold (75%) |
| `retrieval.lambda_mult` | 0.7 | MMR diversity (0-1) |

### User Controls (via UI)

- **Model Selection**: Dropdown at top left (fetches from LM Studio)
- **Number of Documents**: Slider 1-20 (default 5)
- **Relevance Threshold**: Slider 50-100% (default 75%)

These settings are per-session and don't modify config files.

## Adding New Papers

1. Add PDFs to your configured folder (or subfolders, up to 2 levels deep)
2. Restart the Chainlit UI or refresh the chat
3. Click "✅ Index Now" when prompted
4. Papers are automatically:
   - Parsed and chunked (800 chars with 140 overlap)
   - Embedded with nomic-embed-text-v1.5
   - Analyzed by LLM for metadata extraction
   - Added to vector store

### Background Indexing

- Indexing runs in a background task
- Progress indicator shows at top of screen
- You can **still query existing documents** while indexing
- Metadata generation may take time (LLM analyzes each paper)

### Metadata Fields

For each document, the LLM generates:
- **Summary**: Brief overview of the paper
- **Gap**: Research gap or problem addressed
- **Methodology**: Research methods used
- **Results**: Key findings
- **Discussion**: Main interpretations
- **Conclusion**: Main takeaways

This metadata is stored in the vector store and displayed in search results.

## Example Queries

The system is designed for PhD research workflows:

### Literature Review
> "Some paper described a method to calibrate the vibration profile of a DIY drone, recall which one it was and summarize the method step by step."

### Citation Checking
> "Here are 30 papers in my bibliography in my ongoing article named 'my article' in the lot, please review if they were correctly cited at the right passage in my article or if they don't really correlate to what I'm saying"

### Current Research Discovery
> "I want you to search the latest preprints on Arxiv's website that relate to SLAM in constraint hardware. What are the advancements from 2023 to 2025?"

## Troubleshooting

### LM Studio Connection Issues
- Ensure LM Studio is running on the workstation
- Verify server is enabled in LM Studio settings
- Check Tailscale connection: `ping 100.0.0.0` (replace with your IP)
- Test endpoint: `curl http://100.0.0.0:1234/v1/models`

### No Models Available
- Load a model in LM Studio UI
- Refresh the Chainlit page
- Model dropdown will auto-populate

### GPU/CUDA Issues
- Set `EMBEDDING_DEVICE=cpu` in `.env` to use CPU
- Check GPU availability: `python -c "import torch; print(torch.cuda.is_available())"`
- Verify CUDA toolkit matches PyTorch version

### Indexing Taking Long Time
- Normal: ~5-10 seconds per PDF (with metadata generation)
- Metadata extraction requires LLM calls (can be slow for 100+ papers)
- Progress indicator shows real-time status
- GPU embeddings are much faster than CPU

### Low Quality Answers
- Increase **Number of Documents** slider (more context)
- Lower **Relevance Threshold** (include more sources)
- Try different models via model selector
- Check if your papers are indexed: see Library Status

## API Endpoints (LM Studio)

The system uses OpenAI-compatible endpoints from LM Studio:
- `/v1/models` - List available models
- `/v1/chat/completions` - Generate responses

See [LM Studio API docs](https://lmstudio.ai/docs/developer/rest/endpoints) for details.

## License

MIT - Use freely for research and personal projects.
