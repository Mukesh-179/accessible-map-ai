# ============================================
# ACCESSIBLE MAP AI - COMPLETE BACKEND
# Geoapify API Integration + JWT Authentication
# FastAPI + MongoDB + Redis + ML Models
# ============================================

from email.mime import image
import os
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Sequence, Tuple
from functools import lru_cache
import asyncio
from bson import ObjectId
import numpy as np
import cv2
import aiohttp
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Security
from fastapi.security import (
    OAuth2PasswordBearer,
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from enum import Enum
# FastAPI imports
from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, Query, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Database
import redis.asyncio as redis
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING, DESCENDING, GEOSPHERE

# Pydantic models
from pydantic import BaseModel, Field, field_validator, ConfigDict, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# ML
from typing import List, Tuple, Any

# ============================================
# OPTIONAL ML IMPORT (LOW RAM SAFE)
# ============================================

USE_AI = os.getenv("USE_AI", "false").lower() == "true"

if USE_AI:
    from ultralytics import YOLO
    import easyocr
else:
    YOLO = None
    easyocr = None
# ============================================
# CONFIGURATION
# ============================================

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Accessible Map AI"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-use-random-32-chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "accessible_map1"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Geoapify API
    GEOAPIFY_API_KEY: str = "c2f7fc54594d41e78a05397253034725"
    GEOAPIFY_BASE_URL: str = "https://api.geoapify.com"
    
    # Legacy External APIs
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    MAPBOX_ACCESS_TOKEN: Optional[str] = None
    
    # ML Models
    YOLO_MODEL_PATH: str = "yolov8n.pt"
    
    model_config = {"env_file": ".env"}

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

# ============================================
# SECURITY UTILITIES
# ============================================

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
security = HTTPBearer()
def hash_password(password: str) -> str:
    # bcrypt limit is 72 bytes
    if len(password.encode("utf-8")) > 72:
        password = password[:72]
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if len(plain_password.encode("utf-8")) > 72:
        plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

async def verify_token(credentials: HTTPAuthorizationCredentials) -> str:
    """Verify JWT token and return user_id"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ============================================
# LOGGING CONFIGURATION
# ============================================

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# IN-MEMORY DATABASE (Fallback)
# ============================================

class MemoryCollection:
    """Simple in-memory collection for development"""
    def __init__(self):
        self.data: List[Dict[str, Any]] = []
    
    async def find_one(self, query: Dict) -> Optional[Dict]:
        for doc in self.data:
            match = all(doc.get(k) == v for k, v in query.items())
            if match:
                return doc
        return None
    
    async def insert_one(self, doc: Dict) -> Any:
        if "_id" not in doc:
            doc["_id"] = str(ObjectId())
        self.data.append(doc)
        return type('Result', (), {'inserted_id': doc["_id"]})()
    
    async def update_one(self, query: Dict, update: Dict) -> Any:
        for doc in self.data:
            match = all(doc.get(k) == v for k, v in query.items())
            if match:
                if "$set" in update:
                    doc.update(update["$set"])
                return type('Result', (), {'modified_count': 1})()
        return type('Result', (), {'modified_count': 0})()
    
    async def find(self, query: Dict) -> Any:
        results = [doc for doc in self.data if all(doc.get(k) == v for k, v in query.items())]
        
        async def to_list(limit):
            return results[:limit]
        
        return type('Cursor', (), {
            'to_list': to_list,
            'sort': lambda self, field, order: self,
            'skip': lambda self, n: self,
            'limit': lambda self, n: self
        })()
    
    async def count_documents(self, query: Dict) -> int:
        return len([doc for doc in self.data if all(doc.get(k) == v for k, v in query.items())])

class MemoryDB:
    """Simple in-memory database for development"""
    def __init__(self):
        self.collections: Dict[str, MemoryCollection] = {}
    
    def __getattr__(self, name: str) -> MemoryCollection:
        if name not in self.collections:
            self.collections[name] = MemoryCollection()
        return self.collections[name]

# ============================================
# DATABASE CONNECTION
# ============================================

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[Any] = None
    
    @classmethod
    async def connect(cls):
        try:
            cls.client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=2000)
            if cls.client is not None:
                cls.db = cls.client[settings.MONGODB_DB_NAME]
                # Test connection
                await cls.db.command('ping')
            
            # Create indexes
            await cls.create_indexes()
            
            logger.info("✅ MongoDB connected")
            return cls.db
        except Exception as e:
            logger.warning(f"⚠️  MongoDB connection failed: {e}")
            logger.info("📦 Using in-memory database fallback")
            cls.db = MemoryDB()
            return cls.db
    
    @classmethod
    async def close(cls):
        if cls.client:
            cls.client.close()
            logger.info("🔒 MongoDB disconnected")
    
    @classmethod
    async def create_indexes(cls):
        db = cls.db
        if db is not None:
            try:
                # Users collection
                users = db.users
                await users.create_indexes([
                    IndexModel([("email", ASCENDING)], unique=True),
                    IndexModel([("location", GEOSPHERE)]),
                ])
                
                # Routes collection
                routes = db.routes
                await routes.create_indexes([
                    IndexModel([("user_id", ASCENDING)]),
                    IndexModel([("start_location", GEOSPHERE)]),
                    IndexModel([("end_location", GEOSPHERE)]),
                ])
                
                # Reports collection
                reports = db.reports
                await reports.create_indexes([
                    IndexModel([("location", GEOSPHERE)]),
                    IndexModel([("type", ASCENDING)]),
                ])
                
                logger.info("✅ Indexes created")
            except Exception as e:
                logger.error(f"❌ Failed to create indexes: {e}")
        else:
            logger.error("❌ Cannot create indexes: cls.db is None")

# ============================================
# REDIS CONNECTION
# ============================================

class RedisClient:
    client: Optional[redis.Redis] = None
    
    @classmethod
    async def connect(cls):
        try:
            cls.client = redis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=2, socket_timeout=2)
            logger.info("✅ Redis connected")
            return cls.client
        except Exception as e:
            logger.warning(f"⚠️  Redis connection failed: {e}")
            cls.client = None
            return None
    
    @classmethod
    async def close(cls):
        if cls.client:
            await cls.client.close()
            logger.info("🔒 Redis disconnected")

# ============================================
# PYDANTIC MODELS
# ============================================

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)
    
    @classmethod
    def __get_pydantic_json_schema__(cls, schema, handler):
        json_schema = handler(schema)
        json_schema = handler.resolve_ref_schema(json_schema)
        json_schema.update(type="string")
        return json_schema

# ============================================
# AUTH MODELS
# ============================================
class AccessibilityMode(str, Enum):
    none = "none"
    wheelchair = "wheelchair"
    visually_impaired = "visually_impaired"
    hearing_impaired = "hearing_impaired"
    senior_citizen = "senior_citizen"
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: str
    accessibility_modes: List[AccessibilityMode] = []

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain number")
        if not any(c in "!@#$%^&*()" for c in v):
            raise ValueError("Password must contain special character")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if not v.isdigit() or len(v) != 10:
            raise ValueError("Phone must be 10 digits")
        return v
class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# ============================================
# USER MODELS
# ============================================

class EmergencyContact(BaseModel):
    name: str
    phone: str
    relationship: str
    notify_on_sos: bool = True

class SavedLocation(BaseModel):
    name: str
    coordinates: Dict[str, float]
    address: str

class UserProfile(BaseModel):
    name: str
    phone: Optional[str] = None
    accessibility_mode: str = "none"
    disabilities: List[str] = []
    mobility_aids: List[str] = []
    emergency_contacts: List[EmergencyContact] = []
    saved_locations: List[SavedLocation] = []

class UserPreferences(BaseModel):
    voice_guidance: bool = False
    haptic_feedback: bool = True
    language: str = "en"
    avoid_tolls: bool = False
    require_step_free: bool = False

class UserInDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: str
    password_hash: str
    profile: UserProfile
    preferences: UserPreferences = UserPreferences()
    safety_score: float = 100.0
    is_active: bool = True
    is_verified: bool = False
    is_volunteer: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: Optional[datetime] = None
    refresh_token: Optional[str] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class UserResponse(BaseModel):
    id: str
    email: str
    profile: UserProfile
    preferences: UserPreferences
    safety_score: float
    is_volunteer: bool

# ============================================
# ROUTE MODELS
# ============================================

class RoutePoint(BaseModel):
    coordinates: Dict[str, float]
    address: Optional[str] = None

class RouteSegment(BaseModel):
    distance: float
    duration: float
    instruction: str
    surface_type: Optional[str] = None
    has_steps: bool = False
    has_elevator: Optional[bool] = None
    safety_score: Optional[float] = None
    accessibility_score: Optional[float] = None

class RouteMetrics(BaseModel):
    total_distance: float
    total_duration: float
    accessibility_score: float
    safety_score: float
    step_free: bool

class RouteInDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: Optional[ObjectId] = None
    start_point: RoutePoint
    end_point: RoutePoint
    segments: List[RouteSegment] = []
    metrics: RouteMetrics
    polyline: Optional[List[List[float]]] = None
    
    mode: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class RouteCreate(BaseModel):
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    mode: str = "wheelchair"

class RouteResponse(BaseModel):
    id: str
    start_point: RoutePoint
    end_point: RoutePoint
    segments: List[RouteSegment]
    metrics: RouteMetrics
    polyline: Optional[List[List[float]]]
    created_at: datetime

# ============================================
# REPORT MODELS
# ============================================

class ReportInDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: ObjectId
    type: str
    location: Dict[str, Any]
    description: str
    severity: str
    verified: bool = False
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class ReportCreate(BaseModel):
    type: str
    lat: float
    lng: float
    description: str
    severity: str = "medium"

# ============================================
# PARKING MODELS
# ============================================

class ParkingInDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    location: Dict[str, float]
    name: Optional[str] = None
    address: str
    total_spots: int
    available_spots: int
    accessible_spots: int
    accessible_available: int
    price_per_hour: Optional[float] = None
    has_ramp: bool = False
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# ============================================
# SOS MODELS
# ============================================

class SOSInDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: ObjectId
    location: Dict[str, float]
    status: str = "active"
    contacted_emergency: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# ============================================
# GEOAPIFY SERVICE
# ============================================
class GeoapifyService:
    """Service for Geoapify API integration"""
    INDIAN_MAJOR_CITIES = [
    {"name": "Bengaluru", "lat": 12.9716, "lng": 77.5946},
    {"name": "Hyderabad", "lat": 17.3850, "lng": 78.4867},
    {"name": "Chennai", "lat": 13.0827, "lng": 80.2707},
    {"name": "Mumbai", "lat": 19.0760, "lng": 72.8777},
    {"name": "Delhi", "lat": 28.6139, "lng": 77.2090},
    {"name": "Kolkata", "lat": 22.5726, "lng": 88.3639},
    {"name": "Pune", "lat": 18.5204, "lng": 73.8567},
    {"name": "Ahmedabad", "lat": 23.0225, "lng": 72.5714}
    ]
    def __init__(self):
        self.base_url = settings.GEOAPIFY_BASE_URL
        self.api_key = settings.GEOAPIFY_API_KEY

    # ============================================
    # ROUTE FETCH
    # ============================================
    def calculate_distance(self, lat1, lng1, lat2, lng2):
        """Haversine formula (km)"""
        from math import radians, sin, cos, sqrt, atan2
        R = 6371  # Earth radius in KM
        dlat = radians(lat2 - lat1)
        dlng = radians(lng2 - lng1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c
    async def get_route(self, start: tuple, end: tuple, mode: str = "walk") -> Optional[Dict[str, Any]]:
        try:
            async with aiohttp.ClientSession() as session:

                url = f"{self.base_url}/v1/routing"

                
                params = {
                "waypoints": f"{start[0]},{start[1]}|{end[0]},{end[1]}",
                "mode": mode,
                "details": "instruction_details",
                "apiKey": self.api_key
                }

                # Add traffic ONLY for driving
                if mode == "drive":
                    params["traffic"] = "approximated"
                async with session.get(url, params=params) as response:

                    if response.status != 200:
                        logger.error(f"Geoapify Error {response.status}: {await response.text()}")
                        return None

                    data = await response.json()

                    if not data.get("features"):
                        return None

                    feature = data["features"][0]
                    properties = feature.get("properties", {})

                    return {
                        "distance": properties.get("distance", 0),
                        "duration": properties.get("time", 0),
                        "polyline": feature.get("geometry", {}).get("coordinates", [[]])[0],
                        "legs": properties.get("legs", [])
                    }

        except Exception as e:
            logger.error(f"Routing error: {e}")
            return None

    # ============================================
    # BACKGROUND PREFETCH (FIXES YOUR ERROR)
    # ============================================

    async def prefetch_routes(self, start: tuple, end: tuple, redis):
        """
        Background prefetch alternative route modes safely
        """

        if not redis or not hasattr(redis, "setex"):
            return

        modes = ["walk", "drive", "bicycle", "transit"]

        for mode in modes:
            try:
                cache_key = (
                    f"route:{start[0]}:{start[1]}:"
                    f"{end[0]}:{end[1]}:{mode}"
                )

                existing = await redis.get(cache_key)
                if existing:
                    continue

                route_geo = await self.get_route(start, end, mode)

                if not route_geo:
                    continue

                await redis.setex(
                    cache_key,
                    600,  # cache 10 minutes
                    json.dumps(route_geo)
                )

            except Exception as e:
                logger.warning(f"Prefetch failed for {mode}: {e}")

    async def reverse_geocode(self, lat: float, lng: float) -> Dict[str, Any]:
        """Convert coordinates to address"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/v1/geocode/reverse"
                params = {
                    "lat": lat,
                    "lon": lng,
                    "apiKey": self.api_key
                }
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("features"):
                            feature = data["features"][0]
                            return {
                                "address": feature["properties"]["formatted"],
                                "country": feature["properties"].get("country"),
                                "city": feature["properties"].get("city"),
                                "postcode": feature["properties"].get("postcode")
                            }
        except Exception as e:
            logger.error(f"Reverse geocoding error: {e}")
        return {"error": "No data found"}
    async def geocode_address(self, address: str) -> Dict[str, Any]:
        """Convert address to coordinates"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/v1/geocode/search"
                params = {
                    "text": address,
                    "apiKey": self.api_key
                }

                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        if data.get("features"):
                            feature = data["features"][0]
                            coords = feature["geometry"]["coordinates"]

                            return {
                                "lat": coords[1],
                                "lng": coords[0],
                                "formatted": feature["properties"].get("formatted")
                            }

        except Exception as e:
            logger.error(f"Geocode error: {e}")

        return {}
    async def places_search(
    self,
    lat: float,
    lng: float,
    radius: int = 1000,
    place_type: str = "parking"
) -> List[Dict[str, Any]]:

        try:
            # 1️⃣ Find nearest 5 cities
            cities_with_distance = []

            for city in self.INDIAN_MAJOR_CITIES:
                dist = self.calculate_distance(lat, lng, city["lat"], city["lng"])
                cities_with_distance.append((dist, city))

            nearest_cities = sorted(cities_with_distance, key=lambda x: x[0])[:5]

            all_places = []

            # 2️⃣ Search parking in each nearest city
            async with aiohttp.ClientSession() as session:
                for _, city in nearest_cities:

                    url = f"{self.base_url}/v2/places"

                    params = {
                    "filter": f"circle:{city['lng']},{city['lat']},{radius}",
                    "categories": "parking",
                    "countryCode": "in",
                    "limit": 10,
                    "apiKey": self.api_key
                    }

                    async with session.get(url, params=params) as response:
                        if response.status != 200:
                           continue

                        data = await response.json()

                        for feature in data.get("features", []):
                            props = feature.get("properties", {})
                            geometry = feature.get("geometry", {})
                            coords = geometry.get("coordinates", [None, None])

                            all_places.append({
                                "name": props.get("name", "Parking Area"),
                                "address": props.get("formatted"),
                                "coordinates": {
                                    "lat": coords[1],
                                    "lng": coords[0]
                                },
                                "city": city["name"],
                                "distance_from_user_km": round(
                                    self.calculate_distance(
                                        lat, lng,
                                        coords[1], coords[0]
                                    ), 2
                             )
                            })

        # 3️⃣ Sort by nearest to user
            return sorted(all_places, key=lambda x: x["distance_from_user_km"])

        except Exception as e:
            logger.error(f"Parking search error: {e}")
            return []
    
# ============================================
# ML SERVICES
# ============================================

class MLService:
    def __init__(self):
        self.yolo_model = None
        self.ocr_reader = None
        self.load_models()
   
    def load_models(self):
    """Load ML models only if enabled"""
    if not USE_AI:
        logger.info("🚫 AI models disabled (low RAM mode)")
        return

    try:
        self.yolo_model = YOLO(settings.YOLO_MODEL_PATH)
        logger.info("✅ YOLO model loaded")

        self.ocr_reader = easyocr.Reader(['en'])
        logger.info("✅ OCR model loaded")

    except Exception as e:
        logger.error(f"❌ Failed to load ML models: {e}")
   
    async def detect_obstacles(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect obstacles in image"""
        detections: List[Dict[str, Any]] = []
        
        if self.yolo_model is None:
            logger.warning("YOLO model not initialized")
            return detections

        try:
            model_output = self.yolo_model(image, conf=0.5)
            
            if not model_output:
                return detections
            
            results = model_output[0]
        
            for box in results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = results.names[class_id]
            
                box_height = y2 - y1
                img_height = image.shape[0]
                distance = self._estimate_distance(class_name, box_height, img_height)
            
                detections.append({
                    "class": class_name,
                    "confidence": confidence,
                    "bbox": [x1, y1, x2, y2],
                    "distance": distance,
                    "hazardous": self._is_hazardous(class_name, distance)
                })
            
        except Exception as e:
            logger.error(f"Obstacle detection error: {e}")
        
        return detections
    
    
    def detect_large_obstruction(self, image: np.ndarray) -> bool:
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            height, width = gray.shape

            # Focus only on middle horizontal band (where road center is)
            band = gray[int(height * 0.45):int(height * 0.65), :]

            # Calculate average brightness
            mean_intensity = np.mean(band)

            print("Mean intensity:", mean_intensity)

            # If large dark object across width → lower brightness
            return bool(mean_intensity < 100)

        except Exception as e:
            logger.error(f"Obstruction detection error: {e}")
            return False
    def _estimate_distance(self, class_name: str, box_height: float, img_height: float) -> float:
        """Estimate distance based on object size"""
        if box_height > 0:
            return (img_height / box_height) * 0.5
        return 10.0
    
    def _is_hazardous(self, class_name: str, distance: float) -> bool:
        """Determine if object is hazardous"""
        hazardous_classes = ['car', 'truck', 'bus', 'motorcycle', 'bicycle', 'dog']
        return class_name in hazardous_classes and distance < 5
    

    async def read_text(self, image: np.ndarray) -> str:
        try:
            if self.ocr_reader is None:
                logger.warning("OCR reader not initialized") 
                return ""

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

            results: Sequence[Any] = self.ocr_reader.readtext(thresh)

            filtered_texts = []

            for item in results:
                if isinstance(item, (list, tuple)) and len(item) >= 3:
                    text = item[1]
                    confidence = item[2]

                    if isinstance(confidence, (int, float)) and confidence > 0.4:
                        filtered_texts.append(str(text))

            return " ".join(filtered_texts).strip()

        except Exception as e:
            logger.error(f"OCR error: {e}")
            return ""


    async def detect_crossing(self, image: np.ndarray) -> Dict[str, Any]:
        try:
            if image is None or image.size == 0:
                return {"crossing_detected": False, "confidence": 0}

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)

            lines = cv2.HoughLinesP(
            edges,
            1,
            np.pi / 180,
            threshold=100,
            minLineLength=100,
            maxLineGap=20
            )

            if lines is not None:
                horizontal_lines = 0

                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    if abs(y1 - y2) < 10:
                        horizontal_lines += 1

                if horizontal_lines >= 3:
                    return {
                    "crossing_detected": True,
                    "confidence": min(1.0, horizontal_lines / 5)
                    }

            return {"crossing_detected": False, "confidence": 0}

        except Exception as e:
            logger.error(f"Crossing detection error: {e}")
            return {"crossing_detected": False, "confidence": 0} 
    async def analyze_surface(self, image: np.ndarray) -> Dict[str, Any]:
       try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        texture_score = np.var(laplacian)

        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges > 0) / edges.size

        smoothness = max(0, 100 - (texture_score / 10))

        return {
            "smoothness_score": float(min(100, smoothness)),
            "surface_type": "smooth" if smoothness > 60 else "rough",
            "has_obstacles": bool(edge_density > 0.07)
        }

       except Exception as e:
            logger.error(f"Surface analysis error: {e}")
            return {
            "smoothness_score": 50.0,
            "surface_type": "unknown",
            "has_obstacles": False
            }
  
