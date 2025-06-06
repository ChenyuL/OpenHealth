"""
Authentication endpoints for OpenHealth
Handles user registration, login, token management for both users and admins
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import logging
from email_validator import validate_email, EmailNotValidError

from ....database.dependencies import get_db_session
from ....database.models import User, AdminUser
from ....auth.dependencies import (
    hash_password, verify_password, create_access_token, 
    create_refresh_token, verify_refresh_token, get_current_user,
    get_current_admin_user
)
from ....config import settings

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


# Pydantic Models
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v.strip()


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class AdminLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordReset(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class WidgetUserCreate(BaseModel):
    session_id: str
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    company: Optional[str] = None


# Helper Functions
async def get_user_by_email(email: str, db_session: Session) -> Optional[User]:
    """Get user by email address"""
    stmt = select(User).where(User.email == email)
    result = db_session.execute(stmt)
    return result.scalar_one_or_none()


async def get_admin_by_email(email: str, db_session: Session) -> Optional[AdminUser]:
    """Get admin user by email address"""
    stmt = select(AdminUser).where(AdminUser.email == email)
    result = db_session.execute(stmt)
    return result.scalar_one_or_none()


async def create_user_response(user: User) -> Dict[str, Any]:
    """Create user response dictionary"""
    return {
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
        "company": user.company,
        "role": user.role,
        "phone": user.phone,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_active": user.last_active.isoformat() if user.last_active else None
    }


async def create_admin_response(admin: AdminUser) -> Dict[str, Any]:
    """Create admin user response dictionary"""
    return {
        "id": str(admin.id),
        "name": admin.name,
        "email": admin.email,
        "role": admin.role,
        "permissions": admin.permissions or [],
        "created_at": admin.created_at.isoformat() if admin.created_at else None,
        "last_login": admin.last_login.isoformat() if admin.last_login else None
    }


# Authentication Endpoints
@router.post("/register", response_model=TokenResponse)
async def register_user(
    user_data: UserRegister,
    db_session: Session = Depends(get_db_session)
):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = await get_user_by_email(user_data.email, db_session)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Create new user
        new_user = User(
            id=uuid.uuid4(),
            name=user_data.name,
            email=user_data.email,
            company=user_data.company,
            role=user_data.role,
            phone=user_data.phone,
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow(),
            metadata={"password_hash": hashed_password, "email_verified": False}
        )
        
        db_session.add(new_user)
        db_session.commit()
        db_session.refresh(new_user)
        
        # Create tokens
        access_token = create_access_token(
            data={"sub": str(new_user.id), "type": "user"}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(new_user.id), "type": "user"}
        )
        
        # Create response
        user_response = await create_user_response(new_user)
        
        logger.info(f"New user registered: {new_user.email}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


@router.post("/login", response_model=TokenResponse)
async def login_user(
    login_data: UserLogin,
    db_session: Session = Depends(get_db_session)
):
    """Login user and return tokens"""
    try:
        # Get user by email
        user = await get_user_by_email(login_data.email, db_session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        stored_password_hash = user.metadata.get("password_hash") if user.metadata else None
        if not stored_password_hash or not verify_password(login_data.password, stored_password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Update last active
        user.last_active = datetime.utcnow()
        db_session.add(user)
        db_session.commit()
        
        # Create tokens
        access_token = create_access_token(
            data={"sub": str(user.id), "type": "user"}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "type": "user"}
        )
        
        # Create response
        user_response = await create_user_response(user)
        
        logger.info(f"User logged in: {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to login"
        )


@router.post("/admin/login", response_model=TokenResponse)
async def login_admin(
    login_data: AdminLogin,
    db_session: Session = Depends(get_db_session)
):
    """Login admin user and return tokens"""
    try:
        # Get admin by email
        admin = await get_admin_by_email(login_data.email, db_session)
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid admin credentials"
            )
        
        # For demo purposes, we'll create a simple password check
        # In production, you'd store hashed passwords in the admin table
        if login_data.password != "admin123":  # Change this in production!
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid admin credentials"
            )
        
        # Update last login
        admin.last_login = datetime.utcnow()
        db_session.add(admin)
        db_session.commit()
        
        # Create tokens
        access_token = create_access_token(
            data={"sub": str(admin.id), "type": "admin"}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(admin.id), "type": "admin"}
        )
        
        # Create response
        admin_response = await create_admin_response(admin)
        
        logger.info(f"Admin logged in: {admin.email}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=admin_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in admin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to login admin"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh_data: RefreshTokenRequest,
    db_session: Session = Depends(get_db_session)
):
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        payload = await verify_refresh_token(refresh_data.refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        user_type = payload.get("type", "user")
        
        # Get user based on type
        if user_type == "admin":
            user = await get_admin_by_email_or_id(user_id, db_session)
            user_response = await create_admin_response(user) if user else None
        else:
            user = await get_user_by_id(user_id, db_session)
            user_response = await create_user_response(user) if user else None
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create new tokens
        access_token = create_access_token(
            data={"sub": str(user.id), "type": user_type}
        )
        new_refresh_token = create_refresh_token(
            data={"sub": str(user.id), "type": user_type}
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )


@router.post("/logout")
async def logout_user():
    """Logout user (client should discard tokens)"""
    # In a more sophisticated setup, you'd maintain a token blacklist
    return {"message": "Successfully logged out"}


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return await create_user_response(current_user)


@router.put("/profile")
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """Update user profile"""
    try:
        # Update user fields
        if profile_data.name is not None:
            current_user.name = profile_data.name.strip()
        
        if profile_data.company is not None:
            current_user.company = profile_data.company.strip() or None
        
        if profile_data.role is not None:
            current_user.role = profile_data.role.strip() or None
        
        if profile_data.phone is not None:
            current_user.phone = profile_data.phone.strip() or None
        
        if profile_data.metadata is not None:
            # Merge with existing metadata
            existing_metadata = current_user.metadata or {}
            existing_metadata.update(profile_data.metadata)
            current_user.metadata = existing_metadata
        
        current_user.updated_at = datetime.utcnow()
        
        db_session.add(current_user)
        db_session.commit()
        db_session.refresh(current_user)
        
        logger.info(f"User profile updated: {current_user.email}")
        
        return {
            "message": "Profile updated successfully",
            "user": await create_user_response(current_user)
        }
        
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.post("/widget/user")
async def get_or_create_widget_user(
    widget_data: WidgetUserCreate,
    db_session: Session = Depends(get_db_session)
):
    """Get or create user for widget interactions"""
    try:
        # Try to find existing user by session_id in metadata
        stmt = select(User).where(
            User.metadata['session_id'].astext == widget_data.session_id
        )
        result = db_session.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            return await create_user_response(existing_user)
        
        # Create new widget user
        user_email = widget_data.email or f"widget-{widget_data.session_id}@temp.openhealth.com"
        user_name = widget_data.name or "Healthcare Entrepreneur"
        
        new_user = User(
            id=uuid.uuid4(),
            name=user_name,
            email=user_email,
            company=widget_data.company,
            role="widget_user",
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow(),
            metadata={
                "session_id": widget_data.session_id,
                "source": "widget",
                "temporary": True
            }
        )
        
        db_session.add(new_user)
        db_session.commit()
        db_session.refresh(new_user)
        
        logger.info(f"Widget user created: {new_user.email}")
        
        return await create_user_response(new_user)
        
    except Exception as e:
        logger.error(f"Error creating widget user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create widget user"
        )


@router.post("/password-reset")
async def request_password_reset(
    reset_data: PasswordReset,
    db_session: Session = Depends(get_db_session)
):
    """Request password reset (placeholder - implement email sending)"""
    try:
        # Check if user exists
        user = await get_user_by_email(reset_data.email, db_session)
        
        # Always return success to prevent email enumeration
        # In production, send actual email with reset link
        
        if user:
            # Generate reset token (placeholder)
            reset_token = str(uuid.uuid4())
            
            # Store reset token in user metadata with expiration
            user_metadata = user.metadata or {}
            user_metadata.update({
                "password_reset_token": reset_token,
                "password_reset_expires": (datetime.utcnow() + timedelta(hours=1)).isoformat()
            })
            user.metadata = user_metadata
            
            db_session.add(user)
            db_session.commit()
            
            logger.info(f"Password reset requested for: {user.email}")
            
            # TODO: Send email with reset link
            # send_password_reset_email(user.email, reset_token)
        
        return {"message": "If the email exists, a password reset link has been sent"}
        
    except Exception as e:
        logger.error(f"Error requesting password reset: {e}")
        return {"message": "If the email exists, a password reset link has been sent"}


# Helper functions for token refresh
async def get_user_by_id(user_id: str, db_session: Session) -> Optional[User]:
    """Get user by ID"""
    try:
        stmt = select(User).where(User.id == uuid.UUID(user_id))
        result = db_session.execute(stmt)
        return result.scalar_one_or_none()
    except Exception:
        return None


async def get_admin_by_email_or_id(user_id: str, db_session: Session) -> Optional[AdminUser]:
    """Get admin by ID"""
    try:
        stmt = select(AdminUser).where(AdminUser.id == uuid.UUID(user_id))
        result = db_session.execute(stmt)
        return result.scalar_one_or_none()
    except Exception:
        return None