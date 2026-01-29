"""
Chainlit UI - Enhanced application interface for the Research RAG system.
Provides chat interface with model selection, document management, and background indexing.
"""
import asyncio
from pathlib import Path
import json
from typing import Optional

import chainlit as cl

from src.config import settings
from src.processing.ingest import get_pending_pdfs, ingest_folder, get_stats
from src.processing.duplicates import ChecksumStore
from src.retrieval.vectorstore import get_vector_store
from src.retrieval.embeddings import embed_documents
from src.graph.graph import RAGPipeline
from src.integrations.lm_studio_client import check_jan_server, get_lm_studio_client


# Global indexing state
indexing_in_progress = False
indexing_progress_msg = None


# ============================================================================
# Model Management
# ============================================================================

async def get_available_models() -> list[str]:
    """Fetch available models from LM Studio server."""
    try:
        client = get_lm_studio_client()
        health = client.health_check()
        if health["status"] == "healthy":
            return health.get("available_models", [])
        return []
    except Exception as e:
        print(f"Error fetching models: {e}")
        return []


# ============================================================================
# Startup and Session Management
# ============================================================================

@cl.on_chat_start
async def on_chat_start():
    """
    Called when a new chat session starts.
    Sets up model selection, settings, and checks for new PDFs.
    """
    # Initialize pipeline in session
    pipeline = RAGPipeline()
    cl.user_session.set("pipeline", pipeline)
    
    # Welcome message
    await cl.Message(
        content="# 📚 Research RAG Assistant\n\n"
                "AI-powered research paper query and analysis system for PhD researchers.\n\n"
                "*Initializing system...*"
    ).send()
    
    # Check LM Studio server status
    lm_studio_status = check_jan_server()
    if lm_studio_status["status"] != "healthy":
        await cl.Message(
            content=f"⚠️ **LM Studio Server Not Available**\n\n"
            f"Please start LM Studio and ensure the server is running.\n\n"
            f"Error: {lm_studio_status.get('error', 'Unknown')}\n"
            f"URL: {lm_studio_status.get('server_url', 'N/A')}"
        ).send()
    else:
        # Get available models
        models = lm_studio_status.get("available_models", [])
        if models:
            model_list = "\n".join([f"  • {m}" for m in models[:10]])
            await cl.Message(
                content=f"✅ **LM Studio Server Connected**\n\n"
                f"Available models:\n{model_list}\n\n"
                f"*You can select a model using the dropdown at the top left.*"
            ).send()
            
            # Store available models
            cl.user_session.set("available_models", models)
            cl.user_session.set("selected_model", models[0])
        else:
            await cl.Message(
                content="⚠️ **No models loaded in LM Studio**\n\n"
                "Please load a model in LM Studio first."
            ).send()
    
    # Send settings panel
    await send_settings_panel()
    
    # Check for new PDFs
    await check_for_new_pdfs()


@cl.on_settings_update
async def on_settings_update(settings_dict):
    """Handle settings updates from the UI."""
    # Update session settings
    if "num_docs" in settings_dict:
        cl.user_session.set("num_docs", int(settings_dict["num_docs"]))
    if "relevance_threshold" in settings_dict:
        cl.user_session.set("relevance_threshold", float(settings_dict["relevance_threshold"]) / 100)
    if "selected_model" in settings_dict:
        cl.user_session.set("selected_model", settings_dict["selected_model"])


async def send_settings_panel():
    """Send retrieval settings panel to the chat."""
    config = settings()
    default_k = config["retrieval"]["k"]
    default_threshold = config["retrieval"].get("score_threshold", 0.75)
    
    # Store default settings in session
    cl.user_session.set("num_docs", default_k)
    cl.user_session.set("relevance_threshold", default_threshold)
    
    # Send settings as Chainlit settings (this creates a UI panel)
    settings_items = [
        cl.input_widget.Slider(
            id="num_docs",
            label="Number of Documents",
            initial=default_k,
            min=1,
            max=20,
            step=1,
            tooltip="Number of documents to retrieve and show in results"
        ),
        cl.input_widget.Slider(
            id="relevance_threshold",
            label="Relevance Threshold (%)",
            initial=int(default_threshold * 100),
            min=50,
            max=100,
            step=5,
            tooltip="Minimum relevance score (0-100%) for documents to be included"
        ),
    ]
    
    # Get available models for selector
    models = cl.user_session.get("available_models", [])
    if models:
        settings_items.append(
            cl.input_widget.Select(
                id="selected_model",
                label="Model",
                values=models,
                initial_value=models[0],
                tooltip="Select the LLM model to use for generation"
            )
        )
    
    await cl.ChatSettings(settings_items).send()


