# Research RAG System

A powerful, privacy-focused Retrieval-Augmented Generation system for PhD research with 100+ papers. Features a modern React frontend and FastAPI backend.

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
- ⚛️ **Modern React UI**: Professional, intuitive interface built with React + TypeScript

## Architecture

The system uses a modern client-server architecture:

### Backend (FastAPI)
```
User Query → REST API → RAG Pipeline → LM Studio → Response
```

### Frontend (React)
```
User Interface → HTTP Requests → API Endpoints → Display Results
```

### Two Query Modes

**Simple LLM Mode (Force Retrieval OFF)**:
```
Query → LM Studio Client → Direct Response
```
Fast and conversational, no document search.

**Full RAG Mode (Force Retrieval ON)**:
```
Query → Preprocess → HyDE → Embed → MMR Retrieval → Rerank → Generate → Answer + Citations
```
Complete pipeline with document retrieval and citations.

## Quick Start

### 1. Install Dependencies

**Backend:**
```bash
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 2. Set Up LM Studio Server

This system uses **LM Studio** running on a remote workstation accessible via Tailscale:

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

### 4. Run the Application

**Start Backend (Terminal 1):**
```bash
python src/api/server.py
```
Backend runs at: http://localhost:8000

**Start Frontend (Terminal 2):**
```bash
cd frontend
npm start
```
Frontend runs at: http://localhost:3000

Open your browser to http://localhost:3000 to use the application.

## Usage

### Force Retrieval Toggle

The React UI features a prominent **Force Retrieval** toggle:

- **OFF (☐)**: Simple LLM chat
  - Direct conversation with the LLM
  - Fast response (~2-5 seconds)
  - No document search
  - Good for general questions

- **ON (☑)**: Full RAG mode
  - Searches your research library
  - Provides cited answers
  - Shows source documents
  - Response time: ~5-15 seconds
  - Good for research questions

### Settings Panel

Adjust retrieval parameters in real-time:
- **Model**: Select LLM model from LM Studio
- **Documents**: Number of documents to retrieve (1-20)
- **Relevance**: Minimum relevance threshold (50-100%)

### System Status

Monitor system health:
- LM Studio connection status
- PDF library statistics
- Indexing progress

## Components

- **React + TypeScript**: Modern frontend framework
- **FastAPI**: High-performance Python backend
- **LangGraph**: Orchestrates the RAG pipeline with state management
- **Chroma**: Vector storage with cosine similarity and persistence
- **nomic-embed-text-v1.5**: GPU-accelerated embeddings
- **ms-marco-MiniLM**: Cross-encoder reranking
- **LM Studio**: Remote LLM inference (30B+ models supported)

## Project Structure

```
research-paper-rag/
├── frontend/               # React application
│   ├── src/
│   │   ├── App.tsx        # Main React component
│   │   └── App.css        # Styles
│   ├── public/
│   └── package.json
├── src/
│   ├── api/
│   │   └── server.py      # FastAPI backend
│   ├── graph/             # LangGraph RAG pipeline
│   ├── processing/        # PDF ingestion
│   ├── retrieval/         # Embeddings, MMR, reranking
│   ├── integrations/      # LM Studio client
│   └── utils/             # Diagnostics
├── config/
│   ├── settings.yaml      # Configuration
│   └── prompts.yaml       # Prompt templates
├── data/
│   ├── pdfs/              # Your PDF papers
│   ├── chroma_db/         # Vector store
│   └── metadata/          # Checksums
├── requirements.txt       # Python dependencies
└── README.md
```

## API Endpoints

The FastAPI backend provides the following endpoints:

- `GET /api/health` - Health check
- `GET /api/status` - System status
- `POST /api/chat` - Chat with RAG or simple LLM
- `GET /api/models` - List available models
- `POST /api/index` - Start PDF indexing
- `GET /api/indexing-status` - Check indexing progress

## Configuration

### Key Settings (config/settings.yaml)

| Setting | Default | Description |
|---------|---------|-------------|
| `lm_studio.base_url` | http://100.0.0.0:1234/v1 | LM Studio server URL |
| `lm_studio.model` | local-model | Default model |
| `embeddings.device` | cuda | GPU or CPU for embeddings |
| `chunking.chunk_size` | 800 | Characters per chunk |
| `retrieval.k` | 5 | Default number of documents |
| `retrieval.score_threshold` | 0.75 | Default relevance threshold (75%) |

## Adding New Papers

1. Add PDFs to your configured folder
2. Click "Start Indexing" in the UI
3. Wait for indexing to complete
4. Papers are automatically chunked, embedded, and indexed

## Development

**Backend:**
```bash
# Run with auto-reload
uvicorn src.api.server:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm start  # Development mode with hot reload
npm run build  # Production build
```

## Troubleshooting

### Backend not starting
- Check Python dependencies are installed
- Verify .env configuration
- Check if port 8000 is available

### Frontend not connecting
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify API URL in frontend code

### LM Studio not available
- Ensure LM Studio is running
- Check Tailscale connection
- Verify LM_STUDIO_BASE_URL in .env
- Test: `curl http://YOUR_IP:1234/v1/models`

## License

MIT - Use freely for research and personal projects.
