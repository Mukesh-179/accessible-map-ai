# 🗺️ Accessible Map AI

**A complete AI-powered inclusive mobility ecosystem combining accessibility routing, virtual vision for blind users, smart crossovers, highway safety, traffic intelligence, cost optimization, parking assistance, and community-based travel support.**

## Overview

Accessible Map AI is a comprehensive platform designed to make mobility more accessible and safe for everyone, especially people with disabilities. It combines cutting-edge AI/ML technologies with community intelligence to provide accessible routing, computer vision assistance, emergency services integration, and real-time accessibility information.

## 🎯 Core Features (18 Categories, 70+ Capabilities)

### Accessibility & Mobility
- ✅ **Accessible Routing** - Step-free, wheelchair-friendly, and accessibility-optimized routes
- ✅ **Smart Crossovers** - Pedestrian crossing detection and safe crossing guidance
- ✅ **Surface Analysis** - Pavement and surface type analysis for wheelchairs
- ✅ **Highway Safety** - Accident detection, speed monitoring, and safety alerts

### Vision & Navigation
- ✅ **Obstacle Detection** - Real-time obstacle detection for blind and visually impaired users
- ✅ **Sign Reading** - OCR-based text extraction from signs, menus, and displays
- ✅ **Crossing Detection** - Automated pedestrian crossing identification
- ✅ **Virtual Vision** - AI-powered visual understanding for users with visual impairments

### Smart Services
- ✅ **Smart Parking** - Find accessible parking with real-time availability
- ✅ **Emergency SOS** - One-touch emergency alerts with automatic location sharing
- ✅ **Community Reports** - Crowdsourced accessibility barrier reporting
- ✅ **Route Caching** - Redis-based route optimization and caching

### Intelligence & Optimization
- ✅ **Traffic Intelligence** - Real-time traffic and crowd density monitoring
- ✅ **Cost Optimization** - Cost-efficient route alternatives with fare estimation
- ✅ **Accident Detection** - Automatic detection of accident-prone zones
- ✅ **Speed Monitoring** - Real-time speed and traffic flow analysis

### Community & Support
- ✅ **Volunteer Network** - Community-based travel assistance and support
- ✅ **Smart City Integration** - Integration with government accessibility data
- ✅ **User Preferences** - Customizable accessibility and mobility preferences
- ✅ **System Health Monitoring** - Real-time platform status and diagnostics

## 📱 Platform Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   User Interface Layer                       │
│           Streamlit Frontend (accessible-map-frontend)       │
│  • Route Planning    • Vision Assistance                     │
│  • Emergency SOS     • Community Reports                     │
│  • Smart Parking     • User Profile & Settings              │
│  • Dashboard         • Health Monitoring                     │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API (JWT Auth)
┌────────────────────────▼────────────────────────────────────┐
│                   API Server Layer                           │
│             FastAPI Backend (accessible-map-backend)         │
│  • Authentication (JWT, bcrypt)                              │
│  • Route Planning Engine                                     │
│  • Vision Services (YOLO, EasyOCR)                           │
│  • Emergency & Community Services                            │
│  • Health Monitoring & Caching                               │
└────────────────────────┬────────────────────────────────────┘
              ┌──────────┼──────────┐
              │          │          │
    ┌─────────▼──┐  ┌────▼────┐  ┌─┴──────────┐
    │  MongoDB   │  │  Redis   │  │  ML Models │
    │ (Document  │  │ (Cache)  │  │ (YOLO,    │
    │  Database) │  │          │  │  EasyOCR) │
    └────────────┘  └──────────┘  └───────────┘