async def check_for_new_pdfs():
    """Check for unindexed PDFs and prompt user to index them."""
    global indexing_in_progress
    
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
                content="Would you like to index these PDFs now?\n\n"
                        "*Note: You can still query already-indexed documents while indexing is in progress.*",
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
    """Run the PDF indexing pipeline with progress updates in background."""
    global indexing_in_progress, indexing_progress_msg
    
    if indexing_in_progress:
        await cl.Message(content="⚠️ Indexing is already in progress.").send()
        return
    
    indexing_in_progress = True
    
    # Create a persistent progress message
    indexing_progress_msg = await cl.Message(
        content="🔄 **Indexing in Progress**\n\nStarting PDF processing...\n\n"
                "*You can still query existing documents while this completes.*"
    ).send()
    
    try:
        # Run indexing in background task
        asyncio.create_task(run_indexing_background())
    except Exception as e:
        indexing_in_progress = False
        await cl.Message(content=f"❌ **Indexing Error**: {e}").send()


async def run_indexing_background():
    """Background task for PDF indexing with LLM metadata extraction."""
    global indexing_in_progress, indexing_progress_msg
    
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
            await indexing_progress_msg.update(
                content="ℹ️ No new documents to index."
            )
            indexing_in_progress = False
            return
        
        # Update progress
        await indexing_progress_msg.update(
            content=f"🔄 **Indexing in Progress**\n\n"
                    f"Extracted {len(chunks)} chunks from {len(docs)} documents.\n\n"
                    f"Now generating metadata with LLM...\n\n"
                    f"*This may take a while. You can still query existing documents.*"
        )
        
        # Generate metadata for each document using LLM
        metadata_generated = await generate_document_metadata(docs)
        
        # Add chunks to vector store
        await indexing_progress_msg.update(
            content=f"🔄 **Indexing in Progress**\n\n"
                    f"Adding {len(chunks)} chunks to vector store..."
        )
        
        store = get_vector_store()
        added = await loop.run_in_executor(
            None,
            lambda: store.add_chunks(chunks)
        )
        
        # Final success message
        await indexing_progress_msg.update(
            content=f"✅ **Indexing Complete!**\n"
                    f"- Documents processed: {len(docs)}\n"
                    f"- Chunks added: {added}\n"
                    f"- Total chunks in store: {store.count()}\n"
                    f"- Metadata fields generated: summary, gap, methodology, results, discussions, conclusion\n\n"
                    f"You can now query all indexed documents!"
        )
    
    except Exception as e:
        await indexing_progress_msg.update(
            content=f"❌ **Indexing Error**: {e}"
        )
    
    finally:
        indexing_in_progress = False


