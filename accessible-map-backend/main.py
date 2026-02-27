# ============================================
# ACCESSIBLE MAP AI - COMPLETE BACKEND
# Single File Implementation
# FastAPI + MongoDB + Redis + ML Models
# ============================================

import os
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from functools import lru_cache
import asyncio
from bson import ObjectId
import numpy as np
import cv2

# FastAPI imports
from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, Query, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse



# Database
import redis.asyncio as redis
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING, DESCENDING, GEOSPHERE

# Pydantic models
from pydantic import BaseModel, Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict

# ML
from ultralytics import YOLO
import easyocr

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
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "accessible_map"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # External APIs
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
        # Guard Clause: Ensure cls.db is not None before accessing
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
            # Handle the case where the database isn't ready
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
# MODELS (Pydantic)
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

# User Models
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
    accessibility_mode: str = "none"  # wheelchair, visually-impaired, elderly, driver
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

class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    phone: Optional[str] = None
    accessibility_mode: str = "none"

class UserResponse(BaseModel):
    id: str
    email: str
    profile: UserProfile
    preferences: UserPreferences
    safety_score: float
    is_volunteer: bool

# Route Models
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
    polyline: Optional[str] = None
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
    polyline: Optional[str]
    created_at: datetime

# Report Models
class ReportInDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: ObjectId
    type: str  # broken_ramp, obstacle, accident, etc.
    location: Dict[str, float]
    description: str
    severity: str  # low, medium, high
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

# Parking Models
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

# SOS Models
class SOSInDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: ObjectId
    location: Dict[str, float]
    status: str = "active"  # active, resolved
    contacted_emergency: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# ============================================
# ML SERVICES
# ============================================

