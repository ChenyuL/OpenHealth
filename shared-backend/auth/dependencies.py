"""
Authentication dependencies for FastAPI
Provides user and admin authentication via JWT tokens
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
import logging

from ..config import settings
from ..database.dependencies import get_db_session
from ..database.models import User, AdminUser

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


class AuthenticationError(HTTPException):
    """Custom authentication error"""
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_token(token: str) -> Optional[dict]:
    """
    Verify JWT token and return payload
    """
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.error(f"JWT verification failed: {e}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db_session: Session = Depends(get_db_session)
) -> User:
    """
    Get current authenticated user from JWT token
    """
    try:
        # Verify token
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise AuthenticationError("Invalid token")
        
        # Extract user ID from token
        user_id: str = payload.get("sub")
        user_type: str = payload.get("type", "user")
        
        if user_id is None:
            raise AuthenticationError("Token missing user ID")
        
        if user_type != "user":
            raise AuthenticationError("Invalid token type for user access")
        
        # Get user from database
        stmt = select(User).where(User.id == user_id)
        result = db_session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user is None:
            raise AuthenticationError("User not found")
        
        # Update last active timestamp
        from datetime import datetime
        user.last_active = datetime.utcnow()
        db_session.add(user)
        db_session.commit()
        
        return user
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error in get_current_user: {e}")
        raise AuthenticationError()


async def get_current_admin_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db_session: Session = Depends(get_db_session)
) -> AdminUser:
    """
    Get current authenticated admin user from JWT token
    """
    try:
        # Verify token
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise AuthenticationError("Invalid token")
        
        # Extract admin user ID from token
        admin_user_id: str = payload.get("sub")
        user_type: str = payload.get("type", "user")
        
        if admin_user_id is None:
            raise AuthenticationError("Token missing admin user ID")
        
        if user_type != "admin":
            raise AuthenticationError("Invalid token type for admin access")
        
        # Get admin user from database
        stmt = select(AdminUser).where(AdminUser.id == admin_user_id)
        result = db_session.execute(stmt)
        admin_user = result.scalar_one_or_none()
        
        if admin_user is None:
            raise AuthenticationError("Admin user not found")
        
        # Update last login timestamp
        from datetime import datetime
        admin_user.last_login = datetime.utcnow()
        db_session.add(admin_user)
        db_session.commit()
        
        return admin_user
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error in get_current_admin_user: {e}")
        raise AuthenticationError()


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db_session: Session = Depends(get_db_session)
) -> Optional[User]:
    """
    Get current user if token is provided, otherwise return None
    Useful for endpoints that work for both authenticated and anonymous users
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials, db_session)
    except HTTPException:
        return None


def check_admin_permissions(admin_user: AdminUser, required_permissions: list) -> bool:
    """
    Check if admin user has required permissions
    """
    if not admin_user.permissions:
        return False
    
    # Super admin has all permissions
    if "super_admin" in admin_user.permissions:
        return True
    
    # Check if user has all required permissions
    user_permissions = set(admin_user.permissions)
    required_permissions_set = set(required_permissions)
    
    return required_permissions_set.issubset(user_permissions)


def require_admin_permissions(required_permissions: list):
    """
    Dependency factory for requiring specific admin permissions
    """
    async def permission_checker(
        admin_user: AdminUser = Depends(get_current_admin_user)
    ) -> AdminUser:
        if not check_admin_permissions(admin_user, required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {required_permissions}"
            )
        return admin_user
    
    return permission_checker


async def get_admin_with_permissions(permissions: list):
    """
    Get admin user with specific permissions
    """
    return Depends(require_admin_permissions(permissions))


# Common permission checks
async def get_admin_analyst(
    admin_user: AdminUser = Depends(require_admin_permissions(["view_conversations", "analyze_ventures"]))
) -> AdminUser:
    """Get admin user with analyst permissions"""
    return admin_user


async def get_admin_manager(
    admin_user: AdminUser = Depends(require_admin_permissions(["manage_users", "manage_ventures", "view_analytics"]))
) -> AdminUser:
    """Get admin user with manager permissions"""
    return admin_user


async def get_super_admin(
    admin_user: AdminUser = Depends(require_admin_permissions(["super_admin"]))
) -> AdminUser:
    """Get super admin user"""
    return admin_user


def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    """
    Create JWT access token
    """
    from datetime import datetime, timedelta
    
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create JWT refresh token
    """
    from datetime import datetime, timedelta
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


async def verify_refresh_token(token: str) -> Optional[dict]:
    """
    Verify refresh token and return payload
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Check if it's a refresh token
        if payload.get("type") != "refresh":
            return None
            
        return payload
    except JWTError:
        return None


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt
    """
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash
    """
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)