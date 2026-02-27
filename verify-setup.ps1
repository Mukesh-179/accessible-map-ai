# System Setup Verification Script
# Checks that all components of Accessible Map AI are properly configured

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Accessible Map AI - Setup Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$checks_passed = 0
$checks_failed = 0
$warnings = @()

# ==================== PYTHON CHECK ====================
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $python_version = python --version 2>&1 | Select-String "Python"
    Write-Host "✓ Python: $python_version" -ForegroundColor Green
    $checks_passed++
} catch {
    Write-Host "✗ Python not found" -ForegroundColor Red
    $checks_failed++
}

# ==================== VIRTUAL ENVIRONMENT CHECK ====================
Write-Host "Checking Virtual Environment..." -ForegroundColor Yellow
$venv_path = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $venv_path) {
    Write-Host "✓ Virtual environment exists" -ForegroundColor Green
    $checks_passed++
} else {
    Write-Host "⚠ Virtual environment not found" -ForegroundColor Yellow
    $warnings += "Run: python -m venv .venv"
}

# ==================== BACKEND DIRECTORY CHECK ====================
Write-Host ""
Write-Host "Checking Backend Directory..." -ForegroundColor Yellow
if (Test-Path "accessible-map-backend") {
    Write-Host "✓ Backend directory found" -ForegroundColor Green
    $checks_passed++
    
    # Check main.py
    if (Test-Path "accessible-map-backend\main.py") {
        Write-Host "  ✓ main.py exists" -ForegroundColor Green
        $checks_passed++
    } else {
        Write-Host "  ✗ main.py missing" -ForegroundColor Red
        $checks_failed++
    }
    
    # Check requirements.txt
    if (Test-Path "accessible-map-backend\requirements.txt") {
        Write-Host "  ✓ requirements.txt exists" -ForegroundColor Green
        $checks_passed++
    } else {
        Write-Host "  ✗ requirements.txt missing" -ForegroundColor Red
        $checks_failed++
    }
    
    # Check YOLO model
    if (Test-Path "accessible-map-backend\yolov8n.pt") {
        $model_size = (Get-Item "accessible-map-backend\yolov8n.pt").Length / 1MB
        Write-Host "  ✓ YOLO model exists ($([Math]::Round($model_size, 2)) MB)" -ForegroundColor Green
        $checks_passed++
    } else {
        Write-Host "  ⚠ YOLO model not found (will download on first run)" -ForegroundColor Yellow
        $warnings += "YOLO model download requires internet connection"
    }
} else {
    Write-Host "✗ Backend directory not found" -ForegroundColor Red
    $checks_failed++
}

# ==================== FRONTEND DIRECTORY CHECK ====================
Write-Host ""
Write-Host "Checking Frontend Directory..." -ForegroundColor Yellow
if (Test-Path "accessible-map-frontend") {
    Write-Host "✓ Frontend directory found" -ForegroundColor Green
    $checks_passed++
    
    # Check app.py
    if (Test-Path "accessible-map-frontend\app.py") {
        Write-Host "  ✓ app.py exists" -ForegroundColor Green
        $checks_passed++
    } else {
        Write-Host "  ✗ app.py missing" -ForegroundColor Red
        $checks_failed++
    }
    
    # Check requirements.txt
    if (Test-Path "accessible-map-frontend\requirements.txt") {
        Write-Host "  ✓ requirements.txt exists" -ForegroundColor Green
        $checks_passed++
    } else {
        Write-Host "  ✗ requirements.txt missing" -ForegroundColor Red
        $checks_failed++
    }
} else {
    Write-Host "✗ Frontend directory not found" -ForegroundColor Red
    $checks_failed++
}

# ==================== PYTHON PACKAGES CHECK ====================
Write-Host ""
Write-Host "Checking Python Packages..." -ForegroundColor Yellow

$packages = @(
    "fastapi",
    "pydantic",
    "motor",
    "redis",
    "opencv-python",
    "numpy",
    "ultralytics",
    "easyocr",
    "streamlit",
    "requests"
)

# Try to activate venv first
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    & ".\.venv\Scripts\Activate.ps1"
}

foreach ($package in $packages) {
    try {
        $version = pip show $package 2>$null | Select-String "Version" | ForEach-Object { $_ -split ": " | Select-Object -Last 1 }
        if ($version) {
            Write-Host "  ✓ $package ($version)" -ForegroundColor Green
            $checks_passed++
        }
    } catch {
        Write-Host "  ⚠ $package not installed" -ForegroundColor Yellow
        $warnings += "Run: pip install -r requirements.txt"
    }
}

# ==================== PORT AVAILABILITY CHECK ====================
Write-Host ""
Write-Host "Checking Port Availability..." -ForegroundColor Yellow

$ports = @(
    @{port=8000; service="Backend API"},
    @{port=8501; service="Frontend (Streamlit)"},
    @{port=27017; service="MongoDB"},
    @{port=6379; service="Redis"}
)

