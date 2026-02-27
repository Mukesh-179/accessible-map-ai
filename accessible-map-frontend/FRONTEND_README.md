# Accessible Map AI Frontend

Complete Streamlit web application for the 18-feature smart mobility ecosystem. This frontend provides user-friendly interfaces for accessibility routing, vision assistance, emergency services, and community-based travel support.

## Features

### 🔐 Authentication
- User registration with accessibility mode selection
- Login with JWT token authentication
- Session persistence across page navigation
- Automatic token refresh

### 🗺️ Route Planning
- Step-free route optimization
- Accessibility filters (wheelchair, visual impairment, elderly)
- Real-time route metrics (distance, duration, accessibility score, safety score)
- Interactive map visualization with Folium
- Multiple route options comparison

### 👁️ Vision Assistance (AI-Powered)
**Computer Vision Integration for Blind & Visually Impaired Users:**
- **Obstacle Detection**: Real-time identification of obstacles with distance estimation
- **Sign Reading**: OCR-based text extraction from images (traffic signs, directions, accessibility info)
- **Crossing Detection**: Pedestrian crossing identification and safe crossing guidance
- **Surface Analysis**: Wheelchair-friendliness assessment of pavements and surfaces

### 🆘 Emergency SOS
- One-touch emergency alert button
- Automated location sharing with emergency services
- Emergency contact management (add/edit/delete contacts)
- Caregiver notification system
- Quick SOS trigger with predefined messages

### 📍 Community Reports
- Create accessibility issue reports (obstacles, potholes, accessibility problems)
- Report categories: accessibility barriers, infrastructure issues, safety concerns
- View nearby reports with filtering by type and distance
- Community verification and upvoting system
- Real-time crisis management

### 🅿️ Smart Parking
- Find accessible parking spaces nearby
- Accessibility-specific parking (wheelchair spaces, van accessible)
- Real-time availability tracking
- Cost information and payment integration
- Reserved parking location management

### 👤 User Profile
- Personal information management
- Accessibility preference selection:
  - Wheelchair mobility
  - Visual impairment
  - Elderly/mobility assistance
- Accessibility certifications and ID verification
- Notification preferences
- Saved locations and routes

### 📊 Dashboard
- Quick statistics (routes planned, saved places, safety metrics, volunteers nearby)
- Real-time system health monitoring
- Traffic and crowd density overview
- Weather and environmental alerts
- Quick access to main features

## Installation

### Option 1: Using Windows Batch Script (Easiest)
```bash
cd accessible-map-frontend
run.bat
```

### Option 2: Using PowerShell Script
```powershell
cd accessible-map-frontend
.\run.ps1
```

### Option 3: Manual Installation
```bash
# Navigate to frontend directory
cd accessible-map-frontend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows Command Prompt:
venv\Scripts\activate
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start the app
streamlit run app.py
```

## Backend Setup

Before running the frontend, ensure the backend is running:

```bash
cd accessible-map-backend

# Activate virtual environment
venv\Scripts\activate  # Windows

# Install backend dependencies
pip install -r requirements.txt

# Setup MongoDB and Redis (see MONGODB_SETUP.md and REDIS_SETUP.md)

# Start backend server
python main.py
```

**Backend Health Check:**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

## Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:8501 | User-facing web application |
| **Backend API** | http://localhost:8000 | REST API endpoints |
| **API Docs** | http://localhost:8000/docs | Swagger API documentation |
| **MongoDB** | mongodb://localhost:27017 | Document database (default) |
| **Redis** | localhost:6379 | Caching layer (default) |

## Configuration

### Environment Variables

Create `.env` file in the `accessible-map-frontend` directory:

```env
# Backend API Configuration
API_URL=http://localhost:8000

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
STREAMLIT_SERVER_HEADLESS=false

# Session Configuration
SESSION_TIMEOUT=3600  # 1 hour
MAX_UPLOAD_SIZE=10    # MB
```

### Streamlit Config (.streamlit/config.toml)

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#31333D"

[client]
showErrorDetails = true
toolbarMode = "minimal"

[logger]
level = "info"
```

## Project Structure

```
accessible-map-frontend/
├── app.py                      # Main Streamlit application (750+ lines)
├── requirements.txt            # Python dependencies
├── run.bat                      # Windows batch startup script
├── run.ps1                      # PowerShell startup script
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## API Integration

### Authentication Flow

1. **Register/Login**
   ```
   POST /api/v1/auth/register
   POST /api/v1/auth/login
   ```
   Response includes JWT token stored in session state

2. **API Calls with Token**
   ```
   Authorization: Bearer {token}
   ```

### Example API Call (Route Planning)

```python
response = requests.post(
    f"{API_URL}/api/v1/routes/plan",
    json={
        "start_lat": 40.7128,
        "start_lng": -74.0060,
        "end_lat": 40.7489,
        "end_lng": -73.9680,
        "mode": "wheelchair"
    },
    headers={"Authorization": f"Bearer {st.session_state.token}"}
)
```

### Supported Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Create new user
- `POST /api/v1/auth/login` - Authenticate user
- `POST /api/v1/auth/logout` - Logout current user
- `POST /api/v1/auth/refresh` - Refresh JWT token

#### Routes
- `POST /api/v1/routes/plan` - Plan accessible route
- `GET /api/v1/routes/{route_id}` - Get route details
- `GET /api/v1/routes/user` - List user's routes

#### Vision (Computer Vision)
- `POST /api/v1/vision/detect-obstacles` - Detect obstacles in image
- `POST /api/v1/vision/read-text` - Extract text from image (OCR)
- `POST /api/v1/vision/detect-crossings` - Detect pedestrian crossings
- `POST /api/v1/vision/analyze-surface` - Analyze pavement/surface

