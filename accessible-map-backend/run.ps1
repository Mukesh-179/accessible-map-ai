# ============================================
# Accessible Map AI - Quick Start Script
# ============================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Accessible Map AI - Setup & Run" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env file created - please update with your MongoDB and Redis URLs" -ForegroundColor Green
    Write-Host ""
}

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
python --version | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Python not found. Please install Python 3.10+" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "✓ Python found" -ForegroundColor Green

# Check virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
$venvPath = "..\..\.venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "⚠ Virtual environment not found at expected location" -ForegroundColor Yellow
}

# Check dependencies
Write-Host ""
Write-Host "Checking dependencies..." -ForegroundColor Yellow
python -c "import pydantic" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing required packages..." -ForegroundColor Yellow
    python -m pip install -q -r requirements.txt
}
Write-Host "✓ Dependencies OK" -ForegroundColor Green

# Show settings
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Environment Configuration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Before running the server, ensure:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. MongoDB:" -ForegroundColor Green
Write-Host "   - Local: mongod running on localhost:27017"
Write-Host "   - Docker: docker run -d -p 27017:27017 mongo"
Write-Host "   - Atlas: MongoDB connection string in .env"
Write-Host ""
Write-Host "2. Redis:" -ForegroundColor Green
Write-Host "   - Local: redis-server running on localhost:6379"
Write-Host "   - Docker: docker run -d -p 6379:6379 redis"
Write-Host "   - WSL2: sudo redis-server"
Write-Host ""
Write-Host "3. Update .env file with:" -ForegroundColor Green
Write-Host "   MONGODB_URL=your_mongodb_url"
Write-Host "   REDIS_URL=redis://localhost:6379"
Write-Host ""

# Ask user if ready
$ready = Read-Host "Start the server now? (y/n)"
if ($ready -eq "y" -or $ready -eq "Y") {
    Write-Host ""
    Write-Host "Starting FastAPI server..." -ForegroundColor Green
    Write-Host "Server running at: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "API Docs at: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    python main.py
} else {
    Write-Host "Setup complete. Run 'python main.py' when ready." -ForegroundColor Yellow
}
