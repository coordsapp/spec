"""
Coords - Data Models
Event-disciplined, immutable, versioned, tenant-scoped
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Literal
from datetime import datetime, timezone
from enum import Enum
import uuid


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix"""
    return f"{prefix}{uuid.uuid4().hex[:12]}" if prefix else uuid.uuid4().hex[:12]


def utc_now() -> datetime:
    """Get current UTC datetime"""
    return datetime.now(timezone.utc)


# =============================================================================
# ENUMS
# =============================================================================

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ORG_ADMIN = "org_admin"
    OPERATOR = "operator"
    CARRIER_VIEWER = "carrier_viewer"


class DockStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"
    RESERVED = "reserved"


class CarrierStatus(str, Enum):
    ENROUTE = "enroute"
    ARRIVED = "arrived"
    LOADING = "loading"
    DEPARTED = "departed"
    DELAYED = "delayed"


class SLAStatus(str, Enum):
    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    BREACHED = "breached"


# =============================================================================
# AUTH MODELS
# =============================================================================

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    user_id: str = Field(default_factory=lambda: generate_id("user_"))
    email: str
    name: str
    picture: Optional[str] = None
    role: UserRole = UserRole.OPERATOR
    tenant_id: str = "default"
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class UserSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    session_id: str = Field(default_factory=lambda: generate_id("sess_"))
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=utc_now)


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user: User


# =============================================================================
# TENANT MODELS
# =============================================================================

class Tenant(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    tenant_id: str = Field(default_factory=lambda: generate_id("tenant_"))
    name: str
    handle: str  # e.g., "acme"
    plan: Literal["free", "team", "business", "enterprise"] = "free"
    created_at: datetime = Field(default_factory=utc_now)


# =============================================================================
# SPATIAL / LOCATION MODELS
# =============================================================================

class L1Coordinate(BaseModel):
    """Immutable Spatial Identifier (L1)"""
    model_config = ConfigDict(extra="ignore")
    
    coord_id: str = Field(default_factory=lambda: generate_id("coord_"))
    lat: float
    lng: float
    altitude: Optional[float] = None
    checksum: str  # FNV-1a 32-bit checksum
    raw: str  # Full L1 string: coords:l1:v1:38.8977,-77.0365,12.3*a7f3b912
    created_at: datetime = Field(default_factory=utc_now)


class L2Handle(BaseModel):
    """Human-Friendly Handle (L2)"""
    model_config = ConfigDict(extra="ignore")
    
    handle_id: str = Field(default_factory=lambda: generate_id("handle_"))
    handle: str  # e.g., @acme/warehouse/dock-1
    l1_coord_id: str  # Reference to L1Coordinate
    tenant_id: str
    verified: bool = False
    created_at: datetime = Field(default_factory=utc_now)


class Location(BaseModel):
    """Location with L1 and optional L2"""
    model_config = ConfigDict(extra="ignore")
    
    location_id: str = Field(default_factory=lambda: generate_id("loc_"))
    name: str
    lat: float
    lng: float
    l1_raw: Optional[str] = None
    l2_handle: Optional[str] = None
    tenant_id: str = "default"
    location_type: Literal["warehouse", "dock", "checkpoint", "custom"] = "custom"
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)


# =============================================================================
# DOCK MODELS
# =============================================================================

class Dock(BaseModel):
    """Dock entity with status and assignment"""
    model_config = ConfigDict(extra="ignore")
    
    dock_id: str = Field(default_factory=lambda: generate_id("dock_"))
    name: str
    location_id: str
    tenant_id: str = "default"
    status: DockStatus = DockStatus.AVAILABLE
    assigned_carrier_id: Optional[str] = None
    capacity: int = 1
    lat: float
    lng: float
    l2_handle: Optional[str] = None  # e.g., @acme/dock-1
    last_activity: Optional[datetime] = None
    turnaround_avg_mins: float = 45.0
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class DockAssignment(BaseModel):
    """Dock assignment event"""
    model_config = ConfigDict(extra="ignore")
    
    assignment_id: str = Field(default_factory=lambda: generate_id("assign_"))
    dock_id: str
    carrier_id: str
    assigned_by: str  # user_id
    assigned_at: datetime = Field(default_factory=utc_now)
    expected_arrival: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    departure_time: Optional[datetime] = None
    sla_deadline: Optional[datetime] = None
    status: Literal["pending", "active", "completed", "cancelled"] = "pending"


class DockCreate(BaseModel):
    name: str
    lat: float
    lng: float
    capacity: int = 1
    l2_handle: Optional[str] = None


class DockUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[DockStatus] = None
    capacity: Optional[int] = None


# =============================================================================
# CARRIER MODELS
# =============================================================================

class Carrier(BaseModel):
    """Carrier entity (truck, vehicle)"""
    model_config = ConfigDict(extra="ignore")
    
    carrier_id: str = Field(default_factory=lambda: generate_id("carrier_"))
    name: str
    code: str  # e.g., "TRK-001"
    tenant_id: str = "default"
    status: CarrierStatus = CarrierStatus.ENROUTE
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None
    destination_dock_id: Optional[str] = None
    eta_minutes: Optional[int] = None
    distance_km: Optional[float] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class CarrierCreate(BaseModel):
    name: str
    code: str
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None


class CarrierPositionUpdate(BaseModel):
    lat: float
    lng: float


# =============================================================================
# ROUTING MODELS
# =============================================================================

class RoutePlan(BaseModel):
    """Route plan for carrier"""
    model_config = ConfigDict(extra="ignore")
    
    route_id: str = Field(default_factory=lambda: generate_id("route_"))
    carrier_id: str
    origin_lat: float
    origin_lng: float
    destination_dock_id: str
    destination_lat: float
    destination_lng: float
    distance_km: float
    eta_minutes: int
    created_at: datetime = Field(default_factory=utc_now)


class RoutePlanRequest(BaseModel):
    carrier_id: str
    origin_lat: float
    origin_lng: float
    destination_dock_id: str


# =============================================================================
# SLA / ANALYTICS MODELS
# =============================================================================

class SLAMetric(BaseModel):
    """SLA compliance metric"""
    model_config = ConfigDict(extra="ignore")
    
    metric_id: str = Field(default_factory=lambda: generate_id("sla_"))
    tenant_id: str
    period_start: datetime
    period_end: datetime
    total_assignments: int = 0
    on_time_arrivals: int = 0
    late_arrivals: int = 0
    avg_turnaround_mins: float = 0.0
    compliance_rate: float = 0.0
    created_at: datetime = Field(default_factory=utc_now)


class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_docks: int
    available_docks: int
    occupied_docks: int
    active_carriers: int
    sla_compliance: float
    avg_turnaround: float
    pending_arrivals: int


# =============================================================================
# PROTOCOL VALIDATION MODELS
# =============================================================================

class L1ValidationRequest(BaseModel):
    l1_string: str


class L1ValidationResponse(BaseModel):
    valid: bool
    lat: Optional[float] = None
    lng: Optional[float] = None
    altitude: Optional[float] = None
    checksum: Optional[str] = None
    checksum_valid: Optional[bool] = None
    error: Optional[str] = None


class L2ResolveResponse(BaseModel):
    handle: str
    l1_raw: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    tenant_id: Optional[str] = None
    verified: bool = False
    error: Optional[str] = None
