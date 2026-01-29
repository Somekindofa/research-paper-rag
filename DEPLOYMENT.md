# Deployment Guide - Research RAG System

## Quick Start (5 Minutes)

### Prerequisites Checklist
- [ ] Python 3.10+ installed
- [ ] LM Studio running on workstation (accessible via Tailscale)
- [ ] At least one model loaded in LM Studio
- [ ] Git installed

### Step 1: Clone and Setup
```bash
git clone https://github.com/Somekindofa/research-paper-rag.git
cd research-paper-rag
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```bash
# Your LM Studio Tailscale IP (replace 100.0.0.0)
LM_STUDIO_BASE_URL=http://100.xxx.xxx.xxx:1234/v1

# Where your PDFs are located
PDF_FOLDER_PATH=data/pdfs

# Use GPU if available
EMBEDDING_DEVICE=cuda
```

### Step 3: Validate Installation
```bash
python validate_system.py
```

Expected output:
```
============================================================
Research RAG System - Validation Tests
============================================================
Testing configuration... ✓
Testing LM Studio client... ✓
Testing graph structure... ✓
Testing UI features... ✓
Testing custom assets... ✓

Passed: 5/5 tests
✓ All validation tests passed!
```

### Step 4: Add Your PDFs
```bash
# Copy your research papers to the PDF folder
cp /path/to/your/papers/*.pdf data/pdfs/

# Or organize in subfolders (2 levels deep supported)
mkdir -p data/pdfs/2024
cp /path/to/papers/2024/*.pdf data/pdfs/2024/
```

### Step 5: Start the Application
```bash
chainlit run src/ui/app.py
```

The UI will open at: http://localhost:8000

## First Time Usage

### 1. Check LM Studio Connection
When the UI starts, you should see:
```
✅ LM Studio Server Connected
Available models:
  • llama-70b-chat
  • mistral-7b-instruct
```

If not, troubleshoot:
- Is LM Studio running?
- Is the server enabled in LM Studio?
- Is Tailscale connected?
- Test: `curl http://100.xxx.xxx.xxx:1234/v1/models`

### 2. Select Your Model
- Look at top left of the screen
- You'll see a dropdown with available models
- Select your preferred model (larger models = better quality)

### 3. Adjust Settings
Open the settings panel (gear icon or sidebar):
- **Number of Documents**: 5 (good default)
- **Relevance Threshold**: 75% (adjust if getting too few/many results)

### 4. Index Your Papers
The UI will show:
```
📥 27 New PDFs Found
```

Click "✅ Index Now" to start:
- Indexing runs in background
- Progress shown at top of screen
- You can still query already-indexed papers
- For 100 papers: expect ~10-15 minutes

### 5. Start Querying
Type your research question, for example:
```
What are the main approaches to SLAM in resource-constrained hardware?
```

The system will:
1. Generate a hypothetical answer (HyDE)
2. Search your papers
3. Rerank results
4. Filter by your threshold
5. Generate answer with citations

## Advanced Configuration

### Performance Tuning

#### For Speed
```yaml
# config/settings.yaml
retrieval:
  k: 3  # Fewer documents = faster
  fetch_k: 10  # Smaller candidate pool

reranker:
  top_k: 3  # Less reranking
```

#### For Quality
```yaml
retrieval:
  k: 10  # More documents = better context
  fetch_k: 30  # Larger candidate pool

reranker:
  top_k: 10  # More precise reranking
```

### GPU Configuration

#### Check GPU Status
```bash
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

#### Force CPU (if GPU issues)
```bash
# In .env
EMBEDDING_DEVICE=cpu
```

### Custom Models

#### Add More Models in LM Studio
1. Open LM Studio
2. Go to "Models" tab
3. Download/load your model
4. Refresh the Chainlit UI
5. New model appears in dropdown

#### Recommended Models
- **Fast**: Mistral-7B (~2-3s generation)
- **Balanced**: Llama-3-8B (~3-5s generation)
- **Quality**: Llama-3-70B (~10-20s generation)
- **Specialized**: Qwen-14B-Chat (great for technical papers)

## Troubleshooting

### Issue: No Models in Dropdown
**Cause**: LM Studio not running or no models loaded
**Fix**:
1. Open LM Studio
2. Load a model
3. Ensure "Local Server" is running
4. Refresh browser

### Issue: Indexing Stuck
**Cause**: LLM server not responding
**Fix**:
1. Check LM Studio is running
2. Check model is loaded
3. Test: `curl -X POST http://100.xxx.xxx.xxx:1234/v1/chat/completions -d '{"model":"your-model","messages":[{"role":"user","content":"test"}]}'`

### Issue: Slow Embeddings
**Cause**: Using CPU instead of GPU
**Fix**:
```bash
# Check GPU
nvidia-smi

# Verify PyTorch sees GPU
python -c "import torch; print(torch.cuda.get_device_name(0))"

# Reinstall PyTorch with CUDA if needed
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### Issue: Out of Memory
**Cause**: Too many documents or model too large
**Fix**:
1. Reduce `retrieval.k` in settings
2. Use smaller model in LM Studio
3. Clear vector store: `rm -rf data/chroma_db`
4. Reindex with fewer papers

### Issue: Low Quality Answers
**Cause**: Threshold too high or not enough context
**Fix**:
1. Lower relevance threshold (try 60%)
2. Increase number of documents (try 10)
3. Use larger LM model
4. Check if papers are relevant to query

## Maintenance

### Backup Your Data
```bash
# Backup vector store
tar -czf chroma_backup.tar.gz data/chroma_db/

# Backup metadata
tar -czf metadata_backup.tar.gz data/metadata/
```

### Update Papers
```bash
# Add new papers
cp /path/to/new/papers/*.pdf data/pdfs/

# Restart UI or refresh chat
# Click "Index Now" when prompted
```

### Clear and Reindex
```bash
# Remove vector store
rm -rf data/chroma_db

# Remove metadata
rm -rf data/metadata

# Restart UI - all papers will be reindexed
```

### Monitor Performance
```bash
# Check vector store size
du -sh data/chroma_db

# Check number of indexed papers
python -c "from src.retrieval.vectorstore import get_vector_store; print(f'Chunks: {get_vector_store().count()}')"

# Check GPU usage during query
nvidia-smi -l 1
```

## Production Deployment

### Docker Deployment (Optional)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["chainlit", "run", "src/ui/app.py", "--host", "0.0.0.0"]
```

```bash
docker build -t research-rag .
docker run -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e LM_STUDIO_BASE_URL=http://100.xxx.xxx.xxx:1234/v1 \
  research-rag
```

### Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name research-rag.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Systemd Service
```ini
[Unit]
Description=Research RAG System
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/research-paper-rag
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/chainlit run src/ui/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Security Best Practices

1. **Network Security**
   - Use Tailscale for secure remote access
   - Never expose LM Studio to public internet
   - Use firewall rules

2. **Data Privacy**
   - All data stays local/in private network
   - No external API calls
   - PDFs never leave infrastructure

3. **Access Control**
   - Consider adding authentication to Chainlit
   - Use environment variables for secrets
   - Don't commit .env to git

## Support

### Get Help
1. Check `README.md` for features
2. Check `IMPLEMENTATION_SUMMARY.md` for technical details
3. Check `UI_GUIDE.md` for UI mockups
4. Run `validate_system.py` for diagnostics

### Common Questions

**Q: Can I use OpenAI instead of LM Studio?**
A: Yes! Just update `LM_STUDIO_BASE_URL` to OpenAI's API endpoint.

**Q: How do I add more metadata fields?**
A: Edit `config/prompts.yaml` metadata_extraction template.

**Q: Can I search by author or year?**
A: Not yet, but metadata is stored - feature can be added.

**Q: Does it support non-English papers?**
A: Yes, if your model supports the language.

**Q: Can I use multiple vector stores?**
A: Yes, change `CHROMA_PERSIST_DIR` in .env for different projects.

## Success Checklist

After deployment, verify:
- [ ] UI loads at http://localhost:8000
- [ ] Model selector shows available models
- [ ] Settings panel with sliders visible
- [ ] PDFs detected and indexing offered
- [ ] Indexing completes with metadata
- [ ] Query returns relevant results with citations
- [ ] Sources show extracted metadata
- [ ] Can query during indexing

If all checked: **You're ready to go!** 🎉
