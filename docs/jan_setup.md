# Jan Local LLM Server Setup Guide

This guide will walk you through setting up Jan as your local LLM server for the Research RAG system.

## What is Jan?

Jan is a free, open-source application that lets you run LLMs locally on your machine. It provides an OpenAI-compatible API, making it easy to use with existing tools.

## System Requirements

- **GPU**: NVIDIA RTX Ada 5000 (24GB VRAM) ✅ More than enough
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: ~10GB for Jan + model

## Step 1: Download and Install Jan

1. Go to [jan.ai](https://jan.ai)
2. Click **Download** and select **Windows**
3. Run the installer
4. Launch Jan

## Step 2: Download the LLM Model

1. In Jan, click the **Hub** tab (left sidebar)
2. Search for **"Llama 3"** or **"llama-3.3"**
3. Find **Llama 3.3 8B Instruct** (or similar 8B instruct model)
4. Click **Download**

**Note**: The download is ~5-8GB. Wait for it to complete.

### Alternative Models (if Llama 3.3 isn't available)

- **Mistral 7B Instruct** - Excellent for research tasks
- **Llama 3.1 8B Instruct** - Previous version, also good
- **Qwen 2.5 7B Instruct** - Great multilingual support

## Step 3: Configure the Model

1. Go to **Model Settings** (click the model name)
2. Set these parameters:
   - **Context Length**: 4096 (or 8192 if you have headroom)
   - **Temperature**: 0.7
   - **Max Tokens**: 2048

## Step 4: Enable the Local API Server

This is the critical step that allows our RAG system to communicate with Jan.

1. Click the **⚙️ Settings** icon (bottom left)
2. Navigate to **Local API Server**
3. Configure:
   - **Enable Local Server**: ✅ ON
   - **Port**: `1337` (default)
   - **CORS**: ✅ Enabled
4. Click **Start Server**

You should see a green indicator showing the server is running.

## Step 5: Verify the Server is Working

Open a terminal (PowerShell) and run:

```powershell
curl http://localhost:1337/v1/models
```

You should see a JSON response listing available models:

```json
{
  "data": [
    {
      "id": "llama-3.3-8b-instruct",
      "object": "model",
      ...
    }
  ]
}
```

## Step 6: Test with a Simple Request

```powershell
curl http://localhost:1337/v1/chat/completions `
  -H "Content-Type: application/json" `
  -d '{
    "model": "llama-3.3-8b-instruct",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 50
  }'
```

You should get a response with the model's reply.

## Step 7: Update RAG Configuration (if needed)

If your model has a different name than `llama-3.3-8b-instruct`, update `config/settings.yaml`:

```yaml
jan:
  base_url: "http://localhost:1337/v1"
  model: "your-model-name-here"  # Match the model ID from step 5
```

## Troubleshooting

### "Cannot connect to Jan server"

1. Ensure Jan is running
2. Check that Local API Server is enabled and started
3. Verify the port (default 1337) is not blocked by firewall

### "Model not found"

1. Ensure the model is fully downloaded in Jan
2. Check the exact model ID in Jan's Hub tab
3. Update `config/settings.yaml` with the correct model name

### "CUDA out of memory"

1. Close other GPU-intensive applications
2. Reduce context length in Jan's model settings
3. Use a smaller model (7B instead of 8B)

### Slow responses

1. Ensure Jan is using GPU (check settings)
2. Reduce max_tokens for faster responses
3. Close other applications using GPU

## GPU Memory Usage

With RTX Ada 5000 (24GB):

| Component | VRAM Usage |
|-----------|------------|
| Llama 3.3 8B (4-bit) | ~6-8 GB |
| Llama 3.3 8B (8-bit) | ~10-12 GB |
| Embedding Model | ~1-2 GB |
| **Total** | **~8-14 GB** |

You have plenty of headroom for 4k-8k context length.

## Keeping Jan Running

For the RAG system to work, Jan must be:
1. Running (the application open)
2. With a model loaded
3. Local API Server started

Consider adding Jan to Windows startup if you use the RAG frequently.

---

## Quick Checklist

- [ ] Jan installed and running
- [ ] Llama 3.3 8B (or similar) downloaded
- [ ] Model settings configured (4096 context, 0.7 temp)
- [ ] Local API Server enabled and started
- [ ] Port 1337 accessible
- [ ] `curl localhost:1337/v1/models` returns model list
- [ ] Config updated with correct model name

Once all items are checked, run the RAG diagnostics:

```powershell
cd c:\Users\romaric\Documents\research_RAG
python -m src.utils.diagnostics
```
