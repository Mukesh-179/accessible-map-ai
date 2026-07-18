  # 🌍 Accessible Map AI



<h3 align="center">
AI-Powered Smart Inclusive Mobility Platform
</h3>

<p align="center">
Helping wheelchair users, visually impaired individuals, elderly citizens, and people with mobility challenges navigate the world safely using Artificial Intelligence, Computer Vision, and Smart Navigation.
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?logo=mongodb)
![Redis](https://img.shields.io/badge/Redis-DC382D?logo=redis)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker)

</p>

---

# 📖 Overview

Accessible Map AI is an AI-powered navigation platform designed to improve mobility and accessibility for everyone.

The platform combines **Artificial Intelligence**, **Computer Vision**, **Geo-Spatial Intelligence**, and **Modern Cloud Technologies** to provide safer, smarter, and more inclusive navigation.

---

# ✨ Key Features

## 🧭 Smart Navigation

- Route Planning
- Accessibility-aware Routing
- Step-Free Navigation
- Distance & Time Estimation
- Safety Score
- Parking Assistance

---

## 👁️ AI Vision Assist

- 🚧 Obstacle Detection (YOLOv8)
- 📄 Sign Reading (EasyOCR)
- 🚸 Crossing Detection
- 🛣️ Surface Analysis

---

## 📍 Smart Places

- Hospitals
- Pharmacies
- Restaurants
- Hotels
- Public Toilets
- Fuel Stations
- Parking
- Bus Stops

---

## 🔐 User Management

- Registration
- Login
- JWT Authentication
- Secure Password Hashing

---

## 📊 Dashboard

- Smart Analytics
- Route History
- Reports
- Emergency Contacts
- Safety Score

---

# 📸 Application Screenshots

## Login & Registration

<img width="2840" height="1256" alt="Screenshot 2026-07-18 224518" src="https://github.com/user-attachments/assets/8e499851-e1d6-4085-a3ef-6d117c3952af" />

## Dashboard
<img width="2852" height="1246" alt="Screenshot 2026-07-18 224617" src="https://github.com/user-attachments/assets/b7fe4bde-7eef-4bd3-8ce2-9fbda6406e35" />


# 🏗️ System Architecture

```
                User
                  │
                  │
          Streamlit Frontend
                  │
        REST API (FastAPI)
                  │
      ┌───────────┼─────────────┐
      │           │             │
 MongoDB       Redis      Geoapify APIs
      │                         │
      └───────────┬─────────────┘
                  │
          AI Vision Module
      (YOLOv8 + EasyOCR + OpenCV)
```

---

# 🛠️ Tech Stack

## Frontend

- Streamlit
- HTML
- CSS
- Streamlit Folium
- Requests

## Backend

- FastAPI
- Uvicorn
- Pydantic
- JWT
- Passlib

## AI & Computer Vision

- YOLOv8
- EasyOCR
- OpenCV
- NumPy
- Pillow

## Database

- MongoDB Atlas
- Redis

## APIs

- Geoapify Routing
- Geoapify Places
- Geoapify Geocoding

## Deployment

- Docker
- Render
- Zoho Catalyst AppSail

---

# 📂 Project Structure

```
accessible-map-ai/

│
├── backend/
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│
├── frontend/
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/Mukesh-179/accessible-map-ai.git

cd accessible-map-ai
```

---

## Backend

```bash
cd backend

pip install -r requirements.txt

uvicorn main:app --reload
```

Backend

```
http://localhost:8000
```

---

## Frontend

```bash
cd frontend

pip install -r requirements.txt

streamlit run app.py
```

Frontend

```
http://localhost:8501
```

---

# 🐳 Docker

Backend

```bash
cd backend

docker build -t accessible-map-backend .

docker run -p 8000:8000 accessible-map-backend
```

Frontend

```bash
cd frontend

docker build -t accessible-map-frontend .

docker run -p 8501:8501 accessible-map-frontend
```

---

# 🌐 Live Demo

### Frontend

https://accessible-map-frontend.onrender.com

### Backend

https://accessible-map-backend-50044139017.development.catalystappsail.in

---
> [!IMPORTANT]
> **Preview Notes**
>
> - ⏳ The backend is hosted on a free cloud service and may take **1–2 minutes** to wake up after a period of inactivity.
> - 🔄 If the application appears to load slowly or requests initially fail, please wait a moment and try again.
> - 📝 During registration, ensure that all required fields are filled with **valid information**.
> - ⚠️ Invalid, incomplete, or incorrectly formatted input may result in backend validation errors.
> - ✅ Once the backend has started, the application functions normally.

---

# 🚀 Future Improvements

- Mobile Application
- Voice Navigation
- Live Camera Support
- AI Route Recommendation
- Crowd Density Detection
- Offline Maps
- Public Transport Accessibility
- Multi-language Support

---

# 👨‍💻 Author

**Mukesh Vemuri**

B.Tech – Computer Science & Data Science

GitHub

https://github.com/Mukesh-179

---

# ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.