```

## 🚀 Quick Start

### Prerequisites
- Windows 10+ / WSL2 / macOS
- Python 3.10+
- 4GB+ RAM
- Optional: Docker

### 1. Start Backend (5 seconds)

```powershell
cd accessible-map-backend
python main.py
```

✅ Server runs at http://localhost:8000

### 2. Start Frontend (10 seconds)

```powershell
cd accessible-map-frontend
.\run.bat
```

✅ App runs at http://localhost:8501

### 3. Create Account & Explore

1. Register on login page
2. Select accessibility mode
3. Explore features (Route Planning, Vision, Emergency, etc.)

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

## 📁 Project Structure

```
accessible-map-ai/
├── accessible-map-backend/              # FastAPI REST API
│   ├── main.py                          # Complete backend server (1,339 lines)
│   ├── requirements.txt                 # 21 Python dependencies
│   ├── .env.example                     # Configuration template
│   ├── MONGODB_SETUP.md                 # Database setup guide
│   ├── REDIS_SETUP.md                   # Cache setup guide
│   ├── README.md                        # Backend documentation (420+ lines)
│   ├── run.bat / run.ps1               # Startup scripts
│   └── yolov8n.pt                       # YOLO v8n model
│
├── accessible-map-frontend/             # Streamlit Web App
│   ├── app.py                           # Streamlit application (750+ lines)
│   ├── requirements.txt                 # 8 Python dependencies
│   ├── .env.example                     # Configuration template
│   ├── FRONTEND_README.md               # Frontend documentation
│   ├── run.bat / run.ps1               # Startup scripts
│   └── .gitignore                       # Git ignore rules
│
├── verify-setup.ps1                     # System verification script
├── QUICKSTART.md                        # Quick start guide
└── README.md                            # This file
```

## 🔧 Technology Stack

### Backend
- **Framework**: FastAPI (async Python web framework)
- **Database**: MongoDB (document storage with geospatial indexing)
- **Cache**: Redis (session/route caching)
- **ML/Vision**: 
  - YOLO v8n (object detection)
  - EasyOCR (text recognition)
  - OpenCV (image processing)
- **Authentication**: JWT (HS256), bcrypt password hashing
- **Async**: asyncio, Motor, redis.asyncio

### Frontend
- **Framework**: Streamlit (interactive Python web framework)
- **Maps**: Folium + Streamlit-Folium (interactive maps)
- **HTTP**: Requests library (REST API calls)
- **Data**: Pandas, NumPy
- **UI**: Streamlit components, session state

### Infrastructure
- **Python**: 3.10+ (3.13.1 recommended)
- **Virtual Environment**: .venv (pip-based)
- **Containerization**: Docker (optional)
- **Version Control**: Git

## 📊 Key Endpoints (20+)

### Authentication
- `POST /api/v1/auth/register` - Create user account
- `POST /api/v1/auth/login` - Login and get JWT token
- `POST /api/v1/auth/logout` - Logout
- `POST /api/v1/auth/refresh` - Refresh token

### Routing
- `POST /api/v1/routes/plan` - Plan accessible route
- `GET /api/v1/routes/{id}` - Get route details
- `GET /api/v1/routes/user` - List user's routes

### Vision/ML
- `POST /api/v1/vision/detect-obstacles` - Detect obstacles
- `POST /api/v1/vision/read-text` - OCR text extraction
- `POST /api/v1/vision/detect-crossings` - Find crossings
- `POST /api/v1/vision/analyze-surface` - Analyze surfaces

### Emergency
- `POST /api/v1/emergency/sos` - Trigger SOS alert
- `GET/POST /api/v1/emergency/contacts` - Manage contacts

### Community
- `POST /api/v1/reports/create` - Create report
- `GET /api/v1/reports/nearby` - Get nearby reports

### Parking
- `GET /api/v1/parking/search` - Search parking
- `GET /api/v1/parking/nearby` - Find nearby parking

### System
- `GET /health` - Health check endpoint

## 🎨 User Interface Pages

### Dashboard
- Real-time system metrics and monitoring
- Quick access to main features
- Traffic and crowd density overview

### Route Planning
- Interactive map-based route planner
- Accessibility filters and mode selection
- Route comparison with metrics

### Vision Assistance
- 4 ML-powered vision capabilities
- File upload for image analysis
- Real-time detection results

### Emergency SOS
- One-touch emergency alert button
- Emergency contact management
- Caregiver location sharing

### Community Reports
- Create accessibility issue reports
- View nearby reports
- Community verification system

### Smart Parking
- Search accessible parking
- Real-time availability tracking
- Cost and booking information

### User Profile
- Personal information management
- Accessibility preferences
- Notification settings

## 🔐 Security Features

- **Password Security**: bcrypt hashing with salt
- **Token Authentication**: JWT tokens (HS256 algorithm)
- **CORS Protection**: Configured for cross-origin requests
- **Input Validation**: Pydantic v2 schema validation
- **Rate Limiting**: Endpoint protection against abuse
- **Input Sanitization**: XSS and injection prevention

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### Route Planning Test
```bash
curl -X POST http://localhost:8000/api/v1/routes/plan \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "start_lat": 40.7128,
    "start_lng": -74.0060,
    "end_lat": 40.7489,
    "end_lng": -73.9680,
    "mode": "wheelchair"
  }'
