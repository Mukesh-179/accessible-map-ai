# MongoDB Integration Setup Guide

## Installation Options

### Option 1: Local MongoDB (Windows)

#### 1. Download and Install MongoDB Community Edition
- Visit: https://www.mongodb.com/try/download/community
- Choose Windows MSI installer
- Run the installer and follow the setup wizard
- Select "Install MongoDB as a Windows Service"

#### 2. Verify Installation
```powershell
mongod --version
```

#### 3. Start MongoDB Service
```powershell
# MongoDB should start automatically as a Windows Service
# Or manually start it with:
mongod
```

#### 4. Connect with MongoDB Compass (Optional GUI)
- Download: https://www.mongodb.com/products/compass
- Connection string: `mongodb://localhost:27017`

---

### Option 2: MongoDB Atlas (Cloud - Recommended for Development)

#### 1. Create Atlas Account
- Go to: https://www.mongodb.com/cloud/atlas
- Sign up with email
- Create a new organization and project

#### 2. Create a Cluster
- Choose "Free Tier" (M0)
- Select cloud provider and region (closest to you)
- Create cluster

#### 3. Get Connection String
- Go to "Databases" → Click "Connect"
- Choose "Drivers" option
- Copy the connection string
- Replace `<username>` and `<password>` with your credentials

#### 4. Update .env File
```
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/accessible_map?retryWrites=true&w=majority
```

---

### Option 3: Docker (Easiest for Development)

#### 1. Install Docker
- Download from: https://www.docker.com/products/docker-desktop

#### 2. Run MongoDB Container
```powershell
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

#### 3. Verify Connection
```powershell
docker logs mongodb
```

---

## Configuration

### 1. Copy .env File
```powershell
copy .env.example .env
```

### 2. Update MongoDB URL
Edit `.env` and set `MONGODB_URL` to your connection string:
- **Local**: `mongodb://localhost:27017`
- **Atlas**: `mongodb+srv://username:password@cluster.mongodb.net/accessible_map?retryWrites=true&w=majority`
- **Docker**: `mongodb://localhost:27017`

### 3. Set Database Name
```
MONGODB_DB_NAME=accessible_map
```

---

## Testing MongoDB Connection

### 1. Run the Application
```powershell
cd accessible-map-backend
python main.py
```

### 2. Check Health Endpoint
```powershell
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-27T12:00:00",
  "database": "connected",
  "redis": "connected"
}
```

### 3. Test API with Sample Data
```powershell
# Register a user
$body = @{
    email = "test@example.com"
    password = "password123"
    name = "Test User"
    accessibility_mode = "wheelchair"
} | ConvertTo-Json

curl -X POST http://localhost:8000/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d $body
```

---

## MongoDB Collections Created

The application automatically creates these collections with indexes:

1. **users** - Store user profiles and authentication
   - Index: email (unique)
   - Index: location (geospatial)

2. **routes** - Store route history
   - Index: user_id
   - Index: start_location (geospatial)
   - Index: end_location (geospatial)

3. **reports** - Store accessibility reports
   - Index: location (geospatial)
   - Index: type

4. **parking** - Store parking information
   - Index: location (geospatial)

5. **sos** - Store SOS emergency calls
   - Index: user_id

---

## Troubleshooting

### MongoDB Won't Connect
```powershell
# Check if MongoDB is running
tasklist | findstr mongod

# Check MongoDB service status
Get-Service | findstr MongoDB

# Restart MongoDB service
Restart-Service MongoDB
```

### Connection Timeout
- Verify MongoDB URL is correct
- Check firewall settings
- For Atlas: Whitelist your IP address in security settings

### Connection Refused
- Ensure MongoDB is running
- Check port 27017 is not blocked
- For local: `mongod` should be running in background

---

## Next Steps

1. ✅ Install MongoDB (local, Docker, or Atlas)
2. ✅ Update `.env` with connection string
3. ✅ Run the application
4. ✅ Test the `/health` endpoint
5. ✅ Create test data with API endpoints

For more info: https://docs.mongodb.com/
