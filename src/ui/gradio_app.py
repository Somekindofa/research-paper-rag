"""
Gradio UI - Enhanced application interface for the Research RAG system.
Provides chat interface with model selection, Force Retrieval toggle, and document management.
"""
import gradio as gr
import threading
import time
from pathlib import Path
from typing import Optional, Tuple, List

from src.config import settings
from src.processing.ingest import get_pending_pdfs, ingest_folder, get_stats
from src.processing.duplicates import ChecksumStore
from src.retrieval.vectorstore import get_vector_store
from src.graph.graph import RAGPipeline
from src.integrations.lm_studio_client import check_jan_server, get_lm_studio_client


# Global state
pipeline = None
indexing_in_progress = False
indexing_status = ""


# ============================================================================
# Initialization and Setup
# ============================================================================

def initialize_system():
    """Initialize the RAG pipeline and check system status."""
    global pipeline
    
    if pipeline is None:
        pipeline = RAGPipeline()
    
    # Check LM Studio server
    lm_studio_status = check_jan_server()
    
    if lm_studio_status["status"] != "healthy":
        status_msg = f"⚠️ **LM Studio Server Not Available**\n\n" \
                     f"Error: {lm_studio_status.get('error', 'Unknown')}\n" \
                     f"URL: {lm_studio_status.get('server_url', 'N/A')}"
        return [], status_msg
    
    # Get available models
    models = lm_studio_status.get("available_models", [])
    
    if not models:
        status_msg = "⚠️ **No models loaded in LM Studio**\n\n" \
                     "Please load a model in LM Studio first."
        return [], status_msg
    
    status_msg = f"✅ **LM Studio Server Connected**\n\n" \
                 f"Available models: {len(models)}\n" \
                 f"Use the dropdown to select a model."
    
    return models, status_msg


def get_library_status():
    """Get the current status of the PDF library."""
    try:
        stats = get_stats()
        store = get_vector_store()
        pending = get_pending_pdfs()
        
        status = f"📊 **Library Status**\n\n" \
                f"- PDFs in folder: {stats['total_pdfs_in_folder']}\n" \
                f"- Already indexed: {stats['processed_pdfs']}\n" \
                f"- Chunks in vector store: {store.count()}\n" \
                f"- Pending PDFs: {len(pending)}\n" \
                f"- PDF folder: `{stats['pdf_folder']}`"
        
        return status
    except Exception as e:
        return f"⚠️ Error checking library: {e}"


# ============================================================================
# Chat Functions
# ============================================================================

def simple_llm_chat(message: str, history: List, selected_model: str) -> Tuple[List, str]:
    """
    Simple LLM chat without RAG - direct conversation.
    
    Args:
        message: User's message
        history: Chat history
        selected_model: Selected LLM model
    
    Returns:
        Updated history and empty string for textbox
    """
    if not message.strip():
        return history, ""
    
    # Add user message to history
    history.append([message, None])
    
    try:
        # Get LLM client
        client = get_lm_studio_client(model=selected_model)
        
        # Generate simple response (no RAG)
        response = client.generate(
            prompt=message,
            system_prompt="You are a helpful AI assistant. Provide concise and accurate responses.",
            temperature=0.7,
            max_tokens=2048
        )
        
        # Update history with response
        history[-1][1] = response
        
    except Exception as e:
        error_msg = f"❌ **Error**: {str(e)}\n\n" \
                    "Make sure LM Studio server is running and accessible."
        history[-1][1] = error_msg
    
    return history, ""


def rag_chat(
    message: str,
    history: List,
    selected_model: str,
    num_docs: int,
    relevance_threshold: float
) -> Tuple[List, str]:
    """
    RAG-enabled chat with document retrieval and citation.
    
    Args:
        message: User's query
        history: Chat history
        selected_model: Selected LLM model
        num_docs: Number of documents to retrieve
        relevance_threshold: Minimum relevance score (0-1)
    
    Returns:
        Updated history and empty string for textbox
    """
    global pipeline
    
    if not message.strip():
        return history, ""
    
    # Add user message to history
    history.append([message, None])
    
    try:
        # Show thinking indicator
        history[-1][1] = "🔍 *Searching your research library...*"
        
        # Run RAG pipeline
        result = pipeline.invoke(
            message,
            num_docs=num_docs,
            relevance_threshold=relevance_threshold,
            selected_model=selected_model
        )
        
        # Get answer and sources
        answer = result.get("answer", "No answer generated.")
        sources = result.get("sources", [])
        error = result.get("error")
        
        # Filter sources by threshold
        filtered_sources = [
            s for s in sources
            if s.get("score", 0) >= relevance_threshold
        ]
        
        # Build response with sources
        response = answer
        
        if error:
            response += f"\n\n⚠️ *Note: {error}*"
        
        # Add source information
        if filtered_sources:
            response += f"\n\n---\n\n📚 **Sources ({len(filtered_sources)} documents):**\n\n"
            
            for source in filtered_sources:
                response += f"**[{source['index']}] {source['title']}**\n"
                response += f"*{source['authors']}* ({source['year']}) - "
                response += f"Score: {source['score']:.2f}\n"
                
                # Add metadata if available
                metadata = source.get('metadata', {})
                if 'summary' in metadata:
                    response += f"📝 {metadata['summary'][:200]}...\n"
                
                response += "\n"
        else:
            response += f"\n\n*No sources met the {int(relevance_threshold * 100)}% relevance threshold.*"
        
        # Update history
        history[-1][1] = response
        
    except Exception as e:
        error_msg = f"❌ **Error**: {str(e)}\n\n" \
                    "Make sure LM Studio server is running and the vector store is indexed."
        history[-1][1] = error_msg
    
    return history, ""


def handle_message(
    message: str,
    history: List,
    force_retrieval: bool,
    selected_model: str,
    num_docs: int,
    relevance_threshold: float
) -> Tuple[List, str]:
    """
    Main message handler - routes to simple LLM or RAG based on Force Retrieval toggle.
    
    Args:
        message: User's message
        history: Chat history
        force_retrieval: Whether to use RAG (True) or simple LLM (False)
        selected_model: Selected LLM model
        num_docs: Number of documents to retrieve
        relevance_threshold: Relevance threshold (percentage, 0-100)
    
    Returns:
        Updated history and empty string for textbox
    """
    # Convert threshold from percentage to decimal
    threshold_decimal = relevance_threshold / 100.0
    
    if force_retrieval:
        return rag_chat(message, history, selected_model, num_docs, threshold_decimal)
    else:
        return simple_llm_chat(message, history, selected_model)


# ============================================================================
# Indexing Functions
# ============================================================================

def run_indexing_background():
    """Run PDF indexing in background thread."""
    global indexing_in_progress, indexing_status
    
    if indexing_in_progress:
        return "⚠️ Indexing already in progress."
    
    indexing_in_progress = True
    indexing_status = "🔄 Starting indexing..."
    
    def indexing_task():
        global indexing_in_progress, indexing_status
        
        try:
            progress_lines = []
            
            def progress_callback(text: str):
                progress_lines.append(text)
                global indexing_status
                indexing_status = f"🔄 Indexing: {text}"
            
            # Run ingestion
            docs, chunks = ingest_folder(progress_callback=progress_callback)
            
            if not chunks:
                indexing_status = "ℹ️ No new documents to index."
                indexing_in_progress = False
                return
            
            # Add to vector store
            indexing_status = f"📦 Adding {len(chunks)} chunks to vector store..."
            store = get_vector_store()
            added = store.add_chunks(chunks)
            
            indexing_status = f"✅ Indexing Complete! Processed {len(docs)} documents, added {added} chunks."
            
        except Exception as e:
            indexing_status = f"❌ Indexing Error: {str(e)}"
        
        finally:
            indexing_in_progress = False
    
    # Start indexing in background thread
    thread = threading.Thread(target=indexing_task, daemon=True)
    thread.start()
    
    return "🔄 Indexing started in background. Check status below."


def get_indexing_status_text():
    """Get current indexing status."""
    global indexing_status
    if indexing_status:
        return indexing_status
    return "No indexing in progress."


# ============================================================================
# Gradio Interface
# ============================================================================

def create_interface():
    """Create the Gradio interface."""
    
    # Initialize system
    models, init_status = initialize_system()
    default_model = models[0] if models else "No models available"
    
    with gr.Blocks(title="Research RAG Assistant") as demo:
        
        # Header
        gr.Markdown(
            """
            # 📚 Research RAG Assistant
            
            AI-powered research paper query and analysis system for PhD researchers.
            
            **Force Retrieval OFF**: Simple LLM chat (fast, no document search)  
            **Force Retrieval ON**: Full RAG with document retrieval and citations
            """
        )
        
        # Main layout
        with gr.Row():
            # Left column - Chat
            with gr.Column(scale=3):
                # Force Retrieval Toggle (prominent)
                force_retrieval = gr.Checkbox(
                    label="🔍 Force Retrieval",
                    value=False,
                    info="Enable to search documents and get cited answers. Disable for faster, simple chat.",
                )
                
                # Chat interface
                chatbot = gr.Chatbot(
                    label="Chat",
                    height=500
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        label="Your message",
                        placeholder="Ask a question about your research papers...",
                        scale=4,
                        lines=2
                    )
                    submit_btn = gr.Button("Send", variant="primary", scale=1)
                
                clear_btn = gr.Button("Clear Chat", variant="secondary")
            
            # Right column - Settings and Status
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Settings")
                
                # Model selection
                model_dropdown = gr.Dropdown(
                    choices=models,
                    value=default_model,
                    label="🤖 Model",
                    info="Select LLM model"
                )
                
                # RAG Settings (only relevant when Force Retrieval is ON)
                with gr.Accordion("📊 Retrieval Settings", open=True):
                    num_docs_slider = gr.Slider(
                        minimum=1,
                        maximum=20,
                        value=5,
                        step=1,
                        label="Number of Documents",
                        info="How many documents to retrieve"
                    )
                    
                    threshold_slider = gr.Slider(
                        minimum=50,
                        maximum=100,
                        value=75,
                        step=5,
                        label="Relevance Threshold (%)",
                        info="Minimum relevance score"
                    )
                
                gr.Markdown("---")
                gr.Markdown("### 📊 System Status")
                
                status_text = gr.Textbox(
                    value=init_status,
                    label="LM Studio Status",
                    interactive=False,
                    lines=4
                )
                
                library_status = gr.Textbox(
                    value=get_library_status(),
                    label="Library Status",
                    interactive=False,
                    lines=6
                )
                
                refresh_status_btn = gr.Button("🔄 Refresh Status")
                
                gr.Markdown("---")
                gr.Markdown("### 📥 Indexing")
                
                indexing_status_text = gr.Textbox(
                    value="No indexing in progress.",
                    label="Indexing Status",
                    interactive=False,
                    lines=3
                )
                
                index_btn = gr.Button("📥 Start Indexing", variant="secondary")
        
        # Event handlers
        def submit_message(msg, history, force_ret, model, num_docs, threshold):
            return handle_message(msg, history, force_ret, model, num_docs, threshold)
        
        # Submit on button click or Enter
        submit_btn.click(
            submit_message,
            inputs=[msg, chatbot, force_retrieval, model_dropdown, num_docs_slider, threshold_slider],
            outputs=[chatbot, msg]
        )
        
        msg.submit(
            submit_message,
            inputs=[msg, chatbot, force_retrieval, model_dropdown, num_docs_slider, threshold_slider],
            outputs=[chatbot, msg]
        )
        
        # Clear chat
        clear_btn.click(lambda: [], outputs=[chatbot])
        
        # Refresh status
        def refresh_statuses():
            models_new, init_status_new = initialize_system()
            lib_status = get_library_status()
            idx_status = get_indexing_status_text()
            return init_status_new, lib_status, idx_status
        
        refresh_status_btn.click(
            refresh_statuses,
            outputs=[status_text, library_status, indexing_status_text]
        )
        
        # Start indexing
        def start_indexing():
            result = run_indexing_background()
            time.sleep(1)  # Give it a moment to start
            return result, get_indexing_status_text()
        
        index_btn.click(
            start_indexing,
            outputs=[status_text, indexing_status_text]
        )
        
        # Footer
        gr.Markdown(
            """
            ---
            
            **Tip**: Use Force Retrieval ON for research questions requiring citations.  
            Use Force Retrieval OFF for general conversation or when documents aren't needed.
            """
        )
    
    return demo


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Launch the Gradio interface."""
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )


if __name__ == "__main__":
    main()