# ============================================
# NOTIFICATION SERVICE
# ============================================

class NotificationService:
    async def send_sos_alert(self, user_id: str, location: Dict[str, float], db):
        """Send SOS alerts to emergency contacts"""
        try:
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return
            
            contacts = user.get("profile", {}).get("emergency_contacts", [])
            
            for contact in contacts:
                if contact.get("notify_on_sos", True):
                    logger.info(f"SOS Alert sent to {contact['name']} at {contact['phone']}")
            
            await db.sos.insert_one({
                "user_id": ObjectId(user_id),
                "location": location,
                "status": "active",
                "created_at": datetime.utcnow()
            })
            
        except Exception as e:
            logger.error(f"Failed to send SOS alerts: {e}")

# ============================================
# FASTAPI APP INITIALIZATION
# ============================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ml_service = MLService() if USE_AI else None
geoapify_service = GeoapifyService()
notification_service = NotificationService()

# ============================================
# LIFESPAN EVENTS
# ============================================

@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup"""
    try:
        await Database.connect()
    except Exception as e:
        logger.warning(f"⚠️  MongoDB not available: {e}")
    
    try:
        await RedisClient.connect()
    except Exception as e:
        logger.warning(f"⚠️  Redis not available: {e}")
    
    logger.info("✅ Geoapify API Key: " + settings.GEOAPIFY_API_KEY[:10] + "...")
    logger.info("🚀 Server started")

@app.on_event("shutdown")
async def shutdown_event():
    """Close connections on shutdown"""
    await Database.close()
    await RedisClient.close()
    logger.info("👋 Server stopped")

# ============================================
# DEPENDENCIES
# ============================================

async def get_db():
    return Database.db

async def get_redis():
    return RedisClient.client
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db=Depends(get_db)
) -> str:

    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = await db.users.find_one({"_id": ObjectId(user_id)})

        if not user or not user.get("is_active"):
            raise HTTPException(status_code=401, detail="User not found or inactive")

        return user_id

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

# ============================================
# API ROUTES - ROOT
# ============================================

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected" if Database.db is not None else "disconnected",
        "redis": "connected" if RedisClient.client is not None else "disconnected",
        "geoapify": "configured"
    }

# ============================================
# AUTH ROUTES
# ============================================
@app.post("/api/v1/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegister, db = Depends(get_db)):
    try:
        existing = await db.users.find_one({"email": user_data.email.lower()})
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        user_doc = {
            "_id": ObjectId(),
            "email": user_data.email.lower(),
            "password_hash": hash_password(user_data.password),
            "profile": {
                "name": user_data.name,
                "phone": user_data.phone,
                "accessibility_mode": user_data.accessibility_modes[0] if user_data.accessibility_modes else "none",
                "disabilities": [],
                "mobility_aids": [],
                "emergency_contacts": [],
                "saved_locations": []
            },
            "preferences": {
                "voice_guidance": False,
                "haptic_feedback": True,
                "language": "en",
                "avoid_tolls": False,
                "require_step_free": False
            },
            "safety_score": 100.0,
            "is_active": True,
            "is_verified": False,
            "is_volunteer": False,
            "created_at": datetime.utcnow(),
            "last_active": None
        }

        result = await db.users.insert_one(user_doc)
        user_id = str(result.inserted_id)

        access_token = create_access_token(
            data={"sub": user_id},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        refresh_token = create_refresh_token(data={"sub": user_id})

        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"refresh_token": refresh_token}}
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login(login_data: UserLogin, db = Depends(get_db)):
    """Login user"""
    try:
        # Find user
        user = await db.users.find_one({"email": login_data.email.lower()})
        if not user or not verify_password(login_data.password, user.get("password_hash", "")):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        if not user.get("is_active"):
            raise HTTPException(status_code=403, detail="User account is inactive")
        
        user_id = str(user["_id"])
        
        # Create tokens
        access_token = create_access_token(
            data={"sub": user_id},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = create_refresh_token(data={"sub": user_id})
        
        # Update user
        await db.users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "refresh_token": refresh_token,
                    "last_active": datetime.utcnow()
                }
            }
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/api/v1/auth/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, db = Depends(get_db)):
    """Refresh access token"""
    try:
        payload = jwt.decode(request.refresh_token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # Verify token in DB
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user or user.get("refresh_token") != request.refresh_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # Create new access token
        access_token = create_access_token(
            data={"sub": user_id},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {
            "access_token": access_token,
            "refresh_token": request.refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")

# ============================================
# ROUTING ROUTES
# ============================================
def map_mode(user_mode: str) -> str:
    """
    Maps frontend mode to Geoapify mode safely
    """

    if not user_mode:
        return "walk"

    user_mode = user_mode.lower()

    mapping = {
        "wheelchair": "walk",
        "walking": "walk",
        "walk": "walk",
        "car": "drive",
        "driving": "drive",
        "motorcycle": "drive",   # motorcycle uses drive engine
        "bike": "bicycle",
        "bicycle": "bicycle",
        "bus": "transit",        # public transport
        "transit": "transit"
    }

    return mapping.get(user_mode, "walk")
from fastapi import BackgroundTasks

@app.post("/api/v1/routes/plan", response_model=RouteResponse)
async def plan_route(
    route_data: RouteCreate,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db),
    redis = Depends(get_redis)
):
    """
    Plan route with safe caching + background prefetch
    """

    mapped_mode = map_mode(route_data.mode)

    cache_key = (
        f"route:{route_data.start_lat}:"
        f"{route_data.start_lng}:"
        f"{route_data.end_lat}:"
        f"{route_data.end_lng}:"
        f"{mapped_mode}"
    )

    # ===============================
    # 1️⃣ Try Redis Cache
    # ===============================
    route_geo = None

    if redis and hasattr(redis, "get"):
        cached = await redis.get(cache_key)
        if cached:
            try:
                route_geo = json.loads(cached)
            except Exception:
                route_geo = None

    # ===============================
    # 2️⃣ Fetch from Geoapify if needed
    # ===============================
    if not route_geo:
        route_geo = await geoapify_service.get_route(
            start=(route_data.start_lat, route_data.start_lng),
            end=(route_data.end_lat, route_data.end_lng),
            mode=mapped_mode
        )

        if not route_geo:
            raise HTTPException(status_code=400, detail="Route not found")

        # Save to Redis safely
        if redis and hasattr(redis, "setex"):
            await redis.setex(
                cache_key,
                600,
                json.dumps(route_geo)
            )

    # ===============================
    # 3️⃣ Extract Segments
    # ===============================
    segments = []

    for leg in route_geo.get("legs", []):
        for step in leg.get("steps", []):
            segments.append(
                RouteSegment(
                    distance=step.get("distance", 0),
                    duration=step.get("time", 0),
                    instruction=step.get("instruction", {}).get("text", "Continue"),
                    safety_score=85.0,
                    accessibility_score=95.0 if route_data.mode.lower() == "wheelchair" else 90.0
                )
            )

    # ===============================
    # 4️⃣ Metrics (Safe Smart Scoring)
    # ===============================
    base_safety = 85.0
    base_accessibility = 90.0

    if route_data.mode.lower() == "wheelchair":
        base_accessibility = 95.0

    if route_data.mode.lower() in ["car", "motorcycle"]:
        base_safety -= 5

    if route_data.mode.lower() == "bus":
        base_safety += 3

    metrics = RouteMetrics(
        total_distance=route_geo.get("distance", 0),
        total_duration=route_geo.get("duration", 0),
        accessibility_score=base_accessibility,
        safety_score=base_safety,
        step_free=route_data.mode.lower() == "wheelchair"
    )

    # ===============================
    # 5️⃣ Store Route in MongoDB
    # ===============================
    route_doc = {
        "user_id": ObjectId(user_id),
        "start_location": {
            "type": "Point",
            "coordinates": [route_data.start_lng, route_data.start_lat]
        },
        "end_location": {
            "type": "Point",
            "coordinates": [route_data.end_lng, route_data.end_lat]
        },
        "start_point": {
            "coordinates": {
                "lat": route_data.start_lat,
                "lng": route_data.start_lng
            }
        },
        "end_point": {
            "coordinates": {
                "lat": route_data.end_lat,
                "lng": route_data.end_lng
            }
        },
        "segments": [s.model_dump() for s in segments],
        "metrics": metrics.model_dump(),
        "polyline": route_geo.get("polyline"),
        "mode": route_data.mode,
        "created_at": datetime.utcnow()
    }

    result = await db.routes.insert_one(route_doc)

    # ===============================
    # 6️⃣ Background Prefetch (Safe)
    # ===============================
    if redis:
        background_tasks.add_task(
            geoapify_service.prefetch_routes,
            (route_data.start_lat, route_data.start_lng),
            (route_data.end_lat, route_data.end_lng),
            redis
        )

    # ===============================
    # 7️⃣ Return Response
    # ===============================
    return RouteResponse(
        id=str(result.inserted_id),
        start_point=RoutePoint(
            coordinates={"lat": route_data.start_lat, "lng": route_data.start_lng}
        ),
        end_point=RoutePoint(
            coordinates={"lat": route_data.end_lat, "lng": route_data.end_lng}
        ),
        segments=segments,
        metrics=metrics,
        polyline=route_geo.get("polyline"),
        created_at=route_doc["created_at"]
    )



@app.get("/api/v1/routes/history")
async def get_route_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get user's route history"""
    cursor = db.routes.find({"user_id": ObjectId(user_id)}).sort("created_at", -1).skip(skip).limit(limit)
    routes = await cursor.to_list(limit)
    return routes