```

See [Backend README](accessible-map-backend/README.md) for comprehensive testing guide.

## 📚 Documentation

| Document | Purpose | Link |
|----------|---------|------|
| **Quick Start** | 5-10 minute setup guide | [QUICKSTART.md](QUICKSTART.md) |
| **Backend README** | API documentation, setup, troubleshooting | [accessible-map-backend/README.md](accessible-map-backend/README.md) |
| **Frontend README** | UI documentation, features, setup | [accessible-map-frontend/FRONTEND_README.md](accessible-map-frontend/FRONTEND_README.md) |
| **MongoDB Setup** | Database configuration & installation | [accessible-map-backend/MONGODB_SETUP.md](accessible-map-backend/MONGODB_SETUP.md) |
| **Redis Setup** | Cache layer configuration & installation | [accessible-map-backend/REDIS_SETUP.md](accessible-map-backend/REDIS_SETUP.md) |

## 🛠️ Troubleshooting

### Common Issues

**Connection refused (port 8000)**
```
Solution: Ensure backend is running: cd accessible-map-backend && python main.py
```

**ModuleNotFoundError**
```
Solution: Install dependencies: pip install -r requirements.txt
```

**Port already in use**
```
Solution: Kill process or change port in config
```

**Database connection error**
```
Solution: Start MongoDB: docker run -d -p 27017:27017 mongo:latest
```

For more troubleshooting, see:
- [Backend README Troubleshooting](accessible-map-backend/README.md#troubleshooting)
- [Frontend README Troubleshooting](accessible-map-frontend/FRONTEND_README.md#troubleshooting)

## 🚀 Deployment

### Local Development
See [QUICKSTART.md](QUICKSTART.md)

### Docker Deployment
See [Backend README](accessible-map-backend/README.md#docker-deployment)

### Cloud Deployment (Azure)
See [Backend README](accessible-map-backend/README.md#cloud-deployment)

## 📊 Performance

- **Backend Load Time**: ~5 seconds (YOLO model loading)
- **Frontend Load Time**: ~2 seconds
- **Route Planning**: <500ms (with Redis cache)
- **Vision Analysis**: 1-3 seconds per image
- **Database Queries**: <100ms with indexes

## 🔄 API Integration Flow

```
1. User logs in via Streamlit frontend
   ↓
2. JWT token obtained from /api/v1/auth/login
   ↓
3. Token stored in Streamlit session state
   ↓
4. All subsequent requests include: Authorization: Bearer {token}
   ↓
5. Backend validates token and processes request
   ↓
6. Response returned to frontend (cached in Redis if applicable)
   ↓
7. Frontend displays results to user
```

## 📈 Scalability Considerations

- **MongoDB Indexes**: Geospatial, user_id, timestamp indexes for fast queries
- **Redis Caching**: Route caching with 15-minute TTL
- **Async/Await**: Non-blocking I/O for high concurrency
- **Connection Pooling**: Motor and Redis async connection pools
- **Load Balancing**: Ready for load balancer deployment (Nginx, HAProxy)

## 💾 Data Models

### Key Collections (MongoDB)

**Users**
- Email, password hash, accessibility preferences
- Saved routes, emergency contacts

**Routes**
- Start/end coordinates, waypoints, accessibility score
- Distance, duration, cost, safety metrics

**Reports**
- Location, type, description, creator
- Verification status, upvote count

**Parking**
- Location, accessibility features
- Availability status, cost, booking info

**SOS Alerts**
- User, location, timestamp, status
- Emergency contacts notified

## 🌍 Accessibility Standards

This platform is designed with:
- WCAG 2.1 AA compliance in mind
- Accessibility-first UI/UX
- Multiple input modes (text, voice, gesture)
- Support for: Wheelchair users, Blind/Visually impaired, Elderly, Deaf/Hard of hearing
- Real-world accessibility barrier data

## 🤝 Contributing

Feel free to:
- Report issues and bugs
- Request new accessibility features
- Submit community data improvements
- Contribute code enhancements

## 📄 License

This project is part of the Accessible Map AI ecosystem.

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Streamlit Documentation](https://docs.streamlit.io)
- [MongoDB Documentation](https://docs.mongodb.com)
- [YOLO Documentation](https://docs.ultralytics.com)
- [EasyOCR Documentation](https://github.com/JaidedAI/EasyOCR)

## 📞 Support

For help:
1. Check [QUICKSTART.md](QUICKSTART.md) for quick issues
2. See [Backend README](accessible-map-backend/README.md) for API issues
3. See [Frontend README](accessible-map-frontend/FRONTEND_README.md) for UI issues
4. Check setup verification: `.\verify-setup.ps1`

## ✨ What Makes This Special

- **Complete Ecosystem**: 18 integrated feature categories
- **AI-Powered**: Computer vision, ML models, intelligent routing
- **Community-Driven**: Crowd-sourced accessibility data
- **Emergency-Ready**: One-touch SOS with location sharing
- **Privacy-First**: User data protection and anonymization
- **Open Architecture**: REST API for third-party integration
- **Production-Ready**: Error handling, caching, monitoring
- **Fully Documented**: 1,500+ lines of documentation

## 🚀 Ready to Start?

```powershell
# 1. Verify setup
.\verify-setup.ps1

# 2. Start backend (Terminal 1)
cd accessible-map-backend
python main.py

# 3. Start frontend (Terminal 2)
cd accessible-map-frontend
.\run.bat

# 4. Open browser
# Frontend: http://localhost:8501
# Backend: http://localhost:8000/docs
```

---

**Version**: 1.0.0  
**Last Updated**: 2026-02-27  
**Status**: ✅ Production Ready

**Made with ❤️ for accessibility and inclusive mobility**