#### Emergency
- `POST /api/v1/emergency/sos` - Trigger emergency alert
- `POST /api/v1/emergency/contacts` - Manage emergency contacts
- `GET /api/v1/emergency/contacts` - List emergency contacts

#### Community
- `POST /api/v1/reports/create` - Create accessibility report
- `GET /api/v1/reports/nearby` - Get nearby reports
- `GET /api/v1/reports/{id}` - Get report details

#### Parking
- `GET /api/v1/parking/search` - Search accessible parking
- `GET /api/v1/parking/nearby` - Find nearby parking

#### System
- `GET /health` - Health check endpoint

## Troubleshooting

### Common Issues

#### 1. "Connection refused" when accessing backend
```
Error: Failed to connect to http://localhost:8000
Solution:
  1. Ensure backend is running: python main.py
  2. Check backend is listening on port 8000
  3. Verify firewall isn't blocking port 8000
  4. Check API_URL in .env matches backend address
```

#### 2. "Authentication failed" on login
```
Error: Invalid credentials
Solution:
  1. Ensure user is registered in database
  2. Verify backend MongoDB is running
  3. Check token is being stored correctly
  4. Review backend logs for auth errors
```

#### 3. "ModuleNotFoundError: No module named 'streamlit'"
```
Error: Module not found
Solution:
  1. Activate virtual environment: .\venv\Scripts\activate
  2. Install requirements: pip install -r requirements.txt
  3. Verify you're in the correct directory (accessible-map-frontend)
```

#### 4. "Port 8501 already in use"
```
Error: Address already in use
Solution:
  1. Change port in .streamlit/config.toml
  2. Or kill existing Streamlit process:
     Get-Process streamlit | Stop-Process -Force
  3. Wait 30 seconds and restart
```

#### 5. Vision analysis not working
```
Error: SSL certificate error or YOLO model not loaded
Solution:
  1. Verify backend has loaded YOLO model
  2. Check logs: "✅ YOLO model loaded"
  3. Verify image file format (PNG, JPG supported)
  4. Check image size (max 10MB)
```

### Debugging

**Enable verbose logging:**
```python
# In app.py, add at top:
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Check Streamlit cache:**
```bash
streamlit cache clear
```

**View Streamlit version:**
```bash
streamlit version
```

**Backend health check:**
```powershell
$response = Invoke-WebRequest http://localhost:8000/health
$response.Content | ConvertFrom-Json | Format-Table
```

## Performance Tips

1. **Session Caching**: Routes are cached in Redis for 15 minutes
2. **Image Optimization**: Resize images before vision analysis (max 1920x1080)
3. **Database Indexes**: Ensure MongoDB geospatial indexes are created
4. **Redis TTL**: Adjust cache TTL in backend for your use case

## Security

### Frontend Security

1. **Token Storage**: JWT stored in Streamlit session state (cleared on logout)
2. **HTTPS**: Use HTTPS in production
3. **CORS**: Backend configured for cross-origin requests
4. **Input Validation**: All user inputs validated before API calls

### Backend Security

See [Backend README](../accessible-map-backend/README.md) for:
- Password hashing (bcrypt)
- JWT token validation
- Rate limiting
- Input sanitization

## Development

### Adding a New Page

```python
# In app.py, add to page routing:
elif page == "New Page":
    st.title("New Page")
    
    # Check authentication
    if not st.session_state.logged_in:
        st.error("Please log in first")
        return
    
    # Page content here
```

### Adding API Endpoints

Backend endpoints integrate automatically. After adding backend endpoint:

```python
# In frontend, call new endpoint:
response = api_call("POST", "/api/v1/new-feature", {
    "param1": value1,
    "param2": value2
})
```

## Testing

### Test Route Planning

1. Login with test credentials
2. Navigate to "Route Planning"
3. Enter sample coordinates:
   - Start: 40.7128, -74.0060 (NYC)
   - End: 40.7489, -73.9680 (NYC)
4. Select accessibility mode
5. Click "Plan Route"
6. Verify route displays on map

### Test Vision Features

1. Prepare test image (PNG or JPG)
2. Navigate to "Vision Assistance"
3. Choose vision type (e.g., Obstacle Detection)
4. Upload test image
5. Click "Analyze"
6. Verify results display correctly

### Test Emergency SOS

1. Navigate to "Emergency SOS"
2. Add test emergency contact
3. Click "🆘 EMERGENCY SOS"
4. Verify SOS triggered with location

## Deployment

### Local Deployment (Production)

```bash
streamlit run app.py --logger.level=info --client.showErrorDetails=false
```

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

### Cloud Deployment

For AWS, Azure, Google Cloud: See deployment guides in backend README

## Support & Documentation

- **Backend Documentation**: See `../accessible-map-backend/README.md`
- **API Documentation**: http://localhost:8000/docs
- **Streamlit Docs**: https://docs.streamlit.io
- **FastAPI Docs**: https://fastapi.tiangolo.com

## Resources

- [Streamlit Cheat Sheet](https://docs.streamlit.io/library/cheatsheet)
- [Folium Maps](https://python-visualization.github.io/folium/)
- [Requests Library](https://requests.readthedocs.io/)
- [Accessible Map AI Backend](../accessible-map-backend/README.md)

## License

This project is part of the Accessible Map AI ecosystem. See LICENSE for details.

---

**Last Updated**: 2026-02-27
**Frontend Status**: ✅ Production Ready
**Backend Integration**: ✅ Complete
