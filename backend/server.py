"""
Coords - Unified Spatial OS for Enterprise Logistics
Main FastAPI Server
"""
from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import uuid
import math
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone, timedelta

# Local imports
from models import (
    User, UserRole, Tenant, Location, Dock, DockStatus, DockCreate, DockUpdate,
    DockAssignment, Carrier, CarrierStatus, CarrierCreate, CarrierPositionUpdate,
    RoutePlan, RoutePlanRequest, SLAMetric, DashboardStats,
    L1ValidationRequest, L1ValidationResponse, L2ResolveResponse,
    LoginRequest, LoginResponse
)
from auth import (
    get_current_user, get_session_from_emergent, set_session_cookie,
    clear_session_cookie, hash_password, verify_password, generate_jwt,
    SESSION_EXPIRY_DAYS
)
from protocol import (
    generate_l1, parse_l1, generate_l2_handle,
    parse_l2_handle, coords_to_words, generate_checksum,
    build_canonical_payload, validate_test_vectors
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Coords - Spatial OS", version="1.0.0")

# Create API router
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_id(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:12]}" if prefix else uuid.uuid4().hex[:12]


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance in km using Haversine formula"""
    R = 6371  # Earth's radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


def estimate_eta(distance_km: float, avg_speed_kmh: float = 40) -> int:
    """Estimate ETA in minutes"""
    return int((distance_km / avg_speed_kmh) * 60)


async def get_authenticated_user(request: Request) -> User:
    """Dependency to get authenticated user"""
    user, error = await get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail=error or "Not authenticated")
    return user


# =============================================================================
# AUTH ROUTES
# =============================================================================

@api_router.post("/auth/session")
async def create_session(request: Request, response: Response):
    """
    Exchange Emergent session_id for local session
    REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    """
    body = await request.json()
    session_id = body.get("session_id")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id required")
    
    # Fetch session from Emergent
    session_data = await get_session_from_emergent(session_id)
    if not session_data:
        raise HTTPException(status_code=401, detail="Invalid session_id")
    
    email = session_data.get("email")
    name = session_data.get("name")
    picture = session_data.get("picture")
    session_token = session_data.get("session_token")
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": email}, {"_id": 0})
    
    if existing_user:
        user_id = existing_user["user_id"]
        # Update user info if needed
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"name": name, "picture": picture, "updated_at": utc_now().isoformat()}}
        )
    else:
        # Create new user
        user_id = generate_id("user_")
        new_user = {
            "user_id": user_id,
            "email": email,
            "name": name,
            "picture": picture,
            "role": UserRole.OPERATOR.value,
            "tenant_id": "default",
            "created_at": utc_now().isoformat(),
            "updated_at": utc_now().isoformat()
        }
        await db.users.insert_one(new_user)
    
    # Create session
    expires_at = utc_now() + timedelta(days=SESSION_EXPIRY_DAYS)
    session_doc = {
        "session_id": generate_id("sess_"),
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": expires_at.isoformat(),
        "created_at": utc_now().isoformat()
    }
    await db.user_sessions.insert_one(session_doc)
    
    # Set cookie
    set_session_cookie(response, session_token)
    
    # Get updated user
    user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    
    return {"success": True, "user": user_doc}


@api_router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest, response: Response):
    """Custom email/password login"""
    user_doc = await db.users.find_one({"email": request.email}, {"_id": 0})
    
    if not user_doc or not user_doc.get("password_hash"):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(request.password, user_doc["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate session token
    session_token = generate_jwt(
        user_doc["user_id"],
        user_doc["email"],
        user_doc["role"],
        user_doc["tenant_id"]
    )
    
    # Store session
    expires_at = utc_now() + timedelta(days=SESSION_EXPIRY_DAYS)
    session_doc = {
        "session_id": generate_id("sess_"),
        "user_id": user_doc["user_id"],
        "session_token": session_token,
        "expires_at": expires_at.isoformat(),
        "created_at": utc_now().isoformat()
    }
    await db.user_sessions.insert_one(session_doc)
    
    set_session_cookie(response, session_token)
    
    user = User(**user_doc)
    return LoginResponse(token=session_token, user=user)


@api_router.post("/auth/register")
async def register(request: Request, response: Response):
    """Register new user with email/password"""
    body = await request.json()
    email = body.get("email")
    password = body.get("password")
    name = body.get("name", email.split("@")[0])
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")
    
    # Check if user exists
    existing = await db.users.find_one({"email": email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create user
    user_id = generate_id("user_")
    password_hash = hash_password(password)
    
    user_doc = {
        "user_id": user_id,
        "email": email,
        "name": name,
        "password_hash": password_hash,
        "role": UserRole.OPERATOR.value,
        "tenant_id": "default",
        "created_at": utc_now().isoformat(),
        "updated_at": utc_now().isoformat()
    }
    await db.users.insert_one(user_doc)
    
    # Generate token and session
    session_token = generate_jwt(user_id, email, UserRole.OPERATOR.value, "default")
    expires_at = utc_now() + timedelta(days=SESSION_EXPIRY_DAYS)
    
    session_doc = {
        "session_id": generate_id("sess_"),
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": expires_at.isoformat(),
        "created_at": utc_now().isoformat()
    }
    await db.user_sessions.insert_one(session_doc)
    
    set_session_cookie(response, session_token)
    
    # Remove password_hash from response
    del user_doc["password_hash"]
    
    return {"success": True, "user": user_doc, "token": session_token}


@api_router.get("/auth/me")
async def get_me(request: Request):
    """Get current authenticated user"""
    user = await get_authenticated_user(request)
    return user.model_dump()


@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    """Logout and clear session"""
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_one({"session_token": session_token})
    
    clear_session_cookie(response)
    return {"success": True}


# =============================================================================
# DOCK MANAGEMENT ROUTES
# =============================================================================

@api_router.get("/coordination/docks", response_model=List[dict])
async def get_docks(request: Request, status: Optional[str] = None):
    """Get all docks with optional status filter"""
    user = await get_authenticated_user(request)
    
    query = {"tenant_id": user.tenant_id}
    if status:
        query["status"] = status
    
    docks = await db.docks.find(query, {"_id": 0}).to_list(100)
    return docks


@api_router.get("/coordination/docks/{dock_id}")
async def get_dock(dock_id: str, request: Request):
    """Get dock by ID"""
    user = await get_authenticated_user(request)
    
    dock = await db.docks.find_one(
        {"dock_id": dock_id, "tenant_id": user.tenant_id},
        {"_id": 0}
    )
    if not dock:
        raise HTTPException(status_code=404, detail="Dock not found")
    
    return dock


@api_router.post("/coordination/docks")
async def create_dock(dock_data: DockCreate, request: Request):
    """Create a new dock"""
    user = await get_authenticated_user(request)
    
    # Generate L1 string for the dock location (spec-compliant with altitude)
    l1_raw = generate_l1(dock_data.lat, dock_data.lng, 0.0)
    
    # Create location entry
    location_id = generate_id("loc_")
    location_doc = {
        "location_id": location_id,
        "name": dock_data.name,
        "lat": dock_data.lat,
        "lng": dock_data.lng,
        "l1_raw": l1_raw,
        "l2_handle": dock_data.l2_handle,
        "tenant_id": user.tenant_id,
        "location_type": "dock",
        "created_at": utc_now().isoformat()
    }
    await db.locations.insert_one(location_doc)
    
    # Create dock
    dock_id = generate_id("dock_")
    dock_doc = {
        "dock_id": dock_id,
        "name": dock_data.name,
        "location_id": location_id,
        "tenant_id": user.tenant_id,
        "status": DockStatus.AVAILABLE.value,
        "assigned_carrier_id": None,
        "capacity": dock_data.capacity,
        "lat": dock_data.lat,
        "lng": dock_data.lng,
        "l1_raw": l1_raw,
        "l2_handle": dock_data.l2_handle,
        "last_activity": None,
        "turnaround_avg_mins": 45.0,
        "created_at": utc_now().isoformat(),
        "updated_at": utc_now().isoformat()
    }
    await db.docks.insert_one(dock_doc)
    
    del dock_doc["_id"] if "_id" in dock_doc else None
    return dock_doc


@api_router.patch("/coordination/docks/{dock_id}")
async def update_dock(dock_id: str, update: DockUpdate, request: Request):
    """Update dock status or details"""
    user = await get_authenticated_user(request)
    
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    update_data["updated_at"] = utc_now().isoformat()
    
    if update.status:
        update_data["status"] = update.status.value
    
    result = await db.docks.update_one(
        {"dock_id": dock_id, "tenant_id": user.tenant_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Dock not found")
    
    dock = await db.docks.find_one({"dock_id": dock_id}, {"_id": 0})
    return dock


@api_router.post("/coordination/assign-dock")
async def assign_dock(request: Request):
    """Assign a carrier to a dock"""
    user = await get_authenticated_user(request)
    body = await request.json()
    
    dock_id = body.get("dock_id")
    carrier_id = body.get("carrier_id")
    expected_arrival = body.get("expected_arrival")
    sla_deadline = body.get("sla_deadline")
    
    if not dock_id or not carrier_id:
        raise HTTPException(status_code=400, detail="dock_id and carrier_id required")
    
    # Check dock availability
    dock = await db.docks.find_one(
        {"dock_id": dock_id, "tenant_id": user.tenant_id},
        {"_id": 0}
    )
    if not dock:
        raise HTTPException(status_code=404, detail="Dock not found")
    
    if dock["status"] != DockStatus.AVAILABLE.value:
        raise HTTPException(status_code=400, detail=f"Dock is {dock['status']}")
    
    # Check carrier exists
    carrier = await db.carriers.find_one(
        {"carrier_id": carrier_id, "tenant_id": user.tenant_id},
        {"_id": 0}
    )
    if not carrier:
        raise HTTPException(status_code=404, detail="Carrier not found")
    
    # Create assignment
    assignment_id = generate_id("assign_")
    assignment_doc = {
        "assignment_id": assignment_id,
        "dock_id": dock_id,
        "carrier_id": carrier_id,
        "assigned_by": user.user_id,
        "assigned_at": utc_now().isoformat(),
        "expected_arrival": expected_arrival,
        "sla_deadline": sla_deadline,
        "status": "pending"
    }
    await db.dock_assignments.insert_one(assignment_doc)
    
    # Update dock status
    await db.docks.update_one(
        {"dock_id": dock_id},
        {"$set": {
            "status": DockStatus.RESERVED.value,
            "assigned_carrier_id": carrier_id,
            "updated_at": utc_now().isoformat()
        }}
    )
    
    # Update carrier destination
    await db.carriers.update_one(
        {"carrier_id": carrier_id},
        {"$set": {
            "destination_dock_id": dock_id,
            "updated_at": utc_now().isoformat()
        }}
    )
    
    del assignment_doc["_id"] if "_id" in assignment_doc else None
    return assignment_doc


# =============================================================================
# CARRIER ROUTES
# =============================================================================

@api_router.get("/carriers", response_model=List[dict])
async def get_carriers(request: Request, status: Optional[str] = None):
    """Get all carriers"""
    user = await get_authenticated_user(request)
    
    query = {"tenant_id": user.tenant_id}
    if status:
        query["status"] = status
    
    carriers = await db.carriers.find(query, {"_id": 0}).to_list(100)
    return carriers


@api_router.get("/carriers/{carrier_id}")
async def get_carrier(carrier_id: str, request: Request):
    """Get carrier by ID"""
    user = await get_authenticated_user(request)
    
    carrier = await db.carriers.find_one(
        {"carrier_id": carrier_id, "tenant_id": user.tenant_id},
        {"_id": 0}
    )
    if not carrier:
        raise HTTPException(status_code=404, detail="Carrier not found")
    
    return carrier


@api_router.post("/carriers")
async def create_carrier(carrier_data: CarrierCreate, request: Request):
    """Create a new carrier"""
    user = await get_authenticated_user(request)
    
    carrier_id = generate_id("carrier_")
    carrier_doc = {
        "carrier_id": carrier_id,
        "name": carrier_data.name,
        "code": carrier_data.code,
        "tenant_id": user.tenant_id,
        "status": CarrierStatus.ENROUTE.value,
        "current_lat": None,
        "current_lng": None,
        "destination_dock_id": None,
        "eta_minutes": None,
        "distance_km": None,
        "driver_name": carrier_data.driver_name,
        "driver_phone": carrier_data.driver_phone,
        "created_at": utc_now().isoformat(),
        "updated_at": utc_now().isoformat()
    }
    await db.carriers.insert_one(carrier_doc)
    
    del carrier_doc["_id"] if "_id" in carrier_doc else None
    return carrier_doc


@api_router.patch("/carriers/{carrier_id}/position")
async def update_carrier_position(carrier_id: str, position: CarrierPositionUpdate, request: Request):
    """Update carrier position and recalculate ETA"""
    user = await get_authenticated_user(request)
    
    carrier = await db.carriers.find_one(
        {"carrier_id": carrier_id, "tenant_id": user.tenant_id},
        {"_id": 0}
    )
    if not carrier:
        raise HTTPException(status_code=404, detail="Carrier not found")
    
    update_data = {
        "current_lat": position.lat,
        "current_lng": position.lng,
        "updated_at": utc_now().isoformat()
    }
    
    # Recalculate ETA if carrier has destination
    if carrier.get("destination_dock_id"):
        dock = await db.docks.find_one(
            {"dock_id": carrier["destination_dock_id"]},
            {"_id": 0}
        )
        if dock:
            distance = calculate_distance(position.lat, position.lng, dock["lat"], dock["lng"])
            eta = estimate_eta(distance)
            update_data["distance_km"] = round(distance, 2)
            update_data["eta_minutes"] = eta
    
    await db.carriers.update_one(
        {"carrier_id": carrier_id},
        {"$set": update_data}
    )
    
    updated = await db.carriers.find_one({"carrier_id": carrier_id}, {"_id": 0})
    return updated


# =============================================================================
# ROUTING ROUTES
# =============================================================================

@api_router.post("/v1/routing/plan")
async def create_route_plan(plan_request: RoutePlanRequest, request: Request):
    """Create a route plan for carrier to dock"""
    user = await get_authenticated_user(request)
    
    # Get destination dock
    dock = await db.docks.find_one(
        {"dock_id": plan_request.destination_dock_id, "tenant_id": user.tenant_id},
        {"_id": 0}
    )
    if not dock:
        raise HTTPException(status_code=404, detail="Destination dock not found")
    
    # Calculate distance and ETA
    distance = calculate_distance(
        plan_request.origin_lat, plan_request.origin_lng,
        dock["lat"], dock["lng"]
    )
    eta = estimate_eta(distance)
    
    # Create route plan
    route_id = generate_id("route_")
    route_doc = {
        "route_id": route_id,
        "carrier_id": plan_request.carrier_id,
        "origin_lat": plan_request.origin_lat,
        "origin_lng": plan_request.origin_lng,
        "destination_dock_id": plan_request.destination_dock_id,
        "destination_lat": dock["lat"],
        "destination_lng": dock["lng"],
        "distance_km": round(distance, 2),
        "eta_minutes": eta,
        "created_at": utc_now().isoformat()
    }
    await db.route_plans.insert_one(route_doc)
    
    # Update carrier with route info
    await db.carriers.update_one(
        {"carrier_id": plan_request.carrier_id},
        {"$set": {
            "destination_dock_id": plan_request.destination_dock_id,
            "distance_km": round(distance, 2),
            "eta_minutes": eta,
            "current_lat": plan_request.origin_lat,
            "current_lng": plan_request.origin_lng,
            "updated_at": utc_now().isoformat()
        }}
    )
    
    del route_doc["_id"] if "_id" in route_doc else None
    return route_doc


# =============================================================================
# PROTOCOL / RESOLVE ROUTES
# =============================================================================

@api_router.post("/v1/protocol/validate", response_model=L1ValidationResponse)
async def validate_l1(validation: L1ValidationRequest):
    """Validate L1 spatial identifier per spec"""
    valid, data, error = parse_l1(validation.l1_string)
    
    if not valid:
        return L1ValidationResponse(valid=False, error=error)
    
    return L1ValidationResponse(
        valid=True,
        lat=data["lat"],
        lng=data["lng"],
        altitude=data.get("alt"),
        checksum=data["checksum"],
        checksum_valid=data["checksum_valid"]
    )


@api_router.post("/v1/protocol/generate")
async def generate_l1_endpoint(request: Request):
    """Generate L1 string from coordinates (spec-compliant)"""
    body = await request.json()
    lat = body.get("lat")
    lng = body.get("lng")
    alt = body.get("alt", 0.0)  # Altitude required per spec, default 0
    
    if lat is None or lng is None:
        raise HTTPException(status_code=400, detail="lat and lng required")
    
    # Validate ranges
    if not (-90 <= lat <= 90):
        raise HTTPException(status_code=400, detail=f"Latitude {lat} out of range [-90, 90]")
    if not (-180 <= lng <= 180):
        raise HTTPException(status_code=400, detail=f"Longitude {lng} out of range [-180, 180]")
    
    l1_uri = generate_l1(lat, lng, alt)
    checksum = generate_checksum(lat, lng, alt)
    canonical = build_canonical_payload(lat, lng, alt)
    words = coords_to_words(lat, lng)
    
    return {
        "l1": l1_uri,
        "checksum": checksum,
        "canonical_payload": canonical,
        "lat": lat,
        "lng": lng,
        "alt": alt,
        "words": words
    }


@api_router.get("/v1/protocol/test-vectors")
async def get_test_vectors():
    """Return spec test vector validation results"""
    results = validate_test_vectors()
    all_pass = all(r["checksum_pass"] and r["uri_pass"] for r in results)
    return {
        "spec_compliant": all_pass,
        "vectors": results
    }


@api_router.get("/v1/resolve/{handle:path}", response_model=L2ResolveResponse)
async def resolve_l2(handle: str, request: Request):
    """Resolve L2 handle to L1 coordinates"""
    # Add @ prefix if not present
    if not handle.startswith("@"):
        handle = f"@{handle}"
    
    valid, data, error = parse_l2_handle(handle)
    if not valid:
        return L2ResolveResponse(handle=handle, error=error)
    
    # Look up in database
    location = await db.locations.find_one(
        {"l2_handle": handle},
        {"_id": 0}
    )
    
    if not location:
        # Try docks
        dock = await db.docks.find_one({"l2_handle": handle}, {"_id": 0})
        if dock:
            location = {
                "l1_raw": dock.get("l1_raw"),
                "lat": dock["lat"],
                "lng": dock["lng"],
                "tenant_id": dock["tenant_id"]
            }
    
    if not location:
        return L2ResolveResponse(handle=handle, error="Handle not found")
    
    return L2ResolveResponse(
        handle=handle,
        l1_raw=location.get("l1_raw"),
        lat=location.get("lat"),
        lng=location.get("lng"),
        tenant_id=location.get("tenant_id"),
        verified=True
    )


# =============================================================================
# ANALYTICS / SLA ROUTES
# =============================================================================

@api_router.get("/v1/analytics/sla-compliance")
async def get_sla_compliance(request: Request):
    """Get SLA compliance metrics"""
    user = await get_authenticated_user(request)
    
    # Get assignments for the tenant
    assignments = await db.dock_assignments.find(
        {"tenant_id": user.tenant_id} if "tenant_id" in await db.dock_assignments.find_one({}, {"_id": 0}) or {} else {}
    ).to_list(1000)
    
    total = len(assignments)
    on_time = sum(1 for a in assignments if a.get("status") == "completed" and 
                  a.get("actual_arrival") and a.get("sla_deadline") and
                  a["actual_arrival"] <= a["sla_deadline"])
    late = sum(1 for a in assignments if a.get("status") == "completed" and
               a.get("actual_arrival") and a.get("sla_deadline") and
               a["actual_arrival"] > a["sla_deadline"])
    
    compliance_rate = (on_time / total * 100) if total > 0 else 100.0
    
    return {
        "total_assignments": total,
        "on_time_arrivals": on_time,
        "late_arrivals": late,
        "compliance_rate": round(compliance_rate, 2),
        "period": "all_time"
    }


@api_router.get("/v1/analytics/dashboard")
async def get_dashboard_stats(request: Request):
    """Get dashboard statistics"""
    user = await get_authenticated_user(request)
    tenant_id = user.tenant_id
    
    # Count docks by status
    total_docks = await db.docks.count_documents({"tenant_id": tenant_id})
    available_docks = await db.docks.count_documents({"tenant_id": tenant_id, "status": DockStatus.AVAILABLE.value})
    occupied_docks = await db.docks.count_documents({"tenant_id": tenant_id, "status": DockStatus.OCCUPIED.value})
    
    # Count active carriers
    active_carriers = await db.carriers.count_documents({
        "tenant_id": tenant_id,
        "status": {"$in": [CarrierStatus.ENROUTE.value, CarrierStatus.LOADING.value]}
    })
    
    # Pending arrivals (reserved docks)
    pending_arrivals = await db.docks.count_documents({
        "tenant_id": tenant_id,
        "status": DockStatus.RESERVED.value
    })
    
    # Average turnaround
    docks = await db.docks.find({"tenant_id": tenant_id}, {"_id": 0, "turnaround_avg_mins": 1}).to_list(100)
    avg_turnaround = sum(d.get("turnaround_avg_mins", 45) for d in docks) / len(docks) if docks else 45.0
    
    # SLA compliance (simplified)
    sla_compliance = 95.5  # Mock value for demo
    
    return {
        "total_docks": total_docks,
        "available_docks": available_docks,
        "occupied_docks": occupied_docks,
        "active_carriers": active_carriers,
        "sla_compliance": sla_compliance,
        "avg_turnaround": round(avg_turnaround, 1),
        "pending_arrivals": pending_arrivals
    }


# =============================================================================
# NOTIFICATIONS ROUTES
# =============================================================================

@api_router.post("/v1/notifications/arrival-alert")
async def send_arrival_alert(request: Request):
    """Send arrival notification (mock)"""
    user = await get_authenticated_user(request)
    body = await request.json()
    
    carrier_id = body.get("carrier_id")
    dock_id = body.get("dock_id")
    message = body.get("message", "Carrier arriving soon")
    
    # In production, this would send actual notifications
    notification = {
        "notification_id": generate_id("notif_"),
        "type": "arrival_alert",
        "carrier_id": carrier_id,
        "dock_id": dock_id,
        "message": message,
        "sent_at": utc_now().isoformat(),
        "sent_by": user.user_id
    }
    
    await db.notifications.insert_one(notification)
    del notification["_id"] if "_id" in notification else None
    
    return {"success": True, "notification": notification}


# =============================================================================
# LOCATIONS ROUTES
# =============================================================================

@api_router.get("/locations", response_model=List[dict])
async def get_locations(request: Request):
    """Get all locations for the tenant"""
    user = await get_authenticated_user(request)
    
    locations = await db.locations.find(
        {"tenant_id": user.tenant_id},
        {"_id": 0}
    ).to_list(100)
    
    return locations


@api_router.post("/locations")
async def create_location(request: Request):
    """Create a new location"""
    user = await get_authenticated_user(request)
    body = await request.json()
    
    lat = body.get("lat")
    lng = body.get("lng")
    name = body.get("name", "Unnamed Location")
    location_type = body.get("type", "custom")
    l2_handle = body.get("l2_handle")
    
    if lat is None or lng is None:
        raise HTTPException(status_code=400, detail="lat and lng required")
    
    l1_raw = generate_l1(lat, lng, 0.0)
    
    location_doc = {
        "location_id": generate_id("loc_"),
        "name": name,
        "lat": lat,
        "lng": lng,
        "l1_raw": l1_raw,
        "l2_handle": l2_handle,
        "tenant_id": user.tenant_id,
        "location_type": location_type,
        "metadata": body.get("metadata", {}),
        "created_at": utc_now().isoformat()
    }
    await db.locations.insert_one(location_doc)
    
    del location_doc["_id"] if "_id" in location_doc else None
    return location_doc


# =============================================================================
# HEALTH CHECK
# =============================================================================

@api_router.get("/")
async def root():
    return {"message": "Coords API v1.0", "status": "operational"}


@api_router.get("/health")
async def health():
    return {"status": "healthy", "timestamp": utc_now().isoformat()}


# =============================================================================
# APP SETUP
# =============================================================================

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Seed demo data on startup"""
    # Check if demo data exists
    demo_exists = await db.docks.find_one({"tenant_id": "default"})
    
    if not demo_exists:
        logger.info("Seeding demo data...")
        await seed_demo_data()


