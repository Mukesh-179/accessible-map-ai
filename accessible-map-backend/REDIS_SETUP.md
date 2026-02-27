# Redis Integration Setup Guide

## Installation Options

### Option 1: Windows Subsystem for Linux (WSL2) - Recommended

#### 1. Install WSL2
```powershell
# Run as Administrator
wsl --install
# Restart your computer
```

#### 2. Install Redis in WSL
```bash
sudo apt update
sudo apt install redis-server
```

#### 3. Start Redis
```bash
redis-server
```

#### 4. Test Connection
```bash
redis-cli ping
# Should return: PONG
```

---

### Option 2: Docker

#### 1. Install Docker Desktop
- Download from: https://www.docker.com/products/docker-desktop

#### 2. Run Redis Container
```powershell
docker run -d -p 6379:6379 --name redis redis:latest
```

#### 3. Verify Running
```powershell
docker logs redis
```

---

### Option 3: Pre-built Windows Binary

#### 1. Download Redis
- Visit: https://github.com/microsoftarchive/redis/releases
- Download latest MSI installer (redis-server-*.msi)

#### 2. Install and Start
- Run installer
- Redis will start as a Windows Service

#### 3. Verify
```powershell
redis-cli ping
# Should return: PONG
```

---

## Configuration

### 1. Update .env File
```
REDIS_URL=redis://localhost:6379
```

### 2. For Docker
```
REDIS_URL=redis://localhost:6379
```

### 3. For WSL2
```
REDIS_URL=redis://localhost:6379
```

---

## Testing Redis Connection

### 1. Using redis-cli
```powershell
redis-cli
> PING
PONG
> SET test_key "Hello Redis"
OK
> GET test_key
"Hello Redis"
```

### 2. Using Python
```python
import redis.asyncio as redis

r = redis.from_url("redis://localhost:6379", decode_responses=True)
await r.ping()  # Should return True
```

---

## Troubleshooting

### Redis Connection Refused
```powershell
# Check if Redis is running
tasklist | findstr redis

# Test connection
redis-cli ping
```

### Port Already in Use
```powershell
# Find process using port 6379
netstat -ano | findstr :6379

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or use different port - update .env
REDIS_URL=redis://localhost:6380
```

### WSL2 Redis Not Accessible from Windows
- Add to WSL .bashrc:
```bash
redis-server --bind 0.0.0.0
```

---

## Full Setup Checklist

- [ ] MongoDB installed and running
- [ ] Redis installed and running
- [ ] `.env` file created with correct URLs
- [ ] FastAPI application running
- [ ] Health endpoint returns "database": "connected" and "redis": "connected"

The application requires **both MongoDB and Redis** to function properly:
- **MongoDB**: Persistent data storage (users, routes, reports)
- **Redis**: Caching and session management
