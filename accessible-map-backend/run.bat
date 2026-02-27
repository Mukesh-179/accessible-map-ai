@echo off
REM ============================================
REM Accessible Map AI - Quick Start Script
REM ============================================

echo.
echo ========================================
echo Accessible Map AI - Setup & Run
echo ========================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo ✓ .env file created - please update with your MongoDB and Redis URLs
    echo.
)

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ✗ Python not found. Please install Python 3.10+
    pause
    exit /b 1
)
echo ✓ Python found

REM Check virtual environment
echo.
echo Activating virtual environment...
if exist "..\..\.venv\Scripts\activate.bat" (
    call ..\..\.venv\Scripts\activate.bat
    echo ✓ Virtual environment activated
) else (
    echo ⚠ Virtual environment not found at expected location
)

REM Check dependencies
echo.
echo Checking dependencies...
python -m pip --quiet show pydantic >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing required packages...
    python -m pip install --quiet -r requirements.txt
)
echo ✓ Dependencies OK

REM Show settings
echo.
echo ========================================
echo Environment Configuration
echo ========================================
echo.
echo Before running the server, ensure:
echo.
echo 1. MongoDB:
echo    - Local: mongod running on localhost:27017
echo    - Docker: docker run -d -p 27017:27017 mongo
echo    - Atlas: MongoDB connection string in .env
echo.
echo 2. Redis:
echo    - Local: redis-server running on localhost:6379
echo    - Docker: docker run -d -p 6379:6379 redis
echo    - WSL2: sudo redis-server
echo.
echo 3. Update .env file with:
echo    MONGODB_URL=your_mongodb_url
echo    REDIS_URL=redis://localhost:6379
echo.

REM Ask user if ready
setlocal enabledelayedexpansion
set /p "ready=Start the server now? (y/n): "
if /i "%ready%"=="y" (
    echo.
    echo Starting FastAPI server...
    echo Server running at: http://localhost:8000
    echo API Docs at: http://localhost:8000/docs
    echo.
    python main.py
) else (
    echo Setup complete. Run 'python main.py' when ready.
)

pause
