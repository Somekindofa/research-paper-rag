"""
FastAPI Backend for Research RAG System
Provides REST API endpoints for the React frontend
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio

from src.config import settings
from src.graph.graph import RAGPipeline
from src.integrations.lm_studio_client import check_jan_server, get_lm_studio_client
from src.processing.ingest import get_pending_pdfs, ingest_folder, get_stats
from src.retrieval.vectorstore import get_vector_store

# Initialize FastAPI app
app = FastAPI(
    title="Research RAG API",
    description="REST API for Research Paper RAG System",
    version="1.0.0"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
pipeline = None
indexing_in_progress = False
indexing_status = ""


# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    force_retrieval: bool = False
    selected_model: Optional[str] = None
    num_docs: int = 5
    relevance_threshold: float = 0.75


class ChatResponse(BaseModel):
    answer: str
    sources: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    mode: str  # "simple" or "rag"


class StatusResponse(BaseModel):
    lm_studio_status: str
    available_models: List[str]
    library_status: Dict[str, Any]
    indexing_in_progress: bool
    indexing_status: str


# ============================================================================
# Initialization
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG pipeline on startup."""
    global pipeline
    pipeline = RAGPipeline()
    print("✓ RAG Pipeline initialized")


# ============================================================================
# Health and Status Endpoints
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "message": "API is running"}


@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    """Get system status including LM Studio, library, and indexing status."""
    global indexing_in_progress, indexing_status
    
    # Check LM Studio
    lm_status = check_jan_server()
    lm_status_text = "connected" if lm_status["status"] == "healthy" else "disconnected"
    models = lm_status.get("available_models", [])
    
    # Get library stats
    try:
        stats = get_stats()
        store = get_vector_store()
        pending = get_pending_pdfs()
        
        library = {
            "total_pdfs": stats['total_pdfs_in_folder'],
            "indexed_pdfs": stats['processed_pdfs'],
            "chunks": store.count(),
            "pending_pdfs": len(pending),
            "pdf_folder": stats['pdf_folder']
        }
    except Exception as e:
        library = {"error": str(e)}
    
    return StatusResponse(
        lm_studio_status=lm_status_text,
        available_models=models,
        library_status=library,
        indexing_in_progress=indexing_in_progress,
        indexing_status=indexing_status
    )


# ============================================================================
# Chat Endpoints
# ============================================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - handles both simple LLM and RAG modes.
    """
    global pipeline
    
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        if request.force_retrieval:
            # RAG mode with document retrieval
            result = await asyncio.to_thread(
                pipeline.invoke,
                request.message,
                num_docs=request.num_docs,
                relevance_threshold=request.relevance_threshold,
                selected_model=request.selected_model
            )
            
            # Filter sources by threshold
            sources = result.get("sources", [])
            filtered_sources = [
                s for s in sources
                if s.get("score", 0) >= request.relevance_threshold
            ]
            
            return ChatResponse(
                answer=result.get("answer", "No answer generated."),
                sources=filtered_sources,
                error=result.get("error"),
                mode="rag"
            )
        else:
            # Simple LLM mode without retrieval
            client = get_lm_studio_client(model=request.selected_model)
            
            response = await asyncio.to_thread(
                client.generate,
                prompt=request.message,
                system_prompt="You are a helpful AI assistant. Provide concise and accurate responses.",
                temperature=0.7,
                max_tokens=2048
            )
            
            return ChatResponse(
                answer=response,
                sources=None,
                error=None,
                mode="simple"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


# ============================================================================
# Indexing Endpoints
# ============================================================================

async def run_indexing_task():
    """Background task for PDF indexing."""
    global indexing_in_progress, indexing_status
    
    try:
        indexing_status = "🔄 Starting indexing..."
        
        # Run ingestion
        docs, chunks = await asyncio.to_thread(ingest_folder)
        
        if not chunks:
            indexing_status = "ℹ️ No new documents to index."
            indexing_in_progress = False
            return
        
        # Add to vector store
        indexing_status = f"📦 Adding {len(chunks)} chunks to vector store..."
        store = get_vector_store()
        added = await asyncio.to_thread(store.add_chunks, chunks)
        
        indexing_status = f"✅ Complete! Processed {len(docs)} documents, added {added} chunks."
        
    except Exception as e:
        indexing_status = f"❌ Error: {str(e)}"
    
    finally:
        indexing_in_progress = False


@app.post("/api/index")
async def start_indexing(background_tasks: BackgroundTasks):
    """Start PDF indexing in the background."""
    global indexing_in_progress
    
    if indexing_in_progress:
        raise HTTPException(status_code=400, detail="Indexing already in progress")
    
    indexing_in_progress = True
    background_tasks.add_task(run_indexing_task)
    
    return {"status": "started", "message": "Indexing started in background"}


@app.get("/api/indexing-status")
async def get_indexing_status():
    """Get current indexing status."""
    global indexing_in_progress, indexing_status
    
    return {
        "in_progress": indexing_in_progress,
        "status": indexing_status
    }


# ============================================================================
# Model Management
# ============================================================================

@app.get("/api/models")
async def get_models():
    """Get available LLM models from LM Studio."""
    lm_status = check_jan_server()
    
    if lm_status["status"] != "healthy":
        raise HTTPException(status_code=503, detail="LM Studio not available")
    
    return {
        "models": lm_status.get("available_models", []),
        "configured_model": lm_status.get("configured_model")
    }


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
