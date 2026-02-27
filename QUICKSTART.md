# Accessible Map AI - Quick Start Guide

Complete setup and deployment guide for the 18-feature smart mobility platform.

## 📋 Prerequisites

- Windows 10+, WSL2, or macOS
- Python 3.10+ installed
- 4GB+ RAM
- Docker (optional, recommended for MongoDB/Redis)
- 2GB disk space

## ⚡ Quick Start (5-10 minutes)

### Step 1: Setup Backend

```powershell
# Navigate to backend
cd accessible-map-backend

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies (if not already done)
pip install -r requirements.txt

# Start backend server
python main.py
```

✅ **Expected Output:**
```
✅ YOLO model loaded
✅ OCR model loaded
Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Setup Frontend (New Terminal)

```powershell
# Navigate to frontend
cd accessible-map-frontend

# Use quickstart script
run.bat
```

Or manually:
```powershell
.\venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

✅ **Expected Output:**
```
You can now view your Streamlit app in your browser.

  URL: http://localhost:8501
```

### Step 3: Access the Platform

1. Open browser: http://localhost:8501
2. Register a new account
3. Select accessibility mode (wheelchair, visually impaired, or elderly)
4. Log in
5. Explore features

## 🗄️ Database Setup (Optional but Recommended)

### Option A: Docker (Easiest)

```powershell
# Start MongoDB
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Start Redis
docker run -d -p 6379:6379 --name redis redis:latest

# Verify
docker ps
```

### Option B: Local Installation

See:
- [MongoDB Setup](accessible-map-backend/MONGODB_SETUP.md)
- [Redis Setup](accessible-map-backend/REDIS_SETUP.md)

### Step 4: Verify Connectivity

```bash
# Check backend health
curl http://localhost:8000/health

# Should return:
# {"status": "healthy", "database": "connected", "redis": "connected"}
```

## 🎯 Feature Overview

### Pages Available

| Page | Features |
|------|----------|
| **Dashboard** | Stats, health monitoring, quick access |
| **Route Planning** | Accessibility routing, maps, metrics |
| **Vision Assistance** | Obstacle detection, OCR, crossing detection, surface analysis |
| **Emergency SOS** | One-touch alert, contact management |
| **Community Reports** | Create/view accessibility reports |
| **Smart Parking** | Find accessible parking spaces |
| **User Profile** | Preferences, accessibility settings |

## 🧪 Test the System

### Test 1: Authentication

1. Click "Register" on login page
2. Enter email and password
3. Select accessibility mode
4. Click "Register"
5. Log in with credentials

### Test 2: Route Planning

1. Go to "Route Planning" page
2. Enter start/end locations:
   - **Start**: 40.7128, -74.0060
   - **End**: 40.7489, -73.9680
3. Select wheelchair mode
4. Click "Plan Route"
5. View route on map

### Test 3: Vision Analysis

1. Go to "Vision Assistance"
2. Choose "Obstacle Detection"
3. Upload an image
4. Click "Analyze"
5. See detection results

## 📂 Directory Structure

```
├── accessible-map-backend/
│   ├── main.py              # FastAPI server
│   ├── requirements.txt      # Backend dependencies
│   ├── .env.example         # Configuration template
│   ├── MONGODB_SETUP.md     # Database setup guide
│   ├── REDIS_SETUP.md       # Cache setup guide
│   ├── README.md            # Backend documentation
│   ├── run.bat              # Startup script
│   └── yolov8n.pt          # YOLO model
│
└── accessible-map-frontend/
    ├── app.py               # Streamlit frontend
    ├── requirements.txt     # Frontend dependencies
    ├── .env.example        # Configuration template
    ├── run.bat             # Startup script
    ├── run.ps1             # PowerShell startup
    ├── FRONTEND_README.md  # Frontend documentation
    └── .gitignore          # Git ignore rules
```

## 🔧 Commands Reference

### Backend Commands

```powershell
# Start backend
cd accessible-map-backend
python main.py

# Check health
curl http://localhost:8000/health

# View API docs
# Open: http://localhost:8000/docs
```

### Frontend Commands

```powershell
# Start frontend
cd accessible-map-frontend
streamlit run app.py

# View in browser
# Open: http://localhost:8501

# Clear cache
streamlit cache clear

# Check version
streamlit version
```

### Docker Commands

```powershell
# Start databases
docker run -d -p 27017:27017 --name mongodb mongo:latest
docker run -d -p 6379:6379 --name redis redis:latest

# Stop databases
docker stop mongodb redis

# Remove containers
docker rm mongodb redis
```