async def seed_demo_data():
    """Seed demo docks, carriers, and locations"""
    tenant_id = "default"
    
    # Demo docks (Washington DC area)
    demo_docks = [
        {"name": "Dock A1", "lat": 38.9072, "lng": -77.0369, "l2_handle": "@demo/dock-a1"},
        {"name": "Dock A2", "lat": 38.9082, "lng": -77.0359, "l2_handle": "@demo/dock-a2"},
        {"name": "Dock B1", "lat": 38.9062, "lng": -77.0379, "l2_handle": "@demo/dock-b1"},
        {"name": "Dock B2", "lat": 38.9092, "lng": -77.0349, "l2_handle": "@demo/dock-b2"},
        {"name": "Dock C1", "lat": 38.9052, "lng": -77.0389, "l2_handle": "@demo/dock-c1"},
        {"name": "Dock C2", "lat": 38.9102, "lng": -77.0339, "l2_handle": "@demo/dock-c2"},
    ]
    
    statuses = [DockStatus.AVAILABLE, DockStatus.OCCUPIED, DockStatus.AVAILABLE, 
                DockStatus.MAINTENANCE, DockStatus.AVAILABLE, DockStatus.RESERVED]
    
    for i, dock in enumerate(demo_docks):
        l1_raw = generate_l1(dock["lat"], dock["lng"], 0.0)
        location_id = generate_id("loc_")
        
        # Create location
        await db.locations.insert_one({
            "location_id": location_id,
            "name": dock["name"],
            "lat": dock["lat"],
            "lng": dock["lng"],
            "l1_raw": l1_raw,
            "l2_handle": dock["l2_handle"],
            "tenant_id": tenant_id,
            "location_type": "dock",
            "created_at": utc_now().isoformat()
        })
        
        # Create dock
        await db.docks.insert_one({
            "dock_id": generate_id("dock_"),
            "name": dock["name"],
            "location_id": location_id,
            "tenant_id": tenant_id,
            "status": statuses[i].value,
            "assigned_carrier_id": None,
            "capacity": 1,
            "lat": dock["lat"],
            "lng": dock["lng"],
            "l1_raw": l1_raw,
            "l2_handle": dock["l2_handle"],
            "last_activity": None,
            "turnaround_avg_mins": 40 + (i * 5),
            "created_at": utc_now().isoformat(),
            "updated_at": utc_now().isoformat()
        })
    
    # Demo carriers
    demo_carriers = [
        {"name": "Carrier Alpha", "code": "TRK-001", "lat": 38.9150, "lng": -77.0400, "status": CarrierStatus.ENROUTE},
        {"name": "Carrier Bravo", "code": "TRK-002", "lat": 38.9000, "lng": -77.0300, "status": CarrierStatus.LOADING},
        {"name": "Carrier Charlie", "code": "TRK-003", "lat": 38.9200, "lng": -77.0450, "status": CarrierStatus.ENROUTE},
        {"name": "Carrier Delta", "code": "TRK-004", "lat": 38.8950, "lng": -77.0250, "status": CarrierStatus.ARRIVED},
    ]
    
    for carrier in demo_carriers:
        await db.carriers.insert_one({
            "carrier_id": generate_id("carrier_"),
            "name": carrier["name"],
            "code": carrier["code"],
            "tenant_id": tenant_id,
            "status": carrier["status"].value,
            "current_lat": carrier["lat"],
            "current_lng": carrier["lng"],
            "destination_dock_id": None,
            "eta_minutes": 15 if carrier["status"] == CarrierStatus.ENROUTE else None,
            "distance_km": 5.2 if carrier["status"] == CarrierStatus.ENROUTE else None,
            "driver_name": f"Driver {carrier['code']}",
            "driver_phone": "+1-555-0100",
            "created_at": utc_now().isoformat(),
            "updated_at": utc_now().isoformat()
        })
    
    logger.info("Demo data seeded successfully")


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
