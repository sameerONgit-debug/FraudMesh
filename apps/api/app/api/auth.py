"""
Authentication API endpoints

JWT-based authentication for FraudMesh.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from typing import Optional
import jwt
import logging

from app.core.config import settings
from app.schemas.schemas import AuthRequest, AuthResponse, TokenData

logger = logging.getLogger(__name__)
router = APIRouter()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


@router.post("/token", response_model=AuthResponse)
async def login(auth_request: AuthRequest):
    """
    Authenticate and get access token
    
    For MVP demo, authentication is simplified.
    In production, integrate with proper identity provider.
    """
    # Simulated authentication
    # In production: verify credentials against identity provider
    
    # Demo users
    demo_users = {
        "admin": {"role": "ADMIN", "institution_id": "FRAUDMESH"},
        "bank_a_analyst": {"role": "BANK_ANALYST", "institution_id": "BANK_A"},
        "bank_b_analyst": {"role": "BANK_ANALYST", "institution_id": "BANK_B"},
        "investigator_a": {"role": "INVESTIGATOR", "institution_id": "BANK_A"},
        "investigator_b": {"role": "INVESTIGATOR", "institution_id": "BANK_B"},
        "auditor": {"role": "AUDITOR", "institution_id": "FRAUDMESH"},
    }
    
    username = auth_request.username
    if username not in demo_users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    user_data = demo_users[username]
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    access_token = create_access_token(
        data={
            "sub": username,
            "institution_id": user_data["institution_id"],
            "role": user_data["role"]
        },
        expires_delta=access_token_expires
    )
    
    logger.info(f"User {username} authenticated as {user_data['role']}")
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        role=user_data["role"],
        institution_id=user_data["institution_id"]
    )


@router.get("/me", response_model=TokenData)
async def get_current_user(token: str):
    """Get current authenticated user info"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return TokenData(
            sub=payload.get("sub"),
            institution_id=payload.get("institution_id"),
            role=payload.get("role"),
            exp=datetime.fromtimestamp(payload.get("exp"))
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )