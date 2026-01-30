# Force Retrieval Toggle - Visual Demonstration

## Interface Screenshots (Text Representation)

### Screenshot 1: Force Retrieval OFF (Simple LLM Mode)

```
┌─────────────────────────────────────────────────────────────────────┐
│ 📚 Research RAG Assistant                                           │
│                                                                       │
│ AI-powered research paper query and analysis system                  │
│ Force Retrieval OFF: Simple LLM chat (fast, no document search)     │
│ Force Retrieval ON: Full RAG with document retrieval and citations  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│ ┌───────────────────────────┬─────────────────────────────────────┐ │
│ │                           │                                     │ │
│ │ ☐ 🔍 Force Retrieval      │  ⚙️ Settings                       │ │
│ │                           │                                     │ │
│ │ Enable to search docs     │  🤖 Model: llama-70b-chat ▼       │ │
│ │ Disable for faster chat   │                                     │ │
│ │                           │  📊 Retrieval Settings             │ │
│ │ ───────────────────────── │  Documents: 5                      │ │
│ │                           │  Threshold: 75%                    │ │
│ │ User:                     │                                     │ │
│ │ What is SLAM?             │  📊 System Status                  │ │
│ │                           │  ✅ LM Studio Connected            │ │
│ │ Bot:                      │  Models: 3                         │ │
│ │ SLAM stands for           │                                     │ │
│ │ Simultaneous Localization │  📊 Library Status                 │ │
│ │ and Mapping, a technique  │  PDFs: 127                         │ │
│ │ used in robotics and      │  Indexed: 100                      │ │
│ │ autonomous vehicles to    │  Chunks: 12,458                    │ │
│ │ build a map of an         │                                     │ │
│ │ unknown environment while │  [🔄 Refresh]                     │ │
│ │ simultaneously keeping    │                                     │ │
│ │ track of their location   │  📥 Indexing                       │ │
│ │ within it.                │  [📥 Start Indexing]              │ │
│ │                           │                                     │ │
│ │ [Direct LLM response,     │                                     │ │
│ │  no citations - FAST]     │                                     │ │
│ │                           │                                     │ │
│ └───────────────────────────┴─────────────────────────────────────┘ │
│                                                                       │
│ Your message: ______________________________________________ [Send]   │
│                                                                       │
│ [Clear Chat]                                                          │
│                                                                       │
│ Tip: Use Force Retrieval OFF for general conversation                │
└─────────────────────────────────────────────────────────────────────┘
```

**Response Time**: ~3 seconds  
**Features**: Direct LLM, no document search, conversational


### Screenshot 2: Force Retrieval ON (Full RAG Mode)

