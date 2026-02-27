# ============================================
# Accessible Map AI Frontend - Startup Script
# ============================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Accessible Map AI Frontend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env" -ErrorAction SilentlyContinue
}

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
python --version | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Python not found. Please install Python 3.10+" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ Python found" -ForegroundColor Green

# Check and activate virtual environment
Write-Host ""
$venvPath = "..\.venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv ..\.venv
    & $venvPath
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -q -r requirements.txt
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Display info
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Frontend Configuration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ensure the backend is running:" -ForegroundColor Yellow
Write-Host "   - API URL: http://localhost:8000" -ForegroundColor White
Write-Host "   - Health: http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "Frontend will start at:" -ForegroundColor Yellow
Write-Host "   - URL: http://localhost:8501" -ForegroundColor White
Write-Host ""

# Ask before running
$ready = Read-Host "Start frontend now? (y/n)"
if ($ready -eq "y" -or $ready -eq "Y") {
    Write-Host ""
    Write-Host "Starting Streamlit app..." -ForegroundColor Green
    Write-Host "Ctrl+C to stop the server" -ForegroundColor Yellow
    Write-Host ""
    streamlit run app.py
} else {
    Write-Host "Run 'streamlit run app.py' when ready" -ForegroundColor Yellow
}