foreach ($port_info in $ports) {
    $port = $port_info.port
    $service = $port_info.service
    
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("127.0.0.1", $port)
        if ($connection.Connected) {
            Write-Host "  ⚠ $service (port $port): IN USE (already running)" -ForegroundColor Yellow
            $connection.Close()
        }
    } catch {
        Write-Host "  ✓ $service (port $port): Available" -ForegroundColor Green
        $checks_passed++
    }
}

# ==================== DOCKER CHECK ====================
Write-Host ""
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    $docker_version = docker --version 2>&1
    Write-Host "✓ Docker: $docker_version" -ForegroundColor Green
    $checks_passed++
    
    # Check if containers are running
    $running = docker ps -q 2>$null | Measure-Object -Line
    if ($running.Lines -gt 0) {
        Write-Host "  ✓ Docker daemon is running" -ForegroundColor Green
        $checks_passed++
    } else {
        Write-Host "  ✓ Docker is installed but no containers running" -ForegroundColor Green
        $checks_passed++
    }
} catch {
    Write-Host "⚠ Docker not found (optional for local development)" -ForegroundColor Yellow
    $warnings += "Docker is recommended for MongoDB/Redis setup"
}

# ==================== GIT CHECK ====================
Write-Host ""
Write-Host "Checking Git..." -ForegroundColor Yellow
try {
    $git_version = git --version 2>&1
    Write-Host "✓ Git: $git_version" -ForegroundColor Green
    $checks_passed++
} catch {
    Write-Host "⚠ Git not found (optional)" -ForegroundColor Yellow
}

# ==================== CONFIGURATION FILES CHECK ====================
Write-Host ""
Write-Host "Checking Configuration Files..." -ForegroundColor Yellow

@(
    @{path="accessible-map-backend\.env.example"; name="Backend .env template"},
    @{path="accessible-map-frontend\.env.example"; name="Frontend .env template"},
    @{path="accessible-map-backend\MONGODB_SETUP.md"; name="MongoDB setup guide"},
    @{path="accessible-map-backend\REDIS_SETUP.md"; name="Redis setup guide"},
    @{path="accessible-map-backend\README.md"; name="Backend README"},
    @{path="accessible-map-frontend\FRONTEND_README.md"; name="Frontend README"},
    @{path="QUICKSTART.md"; name="Quick start guide"}
) | ForEach-Object {
    if (Test-Path $_.path) {
        Write-Host "  ✓ $($_.name)" -ForegroundColor Green
        $checks_passed++
    } else {
        Write-Host "  ⚠ $($_.name) not found" -ForegroundColor Yellow
    }
}

# ==================== STARTUP SCRIPTS CHECK ====================
Write-Host ""
Write-Host "Checking Startup Scripts..." -ForegroundColor Yellow

@(
    @{path="accessible-map-backend\run.bat"; name="Backend batch script"},
    @{path="accessible-map-backend\run.ps1"; name="Backend PowerShell script"},
    @{path="accessible-map-frontend\run.bat"; name="Frontend batch script"},
    @{path="accessible-map-frontend\run.ps1"; name="Frontend PowerShell script"}
) | ForEach-Object {
    if (Test-Path $_.path) {
        Write-Host "  ✓ $($_.name)" -ForegroundColor Green
        $checks_passed++
    } else {
        Write-Host "  ⚠ $($_.name) not found" -ForegroundColor Yellow
    }
}

# ==================== SUMMARY ====================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Checks Passed: $checks_passed" -ForegroundColor Green
Write-Host "Checks Failed: $checks_failed" -ForegroundColor Red
Write-Host ""

if ($warnings.Count -gt 0) {
    Write-Host "Warnings & Recommendations:" -ForegroundColor Yellow
    Write-Host ""
    $warnings | ForEach-Object { Write-Host "  • $_" }
    Write-Host ""
}

# ==================== NEXT STEPS ====================
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. START BACKEND:" -ForegroundColor White
Write-Host "   cd accessible-map-backend" -ForegroundColor Gray
Write-Host "   python main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "2. START FRONTEND (New Terminal):" -ForegroundColor White
Write-Host "   cd accessible-map-frontend" -ForegroundColor Gray
Write-Host "   .\run.bat" -ForegroundColor Gray
Write-Host ""
Write-Host "3. SETUP DATABASES (Optional):" -ForegroundColor White
Write-Host "   docker run -d -p 27017:27017 --name mongodb mongo:latest" -ForegroundColor Gray
Write-Host "   docker run -d -p 6379:6379 --name redis redis:latest" -ForegroundColor Gray
Write-Host ""
Write-Host "4. ACCESS THE PLATFORM:" -ForegroundColor White
Write-Host "   Frontend: http://localhost:8501" -ForegroundColor Gray
Write-Host "   Backend: http://localhost:8000" -ForegroundColor Gray
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""

if ($checks_failed -eq 0) {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✓ System is ready to deploy!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "⚠ Please resolve the failures above" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
}

Write-Host ""