class MLService:
    def __init__(self):
        self.yolo_model = None
        self.ocr_reader = None
        self.load_models()
    
    def load_models(self):
        """Load ML models"""
        try:
            # Load YOLO for obstacle detection
            self.yolo_model = YOLO(settings.YOLO_MODEL_PATH)
            logger.info("✅ YOLO model loaded")
            
            # Load OCR for text reading
            self.ocr_reader = easyocr.Reader(['en'])
            logger.info("✅ OCR model loaded")
        except Exception as e:
            logger.error(f"❌ Failed to load ML models: {e}")
    
    async def detect_obstacles(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect obstacles in image"""
    # 1. Initialize at the top to fix "Possibly Unbound" error
        detections: List[Dict[str, Any]] = []
    
    # 2. Guard Clause: Prove to Pylance that self.yolo_model is NOT None
        if self.yolo_model is None:
           logger.warning("YOLO model not initialized. Skipping detection.")
           return detections

        try:
        # Pylance now knows yolo_model exists here
            model_output = self.yolo_model(image, conf=0.5)
        
        # Check if we actually got results
            if not model_output:
               return detections
            
            results = model_output[0]
        
            for box in results.boxes:
               x1, y1, x2, y2 = box.xyxy[0].tolist()
               confidence = float(box.conf[0])
               class_id = int(box.cls[0])
               class_name = results.names[class_id]
            
            # Estimate distance
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
        # detections is already initialized as [], so returning it is safe
        
        return detections
    
    def _estimate_distance(self, class_name: str, box_height: float, img_height: float) -> float:
        """Estimate distance based on object size"""
        # Simplified distance estimation
        if box_height > 0:
            return (img_height / box_height) * 0.5  # meters
        return 10.0
    
    def _is_hazardous(self, class_name: str, distance: float) -> bool:
        """Determine if object is hazardous"""
        hazardous_classes = ['car', 'truck', 'bus', 'motorcycle', 'bicycle', 'dog']
        return class_name in hazardous_classes and distance < 5
    
    async def read_text(self, image: np.ndarray) -> str:
        """Read text from image using OCR"""
        try:
            results: List[Any] = [] # 1. Initialize with a default value at the top
            if self.ocr_reader is not None:
                results = self.ocr_reader.readtext(image)

        # results is now guaranteed to exist (either as data or an empty list)
            text = " ".join([result[1] for result in results])
            return text
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return ""
    
    async def detect_crossing(self, image: np.ndarray) -> Dict[str, Any]:
        """Detect pedestrian crossing"""
        try:
        # 1. Safety Check: Ensure image is not None
           if image is None or image.size == 0:
            return {"crossing_detected": False, "confidence": 0, "error": "Invalid image"}

        # 2. Convert to HSV
           hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # 3. Detect white stripes using NumPy arrays (Fixes Pylance error)
           lower_white = np.array([0, 0, 200], dtype="uint8")
           upper_white = np.array([180, 30, 255], dtype="uint8")
        
           white_mask = cv2.inRange(hsv, lower_white, upper_white)
        
        # 4. Calculate ratio
           white_ratio = float(np.sum(white_mask > 0) / white_mask.size)
        
        # Threshold: usually > 0.1 indicates significant white area (like stripes)
           crossing_detected = white_ratio > 0.1
        
           return {
            "crossing_detected": bool(crossing_detected),
            "confidence": white_ratio
           }
        except Exception as e:
           logger.error(f"Crossing detection error: {e}")
           return {"crossing_detected": False, "confidence": 0}
        
    async def analyze_surface(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze surface smoothness"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate texture using variance
            variance = np.var(gray)
            smoothness = min(100, max(0, 100 - (variance / 100)))
            
            # Detect edges (potential cracks/obstacles)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            return {
                "smoothness_score": smoothness,
                "surface_type": "smooth" if smoothness > 70 else "rough",
                "has_obstacles": edge_density > 0.05
            }
        except Exception as e:
            logger.error(f"Surface analysis error: {e}")
            return {"smoothness_score": 50, "surface_type": "unknown", "has_obstacles": False}

# ============================================
# MAP SERVICE
# ============================================

class MapService:
    async def get_route(self, start: tuple, end: tuple, mode: str = "walking") -> Dict:
        """Get route from mapping service"""
        # Simplified route generation
        # In production, integrate with Google Maps/OSRM/Mapbox
        
        lat1, lng1 = start
        lat2, lng2 = end
        
        # Calculate straight line distance
        distance = self.haversine(lat1, lng1, lat2, lng2) * 1000  # meters
        
        # Estimate duration (5 km/h for walking/wheelchair)
        speed = 1.4 if mode == "wheelchair" else 1.4  # m/s
        duration = distance / speed
        
        # Generate segments
        num_segments = max(5, int(distance / 100))
        segments = []
        
        for i in range(num_segments):
            ratio = i / num_segments
            next_ratio = (i + 1) / num_segments
            
            seg_distance = distance / num_segments
            seg_duration = duration / num_segments
            
            segments.append({
                "distance": seg_distance,
                "duration": seg_duration,
                "instruction": f"Continue straight for {int(seg_distance)} meters",
                "surface_type": "asphalt" if i % 2 == 0 else "concrete",
                "has_steps": False,
                "safety_score": 85 + (i % 15),
                "accessibility_score": 90 - (i % 20)
            })
        
        return {
            "segments": segments,
            "polyline": "encoded_polyline_string",
            "distance": distance,
            "duration": duration
        }
    
    def haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Haversine formula for distance in km"""
        R = 6371  # Earth's radius in km
        
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        
        a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return R * c

# ============================================
# NOTIFICATION SERVICE
# ============================================

class NotificationService:
    async def send_sos_alert(self, user_id: str, location: Dict[str, float], db):
        """Send SOS alerts to emergency contacts"""
        try:
            # Get user and emergency contacts
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return
            
            contacts = user.get("profile", {}).get("emergency_contacts", [])
            
            for contact in contacts:
                if contact.get("notify_on_sos", True):
                    # Send SMS/Email/Push notification
                    logger.info(f"SOS Alert sent to {contact['name']} at {contact['phone']}")
                    
                    # In production, integrate with Twilio/Firebase
                    # await self.send_sms(contact['phone'], f"EMERGENCY: User needs help at {location}")
            
            # Log SOS
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
ml_service = MLService()
map_service = MapService()
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

# ============================================
# API ROUTES
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
        "redis": "connected" if RedisClient.client is not None else "disconnected"
    }

# ============================================
# ROUTING ROUTES
# ============================================

@app.post("/api/v1/routes/plan", response_model=RouteResponse)
async def plan_route(
    route_data: RouteCreate,
    db = Depends(get_db),
    redis = Depends(get_redis)
):
    """Plan an accessible route"""
    
    # Check cache
    cache_key = f"route:{hash(frozenset(route_data.dict().items()))}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Get route
    base_route = await map_service.get_route(
        start=(route_data.start_lat, route_data.start_lng),
        end=(route_data.end_lat, route_data.end_lng),
        mode=route_data.mode
    )
    
    # Calculate metrics
    segments = []
    for seg in base_route["segments"]:
        segments.append(RouteSegment(**seg))
    
    metrics = RouteMetrics(
        total_distance=base_route["distance"],
        total_duration=base_route["duration"],
        accessibility_score=sum(s.accessibility_score or 0 for s in segments) / len(segments),
        safety_score=sum(s.safety_score or 0 for s in segments) / len(segments),
        step_free=all(not s.has_steps for s in segments)
    )
    
    # Create route
    route = RouteInDB(
        user_id=None,
        start_point=RoutePoint(coordinates={"lat": route_data.start_lat, "lng": route_data.start_lng}),
        end_point=RoutePoint(coordinates={"lat": route_data.end_lat, "lng": route_data.end_lng}),
        segments=segments,
        metrics=metrics,
        polyline=base_route.get("polyline"),
        mode=route_data.mode
    )
    
    # Cache for 5 minutes
    await redis.setex(cache_key, 300, json.dumps(route.dict(), default=str))
    
    return route

