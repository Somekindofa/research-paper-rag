#!/bin/bash
# Startup script for Research RAG System

echo "🚀 Starting Research RAG System"
echo "================================"
echo ""

# Check if backend dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "⚠️  Backend dependencies not found. Installing..."
    pip install -r requirements.txt
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "⚠️  Frontend dependencies not found. Installing..."
    cd frontend && npm install && cd ..
fi

echo ""
echo "✅ Dependencies ready"
echo ""

# Start backend in background
echo "🔧 Starting backend (port 8000)..."
python src/api/server.py &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Start frontend
echo "⚛️  Starting frontend (port 3000)..."
cd frontend
npm start &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"
cd ..

echo ""
echo "================================"
echo "✅ Research RAG System is running!"
echo ""
echo "📍 Frontend: http://localhost:3000"
echo "📍 Backend:  http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both services"
echo "================================"

# Wait for user interrupt
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

# Keep script running
wait
