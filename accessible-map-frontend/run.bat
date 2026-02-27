@echo off
REM ============================================
REM Accessible Map AI Frontend - Startup Script
REM ============================================

echo.
echo ========================================
echo Starting Accessible Map AI Frontend
echo ========================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env 2>nul
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

REM Check and activate virtual environment
echo.
if exist "..\.venv\Scripts\activate.bat" (
    call ..\.venv\Scripts\activate.bat
    echo ✓ Virtual environment activated
) else (
    echo Creating virtual environment...
    python -m venv ..\.venv
    call ..\.venv\Scripts\activate.bat
    echo ✓ Virtual environment created
)

REM Install dependencies
echo.
echo Installing dependencies...
pip install -q -r requirements.txt
echo ✓ Dependencies installed

REM Display info
echo.
echo ========================================
echo Frontend Configuration
echo ========================================
echo.
echo Ensure the backend is running:
echo   - API URL: http://localhost:8000
echo   - Health: http://localhost:8000/health
echo.
echo Frontend will start at:
echo   - URL: http://localhost:8501
echo.

REM Ask before running
setlocal enabledelayedexpansion
set /p "ready=Start frontend now? (y/n): "
if /i "%ready%"=="y" (
    echo.
    echo Starting Streamlit app...
    echo Ctrl+C to stop the server
    echo.
    streamlit run app.py
) else (
    echo Run 'streamlit run app.py' when ready
)

pause
