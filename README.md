# Research RAG System

A local, privacy-focused Retrieval-Augmented Generation system for research papers.

## Features

- 🔍 **HyDE-Enhanced Retrieval**: Hypothetical Document Embeddings for better semantic search
- 📊 **MMR Diversification**: Get diverse, non-redundant results
- 🔄 **Cross-Encoder Reranking**: Precision-focused result refinement
- 📝 **Cited Answers**: Every claim grounded in your papers with proper citations
- 🖥️ **100% Local**: Your papers and queries never leave your machine
- 🚀 **GPU Accelerated**: Fast embeddings and inference on your RTX Ada 5000

## Quick Start

### 1. Install Dependencies

```powershell
cd c:\Users\romaric\Documents\research_RAG
pip install -r requirements.txt
```

### 2. Set Up Jan LLM Server

Follow [docs/jan_setup.md](docs/jan_setup.md) to install and configure Jan with Llama 3.3 8B.

### 3. Configure Your PDF Folder

Copy the example environment file:

```powershell
copy .env.example .env
```

Edit `.env` and set your PDF folder path:

```
PDF_FOLDER_PATH=C:/path/to/your/zotero/pdfs
```

### 4. Run Diagnostics

```powershell
python -m src.utils.diagnostics
```

Ensure all checks pass before proceeding.

### 5. Start the UI

```powershell
chainlit run src/ui/app.py
```

Open `http://localhost:8000` in your browser.

## Architecture

```
Query → Preprocess → HyDE Generation → Embed → MMR Retrieval → Rerank → Generate → Answer
```

### Components

- **LangGraph**: Orchestrates the RAG pipeline
- **Chroma**: Vector storage with persistence
- **nomic-embed-text-v1.5**: GPU-accelerated embeddings
- **ms-marco-MiniLM**: Cross-encoder reranking
- **Jan + Llama 3.3 8B**: Local LLM inference
- **Chainlit**: Modern chat UI

## Project Structure

```
research_RAG/
├── config/
│   ├── settings.yaml       # Main configuration
│   └── prompts.yaml        # Prompt templates
├── data/
│   ├── pdfs/               # Your PDF papers
│   ├── chroma_db/          # Vector store
│   └── metadata/           # Checksums, etc.
├── docs/
│   └── jan_setup.md        # Jan setup guide
├── public/
│   └── style.css           # UI styling
├── src/
│   ├── graph/              # LangGraph pipeline
│   ├── processing/         # PDF ingestion
│   ├── retrieval/          # Embeddings, search
│   ├── integrations/       # Jan client
│   ├── ui/                 # Chainlit app
│   └── utils/              # Diagnostics
├── .env                    # Your configuration
├── chainlit.md             # Welcome message
└── requirements.txt        # Dependencies
```

## Configuration

### Key Settings (config/settings.yaml)

| Setting | Default | Description |
|---------|---------|-------------|
| `jan.model` | llama-3.3-8b-instruct | LLM model name in Jan |
| `embeddings.device` | cuda | GPU or CPU for embeddings |
| `chunking.chunk_size` | 800 | Characters per chunk |
| `retrieval.k` | 10 | Number of results |
| `retrieval.lambda_mult` | 0.7 | MMR diversity (0-1) |

### Environment Variables (.env)

```
JAN_BASE_URL=http://localhost:1337/v1
PDF_FOLDER_PATH=C:/Users/you/Zotero/storage
EMBEDDING_DEVICE=cuda
```

## Adding New Papers

1. Add PDFs to your configured folder (or subfolders)
2. Restart the Chainlit UI
3. Click "Index Now" when prompted
4. Papers are automatically chunked, embedded, and indexed

## Troubleshooting

### Jan Connection Issues
- Ensure Jan is running
- Check Local API Server is enabled (port 1337)
- Verify with: `curl http://localhost:1337/v1/models`

### GPU/CUDA Issues
- Set `EMBEDDING_DEVICE=cpu` in `.env` to use CPU
- Ensure CUDA toolkit matches PyTorch version
- Check GPU memory with: `nvidia-smi`

### Slow Indexing
- Normal: ~2-5 seconds per PDF
- GPU embeddings are much faster than CPU

## License

MIT - Use freely for research and personal projects.
