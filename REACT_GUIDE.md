# React Application Guide

## Overview

The Research RAG system now uses a modern React + TypeScript frontend with a FastAPI backend. This architecture provides better performance, customization, and user experience.

## Architecture

```
┌─────────────────────┐
│   React Frontend    │
│   (TypeScript)      │
│   Port 3000         │
└──────────┬──────────┘
           │ HTTP/REST
           ↓
┌─────────────────────┐
│   FastAPI Backend   │
│   (Python)          │
│   Port 8000         │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│   RAG Pipeline      │
│   + Vector Store    │
│   + LM Studio       │
└─────────────────────┘
```

## Getting Started

### Prerequisites

- **Python 3.10+**: Backend runtime
- **Node.js 16+**: Frontend runtime  
- **npm or yarn**: Package manager
- **LM Studio**: Running on Tailscale network

### Installation

1. **Install Backend Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Frontend Dependencies:**
   ```bash
   cd frontend
   npm install
   ```

3. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

### Running the Application

**Option 1: Use Startup Scripts**

Linux/Mac:
```bash
./start.sh
```

Windows:
```bash
start.bat
```

**Option 2: Manual Start**

Terminal 1 - Backend:
```bash
python src/api/server.py
# Or with auto-reload:
uvicorn src.api.server:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 - Frontend:
```bash
cd frontend
npm start
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs (FastAPI auto-generated)

## Frontend Structure

```
frontend/
├── public/               # Static files
│   ├── index.html       # HTML template
│   └── ...
├── src/
│   ├── App.tsx          # Main component
│   ├── App.css          # Styles
│   ├── index.tsx        # Entry point
│   └── ...
├── package.json         # Dependencies
└── tsconfig.json        # TypeScript config
```

### Main Component (App.tsx)

The App component manages:
- **State Management**: Messages, settings, status
- **API Communication**: Fetch data from backend
- **User Interface**: Chat, settings, status panels
- **Real-time Updates**: Polling for status

### Key Features

#### 1. Force Retrieval Toggle
```typescript
const [forceRetrieval, setForceRetrieval] = useState(false);
```
- Controls whether to use RAG or simple LLM
- Prominently displayed at top of chat
- Affects API call to `/api/chat`

#### 2. Settings Panel
```typescript
const [selectedModel, setSelectedModel] = useState('');
const [numDocs, setNumDocs] = useState(5);
const [threshold, setThreshold] = useState(75);
```
- Model selection dropdown
- Document count slider (1-20)
- Relevance threshold slider (50-100%)

#### 3. Status Monitoring
```typescript
useEffect(() => {
  fetchStatus();
  const interval = setInterval(fetchStatus, 5000);
  return () => clearInterval(interval);
}, []);
```
- Polls backend every 5 seconds
- Shows LM Studio status
- Displays library statistics
- Monitors indexing progress

#### 4. Chat Interface
```typescript
interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  mode?: string;
}
```
- Message history with sources
- Loading states
- Error handling
- Smooth scrolling

## Backend API (FastAPI)

### Endpoints

#### Health Check
```
GET /api/health
Response: { "status": "healthy", "message": "API is running" }
```

#### System Status
```
GET /api/status
Response: {
  "lm_studio_status": "connected",
  "available_models": ["model1", "model2"],
  "library_status": { ... },
  "indexing_in_progress": false,
  "indexing_status": ""
}
```

#### Chat
```
POST /api/chat
Body: {
  "message": "Your question",
  "force_retrieval": false,
  "selected_model": "model-name",
  "num_docs": 5,
  "relevance_threshold": 0.75
}
Response: {
  "answer": "Response text",
  "sources": [...],
  "error": null,
  "mode": "simple" | "rag"
}
```

#### Models
```
GET /api/models
Response: {
  "models": ["model1", "model2"],
  "configured_model": "model1"
}
```

#### Indexing
```
POST /api/index
Response: {
  "status": "started",
  "message": "Indexing started in background"
}

GET /api/indexing-status
Response: {
  "in_progress": false,
  "status": "Complete!"
}
```

## Customization

### Styling

Edit `frontend/src/App.css` to customize:
- Colors and gradients
- Layout and spacing
- Component styles
- Responsive breakpoints

Example:
```css
.app-header {
  background: your-color;
  /* ... */
}
```

### Adding Features

1. **New Component:**
   ```typescript
   // frontend/src/components/MyComponent.tsx
   import React from 'react';
   
   function MyComponent() {
     return <div>Hello</div>;
   }
   
   export default MyComponent;
   ```

2. **New API Endpoint:**
   ```python
   # src/api/server.py
   @app.get("/api/my-endpoint")
   async def my_endpoint():
       return {"data": "value"}
   ```

3. **Call from Frontend:**
   ```typescript
   const fetchData = async () => {
     const response = await fetch('http://localhost:8000/api/my-endpoint');
     const data = await response.json();
   };
   ```

## Development Tips

### Hot Reload

Both frontend and backend support hot reload:
- **Frontend**: Changes to `.tsx` or `.css` files reload automatically
- **Backend**: Use `--reload` flag with uvicorn

### Debugging

**Frontend:**
- Open browser DevTools (F12)
- Check Console for errors
- Use React DevTools extension

**Backend:**
- Check terminal output
- Visit `/docs` for interactive API testing
- Add `print()` statements for debugging

### TypeScript

Type definitions help catch errors:
```typescript
interface MyData {
  field: string;
  count: number;
}

const data: MyData = { field: "value", count: 42 };
```

## Building for Production

### Frontend Build
```bash
cd frontend
npm run build
```
Creates optimized build in `frontend/build/`

### Serve Production Build
```bash
npm install -g serve
serve -s frontend/build -l 3000
```

### Backend Production
```bash
pip install gunicorn
gunicorn src.api.server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Deployment

### Docker (Optional)

**Backend Dockerfile:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile:**
```dockerfile
FROM node:18 AS build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
```

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### CORS Errors
Check `src/api/server.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your domain
    ...
)
```

### TypeScript Errors
```bash
cd frontend
npm install @types/react @types/react-dom @types/node
```

### Module Not Found
```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend && npm install
```

## Performance Optimization

### Frontend
- Use React.memo for expensive components
- Implement virtualization for long lists
- Lazy load components with React.lazy()

### Backend
- Use caching for repeated queries
- Implement connection pooling
- Add rate limiting

### Network
- Enable gzip compression
- Use CDN for static assets
- Implement request debouncing

## Security Considerations

1. **API Keys**: Never commit `.env` files
2. **CORS**: Restrict origins in production
3. **Input Validation**: Backend validates all inputs
4. **XSS**: React escapes content by default
5. **Rate Limiting**: Implement in production

## Resources

- [React Documentation](https://react.dev)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Create React App](https://create-react-app.dev)

## Support

For issues or questions:
1. Check console logs (frontend and backend)
2. Review API documentation at `/docs`
3. Check GitHub repository issues
4. Review this guide

---

The React application provides a modern, professional interface that's easy to use and customize. Enjoy your research!
