@echo off
REM ============================================
REM Database Connectivity Verification Script
REM Tests MongoDB and Redis connections
REM ============================================

color 0A
cls

echo.
echo ========================================
echo Database Connectivity Verification
echo ========================================
echo.

REM Check MongoDB
echo Checking MongoDB connection...
echo.

REM Try Docker MongoDB first
docker ps 2>nul | find "mongodb" >nul
if %errorlevel% equ 0 (
    echo [DOCKER MONGODB]
    docker inspect mongodb 2>nul >nul
    if %errorlevel% equ 0 (
        for /f "tokens=*" %%a in ('docker inspect --format="{{.State.Running}}" mongodb 2^>nul') do set MONGO_RUNNING=%%a
        if "!MONGO_RUNNING!"=="true" (
            echo + Container running
            echo + Host: localhost
            echo + Port: 27017
            echo + Status: CONNECTED
            echo.
        ) else (
            echo - Container not running
            echo   Start with: docker start mongodb
            echo.
        )
    )
) else (
    echo [LOCAL MONGODB]
    netstat -an 2>nul | find ":27017" >nul
    if %errorlevel% equ 0 (
        echo + Listening on localhost:27017
        echo + Status: CONNECTED
        echo.
    ) else (
        echo - Not listening on :27017
        echo   Install from: https://www.mongodb.com/try/download/community
        echo   Or use: docker run -d -p 27017:27017 mongo:latest
        echo.
    )
)

REM Check Redis
echo Checking Redis connection...
echo.

REM Try Docker Redis first
docker ps 2>nul | find "redis" >nul
if %errorlevel% equ 0 (
    echo [DOCKER REDIS]
    docker inspect redis 2>nul >nul
    if %errorlevel% equ 0 (
        for /f "tokens=*" %%a in ('docker inspect --format="{{.State.Running}}" redis 2^>nul') do set REDIS_RUNNING=%%a
        if "!REDIS_RUNNING!"=="true" (
            echo + Container running
            echo + Host: localhost
            echo + Port: 6379
            echo + Status: CONNECTED
            echo.
        ) else (
            echo - Container not running
            echo   Start with: docker start redis
            echo.
        )
    )
) else (
    echo [LOCAL REDIS]
    netstat -an 2>nul | find ":6379" >nul
    if %errorlevel% equ 0 (
        echo + Listening on localhost:6379
        echo + Status: CONNECTED
        echo.
    ) else (
        echo - Not listening on :6379
        echo   Install from: https://github.com/microsoftarchive/redis/releases
        echo   Or use Docker: docker run -d -p 6379:6379 redis:latest
        echo.
    )
)

REM Check backend health
echo Checking Backend Health...
echo.

powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -TimeoutSec 5 -ErrorAction SilentlyContinue; if ($response.StatusCode -eq 200) { Write-Host '+ Backend is running'; Write-Host '+ URL: http://localhost:8000'; $json = $response.Content | ConvertFrom-Json; Write-Host ('+ Database: ' + $json.database); Write-Host ('+ Redis: ' + $json.redis) } else { Write-Host '- Backend not responding' } } catch { Write-Host '- Backend not reachable'; Write-Host '  Start with: cd accessible-map-backend ^&^& python main.py' }"

echo.

REM Display connection strings
echo ========================================
echo Connection Information
echo ========================================
echo.
echo Backend API
echo   URL: http://localhost:8000
echo   Docs: http://localhost:8000/docs
echo.
echo Frontend (Streamlit)
echo   URL: http://localhost:8501
echo.
echo MongoDB
echo   Host: localhost
echo   Port: 27017
echo   URI: mongodb://localhost:27017
echo.
echo Redis
echo   Host: localhost
echo   Port: 6379
echo   URI: redis://localhost:6379
echo.

REM Display next steps
echo ========================================
echo Next Steps
echo ========================================
echo.
echo 1. If MongoDB not connected:
echo    docker run -d -p 27017:27017 --name mongodb mongo:latest
echo.
echo 2. If Redis not connected:
echo    docker run -d -p 6379:6379 --name redis redis:latest
echo.
echo 3. If Backend not running:
echo    cd accessible-map-backend && python main.py
echo.
echo 4. If Frontend not running:
echo    cd accessible-map-frontend && streamlit run app.py
echo.

pause