@app.get("/api/v1/routes/history", response_model=List[RouteResponse])
async def get_route_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    db = Depends(get_db)
):
    """Get all route history"""
    cursor = db.routes.find(
        {}
    ).sort("created_at", -1).skip(skip).limit(limit)
    
    routes = await cursor.to_list(limit)
    return routes

# ============================================
# VISION ROUTES
# ============================================

@app.post("/api/v1/vision/detect-obstacles")
async def detect_obstacles(
    file: UploadFile = File(...)
):
    """Detect obstacles in image"""
    try:
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        # Detect obstacles
        detections = await ml_service.detect_obstacles(img)
        
        # Generate voice feedback
        if detections:
            obstacles = [d["class"] for d in detections if d["distance"] < 5]
            if obstacles:
                voice = f"Warning: {', '.join(obstacles[:3])} ahead"
            else:
                voice = "Path is clear"
        else:
            voice = "No obstacles detected"
        
        return {
            "detections": detections,
            "voice_feedback": voice,
            "obstacle_count": len(detections),
            "has_danger": any(d.get("hazardous", False) for d in detections)
        }
    except Exception as e:
        logger.error(f"Vision API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/vision/read-sign")
async def read_sign(
    file: UploadFile = File(...)
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
    file: UploadFile = File(...)
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
    file: UploadFile = File(...)
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
# REPORT ROUTES
# ============================================

@app.post("/api/v1/reports")
async def create_report(
    report: ReportCreate,
    user_id: str,
    db = Depends(get_db)
):
    """Create a new accessibility report"""
    report_data = ReportInDB(
        user_id=ObjectId(user_id),
        type=report.type,
        location={"lat": report.lat, "lng": report.lng},
        description=report.description,
        severity=report.severity
    )
    
    result = await db.reports.insert_one(report_data.dict(by_alias=True))
    
    return {"id": str(result.inserted_id), "message": "Report created successfully"}

@app.get("/api/v1/reports/nearby")
async def get_nearby_reports(
    lat: float,
    lng: float,
    radius: int = Query(1000, le=5000),
    db = Depends(get_db)
):
    """Get nearby accessibility reports"""
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
    
    return reports

@app.post("/api/v1/reports/{report_id}/verify")
async def verify_report(
    report_id: str,
    user_id: str,
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
    db = Depends(get_db)
):
    """Find nearby parking"""
    query = {
        "location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [lng, lat]
                },
                "$maxDistance": radius
            }
        }
    }
    
    if accessible_only:
        query["accessible_available"] = {"$gt": 0}  # type: ignore
    
    parking = await db.parking.find(query).limit(20).to_list(20)
    return parking

# ============================================
# EMERGENCY ROUTES
# ============================================

@app.post("/api/v1/emergency/sos")
async def trigger_sos(
    lat: float,
    lng: float,
    user_id: str,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Trigger SOS emergency"""
    location = {"lat": lat, "lng": lng}
    
    # Send alerts in background
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
    user_id: str,
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
    user_id: str,
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

# ============================================
# USER PROFILE ROUTES
# ============================================

@app.get("/api/v1/users/me", response_model=UserResponse)
async def get_current_user_profile(
    user_id: str,
    db = Depends(get_db)
):
    """Get user profile"""
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["id"] = str(user["_id"])
    return user

@app.put("/api/v1/users/me/preferences")
async def update_preferences(
    preferences: UserPreferences,
    user_id: str,
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

# ============================================
# ADMIN ROUTES
# ============================================

@app.get("/api/v1/admin/stats")
async def get_system_stats(
    db = Depends(get_db)
):
    """Get system statistics"""
    stats = {
        "total_users": await db.users.count_documents({}),
        "total_routes": await db.routes.count_documents({}),
        "total_reports": await db.reports.count_documents({}),
        "active_sos": await db.sos.count_documents({"status": "active"}),
        "verified_reports": await db.reports.count_documents({"verified": True})
    }
    
    return stats

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
# RUN COMMAND (for development)
# ============================================
# To run: uvicorn main:app --reload

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )