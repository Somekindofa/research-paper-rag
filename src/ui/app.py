"""
Chainlit UI - Main application interface for the Research RAG system.
Provides chat interface with document management and auto-indexing.
"""
import asyncio
from pathlib import Path

import chainlit as cl

from src.config import settings
from src.processing.ingest import get_pending_pdfs, ingest_folder, get_stats
from src.processing.duplicates import ChecksumStore
from src.retrieval.vectorstore import get_vector_store
from src.retrieval.embeddings import embed_documents
from src.graph.graph import RAGPipeline
from src.integrations.jan_client import check_jan_server


# ============================================================================
# Startup and Session Management
# ============================================================================

@cl.on_chat_start
async def on_chat_start():
    """
    Called when a new chat session starts.
    Checks for new PDFs and offers to index them.
    """
    # Initialize pipeline in session
    pipeline = RAGPipeline()
    cl.user_session.set("pipeline", pipeline)
    
    # Welcome message
    await cl.Message(
        content="# 📚 Research RAG Assistant\n\nI can help you find and synthesize information from your research paper library.\n\n*Checking system status...*"
    ).send()
    
    # Check Jan server status
    jan_status = check_jan_server()
    if jan_status["status"] != "healthy":
        await cl.Message(
            content=f"⚠️ **Jan LLM Server Not Available**\n\n"
            f"Please start Jan and enable the Local API Server.\n\n"
            f"Error: {jan_status.get('error', 'Unknown')}\n"
            f"URL: {jan_status.get('server_url', 'N/A')}"
        ).send()
    else:
        model_status = "✅" if jan_status.get("model_available") else "⚠️ Model not found"
        await cl.Message(
            content=f"✅ **LLM Server Connected**\n"
            f"- Model: `{jan_status.get('configured_model')}` {model_status}\n"
            f"- Available models: {', '.join(jan_status.get('available_models', [])[:5])}"
        ).send()
    
    # Check for new PDFs
    await check_for_new_pdfs()


async def check_for_new_pdfs():
    """Check for unindexed PDFs and prompt user to index them."""
    try:
        pending = get_pending_pdfs()
        stats = get_stats()
        
        # Show current stats
        store = get_vector_store()
        
        status_msg = (
            f"📊 **Library Status**\n"
            f"- PDFs in folder: {stats['total_pdfs_in_folder']}\n"
            f"- Already indexed: {stats['processed_pdfs']}\n"
            f"- Chunks in vector store: {store.count()}\n"
            f"- PDF folder: `{stats['pdf_folder']}`"
        )
        await cl.Message(content=status_msg).send()
        
        if pending:
            # Show pending files
            file_list = "\n".join([f"  - `{p.name}`" for p in pending[:20]])
            if len(pending) > 20:
                file_list += f"\n  - ... and {len(pending) - 20} more"
            
            await cl.Message(
                content=f"📥 **{len(pending)} New PDFs Found**\n\n{file_list}"
            ).send()
            
            # Ask user whether to index
            actions = [
                cl.Action(name="index_pdfs", value="yes", label="✅ Index Now", payload={"action": "index"}),
                cl.Action(name="skip_index", value="no", label="⏭️ Skip for Now", payload={"action": "skip"}),
            ]
            
            await cl.Message(
                content="Would you like to index these PDFs now?",
                actions=actions
            ).send()
        else:
            await cl.Message(
                content="✅ All PDFs are indexed. You can start asking questions!"
            ).send()
    
    except Exception as e:
        await cl.Message(
            content=f"⚠️ Error checking PDF folder: {e}\n\n"
            f"Please check that the PDF folder path is correct in your `.env` file."
        ).send()


@cl.action_callback("index_pdfs")
async def on_index_pdfs(action: cl.Action):
    """Handle PDF indexing request."""
    await action.remove()
    await run_indexing()


@cl.action_callback("skip_index")
async def on_skip_index(action: cl.Action):
    """Handle skip indexing request."""
    await action.remove()
    await cl.Message(content="Skipped indexing. You can add PDFs later by restarting the chat.").send()


async def run_indexing():
    """Run the PDF indexing pipeline with progress updates."""
    msg = cl.Message(content="🔄 **Starting indexing...**\n\n")
    await msg.send()
    
    progress_lines = []
    
    def progress_callback(text: str):
        progress_lines.append(text)
    
    try:
        # Run ingestion in thread pool to not block
        loop = asyncio.get_event_loop()
        docs, chunks = await loop.run_in_executor(
            None,
            lambda: ingest_folder(progress_callback=progress_callback)
        )
        
        if not chunks:
            await cl.Message(content="No new documents to index.").send()
            return
        
        # Add chunks to vector store
        await cl.Message(content=f"📦 Adding {len(chunks)} chunks to vector store...").send()
        
        store = get_vector_store()
        added = await loop.run_in_executor(
            None,
            lambda: store.add_chunks(chunks)
        )
        
        await cl.Message(
            content=f"✅ **Indexing Complete!**\n"
            f"- Documents processed: {len(docs)}\n"
            f"- Chunks added: {added}\n"
            f"- Total chunks in store: {store.count()}\n\n"
            f"You can now ask questions about your papers!"
        ).send()
    
    except Exception as e:
        await cl.Message(content=f"❌ **Indexing Error**: {e}").send()


# ============================================================================
# Message Handling
# ============================================================================

@cl.on_message
async def on_message(message: cl.Message):
    """
    Handle user messages - run the RAG pipeline.
    """
    query = message.content.strip()
    
    if not query:
        return
    
    # Get pipeline from session
    pipeline: RAGPipeline = cl.user_session.get("pipeline")
    
    if not pipeline:
        pipeline = RAGPipeline()
        cl.user_session.set("pipeline", pipeline)
    
    # Create response message for streaming
    response_msg = cl.Message(content="")
    await response_msg.send()
    
    try:
        # Show thinking indicator
        await response_msg.stream_token("🔍 *Searching your research library...*\n\n")
        
        # Run pipeline in executor to not block
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: pipeline.invoke(query)
        )
        
        # Clear thinking indicator and show answer
        answer = result.get("answer", "No answer generated.")
        sources = result.get("sources", [])
        error = result.get("error")
        
        # Update message with answer
        response_msg.content = ""
        await response_msg.update()
        await response_msg.stream_token(answer)
        
        # Show error if present
        if error:
            await response_msg.stream_token(f"\n\n⚠️ *Note: {error}*")
        
        # Add sources as elements
        if sources:
            elements = []
            
            for source in sources:
                # Create text element for each source
                source_text = (
                    f"**{source['title']}**\n"
                    f"*{source['authors']}* ({source['year']})\n\n"
                    f"Score: {source['score']:.3f}"
                    + (f" | Page: {source['page']}" if source.get('page') else "")
                    + f"\n\n---\n\n{source['content'][:1000]}..."
                )
                
                elements.append(
                    cl.Text(
                        name=f"[{source['index']}] {source['title'][:50]}",
                        content=source_text,
                        display="side",
                    )
                )
            
            response_msg.elements = elements
            await response_msg.update()
            
            # Also show sources summary
            sources_summary = "\n\n---\n\n📚 **Sources:**\n"
            for source in sources:
                sources_summary += f"- [{source['index']}] {source['title'][:60]}... ({source['authors'][:30]}, {source['year']})\n"
            
            await response_msg.stream_token(sources_summary)
    
    except Exception as e:
        await response_msg.stream_token(f"\n\n❌ **Error**: {e}")


# ============================================================================
# Settings (optional file upload)
# ============================================================================

@cl.on_settings_update
async def on_settings_update(settings):
    """Handle settings updates."""
    pass


# For running directly
if __name__ == "__main__":
    # This is handled by chainlit run command
    pass
