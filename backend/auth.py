"""
Coords - Authentication Utilities
Google OAuth + JWT + Session Management
"""
import os
import uuid
import httpx
import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
from fastapi import HTTPException, Request, Response
from motor.motor_asyncio import AsyncIOMotorDatabase

from models import User, UserSession, UserRole


JWT_SECRET = os.environ.get("JWT_SECRET", "coords-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
SESSION_EXPIRY_DAYS = 7


def generate_jwt(user_id: str, email: str, role: str, tenant_id: str) -> str:
    """Generate JWT token for custom auth"""
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "tenant_id": tenant_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=SESSION_EXPIRY_DAYS),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt(token: str) -> Optional[dict]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


async def get_session_from_emergent(session_id: str) -> Optional[dict]:
    """Fetch session data from Emergent Auth service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_id},
                timeout=10.0
            )
            if response.status_code == 200:
                return response.json()
            return None
    except Exception as e:
        print(f"Error fetching session from Emergent: {e}")
        return None


async def get_current_user(
    request: Request,
    db: AsyncIOMotorDatabase
) -> Tuple[Optional[User], Optional[str]]:
    """
    Get current user from session token (cookie or header)
    Returns: (user, error_message)
    """
    # Try cookie first
    session_token = request.cookies.get("session_token")
    
    # Fallback to Authorization header
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header[7:]
    
    if not session_token:
        return None, "No session token provided"
    
    # Check database for session
    session_doc = await db.user_sessions.find_one(
        {"session_token": session_token},
        {"_id": 0}
    )
    
    if not session_doc:
        return None, "Invalid session token"
    
    # Check expiry
    expires_at = session_doc.get("expires_at")
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        return None, "Session expired"
    
    # Get user
    user_doc = await db.users.find_one(
        {"user_id": session_doc["user_id"]},
        {"_id": 0}
    )
    
    if not user_doc:
        return None, "User not found"
    
    return User(**user_doc), None


def set_session_cookie(response: Response, session_token: str):
    """Set httpOnly session cookie"""
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=SESSION_EXPIRY_DAYS * 24 * 60 * 60
    )


def clear_session_cookie(response: Response):
    """Clear session cookie"""
    response.delete_cookie(
        key="session_token",
        path="/",
        secure=True,
        samesite="none"
    )


def check_permission(user: User, required_roles: list[UserRole]) -> bool:
    """Check if user has required role"""
    return user.role in required_roles


def require_roles(*roles: UserRole):
    """Decorator-style permission check"""
    async def check(user: User):
        if user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required: {[r.value for r in roles]}"
            )
        return True
    return check
