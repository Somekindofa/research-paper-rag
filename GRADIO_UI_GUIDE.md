# Gradio UI Visual Documentation

## Research RAG Assistant - New Gradio Interface

The new Gradio interface replaces Chainlit with better customizability and features a prominent **Force Retrieval** toggle.

### Key Features

1. **Force Retrieval Toggle** - Prominently displayed at top of chat area
   - OFF: Simple LLM mode (fast, no document search)
   - ON: Full RAG mode (retrieval, reranking, citations)

2. **Clean Two-Column Layout**
   - Left: Chat interface with Force Retrieval toggle
   - Right: Settings and system status

3. **Model Selection** - Dropdown to choose LLM model

4. **Retrieval Settings** - Sliders for document count and relevance threshold

5. **System Status** - Live status of LM Studio and library

6. **Background Indexing** - Non-blocking PDF indexing

### Interface Comparison

**Chainlit (Old):**
- Always uses RAG pipeline
- No option to skip retrieval
- Fixed workflow

**Gradio (New):**
- Toggle between simple LLM and RAG
- User controls when to use retrieval
- More flexible for different query types
- Better performance for simple questions

### Force Retrieval Modes

#### Mode 1: Force Retrieval OFF (Simple LLM)
```
User Query → LLM → Direct Response
```
- Fast response time (~2-5 seconds)
- No document search
- No citations
- Good for: General conversation, definitions, quick questions

#### Mode 2: Force Retrieval ON (Full RAG)
```
User Query → HyDE → Embed → MMR Retrieve → Rerank → LLM + Citations
```
- Slower response (~5-15 seconds)
- Searches document library
- Provides cited answers
- Shows source documents
- Good for: Research questions, literature review, finding papers

### Example Usage

**Simple Question (Force Retrieval OFF):**
```
Q: What is SLAM?
A: SLAM stands for Simultaneous Localization and Mapping...
   [Direct LLM response, no citations]
```

**Research Question (Force Retrieval ON):**
```
Q: What are the latest approaches to SLAM in constrained hardware?
A: Based on your research papers:

Recent approaches include... [Smith et al., 2024] proposed...
[Jones et al., 2023] demonstrated...

📚 Sources:
- [1] Lightweight SLAM for Embedded Systems (Smith et al., 2024) - Score: 0.89
- [2] Resource-Efficient Visual SLAM (Jones et al., 2023) - Score: 0.85
- [3] Neural SLAM on Edge Devices (Brown et al., 2024) - Score: 0.82
```

### Technical Implementation

**Force Retrieval Toggle Logic:**
```python
def handle_message(message, history, force_retrieval, ...):
    if force_retrieval:
        return rag_chat(...)  # Full pipeline
    else:
        return simple_llm_chat(...)  # Direct LLM
```

**Simple LLM Mode:**
- Direct call to LM Studio client
- No vector store access
- No HyDE generation
- No retrieval or reranking
- Just: User Query → LLM → Response

**RAG Mode:**
- Full pipeline with all stages
- Vector store queried
- Documents retrieved and reranked
- Citations included
- Same as before, but now optional

### Benefits of Gradio Migration

1. **Better Customizability** - More control over UI layout and behavior
2. **Force Retrieval Toggle** - User decides when to use RAG
3. **Performance** - Faster responses for simple queries
4. **Flexibility** - Can mix modes in same conversation
5. **Cleaner UI** - More professional appearance
6. **Better Status Display** - Clear system information
7. **Standard Web UI** - Works in any browser without special setup