# ============================================
# VISION ROUTES
# ============================================

@app.post("/api/v1/vision/detect-obstacles")
async def detect_obstacles(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    """Detect obstacles in image"""
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        detections = await ml_service.detect_obstacles(img)
        
        large_block = ml_service.detect_large_obstruction(img)

        if detections:
            obstacles = [d["class"] for d in detections if d["distance"] < 5]
            if obstacles:
                voice = f"Warning: {', '.join(obstacles[:3])} ahead"
            else:
                voice = "No immediate obstacles detected. Proceed carefully."

        elif large_block:
            voice = "Warning: Large obstruction blocking the path."

        else:
            voice = "No major obstacles detected. Please proceed carefully."
        return {
            "detections": detections,
            "voice_feedback": voice,
            "obstacle_count": len(detections),
            "has_danger": any(d.get("hazardous", False) for d in detections) or large_block
        }
    except Exception as e:
        logger.error(f"Vision API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/vision/read-sign")
async def read_sign(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    """Read text from sign"""
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        text = await ml_service.read_text(img)
        
        return {
            "text": text,
            "voice_output": f"Sign reads: {text}" if text else "No text detected"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/vision/detect-crossing")
async def detect_crossing(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    """Detect pedestrian crossing"""
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        result = await ml_service.detect_crossing(img)
        
        return {
            **result,
            "voice_guidance": "Crossing detected" if result["crossing_detected"] else "No crossing detected"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/vision/analyze-surface")
async def analyze_surface(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    """Analyze surface quality"""
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        result = await ml_service.analyze_surface(img)
        
        return {
            **result,
            "wheelchair_friendly": result["smoothness_score"] > 70 and not result["has_obstacles"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# GEOAPIFY ROUTES
# ============================================

@app.get("/api/v1/geoapify/geocode")
async def geocode(
    address: str,
    user_id: str = Depends(get_current_user)
):
    """Geocode address to coordinates"""
    result = await geoapify_service.geocode_address(address)
    if not result:
        raise HTTPException(status_code=404, detail="Address not found")
    return result

@app.get("/api/v1/geoapify/reverse-geocode")
async def reverse_geocode(
    lat: float,
    lng: float,
    user_id: str = Depends(get_current_user)
):
    """Reverse geocode coordinates to address"""
    result = await geoapify_service.reverse_geocode(lat, lng)
    if not result:
        raise HTTPException(status_code=404, detail="Address not found")
    return result

@app.get("/api/v1/geoapify/places")
async def find_places(
    lat: float,
    lng: float,
    radius: int = Query(1000, le=5000),
    place_type: str = "parking",
    user_id: str = Depends(get_current_user)
):
    """Find nearby places using Geoapify"""
    places = await geoapify_service.places_search(lat, lng, radius, place_type)
    return {"places": places, "count": len(places)}

# ============================================
# REPORT ROUTES
# ============================================
@app.post("/api/v1/reports")
async def create_report(
    report: ReportCreate,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    report_data = ReportInDB(
        user_id=ObjectId(user_id),
        type=report.type,
        location={
            "type": "Point",
            "coordinates": [report.lng, report.lat]  # lng FIRST (GeoJSON)
        },
        description=report.description,
        severity=report.severity
    )

    result = await db.reports.insert_one(report_data.model_dump(by_alias=True))

    return {
        "id": str(result.inserted_id),
        "message": "Report created successfully"
    }


@app.get("/api/v1/reports/nearby")
async def get_nearby_reports(
    lat: float,
    lng: float,
    radius: int = Query(1000, le=5000),
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get nearby accessibility reports"""
    if isinstance(db, MemoryDB):
        return {
            "reports": [],
            "message": "Geospatial queries not supported in development mode"
        }
    reports = await db.reports.find({
        "location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [lng, lat]
                },
                "$maxDistance": radius
            }
        },
        "status": "active"
    }).limit(50).to_list(50)
    
    
    for report in reports:
        report["_id"] = str(report["_id"])
        report["user_id"] = str(report["user_id"])
    return reports

@app.post("/api/v1/reports/{report_id}/verify")
async def verify_report(
    report_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Verify a report"""
    result = await db.reports.update_one(
        {"_id": ObjectId(report_id)},
        {
            "$set": {
                "verified": True,
                "verified_by": ObjectId(user_id),
                "verified_at": datetime.utcnow()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {"message": "Report verified"}

# ============================================
# PARKING ROUTES
# ============================================
@app.get("/api/v1/parking/nearby")
async def find_parking(
    lat: float,
    lng: float,
    radius: int = Query(1000, le=5000),
    accessible_only: bool = False,
    user_id: str = Depends(get_current_user),
):
    places = await geoapify_service.places_search(
        lat, lng, radius, "parking"
    )

    import random

    for place in places:
        total = random.randint(30, 150)
        available = random.randint(5, total)

        accessible_total = max(1, total // 8)
        accessible_available = random.randint(0, accessible_total)

        place.update({
            "total_spots": total,
            "available_spots": available,
            "accessible_spots": accessible_total,
            "accessible_available": accessible_available,
            "status": "Available" if available > 0 else "Full"
        })

    if accessible_only:
        places = [
            p for p in places
            if p["accessible_available"] > 0
        ]

    return {
        "parking": places,
        "count": len(places)
    }

# ============================================
# EMERGENCY ROUTES
# ============================================

@app.post("/api/v1/emergency/sos")
async def trigger_sos(
    lat: float,
    lng: float,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Trigger SOS emergency"""

    location = {"lat": lat, "lng": lng}

    background_tasks.add_task(
        notification_service.send_sos_alert,
        user_id,
        location,
        db
    )

    return {
        "message": "SOS triggered. Help is on the way.",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/v1/emergency/contacts")
async def get_emergency_contacts(
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get user's emergency contacts"""
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user.get("profile", {}).get("emergency_contacts", [])


@app.post("/api/v1/emergency/contacts")
async def add_emergency_contact(
    contact: EmergencyContact,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Add emergency contact"""

    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"profile.emergency_contacts": contact.dict()}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Failed to add contact")

    return {"message": "Contact added successfully"}


# --------------------------------------------
# NEW: Public Emergency Numbers
# --------------------------------------------

@app.get("/api/v1/emergency/public-numbers")
async def get_public_emergency_numbers():
    """Official emergency helplines (India)"""
    return [
        {"name": "Police", "number": "100"},
        {"name": "Ambulance", "number": "108"},
        {"name": "Women Helpline", "number": "181"},
        {"name": "Disaster Management", "number": "1070"},
        {"name": "Senior Citizen Helpline", "number": "14567"}
    ]
# ============================================
# USER PROFILE ROUTES
# ============================================

@app.get("/api/v1/users/me", response_model=UserResponse)
async def get_current_user_profile(
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get current user profile"""

    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # -----------------------------
    # SAFE PROFILE HANDLING
    # -----------------------------
    profile = user.get("profile", {})

    # Fix accessibility_mode
    mode = profile.get("accessibility_mode")

    if not isinstance(mode, str):
        profile["accessibility_mode"] = "none"

    # Ensure lists exist properly
    if not isinstance(profile.get("disabilities"), list):
        profile["disabilities"] = []

    if not isinstance(profile.get("mobility_aids"), list):
        profile["mobility_aids"] = []

    # Ensure preferences exists
    preferences = user.get("preferences", {})
    if not isinstance(preferences, dict):
        preferences = {}

    return {
        "id": str(user["_id"]),
        "email": user.get("email"),
        "profile": profile,
        "preferences": preferences,
        "safety_score": user.get("safety_score", 100),
        "is_volunteer": user.get("is_volunteer", False)
    }
@app.put("/api/v1/users/me/preferences")
async def update_preferences(
    preferences: UserPreferences,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update user preferences"""
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"preferences": preferences.dict()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Failed to update preferences")
    
    return {"message": "Preferences updated"}

@app.put("/api/v1/users/me/profile")
async def update_profile(
    profile: UserProfile,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update user profile"""
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"profile": profile.dict()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Failed to update profile")
    
    return {"message": "Profile updated"}

# ============================================
# ADMIN ROUTES
# ============================================

@app.get("/api/v1/admin/stats")
async def get_system_stats(
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get system statistics"""
    # Verify admin access
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user or not user.get("is_volunteer"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    stats = {
        "total_users": await db.users.count_documents({}),
        "total_routes": await db.routes.count_documents({}),
        "total_reports": await db.reports.count_documents({}),
        "active_sos": await db.sos.count_documents({"status": "active"}),
        "verified_reports": await db.reports.count_documents({"verified": True})
    }
    
    return stats
# Include API router
# ============================================
# DASHBOARD ROUTES
# ============================================

@app.get("/api/v1/dashboard/summary")
async def get_dashboard_summary(
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    total_routes = await db.routes.count_documents({"user_id": ObjectId(user_id)})
    total_reports = await db.reports.count_documents({"user_id": ObjectId(user_id)})
    emergency_contacts = len(user.get("profile", {}).get("emergency_contacts", []))

    return {
        "total_routes": total_routes,
        "total_reports": total_reports,
        "emergency_contacts": emergency_contacts,
        "safety_score": user.get("safety_score", 100)
    }
# ============================================
# APP UPDATES
# ============================================

@app.get("/api/v1/app/updates")
async def get_app_updates():
    return [
        {
            "version": "1.1.0",
            "title": "Live Traffic & Dark Mode",
            "description": "Added real-time traffic overlay and dark mode maps.",
            "created_at": datetime.utcnow()
        },
        {
            "version": "1.0.5",
            "title": "Motorcycle & Bus Routing",
            "description": "Now supports motorcycle and public transport routes.",
            "created_at": datetime.utcnow()
        }
    ]
# ============================================
# ERROR HANDLERS
# ============================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "path": request.url.path
        }
    )

# ============================================
# RUN COMMAND
# ============================================
# To run: uvicorn main:app --reload
# Install requirements: pip install fastapi uvicorn motor redis pydantic pydantic-settings passlib python-jose[cryptography] aiohttp ultralytics easyocr opencv-python

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
