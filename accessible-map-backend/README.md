# Accessible Map AI - Backend Setup & Integration Guide

Complete integration guide for MongoDB, Redis, and FastAPI backend.

## 📋 Quick Start

### 1️⃣ Setup Environment (1 minute)
```powershell
# Navigate to backend directory
cd accessible-map-backend

# Run setup script (PowerShell)
.\run.ps1

# Or run with batch (Command Prompt)
run.bat
```

### 2️⃣ Configure MongoDB & Redis (5-10 minutes)

#### Option A: Docker (Easiest)
```powershell
# Terminal 1: MongoDB
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Terminal 2: Redis
docker run -d -p 6379:6379 --name redis redis:latest

# Verify
docker logs mongodb
docker logs redis
```

#### Option B: Local Installation
- Follow [MONGODB_SETUP.md](MONGODB_SETUP.md)
- Follow [REDIS_SETUP.md](REDIS_SETUP.md)

#### Option C: MongoDB Atlas + Local Redis
- MongoDB Atlas: https://www.mongodb.com/cloud/atlas (free tier)
- Redis: Local or Docker

### 3️⃣ Start the Server
```powershell
python main.py
```

**Server starts at:** `http://localhost:8000`
**API Documentation:** `http://localhost:8000/docs`

---

## 🗄️ MongoDB Integration Details

### Collections Automatically Created

The application creates these collections with proper indexes:

```
accessible_map
├── users
│   ├── Index: email (unique)
│   └── Index: location (geospatial)
├── routes
│   ├── Index: user_id
│   ├── Index: start_location (geospatial)
│   └── Index: end_location (geospatial)
├── reports
│   ├── Index: location (geospatial)
│   └── Index: type
├── parking
│   └── Index: location (geospatial)
└── sos
    └── Index: user_id
```

### Data Models

#### Users Collection
```json
{
  "_id": ObjectId,
  "email": "user@example.com",
  "password_hash": "hashed_password",
  "profile": {
    "name": "John Doe",
    "phone": "+1234567890",
    "accessibility_mode": "wheelchair",
    "disabilities": ["mobility"],
    "emergency_contacts": [...]
  },
  "preferences": {
    "voice_guidance": true,
    "language": "en"
  },
  "safety_score": 100.0,
  "created_at": ISODate
}
```

#### Routes Collection
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "start_point": {
    "coordinates": {"lat": 0, "lng": 0},
    "address": "123 Main St"
  },
  "end_point": {...},
  "segments": [...],
  "metrics": {
    "total_distance": 1500,
    "accessibility_score": 85,
    "safety_score": 90
  }
}
```

#### Reports Collection
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "type": "broken_ramp",
  "location": {"lat": 0, "lng": 0},
  "description": "Broken wheelchair ramp",
  "severity": "high",
  "verified": false,
  "status": "active",
  "created_at": ISODate
}
```

---

## 🔴 Redis Integration Details

Redis is used for:

1. **Route Caching** - Cache computed routes for 5 minutes
2. **Session Management** - Store user sessions
3. **Real-time Data** - Cache frequently accessed data

### Cache Keys

```
route:{hash}              # Cached route queries
user_session:{user_id}    # User session data
health_check             # Server health status
```

---

## ✅ Health Check Endpoint

Test that everything is connected:

```powershell
# PowerShell
$response = curl -Uri http://localhost:8000/health
$response.RawContent | ConvertFrom-Json | Format-List

# Should show:
# status       : healthy
# database     : connected
# redis        : connected
```

---

## 🔌 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout

### Routes
- `POST /api/v1/routes/plan` - Plan accessible route
- `GET /api/v1/routes/history` - Get user's route history

### Vision (ML)
- `POST /api/v1/vision/detect-obstacles` - Detect obstacles in image
- `POST /api/v1/vision/read-sign` - Read text from sign
- `POST /api/v1/vision/detect-crossing` - Detect pedestrian crossing
- `POST /api/v1/vision/analyze-surface` - Analyze surface quality