## 🐛 Troubleshooting

### Issue: "Connection refused" at http://localhost:8000

**Solution:**
1. Verify backend is running: `cd accessible-map-backend && python main.py`
2. Wait 5 seconds for models to load
3. Check health: `curl http://localhost:8000/health`

### Issue: "ModuleNotFoundError" in Streamlit

**Solution:**
```powershell
.\venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### Issue: MongoDB connection error

**Solution:**
1. Start MongoDB: `docker run -d -p 27017:27017 mongo:latest`
2. Or see MONGODB_SETUP.md for local installation
3. Verify: Check "database": "connected" in health endpoint

### Issue: Port already in use

**Solution:**
```powershell
# Change port in .streamlit/config.toml
# Or kill the process:
Get-Process streamlit | Stop-Process -Force
```

## 📊 System Specifications

### Backend API
- Framework: FastAPI (async)
- Port: 8000
- Models: YOLO v8n (object detection), EasyOCR (text recognition)
- Load time: ~5 seconds

### Frontend
- Framework: Streamlit
- Port: 8501
- Browser: Chrome, Firefox, Edge, Safari
- Load time: ~2 seconds

### Database
- MongoDB: Port 27017 (document store)
- Redis: Port 6379 (cache layer)
- Optional: Can run in Docker or locally

### Python Environment
- Version: 3.10+
- Root folder: `.venv`
- Package manager: pip

## 🌐 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:8501 | User interface |
| Backend API | http://localhost:8000 | REST API |
| Swagger Docs | http://localhost:8000/docs | API documentation |
| ReDoc | http://localhost:8000/redoc | Alternative API docs |
| MongoDB | localhost:27017 | Document database |
| Redis | localhost:6379 | Cache layer |

## 💡 Next Steps

1. ✅ **Start both servers** - Backend + Frontend
2. ✅ **Create test account** - Register on login page
3. ✅ **Test features** - Try route planning, vision analysis
4. ✅ **Setup databases** - Configure MongoDB/Redis for persistence
5. ✅ **Deploy to cloud** - See backend README for Azure deployment

## 📚 Documentation

**For more information, see:**
- [Backend README](accessible-map-backend/README.md) - Full API documentation
- [Frontend README](accessible-map-frontend/FRONTEND_README.md) - UI documentation
- [MongoDB Setup](accessible-map-backend/MONGODB_SETUP.md) - Database configuration
- [Redis Setup](accessible-map-backend/REDIS_SETUP.md) - Cache configuration

## 🚀 Production Deployment

See [Backend README](accessible-map-backend/README.md#production-deployment) for:
- Docker containerization
- Kubernetes deployment
- Azure App Service setup
- CI/CD pipeline configuration
- Environment variable management
- Secret management
- Performance optimization
- Security hardening

## ✨ Features at a Glance

- 🗺️ **Accessibility Routing** - Step-free, wheelchair-friendly routes
- 👁️ **Vision Assistance** - Obstacle detection, OCR, crossing detection, surface analysis
- 🆘 **Emergency SOS** - One-touch emergency alerts with location
- 📍 **Smart Community Reports** - Accessibility barriers and issues
- 🅿️ **Smart Parking** - Find accessible parking spaces
- 🚦 **Traffic Intelligence** - Real-time traffic and crowd density
- 💰 **Cost Optimization** - Cost-efficient route alternatives
- 🛣️ **Highway Safety** - Accident detection and safety alerts
- 🤝 **Volunteer Network** - Community-based travel assistance
- 🏙️ **Smart City Integration** - Government data integration
- 📊 **Real-time Analytics** - Safety metrics and trends
- ⚡ **Performance Optimized** - Redis caching for routes
- 🔐 **Secure Authentication** - JWT tokens and password hashing
- 📱 **Responsive UI** - Mobile-friendly Streamlit interface

## 💬 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review [Backend README](accessible-map-backend/README.md)
3. Check [Frontend README](accessible-map-frontend/FRONTEND_README.md)
4. Review backend logs: `accessible-map-backend/main.py` output
5. Check frontend logs: Streamlit terminal output

## 📄 License

This project is part of the Accessible Map AI ecosystem.

---

**Ready to get started?**

```powershell
# Terminal 1: Start backend
cd accessible-map-backend
python main.py

# Terminal 2: Start frontend
cd accessible-map-frontend
.\run.bat
```

Then open http://localhost:8501 in your browser!

**Last Updated**: 2026-02-27  
**Status**: ✅ Production Ready
