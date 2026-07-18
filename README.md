# 🧭 Accessible Map AI

An AI-powered inclusive navigation system designed to improve mobility, safety, and accessibility for wheelchair users, visually impaired individuals, senior citizens, and the general public.

---

## 🚀 Live Features

### 🗺 Smart Route Planning
- Accessibility-aware routing
- Wheelchair-friendly navigation
- Walking, Car, Bus, Bicycle support
- Safety & Accessibility scoring
- Redis caching for performance

### 👁 Vision Assistance (AI Powered)
- Obstacle Detection (YOLOv8)
- Signboard Text Recognition (EasyOCR)
- Pedestrian Crossing Detection
- Surface Quality Analysis

### 🚨 Emergency System
- SOS trigger with live location
- Emergency contact management
- Public emergency helplines (India)

### 🅿 Smart Parking
- Nearby parking search (Geoapify)
- Accessible parking detection
- Availability simulation

### 📊 Community Reporting
- Report accessibility issues
- Geo-based nearby issue search

---

## 🏗 Architecture

Frontend: Streamlit  
Backend: FastAPI  
Database: MongoDB  
Cache: Redis  
Maps API: Geoapify  
AI Models: YOLOv8 + EasyOCR  
Authentication: JWT  
accessible-map-ai/
│
├── backend/ → FastAPI backend
│ └── main.py
│
├── frontend/ → Streamlit frontend
│ └── app.py
│
└── README.md
accessible-map-ai/
│
├── backend/ → FastAPI backend
│ └── main.py
│
├── frontend/ → Streamlit frontend
│ └── app.py
│
└── README.md
🔧 Backend Setup
Step 1 — Create Virtual Environment
Windows
python -m venv .venv
.venv\Scripts\activate
Mac/Linux
python3 -m venv .venv
source .venv/bin/activate
Step 2 — Install Backend Dependencies
cd backend
pip install -r requirements.txt

If requirements.txt is missing:

pip install fastapi uvicorn motor redis pydantic pydantic-settings passlib python-jose[cryptography] aiohttp ultralytics easyocr opencv-python
Step 3 — Create Environment File

Inside backend/ create .env:

SECRET_KEY=your_secret_key_here
GEOAPIFY_API_KEY=your_geoapify_api_key
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379

⚠️ Never push .env to GitHub.

Step 4 — Run Backend
uvicorn main:app --reload

Backend runs at:

http://127.0.0.1:8000

API Docs:

http://127.0.0.1:8000/docs
🎨 Frontend Setup
Step 1 — Install Frontend Dependencies
cd frontend
pip install streamlit requests folium streamlit-folium pandas
Step 2 — Run Frontend
streamlit run app.py

Frontend runs at:

http://localhost:8501
🧪 Running Full System

Start MongoDB

Start Redis

Run Backend

Run Frontend

Open Streamlit in browser

🔒 Security Features

JWT Authentication

Password Hashing (bcrypt)

Secure environment configuration

CORS enabled

Redis caching

📈 Future Improvements

Live GPS tracking

Real-time traffic integration

Voice navigation system

Mobile app version

Volunteer emergency network

👨‍💻 Author

Mukesh Vemuri
AI & Full Stack Developer
Focused on Accessible Technology