### Reports
- `POST /api/v1/reports` - Create accessibility report
- `GET /api/v1/reports/nearby` - Get nearby reports
- `POST /api/v1/reports/{id}/verify` - Verify report

### Parking
- `GET /api/v1/parking/nearby` - Find nearby parking

### Emergency
- `POST /api/v1/emergency/sos` - Trigger SOS
- `GET /api/v1/emergency/contacts` - Get emergency contacts
- `POST /api/v1/emergency/contacts` - Add emergency contact

---

## 🐛 Troubleshooting

### MongoDB Connection Failed

**Error:** `MongoDB connection failed`

**Solutions:**
1. Verify MongoDB is running
   ```powershell
   mongod --version
   ```

2. Check connection URL in `.env`
   - Local: `mongodb://localhost:27017`
   - Atlas: `mongodb+srv://user:pass@cluster.mongodb.net/db`

3. For Atlas, whitelist your IP address in security settings

### Redis Connection Failed

**Error:** `Redis connection failed`

**Solutions:**
1. Verify Redis is running
   ```powershell
   redis-cli ping
   ```

2. Check connection URL in `.env`
   - Should be: `redis://localhost:6379`

3. Ensure port 6379 is not blocked by firewall

### Port Already in Use

**Error:** `Address already in use`

**Solutions:**
```powershell
# Find process using port
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F

# Or change port in main.py
uvicorn.run("main:app", port=8001)
```

### Database Connected but Can't Access Collections

**Solution:** Collections are created automatically on first use. Make sure:
1. `.env` has correct database name: `MONGODB_DB_NAME=accessible_map`
2. Check MongoDB logs for any errors
3. Verify read/write permissions

---

## 📊 Environment Variables

Create a `.env` file in `accessible-map-backend/`:

```env
# App
APP_NAME=Accessible Map AI
ENVIRONMENT=development
DEBUG=True

# Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=accessible_map

# Cache
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-change-in-production

# APIs
GOOGLE_MAPS_API_KEY=
MAPBOX_ACCESS_TOKEN=
```

---

## 🚀 Running in Production

For production deployment:

1. **Security**
   - Change `SECRET_KEY` to a strong random string
   - Set `DEBUG=False`
   - Use HTTPS

2. **Database**
   - Use MongoDB Atlas with strong credentials
   - Enable network access controls
   - Regular backups

3. **Redis**
   - Use managed Redis service
   - Enable password authentication
   - Configure persistence

4. **Deployment**
   - Use Gunicorn/Uvicorn workers
   - Run behind Nginx reverse proxy
   - Enable logging and monitoring

Example production run:
```bash
# With Gunicorn (multiple workers)
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

---

## 📚 Documentation

- [MongoDB Setup](MONGODB_SETUP.md) - Detailed MongoDB installation & configuration
- [Redis Setup](REDIS_SETUP.md) - Detailed Redis installation & configuration
- [FastAPI Docs](http://localhost:8000/docs) - Interactive API documentation

---

## 💡 Testing the Integration

### Test User Registration
```powershell
$body = @{
    email = "testuser@example.com"
    password = "SecurePassword123!"
    name = "Test User"
    accessibility_mode = "wheelchair"
} | ConvertTo-Json

curl -X POST http://localhost:8000/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d $body
```

### Test Route Planning
```powershell
$body = @{
    start_lat = 40.7128
    start_lng = -74.0060
    end_lat = 40.7580
    end_lng = -73.9855
    mode = "wheelchair"
} | ConvertTo-Json

curl -X POST http://localhost:8000/api/v1/routes/plan `
  -H "Content-Type: application/json" `
  -d $body
```

---

## 🎯 Next Steps

1. ✅ Install MongoDB & Redis
2. ✅ Configure `.env` file
3. ✅ Run `python main.py`
4. ✅ Test health endpoint
5. ✅ Create test data
6. ✅ Deploy to cloud (Firebase, Azure, AWS)

---

**Happy coding! 🚀**