async def generate_document_metadata(docs) -> int:
    """Generate LLM-based metadata for documents."""
    from src.config import prompts
    
    count = 0
    loop = asyncio.get_event_loop()
    prompt_template = prompts().get("metadata_extraction", {}).get("template", "")
    
    if not prompt_template:
        print("Warning: No metadata_extraction prompt template found")
        return 0
    
    for doc in docs:
        try:
            # Get LLM client
            selected_model = cl.user_session.get("selected_model")
            client = get_lm_studio_client(model=selected_model)
            
            # Extract first 2000 characters for context
            text_sample = doc.text[:2000] if hasattr(doc, 'text') else ""
            title = doc.metadata.get('title', 'Unknown') if hasattr(doc, 'metadata') else 'Unknown'
            
            # Generate metadata using LLM
            metadata_prompt = prompt_template.format(
                title=title,
                text_sample=text_sample
            )
            
            # Generate in thread pool
            response = await loop.run_in_executor(
                None,
                lambda: client.generate(
                    prompt=metadata_prompt,
                    temperature=0.3,
                    max_tokens=500
                )
            )
            
            # Parse and store metadata
            try:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    metadata = json.loads(json_match.group())
                    # Update document metadata
                    if hasattr(doc, 'metadata'):
                        doc.metadata.update(metadata)
                    count += 1
                else:
                    # Fallback: store raw response
                    if hasattr(doc, 'metadata'):
                        doc.metadata['llm_analysis'] = response
                    count += 1
            except json.JSONDecodeError:
                # Fallback: store raw response
                if hasattr(doc, 'metadata'):
                    doc.metadata['llm_analysis'] = response
                count += 1
        
        except Exception as e:
            print(f"Error generating metadata for document: {e}")
            continue
    
    return count


# ============================================================================
# Message Handling
# ============================================================================

@cl.on_message
async def on_message(message: cl.Message):
    """
    Handle user messages - run the RAG pipeline with user settings.
    """
    query = message.content.strip()
    
    if not query:
        return
    
    # Get user settings
    num_docs = cl.user_session.get("num_docs", 5)
    relevance_threshold = cl.user_session.get("relevance_threshold", 0.75)
    selected_model = cl.user_session.get("selected_model")
    
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
        
        # Pass user settings to pipeline
        result = await loop.run_in_executor(
            None,
            lambda: pipeline.invoke(
                query,
                num_docs=num_docs,
                relevance_threshold=relevance_threshold,
                selected_model=selected_model
            )
        )
        
        # Filter results by relevance threshold
        sources = result.get("sources", [])
        filtered_sources = [
            s for s in sources
            if s.get("score", 0) >= relevance_threshold
        ]
        
        # Clear thinking indicator and show answer
        answer = result.get("answer", "No answer generated.")
        error = result.get("error")
        
        # Update message with answer
        response_msg.content = ""
        await response_msg.update()
        await response_msg.stream_token(answer)
        
        # Show error if present
        if error:
            await response_msg.stream_token(f"\n\n⚠️ *Note: {error}*")
        
        # Show filtering info if sources were filtered
        if len(filtered_sources) < len(sources):
            await response_msg.stream_token(
                f"\n\n*Filtered to {len(filtered_sources)} documents "
                f"meeting {int(relevance_threshold * 100)}% relevance threshold "
                f"(from {len(sources)} retrieved)*"
            )
        
        # Add sources as elements
        if filtered_sources:
            elements = []
            
            for source in filtered_sources:
                # Create text element for each source with enhanced metadata
                metadata = source.get('metadata', {})
                source_text = (
                    f"**{source['title']}**\n"
                    f"*{source['authors']}* ({source['year']})\n\n"
                    f"**Relevance Score:** {source['score']:.3f}"
                    + (f" | **Page:** {source['page']}" if source.get('page') else "")
                )
                
                # Add LLM-generated metadata if available
                if 'summary' in metadata:
                    source_text += f"\n\n**Summary:** {metadata['summary']}"
                if 'methodology' in metadata:
                    source_text += f"\n\n**Methodology:** {metadata['methodology']}"
                if 'results' in metadata:
                    source_text += f"\n\n**Results:** {metadata['results']}"
                
                source_text += f"\n\n**Relevant Excerpt:**\n{source['content'][:800]}..."
                
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
            for source in filtered_sources:
                sources_summary += (
                    f"- [{source['index']}] {source['title'][:60]}... "
                    f"({source['authors'][:30]}, {source['year']}) - "
                    f"Score: {source['score']:.2f}\n"
                )
            
            await response_msg.stream_token(sources_summary)
    
    except Exception as e:
        await response_msg.stream_token(f"\n\n❌ **Error**: {e}")


# For running directly
if __name__ == "__main__":
    # This is handled by chainlit run command
    pass