```
┌─────────────────────────────────────────────────────────────────────┐
│ 📚 Research RAG Assistant                                           │
│                                                                       │
│ AI-powered research paper query and analysis system                  │
│ Force Retrieval OFF: Simple LLM chat (fast, no document search)     │
│ Force Retrieval ON: Full RAG with document retrieval and citations  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│ ┌───────────────────────────┬─────────────────────────────────────┐ │
│ │                           │                                     │ │
│ │ ☑ 🔍 Force Retrieval      │  ⚙️ Settings                       │ │
│ │                           │                                     │ │
│ │ Enable to search docs     │  🤖 Model: llama-70b-chat ▼       │ │
│ │ Disable for faster chat   │                                     │ │
│ │                           │  📊 Retrieval Settings             │ │
│ │ ───────────────────────── │  Documents: 5                      │ │
│ │                           │  Threshold: 75%                    │ │
│ │ User:                     │                                     │ │
│ │ What are the latest       │  📊 System Status                  │ │
│ │ approaches to SLAM in     │  ✅ LM Studio Connected            │ │
│ │ constrained hardware?     │  Models: 3                         │ │
│ │                           │                                     │ │
│ │ Bot:                      │  📊 Library Status                 │ │
│ │ Based on your research    │  PDFs: 127                         │ │
│ │ papers:                   │  Indexed: 100                      │ │
│ │                           │  Chunks: 12,458                    │ │
│ │ Recent approaches to SLAM │                                     │ │
│ │ in resource-constrained   │  [🔄 Refresh]                     │ │
│ │ hardware focus on three   │                                     │ │
│ │ main strategies:          │  📥 Indexing                       │ │
│ │                           │  [📥 Start Indexing]              │ │
│ │ 1. Feature-based methods  │                                     │ │
│ │ [Smith et al., 2024]      │                                     │ │
│ │ propose a lightweight     │                                     │ │
│ │ ORB-SLAM variant...       │                                     │ │
│ │                           │                                     │ │
│ │ 2. Direct methods         │                                     │ │
│ │ [Johnson & Lee, 2023]...  │                                     │ │
│ │                           │                                     │ │
│ │ 3. Learned features       │                                     │ │
│ │ [Zhang et al., 2024]...   │                                     │ │
│ │                           │                                     │ │
│ │ 📚 Sources (3 documents): │                                     │ │
│ │ [1] Lightweight ORB-SLAM  │                                     │ │
│ │     (Smith, 2024) - 0.89  │                                     │ │
│ │ [2] Direct Visual SLAM    │                                     │ │
│ │     (Johnson, 2023) - 0.85│                                     │ │
│ │ [3] Neural SLAM           │                                     │ │
│ │     (Zhang, 2024) - 0.82  │                                     │ │
│ │                           │                                     │ │
│ │ [RAG with citations -     │                                     │ │
│ │  documents retrieved]     │                                     │ │
│ │                           │                                     │ │
│ └───────────────────────────┴─────────────────────────────────────┘ │
│                                                                       │
│ Your message: ______________________________________________ [Send]   │
│                                                                       │
│ [Clear Chat]                                                          │
│                                                                       │
│ Tip: Use Force Retrieval ON for research questions with citations    │
└─────────────────────────────────────────────────────────────────────┘
```

**Response Time**: ~8 seconds  
**Features**: Full RAG pipeline, document retrieval, citations, metadata


## Key Differences

| Feature | Force Retrieval OFF | Force Retrieval ON |
|---------|-------------------|-------------------|
| **Toggle State** | ☐ Unchecked | ☑ Checked |
| **Pipeline** | Direct LLM | Full RAG (HyDE→Retrieve→Rerank→Generate) |
| **Response Time** | ~2-5 seconds | ~5-15 seconds |
| **Document Search** | ❌ No | ✅ Yes |
| **Citations** | ❌ No | ✅ Yes |
| **Source Documents** | ❌ No | ✅ Yes (with scores) |
| **Best For** | General chat, definitions | Research questions, lit review |
| **Accuracy** | General knowledge | Grounded in your papers |

## Usage Scenarios

### Scenario 1: Quick Definition (Use Simple LLM)
```
Toggle: OFF
Question: "What does SLAM stand for?"
Result: Fast, conversational answer
```

### Scenario 2: Literature Review (Use RAG)
```
Toggle: ON
Question: "Compare the SLAM approaches in papers from 2023-2024"
Result: Detailed answer with citations from your papers
```

### Scenario 3: Mixed Conversation
```
1. Toggle: OFF → "Hello, how are you?" (fast chat)
2. Toggle: ON → "Find papers about drone calibration" (search)
3. Toggle: OFF → "Thank you!" (fast chat)
4. Toggle: ON → "Summarize the methodology" (detailed with citations)
```

## Implementation Details

The toggle controls which function is called:

```python
def handle_message(message, history, force_retrieval, ...):
    if force_retrieval:
        return rag_chat(...)      # Full pipeline
    else:
        return simple_llm_chat(...)  # Direct LLM
```

**Simple LLM Path:**
```
User Input → LM Studio Client → Response
```

**RAG Path:**
```
User Input → Pipeline.invoke() → 
  HyDE → Embed → MMR → Rerank → Generate → 
  Response + Sources
```

## Benefits

1. **User Control**: Choose when to use expensive RAG
2. **Performance**: Faster for simple queries
3. **Flexibility**: Mix modes in same conversation
4. **Efficiency**: Don't search when not needed
5. **Clarity**: Clear indication of which mode is active
