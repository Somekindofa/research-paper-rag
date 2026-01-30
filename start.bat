@echo off
REM Startup script for Research RAG System (Windows)

echo ========================================
echo Starting Research RAG System
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.10+
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found! Please install Node.js
    pause
    exit /b 1
)

REM Install backend dependencies if needed
echo Checking backend dependencies...
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo Installing backend dependencies...
    pip install -r requirements.txt
)

REM Install frontend dependencies if needed
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

echo.
echo Dependencies ready!
echo.

REM Start backend
echo Starting backend (port 8000)...
start "Research RAG Backend" python src\api\server.py

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
echo Starting frontend (port 3000)...
cd frontend
start "Research RAG Frontend" npm start
cd ..

echo.
echo ========================================
echo Research RAG System is starting!
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Close the terminal windows to stop.
echo ========================================
echo.
pause
